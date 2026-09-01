"""
integration.py — Resource & Integration Layer
Owner: Rishabh (Resource & Integration Lead)

Purpose:
This is the single entry point the frontend (Hansika) and chatbot (Sahithya)
should call. It is responsible for:
  1. Validating incoming check-in / task data (fail loud with clear errors
     rather than letting bad data silently corrupt scores/plans).
  2. Persisting the check-in to the database.
  3. Running the SAFETY LAYER FIRST, before any triage/coaching logic.
     If a safety concern is detected, normal flow is skipped entirely and
     a crisis-routing payload is returned instead.
  4. Otherwise, running Rishik's deterministic pipeline
     (scoring + trends + planning) via build_ai_context_payload, with
     defensive handling for edge cases (new students, missing history).
  5. Mapping the results to campus resources.
  6. Packaging one final response dict with everything the UI and the
     AI/chatbot need.

Usage:
    from integration import run_pipeline

    result = run_pipeline(
        student_id="student_001",
        check_in_data={...},
        tasks=[...],
        available_hours=4,
    )

    if result["safety_concern"]:
        # show crisis resources, do NOT proceed to normal dashboard/chat
        ...
    else:
        ui_data = result["ui_data"]
        ai_context = result["ai_prompt_context"]
        resources = result["resources"]
"""

import sqlite3
from datetime import datetime

from database import DB_NAME, init_db
from safety import check_safety
from resources import map_resources
from planner import build_ai_context_payload


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

REQUIRED_CHECK_IN_FIELDS = {
    "sleep_hours": (int, float),
    "mood_score": (int,),
    "energy_level": (int,),
    "workload_level": (int,),
    "academic_pressure": (int,),
    "deadlines_count": (int,),
}

# (field, min, max) — inclusive bounds for the 1-10 style scales.
_SCALE_BOUNDS = {
    "mood_score": (1, 10),
    "energy_level": (1, 10),
    "workload_level": (1, 10),
    "academic_pressure": (1, 10),
}


class ValidationError(ValueError):
    """Raised when incoming check-in or task data is malformed."""


def validate_check_in(check_in_data: dict) -> None:
    if not isinstance(check_in_data, dict):
        raise ValidationError("check_in_data must be a dict.")

    for field, expected_types in REQUIRED_CHECK_IN_FIELDS.items():
        if field not in check_in_data:
            raise ValidationError(f"Missing required check-in field: '{field}'.")
        value = check_in_data[field]
        if not isinstance(value, expected_types) or isinstance(value, bool):
            raise ValidationError(
                f"Field '{field}' must be of type {expected_types}, got {type(value).__name__}."
            )

    if check_in_data["sleep_hours"] < 0 or check_in_data["sleep_hours"] > 24:
        raise ValidationError("Field 'sleep_hours' must be between 0 and 24.")

    if check_in_data["deadlines_count"] < 0:
        raise ValidationError("Field 'deadlines_count' cannot be negative.")

    for field, (lo, hi) in _SCALE_BOUNDS.items():
        value = check_in_data[field]
        if value < lo or value > hi:
            raise ValidationError(f"Field '{field}' must be between {lo} and {hi}, got {value}.")

    message = check_in_data.get("optional_message")
    if message is not None and not isinstance(message, str):
        raise ValidationError("Field 'optional_message' must be a string or None.")


def validate_tasks(tasks: list) -> None:
    if not isinstance(tasks, list):
        raise ValidationError("tasks must be a list.")

    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ValidationError(f"Task at index {i} must be a dict.")
        for field in ("name", "days_until_due", "estimated_hours"):
            if field not in task:
                raise ValidationError(f"Task at index {i} is missing required field '{field}'.")
        if not isinstance(task["name"], str) or not task["name"].strip():
            raise ValidationError(f"Task at index {i} has an invalid 'name'.")
        if not isinstance(task["days_until_due"], (int, float)):
            raise ValidationError(f"Task at index {i}: 'days_until_due' must be numeric.")
        if not isinstance(task["estimated_hours"], (int, float)) or task["estimated_hours"] < 0:
            raise ValidationError(f"Task at index {i}: 'estimated_hours' must be a non-negative number.")
        # Overdue tasks are allowed (days_until_due can be <= 0); planner.py's
        # urgency formula (1 / (days_until_due + 0.1)) only breaks for
        # days_until_due == -0.1 exactly, which we block explicitly:
        if task["days_until_due"] == -0.1:
            raise ValidationError(f"Task at index {i}: 'days_until_due' cannot be exactly -0.1.")


