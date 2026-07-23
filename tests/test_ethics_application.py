import copy
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from docx import Document

from modules.encounter_engine import EncounterEngine, SAMPLE_PROJECT
from modules.encounter_report import build_ethics_application_docx
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
        self.assertEqual(len(readiness["fields"]), 14)
        self.assertIn(
            "review_context", {field["id"] for field in readiness["fields"]}
        )
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

    def test_ai_application_cites_review_sources_and_preserves_supplement(self):
        payload = copy.deepcopy(SAMPLE_PROJECT)
        payload["project"]["uses_ai"] = True
        payload["project"]["context"] += " An AI model proposes interview follow-up prompts."
        payload["artifacts"]["ai_governance"] = (
            "AI role & decision authority: the model recommends prompts; a researcher decides.\n"
            "Data source & intended population: no participant data is used for training.\n"
            "Participant disclosure & consent: participants are told about AI assistance.\n"
            "Human oversight & monitoring: the research lead reviews and may override every prompt.\n"
            "Stopping rule & fallback: disable the model and use the approved interview guide.\n"
            "Correction, complaints & accountable owner: the research lead records corrections and complaints."
        )
        session = self.engine.create_session(payload)
        document = Document(BytesIO(build_ethics_application_docx(session)))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)

        self.assertIn("Submitted AI ethics-review supplement", text)
        self.assertIn("Makridis et al. (2023)", text)
        self.assertIn("Connelly et al. (2025)", text)
        self.assertIn("AI human-subjects review questions", text)
        self.assertIn(
            "Societal & Community Risk Statement (Ethics and Society Review)",
            text,
        )
        self.assertIn("Ethics and society review", text)


if __name__ == "__main__":
    unittest.main()
