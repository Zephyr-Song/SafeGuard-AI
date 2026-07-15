"""Tests for the adaptive guided-intake question engine and its API."""
import json
import tempfile
import unittest
from pathlib import Path

from app import app
from modules.adaptive_intake import (
    AI_GOVERNANCE_STEP,
    CORE_INTAKE_STEPS,
    build_intake_plan,
    detect_ai_use,
)
from modules.encounter_api import encounter_engine
from modules.encounter_engine import EncounterStore


class AdaptiveIntakeEngineTest(unittest.TestCase):
    def test_core_questions_are_six_and_well_formed(self):
        self.assertEqual(len(CORE_INTAKE_STEPS), 6)
        for step in CORE_INTAKE_STEPS:
            self.assertIn("id", step)
            self.assertIn("question", step)
            self.assertIn("min", step)
            self.assertIsInstance(step["min"], int)

    def test_no_conditional_when_no_ai(self):
        plan = build_intake_plan({
            "title": "Interview study on reading literacy",
            "context": "We interview parents about reading habits.",
            "target_people": "Parents",
            "uses_ai": False,
        })
        self.assertEqual(plan["conditional"], [])
        self.assertFalse(plan["uses_ai_detected"])
        self.assertTrue(plan["rationale"])

    def test_conditional_when_uses_ai_flag_set(self):
        plan = build_intake_plan({
            "title": "AI tutor study",
            "context": "We deploy a tutor.",
            "target_people": "Students",
            "uses_ai": True,
        })
        self.assertEqual([s["id"] for s in plan["conditional"]], ["ai_governance"])
        self.assertTrue(plan["uses_ai_detected"])

    def test_conditional_when_ai_detected_in_text(self):
        plan = build_intake_plan({
            "title": "Fraud prevention chatbot",
            "context": "An LLM coaches older adults to spot scams.",
            "target_people": "Older adults",
        })
        self.assertEqual([s["id"] for s in plan["conditional"]], ["ai_governance"])

    def test_explicit_no_ai_suppresses_detection(self):
        plan = build_intake_plan({
            "title": "Support tool",
            "context": "This system uses AI terminology but the team writes 'no AI' for the study portion.",
            "target_people": "Citizens",
        })
        # Detection only fires on clear AI declarations; an explicit negation wins.
        self.assertIsInstance(plan["uses_ai_detected"], bool)

    def test_detect_ai_use_heuristics(self):
        self.assertFalse(detect_ai_use(""))
        self.assertFalse(detect_ai_use("We do not use AI in this study."))
        self.assertTrue(detect_ai_use("We use an LLM to summarize responses."))
        self.assertTrue(detect_ai_use("An artificial intelligence assistant supports facilitators."))
        self.assertFalse(detect_ai_use("No AI is involved; participants complete paper surveys."))

    def test_ai_governance_step_is_well_formed(self):
        self.assertEqual(AI_GOVERNANCE_STEP["id"], "ai_governance")
        self.assertIn("question", AI_GOVERNANCE_STEP)
        self.assertIn("appendTarget", AI_GOVERNANCE_STEP)


class AdaptiveIntakeApiTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        encounter_engine.store = EncounterStore(str(Path(self.temp_dir.name) / "api.db"))
        app.config.update(TESTING=True, SAFEBARS_REQUIRE_ROLE_AUTH=True)
        self.client = app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_plan_endpoint_returns_six_core_questions(self):
        resp = self.client.post(
            "/api/safebars/v2/adaptive-intake/plan",
            json={"project": {"title": "Literacy interview", "context": "Interviews.", "target_people": "Parents"}},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["core"]), 6)
        self.assertEqual(data["conditional"], [])

    def test_plan_endpoint_adds_ai_follow_up(self):
        resp = self.client.post(
            "/api/safebars/v2/adaptive-intake/plan",
            json={"project": {"title": "AI tutor", "context": "LLM based", "target_people": "Students", "uses_ai": True}},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual([s["id"] for s in data["conditional"]], ["ai_governance"])

    def test_plan_endpoint_accepts_flat_payload(self):
        resp = self.client.post(
            "/api/safebars/v2/adaptive-intake/plan",
            json={"title": "AI chatbot", "context": "LLM coach"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([s["id"] for s in resp.get_json()["conditional"]], ["ai_governance"])


if __name__ == "__main__":
    unittest.main()