def validate_available_hours(available_hours) -> None:
    if not isinstance(available_hours, (int, float)) or isinstance(available_hours, bool):
        raise ValidationError("available_hours must be a number.")
    if available_hours < 0:
        raise ValidationError("available_hours cannot be negative.")


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_check_in(student_id: str, check_in_data: dict) -> None:
    """Persists a validated check-in to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO check_ins (
            student_id, sleep_hours, mood_score, energy_level,
            workload_level, academic_pressure, deadlines_count, optional_message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student_id,
            check_in_data["sleep_hours"],
            check_in_data["mood_score"],
            check_in_data["energy_level"],
            check_in_data["workload_level"],
            check_in_data["academic_pressure"],
            check_in_data["deadlines_count"],
            check_in_data.get("optional_message"),
        ),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_pipeline(
    student_id: str,
    check_in_data: dict,
    tasks: list,
    available_hours: float,
    primary_need: str | None = None,
    persist: bool = True,
) -> dict:
    """
    Full end-to-end integration entry point.

    Args:
        student_id: unique student identifier.
        check_in_data: dict matching REQUIRED_CHECK_IN_FIELDS (+ optional
            'optional_message').
        tasks: list of {'name', 'days_until_due', 'estimated_hours'} dicts.
        available_hours: hours the student has available today.
        primary_need: optional category string from Sahithya's AI triage
            engine, used to sharpen resource routing. Safe to omit.
        persist: whether to write this check-in to the database. Defaults
            to True; set False for tests/dry-runs.

    Returns:
        On safety concern:
            {
              "safety_concern": True,
              "message": str,
              "resources": [...],
            }

        On normal flow:
            {
              "safety_concern": False,
              "ui_data": {...},            # -> Hansika (Streamlit UI)
              "ai_prompt_context": str,    # -> Sahithya (LLM system prompt)
              "resources": [...],          # -> both UI display + chatbot routing
            }

    Raises:
        ValidationError: if check_in_data / tasks / available_hours are
            malformed. Callers (UI layer) should catch this and show a
            friendly "please check your inputs" message rather than crash.
    """
    if not student_id or not isinstance(student_id, str):
        raise ValidationError("student_id must be a non-empty string.")

    validate_check_in(check_in_data)
    validate_tasks(tasks)
    validate_available_hours(available_hours)

    # Guarantee the DB schema exists before ANY query touches it — this is
    # unconditional (independent of `persist`) because analytics.py's
    # get_student_trends() assumes the `check_ins` table already exists and
    # will raise "no such table" on a completely fresh environment
    # (new clone, CI run, or a persist=False dry-run) otherwise.
    # init_db() is idempotent (CREATE TABLE IF NOT EXISTS), so this is safe
    # to call on every request.
    _ensure_db_ready()

    # --- Safety gate runs before anything else, on every check-in. ---
    safety_result = check_safety(check_in_data)
    if safety_result["safety_concern"]:
        if persist:
            _safe_persist(student_id, check_in_data)
        return {
            "safety_concern": True,
            "message": safety_result["message"],
            "resources": safety_result["resources"],
        }

    if persist:
        _safe_persist(student_id, check_in_data)

    # --- Normal deterministic pipeline (Rishik's modules). ---
    try:
        system_data = build_ai_context_payload(
            student_id=student_id,
            current_check_in=check_in_data,
            tasks=tasks,
            available_hours=available_hours,
        )
    except Exception as exc:
        # Defensive fallback: don't let a downstream bug (e.g. analytics.py
        # choking on a brand-new student, or a malformed task) take down
        # the whole check-in flow. Surface a degraded-but-usable payload.
        return {
            "safety_concern": False,
            "ui_data": None,
            "ai_prompt_context": (
                "[SYSTEM CONTEXT - DO NOT EXPOSE TO USER]\n"
                "The backend analysis pipeline encountered an error and could not "
                "produce a full assessment. Respond supportively and generically; "
                "do not claim to know the student's specific status."
            ),
            "resources": map_resources(support_level=None),
            "error": f"{type(exc).__name__}: {exc}",
        }

    score_data = system_data["raw_data"]["score"]
    trend_data = system_data["raw_data"]["trends"]

    resources = map_resources(
        flags=score_data.get("identified_flags", []),
        support_level=score_data.get("support_level"),
        chronic_warnings=trend_data.get("warnings", {}),
        primary_need=primary_need,
    )

    return {
        "safety_concern": False,
        "ui_data": system_data["raw_data"],
        "ai_prompt_context": system_data["ai_prompt_context"],
        "resources": resources,
    }


def _ensure_db_ready() -> None:
    """Idempotently ensure the database file and schema exist."""
    try:
        init_db()
    except Exception as exc:
        print(f"[integration] WARNING: failed to initialize database: {exc}")


def _safe_persist(student_id: str, check_in_data: dict) -> None:
    """Persist check-in without letting a DB error break the pipeline."""
    try:
        save_check_in(student_id, check_in_data)
    except Exception as exc:
        # In a hackathon prototype, losing a DB write shouldn't block the
        # student from getting a response. Log and move on.
        print(f"[integration] WARNING: failed to persist check-in: {exc}")


# Manual smoke test
if __name__ == "__main__":
    demo_check_in = {
        "sleep_hours": 4.5,
        "mood_score": 4,
        "energy_level": 3,
        "workload_level": 9,
        "academic_pressure": 9,
        "deadlines_count": 3,
        "optional_message": "I have three assignments and I don't think I can finish.",
    }
    demo_tasks = [
        {"name": "Essay", "days_until_due": 1, "estimated_hours": 3},
        {"name": "Python HW", "days_until_due": 2, "estimated_hours": 4},
    ]

    print("=== Normal flow ===")
    result = run_pipeline("student_demo", demo_check_in, demo_tasks, available_hours=4, persist=False)
    print("safety_concern:", result["safety_concern"])
    print("support_level:", result["ui_data"]["score"]["support_level"])
    print("resources:", [r["key"] for r in result["resources"]])

    print("\n=== Safety-triggered flow ===")
    crisis_check_in = dict(demo_check_in)
    crisis_check_in["optional_message"] = "I want to end my life, I can't do this anymore."
    result = run_pipeline("student_demo", crisis_check_in, demo_tasks, available_hours=4, persist=False)
    print("safety_concern:", result["safety_concern"])
    print("resources:", [r["name"] for r in result["resources"]])

    print("\n=== Validation error flow ===")
    try:
        run_pipeline("student_demo", {"sleep_hours": 5}, demo_tasks, available_hours=4, persist=False)
    except ValidationError as e:
        print("Correctly raised ValidationError:", e)