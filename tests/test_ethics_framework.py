import json
import tempfile
import unittest
from pathlib import Path

from modules.encounter_engine import EncounterEngine, SAMPLE_PROJECT


class EthicsFrameworkTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.engine = EncounterEngine(
            db_path=str(Path(self.temp_dir.name) / "frameworks.db")
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_ict_project_uses_belmont_menlo_vsd_and_esr(self):
        payload = json.loads(json.dumps(SAMPLE_PROJECT))
        payload["project"]["uses_ai"] = False
        session = self.engine.create_session(payload)
        assessment = session["framework_assessment"]

        self.assertEqual(assessment["pathway"], "ict_research")
        framework_ids = {item["id"] for item in assessment["frameworks"]}
        self.assertEqual(framework_ids, {"belmont", "menlo", "vsd", "esr"})
        self.assertNotIn("nist_ai_rmf", framework_ids)
        self.assertEqual(len(assessment["tradeoffs"]), 2)
        self.assertTrue(all(item["boundary"] for item in assessment["dimensions"]))
        dimensions = {item["id"]: item for item in assessment["dimensions"]}
        self.assertEqual(dimensions["respect"]["coverage"], "documented")
        self.assertIn("CON-001", dimensions["respect"]["source_passage_ids"])
        self.assertIn("break", dimensions["beneficence"]["matched_terms"])
        self.assertTrue(
            all(
                item["source_passage_ids"] or item["related_passage_ids"]
                for item in assessment["dimensions"]
            )
        )
        self.assertTrue(all(item["coverage_reason"] for item in assessment["dimensions"]))

    def test_ai_project_adds_nist_extension_and_ai_tradeoff(self):
        payload = json.loads(json.dumps(SAMPLE_PROJECT))
        payload["project"]["uses_ai"] = True
        payload["project"]["context"] += " The study evaluates an AI chatbot used during workshops."
        session = self.engine.create_session(payload)
        assessment = session["framework_assessment"]

        self.assertEqual(assessment["pathway"], "ai_research")
        framework_ids = {item["id"] for item in assessment["frameworks"]}
        self.assertIn("nist_ai_rmf", framework_ids)
        dimension_ids = {item["id"] for item in assessment["dimensions"]}
        self.assertTrue({"ai_govern", "ai_map", "ai_measure", "ai_manage"}.issubset(dimension_ids))
        self.assertEqual(len(assessment["tradeoffs"]), 3)
        self.assertIn("does not determine ethical acceptability", assessment["interpretation_boundary"])

    def test_unmatched_framework_concept_returns_related_material_without_inflating_coverage(self):
        payload = json.loads(json.dumps(SAMPLE_PROJECT))
        payload["project"]["uses_ai"] = True
        session = self.engine.create_session(payload)
        dimensions = {item["id"]: item for item in session["framework_assessment"]["dimensions"]}

        ai_governance = dimensions["ai_govern"]
        self.assertEqual(ai_governance["coverage"], "missing")
        self.assertFalse(ai_governance["source_passage_ids"])
        self.assertTrue(ai_governance["related_passage_ids"])
        self.assertIn("does not yet state", ai_governance["coverage_reason"])


if __name__ == "__main__":
    unittest.main()
