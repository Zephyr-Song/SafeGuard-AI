"""Regression tests for pseudonymous SafeBARS comparative-study instrumentation."""

import json
import tempfile
import unittest
from pathlib import Path

from app import app
from modules.encounter_api import encounter_engine
from modules.encounter_engine import EncounterStore, SAMPLE_PROJECT
from modules.llm_client import LLMProvider


class FakeStudyLLM:
    """Deterministic configured provider shared by both formal conditions."""

    def __init__(self):
        provider = LLMProvider(
            id="study_provider",
            label="Study provider",
            api_key="test-only",
            base_url="https://study.invalid/v1",
            model="study-model-v1",
        )
        self.providers = {provider.id: provider}
        self.active_provider_id = provider.id
        self.calls = []

    def is_configured(self):
        return True

    def configured_provider_summaries(self):
        return [item.public_dict() for item in self.providers.values()]

    def chat_with_provider_detailed(
        self, provider_id, messages, temperature=0.4, timeout=35
    ):
        self.calls.append(
            {
                "provider_id": provider_id,
                "messages": messages,
                "temperature": temperature,
                "timeout": timeout,
            }
        )
        general_chat = "ordinary research-assistance chat" in messages[0]["content"]
        text = (
            "MODEL_PRIVATE_RESPONSE: revise recruitment and withdrawal language."
            if general_chat
            else "[]"
        )
        return {
            "ok": True,
            "text": text,
            "error": "",
            "error_type": "",
            "status_code": 200,
            "model": "study-model-v1",
            "usage": {
                "prompt_tokens": 31,
                "completion_tokens": 9,
                "total_tokens": 40,
            },
        }


class UnconfiguredStudyLLM:
    providers = {}
    active_provider_id = None

    @staticmethod
    def is_configured():
        return False

    @staticmethod
    def configured_provider_summaries():
        return []


class StudyInstrumentationTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        encounter_engine.store = EncounterStore(
            str(Path(self.temp_dir.name) / "study-api.db")
        )
        self.original_llm_client = encounter_engine.llm_client
        encounter_engine.llm_client = FakeStudyLLM()
        app.config.update(TESTING=True, SAFEBARS_REQUIRE_ROLE_AUTH=True)
        self.client = app.test_client()

    def tearDown(self):
        encounter_engine.llm_client = self.original_llm_client
        self.temp_dir.cleanup()

    @staticmethod
    def study_payload(condition="safebars_full"):
        payload = json.loads(json.dumps(SAMPLE_PROJECT))
        # Formal study sessions must override this participant-side value.
        payload["use_llm"] = False
        payload["study_manifest"] = {
            "study_id": "SB-PILOT",
            "participant_id": "P001",
            "condition": condition,
            "case_id": "CASE-A",
            "order": 1,
            "consent_confirmed": True,
            # Client-supplied configuration and identifying fields must be ignored.
            "participant_name": "Alice Example",
            "config_snapshot": {"model": {"provider": "client-injected"}},
        }
        return payload

    def create_study(self, condition="safebars_full"):
        response = self.client.post(
            "/api/safebars/v2/sessions", json=self.study_payload(condition)
        )
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        body = response.get_json()
        return body["session"], {
            "X-SafeBARS-Access": body["access"]["researcher_token"]
        }

    def start_study(self, condition="safebars_full"):
        session, headers = self.create_study(condition)
        started = self.client.post(
            f"/api/safebars/v2/sessions/{session['id']}/study/task/start",
            headers=headers,
        )
        self.assertEqual(started.status_code, 200, started.get_data(as_text=True))
        return started.get_json()["session"], headers

    def save_common_submission(self, session_id, headers):
        response = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/study/submission",
            headers=headers,
            json={
                "final_artifact": (
                    "PRIVATE_FINAL_ARTIFACT: A condition-neutral research plan "
                    "and ethics application response with safeguards."
                ),
                "decision_rationales": [
                    "PRIVATE_RATIONALE_ONE: reduce recruitment pressure.",
                    "PRIVATE_RATIONALE_TWO: preserve staged withdrawal.",
                ],
            },
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        return response

    def test_manifest_is_server_validated_snapshotted_and_locked(self):
        session, headers = self.create_study()
        manifest = session["study_manifest"]

        self.assertEqual(manifest["schema_version"], "1.0")
        self.assertEqual(manifest["participant_id"], "P001")
        self.assertEqual(manifest["condition"], "safebars_full")
        self.assertEqual(manifest["task_status"], "configured")
        self.assertNotIn("participant_name", manifest)
        self.assertNotIn("Alice Example", json.dumps(manifest))
        self.assertEqual(
            manifest["config_snapshot"]["prompt"]["id"],
            "bounded-protocol-critic-v1",
        )
        self.assertEqual(
            len(manifest["config_snapshot"]["prompt"]["template_sha256"]), 64
        )
        model = manifest["config_snapshot"]["model"]
        self.assertTrue(session["use_llm"])
        self.assertTrue(model["enabled"])
        self.assertTrue(model["configured"])
        self.assertEqual(model["provider"]["id"], "study_provider")
        self.assertEqual(model["provider"]["model"], "study-model-v1")
        self.assertEqual(model["temperature"], 0.15)

        blocked_change = self.client.patch(
            f"/api/safebars/v2/sessions/{session['id']}/application-profile",
            json={"profile_id": "generic_human_research"},
            headers=headers,
        )
        self.assertEqual(blocked_change.status_code, 400)
        self.assertIn(
            "Start the instrumented study task",
            blocked_change.get_json()["error"],
        )

        blocked_version = self.client.post(
            f"/api/safebars/v2/sessions/{session['id']}/versions",
            headers=headers,
        )
        self.assertEqual(blocked_version.status_code, 400)
        self.assertIn("study sessions are frozen", blocked_version.get_json()["error"])

    def test_condition_allowlist_and_configured_provider_are_required(self):
        payload = self.study_payload("custom_condition")
        invalid_condition = self.client.post(
            "/api/safebars/v2/sessions", json=payload
        )
        self.assertEqual(invalid_condition.status_code, 400)
        self.assertIn(
            "safebars_full or general_chat",
            invalid_condition.get_json()["error"],
        )

        encounter_engine.llm_client = UnconfiguredStudyLLM()
        for condition in ("safebars_full", "general_chat"):
            missing_provider = self.client.post(
                "/api/safebars/v2/sessions",
                json=self.study_payload(condition),
            )
            self.assertEqual(missing_provider.status_code, 400)
            self.assertIn(
                "configured LLM provider",
                missing_provider.get_json()["error"],
            )

    def test_both_conditions_snapshot_the_same_provider_model_and_settings(self):
        safe_session, _ = self.create_study("safebars_full")
        chat_session, _ = self.create_study("general_chat")
        safe_model = safe_session["study_manifest"]["config_snapshot"]["model"]
        chat_model = chat_session["study_manifest"]["config_snapshot"]["model"]

        self.assertEqual(safe_model, chat_model)
        self.assertEqual(
            chat_session["study_manifest"]["config_snapshot"]["prompt"]["id"],
            "general-research-chat-v1",
        )
        self.assertEqual(chat_session["status"], "study_chat_ready")
        self.assertEqual(chat_session["encounter_map"], [])
        self.assertEqual(chat_session["audit_plan"], [])
        self.assertEqual(chat_session["agent_activity"], [])

    def test_general_chat_is_bounded_instrumented_and_condition_gated(self):
        chat_session, chat_headers = self.start_study("general_chat")
        session_id = chat_session["id"]
        message = "USER_PRIVATE_MESSAGE: help me revise this task response."
        sent = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/study/chat",
            headers=chat_headers,
            json={"message": message},
        )
        self.assertEqual(sent.status_code, 200, sent.get_data(as_text=True))
        turn = sent.get_json()["turn"]
        self.assertEqual(turn["turn_index"], 1)
        self.assertEqual(turn["user_text"], message)
        self.assertTrue(turn["ok"])
        self.assertEqual(turn["model"], "study-model-v1")
        self.assertEqual(turn["temperature"], 0.15)
        self.assertEqual(turn["usage"]["total_tokens"], 40)
        self.assertEqual(len(turn["response_sha256"]), 64)
        self.assertIn("T", turn["user_timestamp"])
        self.assertGreaterEqual(turn["latency_ms"], 0)
        calls = sent.get_json()["session"]["study_llm_calls"]
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["call_type"], "general_chat")
        self.assertNotIn(message, json.dumps(calls))
        self.assertNotIn("MODEL_PRIVATE_RESPONSE", json.dumps(calls))

        too_long = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/study/chat",
            headers=chat_headers,
            json={"message": "x" * 2001},
        )
        self.assertEqual(too_long.status_code, 400)
        self.assertIn("2000", too_long.get_json()["error"])

        blocked_audit = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/audit",
            headers=chat_headers,
            json={"scenario_ids": ["emotional_distress"]},
        )
        self.assertEqual(blocked_audit.status_code, 400)
        self.assertIn("general_chat condition", blocked_audit.get_json()["error"])

        safe_session, safe_headers = self.start_study("safebars_full")
        blocked_chat = self.client.post(
            f"/api/safebars/v2/sessions/{safe_session['id']}/study/chat",
            headers=safe_headers,
            json={"message": "This must be blocked."},
        )
        self.assertEqual(blocked_chat.status_code, 400)
        self.assertIn("general_chat condition", blocked_chat.get_json()["error"])

    def test_submission_and_completion_gate_then_pseudonymous_export(self):
        session, headers = self.start_study("general_chat")
        session_id = session["id"]
        message = "USER_PRIVATE_MESSAGE: help with a decision."
        sent = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/study/chat",
            headers=headers,
            json={"message": message},
        )
        self.assertEqual(sent.status_code, 200)

        blocked_complete = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/study/task/complete",
            headers=headers,
        )
        self.assertEqual(blocked_complete.status_code, 400)
        self.assertIn("exactly two decision rationales", blocked_complete.get_json()["error"])

        bad_submission = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/study/submission",
            headers=headers,
            json={
                "final_artifact": "too short",
                "decision_rationales": ["only one"],
            },
        )
        self.assertEqual(bad_submission.status_code, 400)

        self.save_common_submission(session_id, headers)
        completed = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/study/task/complete",
            headers=headers,
        )
        self.assertEqual(completed.status_code, 200)
        manifest = completed.get_json()["manifest"]
        self.assertEqual(manifest["task_status"], "completed")
        self.assertGreaterEqual(manifest["elapsed_seconds"], 0)

        frozen_submission = self.client.post(
            f"/api/safebars/v2/sessions/{session_id}/study/submission",
            headers=headers,
            json={
                "final_artifact": "x" * 50,
                "decision_rationales": ["rationale one", "rationale two"],
            },
        )
        self.assertEqual(frozen_submission.status_code, 400)

        exported = self.client.get(
            f"/api/safebars/v2/sessions/{session_id}/study/export",
            headers=headers,
        )
        self.assertEqual(exported.status_code, 200)
        record = json.loads(exported.data)
        outcomes = record["outcomes"]
        self.assertEqual(record["manifest"]["participant_id"], "P001")
        self.assertEqual(outcomes["chat_turn_count"], 1)
        self.assertEqual(outcomes["llm_call_count"], 1)
        self.assertEqual(outcomes["llm_success_count"], 1)
        self.assertEqual(outcomes["llm_token_usage"]["total_tokens"], 40)
        self.assertTrue(outcomes["final_artifact_submitted"])
        self.assertEqual(len(outcomes["decision_rationale_chars"]), 2)
        self.assertEqual(outcomes["submission_revision_count"], 1)
        self.assertEqual(
            [event["event_type"] for event in record["task_events"]],
            ["study_task_start", "study_task_complete"],
        )
        export_text = exported.get_data(as_text=True)
        for private_text in (
            "Alice Example",
            "USER_PRIVATE_MESSAGE",
            "MODEL_PRIVATE_RESPONSE",
            "PRIVATE_FINAL_ARTIFACT",
            "PRIVATE_RATIONALE",
            "reviewer_name",
        ):
            self.assertNotIn(private_text, export_text)

    def test_invalid_or_nonconsenting_manifest_is_rejected(self):
        payload = self.study_payload()
        payload["study_manifest"]["participant_id"] = "Alice Smith"
        invalid_code = self.client.post("/api/safebars/v2/sessions", json=payload)
        self.assertEqual(invalid_code.status_code, 400)
        self.assertIn("pseudonymous code", invalid_code.get_json()["error"])

        payload = self.study_payload()
        payload["study_manifest"]["consent_confirmed"] = False
        no_consent = self.client.post("/api/safebars/v2/sessions", json=payload)
        self.assertEqual(no_consent.status_code, 400)
        self.assertIn("consent", no_consent.get_json()["error"].lower())

    def test_nonstudy_sessions_remain_compatible(self):
        payload = json.loads(json.dumps(SAMPLE_PROJECT))
        payload["use_llm"] = False
        created = self.client.post("/api/safebars/v2/sessions", json=payload)
        self.assertEqual(created.status_code, 201)
        body = created.get_json()
        self.assertNotIn("study_manifest", body["session"])
        self.assertTrue(body["session"]["use_llm"])
        self.assertTrue(body["session"]["project"]["uses_ai"])
        headers = {"X-SafeBARS-Access": body["access"]["researcher_token"]}
        status = self.client.get(
            f"/api/safebars/v2/sessions/{body['session']['id']}/study",
            headers=headers,
        )
        self.assertEqual(status.status_code, 400)

    def test_study_workspace_exposes_strict_conditions_and_common_submission(self):
        workspace = self.client.get("/safebars/study")
        self.assertEqual(workspace.status_code, 200)
        for marker in (
            b"Study session setup",
            b"Participant code",
            b"Do not enter a name",
            b'<option value="safebars_full">',
            b'<option value="general_chat">',
            b'id="baselinePanel"',
            b'id="studyChatInput"',
            b'id="studySubmissionPanel"',
            b'id="studyFinalArtifact"',
            b'id="studyRationale1"',
            b'id="studyRationale2"',
            b'id="completeStudyTaskButton"',
            b'data-export-format="study"',
        ):
            self.assertIn(marker, workspace.data)
        self.assertIn(b'<button id="readinessCheckButton" hidden', workspace.data)
        self.assertNotIn(b"See blockers and the next action", workspace.data)


if __name__ == "__main__":
    unittest.main()
