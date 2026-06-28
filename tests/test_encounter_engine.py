import json
import tempfile
import unittest
from pathlib import Path

from modules.encounter_engine import EncounterEngine, SAMPLE_PROJECT


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

    def test_session_builds_nine_stage_encounter_map_and_persists(self):
        session = self.create_sample()

        self.assertEqual(len(session["encounter_map"]), 9)
        self.assertTrue(all(stage["included"] for stage in session["encounter_map"]))
        self.assertEqual(session["status"], "mapped")

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


if __name__ == "__main__":
    unittest.main()
