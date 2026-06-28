import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from docx import Document

from app import app
from modules.encounter_api import encounter_engine
from modules.encounter_engine import EncounterStore, SAMPLE_PROJECT


class EncounterApiTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        encounter_engine.store = EncounterStore(str(Path(self.temp_dir.name) / "api.db"))
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_complete_api_workflow(self):
        options = self.client.get("/api/safebars/v2/options")
        self.assertEqual(options.status_code, 200)
        self.assertEqual(len(options.get_json()["scenarios"]), 6)

        payload = json.loads(json.dumps(SAMPLE_PROJECT))
        payload["use_llm"] = False
        created = self.client.post("/api/safebars/v2/sessions", json=payload)
        self.assertEqual(created.status_code, 201)
        session_id = created.get_json()["session"]["id"]

        audited = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/audit",
            json={"scenario_ids": ["participant_distress", "partial_withdrawal"]},
        )
        self.assertEqual(audited.status_code, 200)
        audited_session = audited.get_json()["session"]
        self.assertEqual(len(audited_session["traces"]), 2)

        issue_id = audited_session["issues"][0]["id"]
        decision = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/issues/{issue_id}/decision",
            json={"decision": "accept", "rationale": "This change is actionable."},
        )
        self.assertEqual(decision.status_code, 200)

        exported = self.client.get(f"/api/safebars/v2/sessions/{session_id}/export")
        self.assertEqual(exported.status_code, 200)
        self.assertEqual(exported.mimetype, "application/json")
        self.assertEqual(json.loads(exported.data)["id"], session_id)

        word_report = self.client.get(f"/api/safebars/v2/sessions/{session_id}/export.docx")
        self.assertEqual(word_report.status_code, 200)
        self.assertEqual(
            word_report.mimetype,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        self.assertTrue(word_report.data.startswith(b"PK"))
        word_document = Document(BytesIO(word_report.data))
        word_text = "\n".join(paragraph.text for paragraph in word_document.paragraphs)
        self.assertIn(SAMPLE_PROJECT["project"]["title"], word_text)

        pdf_report = self.client.get(f"/api/safebars/v2/sessions/{session_id}/export.pdf")
        self.assertEqual(pdf_report.status_code, 200)
        self.assertEqual(pdf_report.mimetype, "application/pdf")
        self.assertTrue(pdf_report.data.startswith(b"%PDF-"))
        self.assertGreater(len(pdf_report.data), 5000)

    def test_workspace_and_v1_routes_are_available(self):
        workspace = self.client.get("/safebars")
        self.assertEqual(workspace.status_code, 200)
        self.assertIn(b"Encounter stress-testing workspace", workspace.data)

        legacy = self.client.get("/safebars/v1")
        self.assertEqual(legacy.status_code, 200)
        self.assertIn(b"Rehearsal Chat", legacy.data)


if __name__ == "__main__":
    unittest.main()
