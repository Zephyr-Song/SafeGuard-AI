import json
import tempfile
import unittest
from pathlib import Path

from modules.encounter_engine import EncounterEngine, SAMPLE_PROJECT
from modules.llm_client import LLMProvider


class EncounterEngineTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "encounters.db"
        self.engine = EncounterEngine(db_path=str(self.db_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_sample(self):
        payload = json.loads(json.dumps(SAMPLE_PROJECT))
        payload["use_llm"] = False
        return self.engine.create_session(payload)

    def test_provider_summary_does_not_expose_key_or_fingerprint(self):
        provider = LLMProvider(
            id="test",
            label="Test provider",
            api_key="secret-provider-key",
            base_url="https://example.invalid/v1",
            model="test-model",
        )

        summary = provider.public_dict()

        self.assertNotIn("api_key", summary)
        self.assertNotIn("key_hint", summary)
        self.assertNotIn("secret-provider-key", json.dumps(summary))

    def test_session_builds_nine_stage_encounter_map_and_persists(self):
        session = self.create_sample()

        self.assertEqual(len(session["encounter_map"]), 9)
        self.assertTrue(all(stage["included"] for stage in session["encounter_map"]))
        self.assertEqual(session["status"], "mapped")
        self.assertEqual(session["audit_plan"][0]["kind"], "orchestrator")
        self.assertEqual(session["audit_plan"][0]["status"], "completed")
        self.assertEqual(
            len([task for task in session["audit_plan"] if task["kind"] == "scenario"]),
            6,
        )
        self.assertTrue(all(task["tools"] for task in session["audit_plan"]))
        self.assertTrue(all(task["stop_condition"] for task in session["audit_plan"]))

        reloaded = self.engine.get_session(session["id"])
        self.assertEqual(reloaded["project"]["title"], SAMPLE_PROJECT["project"]["title"])
        self.assertEqual(reloaded["artifacts"]["interview"], SAMPLE_PROJECT["artifacts"]["interview"])

    def test_audit_produces_traces_grounded_issues_and_handoffs(self):
        session = self.create_sample()
        audited = self.engine.run_audit(
            session["id"],
            ["participant_distress", "partial_withdrawal", "institutional_distrust"],
        )

        self.assertEqual(len(audited["traces"]), 3)
        self.assertGreaterEqual(len(audited["issues"]), 1)
        self.assertGreaterEqual(len(audited["handoffs"]), 1)
        self.assertEqual(audited["status"], "audited")
        self.assertEqual(
            len({trace["uncertainty"] for trace in audited["traces"]}),
            3,
            "Each scenario should explain its own epistemic boundary.",
        )

        source_ids = {
            passage_id
            for issue in audited["issues"]
            for passage_id in issue["source_passage_ids"]
        }
        self.assertTrue(source_ids)
        self.assertTrue(all("-" in source_id for source_id in source_ids))
        self.assertTrue(all(issue["boundary_note"] for issue in audited["issues"]))
        self.assertTrue(all(len(issue["agent_positions"]) == 2 for issue in audited["issues"]))
        self.assertTrue(
            all(issue["contestation_status"] == "human_resolution_required" for issue in audited["issues"])
        )

        planned_scenarios = [
            task for task in audited["audit_plan"] if task["kind"] == "scenario"
        ]
        self.assertEqual(len(planned_scenarios), 3)
        self.assertTrue(all(task["status"] in {"completed", "paused"} for task in planned_scenarios))
        self.assertEqual(
            next(task for task in audited["audit_plan"] if task["kind"] == "boundary_handoff")["status"],
            "completed",
        )

        issues_by_id = {issue["id"]: issue for issue in audited["issues"]}
        self.assertTrue(
            any(source_id.startswith(("CON-", "SAF-", "FOL-")) for source_id in issues_by_id["issue_partial_withdrawal"]["source_passage_ids"])
        )
        self.assertFalse(
            any(source_id.startswith("REC-") for source_id in issues_by_id["issue_partial_withdrawal"]["source_passage_ids"])
        )

    def test_decision_is_recorded_in_ledger_and_event_log(self):
        session = self.create_sample()
        audited = self.engine.run_audit(session["id"], ["partial_withdrawal"])
        issue = audited["issues"][0]

        decided = self.engine.record_decision(
            session["id"],
            issue["id"],
            "defer",
            "A safeguarding advisor needs to check the local referral route.",
            "Add a named local support contact after partner review.",
        )

        saved_issue = next(item for item in decided["issues"] if item["id"] == issue["id"])
        self.assertEqual(saved_issue["decision"], "defer")
        self.assertIn("safeguarding advisor", saved_issue["decision_rationale"])
        self.assertEqual(decided["event_log"][-1]["event_type"], "issue_decision")

    def test_llm_handoff_boundaries_are_contextual_and_not_severity_labels(self):
        psychological = self.engine._llm_boundary_explanation(
            "Lack of psychological support protocol",
            "psychological_safety",
            "research psychologist or mental health professional",
        )
        data_protection = self.engine._llm_boundary_explanation(
            "Insufficient data protection measures",
            "data_protection",
            "data protection officer or IT security specialist",
        )

        self.assertIn("psychological support", psychological)
        self.assertIn("access, storage, retention, and deletion", data_protection)
        self.assertNotEqual(psychological, data_protection)
        self.assertNotIn(psychological.strip().lower(), {"high", "medium", "low"})
        self.assertNotIn(data_protection.strip().lower(), {"high", "medium", "low"})

    def test_plan_can_be_rescoped_and_one_specialist_task_rerun(self):
        session = self.create_sample()
        planned = self.engine.update_audit_plan(
            session["id"], ["participant_distress", "partial_withdrawal"]
        )
        scenario_tasks = [task for task in planned["audit_plan"] if task["kind"] == "scenario"]
        self.assertEqual(
            [task["scenario_id"] for task in scenario_tasks],
            ["participant_distress", "partial_withdrawal"],
        )
        self.assertEqual(planned["event_log"][-1]["event_type"], "audit_plan_updated")

        audited = self.engine.run_audit(session["id"], planned["selected_scenarios"])
        task = next(
            item
            for item in audited["audit_plan"]
            if item.get("scenario_id") == "partial_withdrawal"
        )
        rerun = self.engine.rerun_task(session["id"], task["id"])
        rerun_task = next(item for item in rerun["audit_plan"] if item["id"] == task["id"])
        self.assertEqual(rerun_task["attempts"], 2)
        self.assertEqual(rerun["event_log"][-1]["event_type"], "audit_task_rerun")
        self.assertEqual(
            len([trace for trace in rerun["traces"] if trace["scenario_id"] == "partial_withdrawal"]),
            1,
        )

        issue = next(
            item for item in rerun["issues"] if item.get("trigger_trace_id") == "trace_partial_withdrawal"
        )
        self.engine.record_decision(session["id"], issue["id"], "accept", "Keep this revision.")
        with self.assertRaises(ValueError):
            self.engine.rerun_task(session["id"], task["id"])
        with self.assertRaises(ValueError):
            self.engine.update_audit_plan(session["id"], ["partial_withdrawal"])

    def test_handoff_routes_to_expert_and_records_review(self):
        session = self.create_sample()
        audited = self.engine.run_audit(session["id"], ["partial_withdrawal"])
        handoff = next(
            item for item in audited["handoffs"] if item["issue_id"] == "issue_partial_withdrawal"
        )
        self.assertEqual(handoff["recommended_role"], "ethics_board")
        self.assertEqual(handoff["priority"], "high")
        self.assertTrue(handoff["triage_factors"])

        reviewed = self.engine.review_handoff(
            session["id"],
            handoff["id"],
            "advise",
            "ethics_board",
            "School ethics advisor",
            "Clarify the deletion limit and the latest point at which withdrawal remains possible.",
            "The current text does not distinguish raw recordings from de-identified extracts.",
        )
        saved = next(item for item in reviewed["handoffs"] if item["id"] == handoff["id"])
        self.assertEqual(saved["status"], "advised")
        self.assertEqual(saved["assigned_role"], "ethics_board")
        self.assertEqual(saved["assigned_reviewer_name"], "School ethics advisor")
        self.assertIn("deletion limit", saved["expert_advice"])
        self.assertEqual(len(saved["review_history"]), 1)
        self.assertEqual(reviewed["event_log"][-1]["event_type"], "expert_handoff_review")

        summary = self.engine.expert_summary(session["id"])
        self.assertEqual(summary["counts"]["advised"], 1)
        self.assertEqual(summary["queue"][0]["issue"]["title"], handoff["question"].removeprefix("How should the project address: ").removesuffix("?"))


    def test_update_tradeoff_deliberations_validates_and_persists(self):
        session = self.create_sample()

        # Happy path: valid positions + rationale are stored.
        updated = self.engine.update_tradeoff_deliberations(
            session["id"],
            [
                {"id": "recruitment_reach", "value": 72, "rationale": "Broader access is justified by community need."},
                {"id": "data_richness_privacy", "value": 40, "rationale": "Minimize identifiable data for this sensitive topic."},
            ],
        )
        stored = updated["tradeoff_deliberations"]
        self.assertEqual(stored["recruitment_reach"]["value"], 72)
        self.assertEqual(
            stored["recruitment_reach"]["rationale"],
            "Broader access is justified by community need.",
        )
        # Persisted to the store, not only in memory.
        reloaded = self.engine.get_session(session["id"])
        self.assertEqual(
            reloaded["tradeoff_deliberations"]["data_richness_privacy"]["value"], 40
        )

    def test_update_tradeoff_deliberations_rejects_invalid_values(self):
        session = self.create_sample()

        # Out-of-range positions are rejected with a clear error.
        with self.assertRaises(ValueError):
            self.engine.update_tradeoff_deliberations(
                session["id"], [{"id": "recruitment_reach", "value": 150}]
            )
        with self.assertRaises(ValueError):
            self.engine.update_tradeoff_deliberations(
                session["id"], [{"id": "recruitment_reach", "value": -5}]
            )

        # Submitting only unrecognized trade-off ids is rejected because the
        # deliberation would record nothing.
        with self.assertRaises(ValueError):
            self.engine.update_tradeoff_deliberations(
                session["id"], [{"id": "not_a_real_tradeoff", "value": 50}]
            )

        # A recognized id among others is kept; the bad id is ignored and a
        # valid deliberation is still saved.
        updated = self.engine.update_tradeoff_deliberations(
            session["id"],
            [
                {"id": "recruitment_reach", "value": 60},
                {"id": "ghost_tradeoff", "value": 99},
            ],
        )
        self.assertIn("recruitment_reach", updated["tradeoff_deliberations"])
        self.assertNotIn("ghost_tradeoff", updated["tradeoff_deliberations"])

    def test_update_tradeoff_deliberations_caps_rationale_length(self):
        session = self.create_sample()
        updated = self.engine.update_tradeoff_deliberations(
            session["id"],
            [{"id": "recruitment_reach", "value": 50, "rationale": "x" * 5000}],
        )
        self.assertEqual(
            len(updated["tradeoff_deliberations"]["recruitment_reach"]["rationale"]), 2000
        )


if __name__ == "__main__":
    unittest.main()
