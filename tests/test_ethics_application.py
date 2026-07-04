import copy
import tempfile
import unittest
from pathlib import Path

from modules.encounter_engine import EncounterEngine, SAMPLE_PROJECT
from modules.ethics_application import build_application_readiness


class EthicsApplicationReadinessTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.engine = EncounterEngine(
            db_path=str(Path(self.temp_dir.name) / "application.db")
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_ai_project_uses_extended_generic_profile(self):
        payload = copy.deepcopy(SAMPLE_PROJECT)
        payload["project"]["uses_ai"] = True
        session = self.engine.create_session(payload)
        readiness = session["application_readiness"]

        self.assertEqual(readiness["profile_id"], "generic_ai_research")
        self.assertEqual(len(readiness["fields"]), 13)
        self.assertIn("not an ethics verdict", readiness["boundary"])
        self.assertFalse(readiness["submission_ready"])

    def test_profile_can_be_changed_without_claiming_official_mapping(self):
        session = self.engine.create_session(copy.deepcopy(SAMPLE_PROJECT))
        updated = self.engine.update_application_profile(
            session["id"], "generic_ai_research"
        )
        readiness = build_application_readiness(updated)

        self.assertEqual(readiness["profile_id"], "generic_ai_research")
        self.assertFalse(readiness["profile"]["official"])
        self.assertGreater(readiness["counts"]["partial"], 0)


if __name__ == "__main__":
    unittest.main()
