"""
safety.py — Safety Layer
Owner: Rishabh (Resource & Integration Lead)

Purpose:
This module is a FIRST-PASS, keyword-based safety net that scans a student's
check-in (primarily the free-text `optional_message`) for language that may
indicate an immediate safety concern. If triggered, the normal coaching /
triage / chatbot flow must be interrupted and the student should instead be
shown crisis and professional-support resources.

IMPORTANT — prototype scope & limitations:
- This is a deterministic keyword matcher, not a clinical assessment tool.
  It WILL miss things (false negatives) and WILL occasionally over-trigger
  (false positives). That's an intentional trade-off for a 5-hour hackathon:
  a keyword net is fast, transparent, and explainable to judges.
- In a real deployment this should be paired with (not replaced by) an LLM
  classifier for nuance, and reviewed with a campus counseling/safety
  professional before going live with real students.
- This module NEVER attempts to diagnose. It only flags "this needs a human,
  now" and routes accordingly.
- The system should not make this feel punitive — the resource copy is
  written to be calm and supportive, not alarming.
"""

from typing import Optional

# Phrases that plausibly indicate an immediate safety concern (self-harm,
# suicidal ideation, or intent to harm others). Kept as whole phrases rather
# than single high-frequency words (e.g. "die", "hurt") to reduce false
# positives from normal academic-stress language like "this exam is killing me".
_CRISIS_PHRASES = [
    "kill myself",
    "killing myself",
    "want to die",
    "wish i was dead",
    "wish i were dead",
    "end my life",
    "ending my life",
    "not want to be alive",
    "don't want to be alive",
    "no reason to live",
    "better off without me",
    "better off dead",
    "suicidal",
    "suicide",
    "self harm",
    "self-harm",
    "hurt myself",
    "hurting myself",
    "cutting myself",
    "harm myself",
    "can't go on",
    "cannot go on",
    "hurt someone",
    "hurt others",
    "kill someone",
]

_CRISIS_RESOURCES = [
    {
        "name": "988 Suicide & Crisis Lifeline",
        "description": "Free, confidential support available 24/7 by call or text.",
        "contact": "Call or text 988 (US)",
    },
    {
        "name": "Crisis Text Line",
        "description": "24/7 text-based crisis support from a trained counselor.",
        "contact": "Text HOME to 741741 (US)",
    },
    {
        "name": "Campus Counseling & Crisis Line",
        "description": "Same-day and emergency support through your campus counseling center.",
        "contact": "See campus counseling center website — REPLACE with actual campus number before demo/deploy",
    },
    {
        "name": "Emergency Services",
        "description": "If there is immediate danger to yourself or someone else.",
        "contact": "Call 911 (US) or campus public safety",
    },
]

_SUPPORTIVE_MESSAGE = (
    "It sounds like you might be going through something really difficult right now. "
    "You don't have to handle this alone — the resources below connect you with people "
    "who can help immediately."
)


def check_safety(check_in_data: dict) -> dict:
    """
    Scans a check-in for immediate safety concern signals.

    Args:
        check_in_data: dict that may include 'optional_message' (str) and
            other check-in fields. Only 'optional_message' is scanned;
            numeric fields (low sleep, high pressure, etc.) are handled by
            scoring.py and are NOT treated as safety signals on their own —
            severe academic stress is not the same thing as a safety crisis,
            and conflating the two would over-trigger constantly.

    Returns:
        dict:
            safety_concern (bool): True if the flow should be interrupted.
            trigger_source (str | None): where the match came from
                ('optional_message' or None).
            message (str | None): supportive framing text for the UI.
            resources (list[dict]): crisis resources to display, empty if
                no concern was found.
            action (str): 'interrupt_and_route' or 'continue_normal_flow'.
    """
    message: Optional[str] = check_in_data.get("optional_message")

    if not message or not isinstance(message, str):
        return _no_concern_result()

    normalized = message.lower()

    for phrase in _CRISIS_PHRASES:
        if phrase in normalized:
            return {
                "safety_concern": True,
                "trigger_source": "optional_message",
                "message": _SUPPORTIVE_MESSAGE,
                "resources": _CRISIS_RESOURCES,
                "action": "interrupt_and_route",
            }

    return _no_concern_result()


def _no_concern_result() -> dict:
    return {
        "safety_concern": False,
        "trigger_source": None,
        "message": None,
        "resources": [],
        "action": "continue_normal_flow",
    }


# Manual smoke tests
if __name__ == "__main__":
    test_cases = [
        {"optional_message": "I have three assignments and I don't think I can finish."},
        {"optional_message": "I just want to end my life, I can't do this anymore."},
        {"optional_message": None},
        {},
        {"optional_message": "This exam is literally killing me lol"},
    ]
    for case in test_cases:
        print(case, "->", check_safety(case)["safety_concern"])
