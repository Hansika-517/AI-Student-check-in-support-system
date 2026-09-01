"""
test_integration.py — Test suite for the Integration & Safety Layer
Owner: Rishabh (Resource & Integration Lead)

Run with:  python3 -m pytest test_integration.py -v
       or:  python3 test_integration.py
"""

import os
import sqlite3
import unittest

from database import DB_NAME, init_db
from safety import check_safety
from resources import map_resources, RESOURCE_DATABASE
from integration import (
    run_pipeline,
    validate_check_in,
    validate_tasks,
    validate_available_hours,
    ValidationError,
)


GOOD_CHECK_IN = {
    "sleep_hours": 4.5,
    "mood_score": 4,
    "energy_level": 3,
    "workload_level": 9,
    "academic_pressure": 9,
    "deadlines_count": 3,
    "optional_message": "I have three assignments and I don't think I can finish.",
}

GOOD_TASKS = [
    {"name": "Essay", "days_until_due": 1, "estimated_hours": 3},
    {"name": "Python HW", "days_until_due": 2, "estimated_hours": 4},
]


class TestSafetyLayer(unittest.TestCase):
    def test_no_message_is_safe(self):
        self.assertFalse(check_safety({})["safety_concern"])

    def test_none_message_is_safe(self):
        self.assertFalse(check_safety({"optional_message": None})["safety_concern"])

    def test_normal_stressed_message_is_safe(self):
        result = check_safety({"optional_message": "I have three assignments and I don't think I can finish."})
        self.assertFalse(result["safety_concern"])

    def test_hyperbolic_language_does_not_false_positive(self):
        result = check_safety({"optional_message": "This exam is literally killing me lol"})
        self.assertFalse(result["safety_concern"])

    def test_crisis_phrase_triggers_concern(self):
        result = check_safety({"optional_message": "I just want to end my life."})
        self.assertTrue(result["safety_concern"])
        self.assertEqual(result["action"], "interrupt_and_route")
        self.assertGreater(len(result["resources"]), 0)

    def test_case_insensitivity(self):
        result = check_safety({"optional_message": "I WANT TO KILL MYSELF"})
        self.assertTrue(result["safety_concern"])

    def test_harm_to_others_triggers_concern(self):
        result = check_safety({"optional_message": "Honestly I just want to hurt someone right now."})
        self.assertTrue(result["safety_concern"])


class TestResourceMapping(unittest.TestCase):
    def test_high_support_level_always_includes_counseling(self):
        resources = map_resources(flags=[], support_level="High")
        keys = [r["key"] for r in resources]
        self.assertIn("counseling", keys)

    def test_low_support_no_flags_returns_fallback(self):
        resources = map_resources(flags=[], support_level="Low")
        self.assertEqual([r["key"] for r in resources], ["student_life"])

    def test_flags_map_to_expected_resources(self):
        resources = map_resources(flags=["Low Sleep"], support_level="Low")
        keys = [r["key"] for r in resources]
        self.assertIn("student_life", keys)
        self.assertIn("counseling", keys)

    def test_primary_need_writing_difficulty(self):
        resources = map_resources(primary_need="writing_difficulty")
        self.assertEqual([r["key"] for r in resources], ["writing_center"])

    def test_primary_need_financial_concern(self):
        resources = map_resources(primary_need="financial_concern")
        self.assertEqual([r["key"] for r in resources], ["financial_aid"])

    def test_no_duplicate_resources(self):
        resources = map_resources(
            flags=["High Pressure", "High Workload/Deadlines"],
            support_level="High",
            chronic_warnings={"chronic_academic_pressure": True},
        )
        keys = [r["key"] for r in resources]
        self.assertEqual(len(keys), len(set(keys)))

    def test_unknown_flag_does_not_crash(self):
        resources = map_resources(flags=["Some Unrecognized Flag"], support_level="Low")
        self.assertTrue(len(resources) >= 1)  # falls back to student_life

    def test_all_resource_database_entries_have_required_fields(self):
        for key, entry in RESOURCE_DATABASE.items():
            self.assertIn("name", entry)
            self.assertIn("description", entry)
            self.assertIn("contact", entry)


