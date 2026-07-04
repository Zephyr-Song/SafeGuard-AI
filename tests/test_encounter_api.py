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
        app.config.update(TESTING=True, SAFEBARS_REQUIRE_ROLE_AUTH=True)
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
        created_payload = created.get_json()
        session_id = created_payload["session"]["id"]
        researcher_headers = {
            "X-SafeBARS-Access": created_payload["access"]["researcher_token"]
        }
        expert_headers = {
            "X-SafeBARS-Access": created_payload["access"]["expert_token"]
        }

        planned = self.client.patch(
            f"/api/safebars/v2/sessions/{session_id}/plan",
            json={"scenario_ids": ["participant_distress", "partial_withdrawal"]},
            headers=researcher_headers,
        )
        self.assertEqual(planned.status_code, 200)
        planned_session = planned.get_json()["session"]
        self.assertEqual(
            len([task for task in planned_session["audit_plan"] if task["kind"] == "scenario"]),
            2,
        )

        audited = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/audit",
            json={"scenario_ids": ["participant_distress", "partial_withdrawal"]},
            headers=researcher_headers,
        )
        self.assertEqual(audited.status_code, 200)
        audited_session = audited.get_json()["session"]
        self.assertEqual(len(audited_session["traces"]), 2)

        rerunnable = next(
            task
            for task in audited_session["audit_plan"]
            if task.get("scenario_id") == "partial_withdrawal"
        )
        rerun = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/tasks/{rerunnable['id']}/rerun",
            headers=researcher_headers,
        )
        self.assertEqual(rerun.status_code, 200)
        audited_session = rerun.get_json()["session"]

        handoff = audited_session["handoffs"][0]
        summary = self.client.get(
            f"/api/safebars/v2/sessions/{session_id}/expert-summary",
            headers=expert_headers,
        )
        self.assertEqual(summary.status_code, 200)
        self.assertGreaterEqual(summary.get_json()["summary"]["counts"]["total"], 1)
        expert_review = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/handoffs/{handoff['id']}/review",
            json={
                "action": "advise",
                "reviewer_role": "ethics_board",
                "reviewer_name": "School ethics advisor",
                "advice": "Clarify the withdrawal and deletion boundary.",
                "rationale": "The current procedure is ambiguous.",
            },
            headers=expert_headers,
        )
        self.assertEqual(expert_review.status_code, 200)

        researcher_response = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/handoffs/{handoff['id']}/researcher-response",
            json={
                "response": "We clarified the deletion boundary and escalation owner.",
                "revised_text": "Participants may request deletion until anonymised analysis begins; the study lead records and confirms the request.",
            },
            headers=researcher_headers,
        )
        self.assertEqual(researcher_response.status_code, 200)
        self.assertEqual(
            next(
                item
                for item in researcher_response.get_json()["session"]["handoffs"]
                if item["id"] == handoff["id"]
            )["status"],
            "researcher_revised",
        )
        protected_rerun = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/audit",
            json={"scenario_ids": ["partial_withdrawal"]},
            headers=researcher_headers,
        )
        self.assertEqual(protected_rerun.status_code, 400)

        versioned = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/versions",
            headers=researcher_headers,
        )
        self.assertEqual(versioned.status_code, 201)
        self.assertEqual(versioned.get_json()["session"]["lineage"]["parent_session_id"], session_id)
        self.assertEqual(versioned.get_json()["session"]["lineage"]["version_number"], 2)

        issue_id = audited_session["issues"][0]["id"]
        decision = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/issues/{issue_id}/decision",
            json={"decision": "accept", "rationale": "This change is actionable."},
            headers=researcher_headers,
        )
        self.assertEqual(decision.status_code, 200)

        exported = self.client.get(
            f"/api/safebars/v2/sessions/{session_id}/export",
            headers=researcher_headers,
        )
        self.assertEqual(exported.status_code, 200)
        self.assertEqual(exported.mimetype, "application/json")
        self.assertEqual(json.loads(exported.data)["id"], session_id)
        self.assertNotIn(created_payload["access"]["researcher_token"], exported.get_data(as_text=True))
        self.assertNotIn(created_payload["access"]["expert_token"], exported.get_data(as_text=True))

        word_report = self.client.get(
            f"/api/safebars/v2/sessions/{session_id}/export.docx",
            headers=researcher_headers,
        )
        self.assertEqual(word_report.status_code, 200)
        self.assertEqual(
            word_report.mimetype,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        self.assertTrue(word_report.data.startswith(b"PK"))
        self.assertIn("full_audit_report.docx", word_report.headers["Content-Disposition"])
        word_document = Document(BytesIO(word_report.data))
        word_text = "\n".join(paragraph.text for paragraph in word_document.paragraphs)
        self.assertIn(SAMPLE_PROJECT["project"]["title"], word_text)
        self.assertIn("SAFEBARS FULL AUDIT REPORT", word_text)
        self.assertIn("Framework-grounded ethics map", word_text)
        self.assertIn("Inspectable audit plan", word_text)
        self.assertIn("Resolution rule", word_text)

        pdf_report = self.client.get(
            f"/api/safebars/v2/sessions/{session_id}/export.pdf",
            headers=researcher_headers,
        )
        self.assertEqual(pdf_report.status_code, 200)
        self.assertEqual(pdf_report.mimetype, "application/pdf")
        self.assertTrue(pdf_report.data.startswith(b"%PDF-"))
        self.assertGreater(len(pdf_report.data), 5000)
        self.assertIn("full_audit_report.pdf", pdf_report.headers["Content-Disposition"])

        application = self.client.get(
            f"/api/safebars/v2/sessions/{session_id}/export.application.docx"
            , headers=researcher_headers
        )
        self.assertEqual(application.status_code, 200)
        application_document = Document(BytesIO(application.data))
        application_text = "\n".join(
            paragraph.text for paragraph in application_document.paragraphs
        )
        self.assertIn("ETHICS APPLICATION DRAFT", application_text)
        self.assertIn("formal approval", application_text)

        expert_export = self.client.get(
            f"/api/safebars/v2/sessions/{session_id}/export.expert.docx"
            , headers=expert_headers
        )
        self.assertEqual(expert_export.status_code, 200)
        expert_document = Document(BytesIO(expert_export.data))
        expert_text = "\n".join(paragraph.text for paragraph in expert_document.paragraphs)
        self.assertIn("SAFEBARS EXPERT REVIEW SUMMARY", expert_text)
        self.assertIn("Expert advice", expert_text)

    def test_role_tokens_and_expert_invite_rotation(self):
        payload = json.loads(json.dumps(SAMPLE_PROJECT))
        created = self.client.post("/api/safebars/v2/sessions", json=payload).get_json()
        session_id = created["session"]["id"]
        researcher_token = created["access"]["researcher_token"]
        expert_token = created["access"]["expert_token"]
        researcher_headers = {"X-SafeBARS-Access": researcher_token}
        expert_headers = {"X-SafeBARS-Access": expert_token}

        self.assertEqual(
            self.client.get(f"/api/safebars/v2/sessions/{session_id}").status_code,
            401,
        )
        self.assertEqual(
            self.client.get(
                f"/api/safebars/v2/sessions/{session_id}", headers=expert_headers
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(
                f"/api/safebars/v2/sessions/{session_id}/expert-summary",
                headers=researcher_headers,
            ).status_code,
            403,
        )

        rotated = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/access/rotate-expert",
            headers=researcher_headers,
        )
        self.assertEqual(rotated.status_code, 200)
        new_expert_headers = {
            "X-SafeBARS-Access": rotated.get_json()["expert_token"]
        }
        self.assertEqual(
            self.client.get(
                f"/api/safebars/v2/sessions/{session_id}/expert-summary",
                headers=expert_headers,
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(
                f"/api/safebars/v2/sessions/{session_id}/expert-summary",
                headers=new_expert_headers,
            ).status_code,
            200,
        )

    def test_workspace_and_v1_routes_are_available(self):
        workspace = self.client.get("/safebars")
        self.assertEqual(workspace.status_code, 200)
        self.assertIn(b"Encounter stress-testing workspace", workspace.data)
        self.assertIn(b"Start quick intake", workspace.data)
        self.assertIn(b"Six core questions", workspace.data)
        self.assertIn(b"Full audit report (.docx)", workspace.data)
        self.assertIn(b"Application draft (.docx)", workspace.data)

        legacy = self.client.get("/safebars/v1")
        self.assertEqual(legacy.status_code, 200)
        self.assertIn(b"Rehearsal Chat", legacy.data)

        expert = self.client.get("/safebars/expert/example_session")
        self.assertEqual(expert.status_code, 200)
        self.assertIn(b"SafeBARS Expert Review", expert.data)

        expert_dashboard = self.client.get("/safebars/expert")
        self.assertEqual(expert_dashboard.status_code, 200)
        self.assertIn(b"SafeBARS Expert Caseload", expert_dashboard.data)


if __name__ == "__main__":
    unittest.main()
