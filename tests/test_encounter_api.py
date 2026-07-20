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
        self.assertTrue(all(item["trigger_stage"] for item in options.get_json()["scenarios"]))

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

        tradeoffs = self.client.patch(
            f"/api/safebars/v2/sessions/{session_id}/tradeoffs",
            json={
                "deliberations": [
                    {
                        "id": "recruitment_reach",
                        "value": 70,
                        "rationale": "A narrower group is methodologically necessary, with community review of exclusion effects.",
                    },
                    {
                        "id": "data_richness_privacy",
                        "value": 35,
                        "rationale": "Data minimization outweighs richer recordings for this sensitive topic.",
                    },
                ]
            },
            headers=researcher_headers,
        )
        self.assertEqual(tradeoffs.status_code, 200)
        self.assertEqual(
            tradeoffs.get_json()["session"]["tradeoff_deliberations"]["recruitment_reach"]["value"],
            70,
        )

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
        reviewed_handoff = next(
            item
            for item in expert_review.get_json()["session"]["handoffs"]
            if item["id"] == handoff["id"]
        )
        self.assertEqual(reviewed_handoff["assigned_role"], "ethics_board")
        self.assertEqual(reviewed_handoff["assigned_reviewer_name"], "School ethics advisor")
        self.assertGreaterEqual(len(reviewed_handoff["review_history"]), 1)
        reviewed_summary = self.client.get(
            f"/api/safebars/v2/sessions/{session_id}/expert-summary",
            headers=expert_headers,
        ).get_json()["summary"]
        self.assertGreaterEqual(reviewed_summary["counts"]["assigned"], 1)
        self.assertIn("ethics_board", reviewed_summary["role_counts"])

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
        self.assertEqual(
            versioned.get_json()["session"]["tradeoff_deliberations"]["recruitment_reach"]["value"],
            70,
        )

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

        research_design = self.client.get(
            f"/api/safebars/v2/sessions/{session_id}/export.research-design.docx",
            headers=researcher_headers,
        )
        self.assertEqual(research_design.status_code, 200)
        self.assertIn("research_design.docx", research_design.headers["Content-Disposition"])
        design_document = Document(BytesIO(research_design.data))
        design_text = "\n".join(paragraph.text for paragraph in design_document.paragraphs)
        self.assertIn("RESEARCH DESIGN AND ETHICS-IN-PRACTICE PLAN", design_text)
        self.assertIn("Research setting, procedures, and participant journey", design_text)
        self.assertIn("Ethics-informed trade-offs and design decisions", design_text)
        self.assertIn("Expert dependencies and unresolved design questions", design_text)
        self.assertIn("Narrow eligibility: 70", design_text)
        self.assertIn("A narrower group is methodologically necessary", design_text)

        expert_export = self.client.get(
            f"/api/safebars/v2/sessions/{session_id}/export.expert.docx"
            , headers=expert_headers
        )
        self.assertEqual(expert_export.status_code, 200)
        expert_document = Document(BytesIO(expert_export.data))
        expert_text = "\n".join(paragraph.text for paragraph in expert_document.paragraphs)
        self.assertIn("SAFEBARS EXPERT REVIEW SUMMARY", expert_text)
        self.assertIn("Expert advice", expert_text)

        second_payload = json.loads(json.dumps(SAMPLE_PROJECT))
        second_payload["project"]["title"] = "Second sensitive-service protocol"
        second_created = self.client.post(
            "/api/safebars/v2/sessions", json=second_payload
        ).get_json()
        portfolio = self.client.post(
            "/api/safebars/v2/expert/export.portfolio.docx",
            json={
                "cases": [
                    {
                        "session_id": session_id,
                        "expert_token": created_payload["access"]["expert_token"],
                    },
                    {
                        "session_id": second_created["session"]["id"],
                        "expert_token": second_created["access"]["expert_token"],
                    },
                ]
            },
        )
        self.assertEqual(portfolio.status_code, 200)
        self.assertIn("expert_caseload_summary.docx", portfolio.headers["Content-Disposition"])
        portfolio_document = Document(BytesIO(portfolio.data))
        portfolio_text = "\n".join(
            paragraph.text for paragraph in portfolio_document.paragraphs
        )
        self.assertIn("SAFEBARS EXPERT CASELOAD SUMMARY", portfolio_text)
        self.assertIn("Applications in scope: 2", portfolio_text)
        self.assertIn(SAMPLE_PROJECT["project"]["title"], portfolio_text)
        self.assertIn("Second sensitive-service protocol", portfolio_text)
        self.assertIn("Clarify the withdrawal and deletion boundary.", portfolio_text)
        self.assertIn("Recorded research-design trade-offs", portfolio_text)
        self.assertIn("Data minimization outweighs richer recordings", portfolio_text)

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
        self.assertEqual(
            self.client.post(
                "/api/safebars/v2/expert/export.portfolio.docx",
                json={
                    "cases": [
                        {
                            "session_id": session_id,
                            "expert_token": researcher_token,
                        }
                    ]
                },
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
        self.assertIn(b"How to use SafeBARS", workspace.data)
        self.assertIn(b'aria-label="Close instructions"', workspace.data)
        self.assertIn(b'class="dialog-close-symbol"', workspace.data)
        self.assertIn(b"For researchers", workspace.data)
        self.assertIn(b"For ethics experts", workspace.data)
        self.assertIn(b"Keep your record", workspace.data)
        self.assertIn(b"Six core questions", workspace.data)
        self.assertIn(b"Intake completed", workspace.data)
        self.assertIn(b"Done \xc2\xb7 review populated fields", workspace.data)
        self.assertIn(b"Full audit report (.docx)", workspace.data)
        self.assertIn(b"Application draft (.docx)", workspace.data)
        self.assertIn(b"Research design (.docx)", workspace.data)
        self.assertIn(b"Expert workspace", workspace.data)
        self.assertIn(b'id="expertWorkspaceButton"', workspace.data)
        self.assertIn(b"Open expert review", workspace.data)
        self.assertNotIn(b"no handoffs yet", workspace.data)
        self.assertIn(b"Plain-language guide to interface terms", workspace.data)
        self.assertIn(b"Internal source ID", workspace.data)
        self.assertIn(b"Evidence from", workspace.data)
        self.assertIn(b"How to read a source label", workspace.data)
        self.assertIn(b"Needs attention", workspace.data)
        self.assertIn(b"Closest submitted material to inspect", workspace.data)
        self.assertIn(b"Show in protocol", workspace.data)
        self.assertIn(b"Connected design decisions", workspace.data)
        self.assertIn(b"Research rehearsal", workspace.data)
        self.assertIn(b"frameworkCoverageSummary", workspace.data)
        self.assertIn(b"frameworkCoverageDonut", workspace.data)
        self.assertIn(b"Evidence coverage at a glance", workspace.data)
        self.assertIn(b"Participant journey stress map", workspace.data)
        self.assertIn(b'data-journey-lens="combined"', workspace.data)
        self.assertIn(b"Open scenario result", workspace.data)
        self.assertIn(b"Unsaved material changes", workspace.data)
        self.assertIn(b"Excluded from scope", workspace.data)
        self.assertIn(b"hadUnsavedMaterialChanges", workspace.data)
        self.assertIn(b"Optional bounded LLM critic", workspace.data)
        self.assertIn(b"Run this check again", workspace.data)
        self.assertIn(b"The plan has already run", workspace.data)
        self.assertNotIn(b">V1</span>", workspace.data)
        self.assertNotIn(b">Rerun</button>", workspace.data)
        self.assertIn(b"window.location.assign(expertInviteUrl())", workspace.data)
        self.assertIn(b"Framework-linked Trade-off Board", workspace.data)
        self.assertIn(b"Downstream outputs", workspace.data)
        self.assertIn(b"10.1145/3334480.3382795", workspace.data)

        legacy = self.client.get("/safebars/v1")
        self.assertEqual(legacy.status_code, 200)
        self.assertIn(b"Rehearsal Chat", legacy.data)

        expert = self.client.get("/safebars/expert/example_session")
        self.assertEqual(expert.status_code, 200)
        self.assertIn(b"SafeBARS Expert Workspace", expert.data)
        self.assertIn(b"All expert roles", expert.data)
        self.assertIn(b"Workflow timeline and comment history", expert.data)
        self.assertIn(b"Needs expert action", expert.data)
        self.assertIn(b"The decision you are being asked to make", expert.data)
        self.assertIn(b"Downstream outputs", expert.data)
        self.assertIn(b"Before you save a decision", expert.data)
        self.assertIn(b"Enter your expert response below", expert.data)
        self.assertIn(b"Expert response \xc2\xb7 enter advice", expert.data)
        self.assertIn(b"function openDecisionForm", expert.data)
        self.assertIn(b"field.scrollIntoView", expert.data)
        self.assertIn(b"Send advice to researcher", expert.data)
        self.assertIn(b"Ask researcher", expert.data)
        self.assertIn(b"Redirect handoff", expert.data)
        self.assertIn(b"Close handoff", expert.data)
        self.assertIn(b"Advice sent to the researcher", expert.data)
        self.assertIn(b"Internal source ID", expert.data)
        self.assertIn(b"source ID", expert.data)

        expert_dashboard = self.client.get("/safebars/expert")
        self.assertEqual(expert_dashboard.status_code, 200)
        self.assertIn(b"SafeBARS Expert Caseload", expert_dashboard.data)
        self.assertIn(b"Download caseload summary", expert_dashboard.data)
        self.assertIn(b"filter by assigned or recommended expert role", expert_dashboard.data)
        self.assertIn(b"No review case is open", expert_dashboard.data)
        self.assertIn(b"not an empty input form", expert_dashboard.data)


    def test_tradeoffs_rejects_out_of_range_and_unknown_ids(self):
        payload = json.loads(json.dumps(SAMPLE_PROJECT))
        payload["use_llm"] = False
        created = self.client.post("/api/safebars/v2/sessions", json=payload)
        self.assertEqual(created.status_code, 201)
        researcher_headers = {
            "X-SafeBARS-Access": created.get_json()["access"]["researcher_token"]
        }
        session_id = created.get_json()["session"]["id"]

        # Out-of-range position -> 400 (server-side validation, never trusted blindly).
        bad_range = self.client.patch(
            f"/api/safebars/v2/sessions/{session_id}/tradeoffs",
            json={"deliberations": [{"id": "recruitment_reach", "value": 250}]},
            headers=researcher_headers,
        )
        self.assertEqual(bad_range.status_code, 400)

        # Only unrecognized ids -> 400.
        bad_ids = self.client.patch(
            f"/api/safebars/v2/sessions/{session_id}/tradeoffs",
            json={"deliberations": [{"id": "ghost", "value": 50}]},
            headers=researcher_headers,
        )
        self.assertEqual(bad_ids.status_code, 400)

        # A mixed payload with one valid id still saves the valid one (200).
        mixed = self.client.patch(
            f"/api/safebars/v2/sessions/{session_id}/tradeoffs",
            json={
                "deliberations": [
                    {"id": "recruitment_reach", "value": 65},
                    {"id": "ghost", "value": 50},
                ]
            },
            headers=researcher_headers,
        )
        self.assertEqual(mixed.status_code, 200)
        self.assertIn(
            "recruitment_reach",
            mixed.get_json()["session"]["tradeoff_deliberations"],
        )


if __name__ == "__main__":
    unittest.main()
