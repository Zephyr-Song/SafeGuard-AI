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


if __name__ == "__main__":
    unittest.main()