class TestValidation(unittest.TestCase):
    def test_valid_check_in_passes(self):
        validate_check_in(GOOD_CHECK_IN)  # should not raise

    def test_missing_field_raises(self):
        bad = dict(GOOD_CHECK_IN)
        del bad["mood_score"]
        with self.assertRaises(ValidationError):
            validate_check_in(bad)

    def test_wrong_type_raises(self):
        bad = dict(GOOD_CHECK_IN)
        bad["energy_level"] = "high"  # should be int
        with self.assertRaises(ValidationError):
            validate_check_in(bad)

    def test_bool_rejected_for_numeric_field(self):
        # bool is a subclass of int in Python; must not silently pass as a score.
        bad = dict(GOOD_CHECK_IN)
        bad["mood_score"] = True
        with self.assertRaises(ValidationError):
            validate_check_in(bad)

    def test_out_of_range_scale_raises(self):
        bad = dict(GOOD_CHECK_IN)
        bad["academic_pressure"] = 15
        with self.assertRaises(ValidationError):
            validate_check_in(bad)

    def test_negative_sleep_hours_raises(self):
        bad = dict(GOOD_CHECK_IN)
        bad["sleep_hours"] = -1
        with self.assertRaises(ValidationError):
            validate_check_in(bad)

    def test_negative_deadlines_raises(self):
        bad = dict(GOOD_CHECK_IN)
        bad["deadlines_count"] = -2
        with self.assertRaises(ValidationError):
            validate_check_in(bad)

    def test_non_string_optional_message_raises(self):
        bad = dict(GOOD_CHECK_IN)
        bad["optional_message"] = 12345
        with self.assertRaises(ValidationError):
            validate_check_in(bad)

    def test_valid_tasks_pass(self):
        validate_tasks(GOOD_TASKS)  # should not raise

    def test_tasks_not_a_list_raises(self):
        with self.assertRaises(ValidationError):
            validate_tasks({"name": "Essay"})

    def test_task_missing_field_raises(self):
        bad_tasks = [{"name": "Essay", "days_until_due": 1}]  # missing estimated_hours
        with self.assertRaises(ValidationError):
            validate_tasks(bad_tasks)

    def test_task_negative_estimated_hours_raises(self):
        bad_tasks = [{"name": "Essay", "days_until_due": 1, "estimated_hours": -3}]
        with self.assertRaises(ValidationError):
            validate_tasks(bad_tasks)

    def test_overdue_task_is_allowed(self):
        # days_until_due can legitimately be 0 or negative (overdue) —
        # should NOT raise.
        overdue_tasks = [{"name": "Late HW", "days_until_due": -2, "estimated_hours": 1}]
        validate_tasks(overdue_tasks)

    def test_task_division_edge_case_blocked(self):
        # planner.py computes 1 / (days_until_due + 0.1); days_until_due
        # == -0.1 would be a ZeroDivisionError downstream.
        bad_tasks = [{"name": "Edge", "days_until_due": -0.1, "estimated_hours": 1}]
        with self.assertRaises(ValidationError):
            validate_tasks(bad_tasks)

    def test_empty_tasks_list_is_allowed(self):
        validate_tasks([])  # a student with no tasks is valid

    def test_negative_available_hours_raises(self):
        with self.assertRaises(ValidationError):
            validate_available_hours(-1)

    def test_non_numeric_available_hours_raises(self):
        with self.assertRaises(ValidationError):
            validate_available_hours("four")


class TestPipelineIntegration(unittest.TestCase):
    def test_killer_demo_flow_returns_high_support(self):
        result = run_pipeline("test_student_demo", GOOD_CHECK_IN, GOOD_TASKS, available_hours=4, persist=False)
        self.assertFalse(result["safety_concern"])
        self.assertEqual(result["ui_data"]["score"]["support_level"], "High")
        self.assertIn("ai_prompt_context", result)
        self.assertTrue(len(result["resources"]) > 0)

    def test_safety_concern_short_circuits_normal_flow(self):
        crisis_check_in = dict(GOOD_CHECK_IN)
        crisis_check_in["optional_message"] = "I want to end my life."
        result = run_pipeline("test_student_crisis", crisis_check_in, GOOD_TASKS, available_hours=4, persist=False)
        self.assertTrue(result["safety_concern"])
        self.assertNotIn("ui_data", result)  # normal payload keys absent
        self.assertTrue(len(result["resources"]) > 0)

    def test_invalid_input_raises_before_touching_pipeline(self):
        with self.assertRaises(ValidationError):
            run_pipeline("test_student_bad", {"sleep_hours": 5}, GOOD_TASKS, available_hours=4, persist=False)

    def test_empty_tasks_does_not_crash_pipeline(self):
        result = run_pipeline("test_student_notasks", GOOD_CHECK_IN, [], available_hours=4, persist=False)
        self.assertFalse(result["safety_concern"])
        self.assertEqual(result["ui_data"]["plan"]["action_plan"], [])

    def test_works_on_completely_fresh_environment_no_db_file(self):
        # Regression test: on a brand-new clone / CI run, student_support.db
        # doesn't exist yet and has no tables. run_pipeline must not depend
        # on persist=True having already created the schema.
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        self.assertFalse(os.path.exists(DB_NAME))
        result = run_pipeline("fresh_env_student", GOOD_CHECK_IN, GOOD_TASKS, available_hours=4, persist=False)
        self.assertFalse(result["safety_concern"])
        self.assertIsNotNone(result["ui_data"])
        self.assertNotIn("error", result)
        self.assertEqual(result["ui_data"]["score"]["support_level"], "High")

    def test_new_student_insufficient_history_does_not_crash(self):
        # A student with zero prior DB rows should degrade gracefully
        # (analytics.py returns status='insufficient_data') rather than error.
        result = run_pipeline(
            "brand_new_student_never_seen_before",
            GOOD_CHECK_IN,
            GOOD_TASKS,
            available_hours=4,
            persist=False,
        )
        self.assertFalse(result["safety_concern"])
        self.assertIn(result["ui_data"]["trends"]["status"], ("insufficient_data", "success"))

    def test_primary_need_sharpens_resources(self):
        result = run_pipeline(
            "test_student_writing",
            GOOD_CHECK_IN,
            GOOD_TASKS,
            available_hours=4,
            primary_need="writing_difficulty",
            persist=False,
        )
        keys = [r["key"] for r in result["resources"]]
        self.assertIn("writing_center", keys)

    def test_persist_true_writes_to_db(self):
        init_db()
        conn = sqlite3.connect(DB_NAME)
        before = conn.execute(
            "SELECT COUNT(*) FROM check_ins WHERE student_id = ?", ("test_student_persist",)
        ).fetchone()[0]
        conn.close()

        run_pipeline("test_student_persist", GOOD_CHECK_IN, GOOD_TASKS, available_hours=4, persist=True)

        conn = sqlite3.connect(DB_NAME)
        after = conn.execute(
            "SELECT COUNT(*) FROM check_ins WHERE student_id = ?", ("test_student_persist",)
        ).fetchone()[0]
        conn.close()
        self.assertEqual(after, before + 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)