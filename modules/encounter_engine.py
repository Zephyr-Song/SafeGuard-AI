"""Artifact-centered encounter stress testing for SafeBARS v2."""

from __future__ import annotations

from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import threading
import time
from typing import Any, Dict, Iterable, List, Optional
import uuid

from .llm_client import LLMClient
from .ethics_framework import (
    EXPERT_ROLES,
    FRAMEWORKS,
    build_framework_assessment,
    recommend_expert_role,
)

from .scenarios import (
    ARTIFACT_LABELS,
    STAGE_DEFINITIONS,
    SCENARIO_LIBRARY,
    PRIORITY_ORDER,
    SAMPLE_PROJECT,
    utc_now,
)
from .encounter_store import EncounterStore
from .ethics_application import APPLICATION_PROFILES, build_application_readiness

STUDY_MANIFEST_SCHEMA_VERSION = "1.0"
STUDY_PROMPT_VERSION = "bounded-protocol-critic-v1"
STUDY_LLM_TEMPERATURE = 0.15
STUDY_LLM_MAX_TOKENS = 700
STUDY_LLM_TIMEOUT_SECONDS = 25
STUDY_CHAT_MAX_TURNS = 12
STUDY_CHAT_MAX_INPUT_CHARS = 2000
STUDY_CHAT_MAX_OUTPUT_CHARS = 6000
EXPERT_ADVICE_TYPES = {
    "required_change": {
        "label": "Required change",
        "description": "A change that must be made before this handoff can be closed.",
    },
    "optional_recommendation": {
        "label": "Optional recommendation",
        "description": "A beneficial improvement that is not required for closure.",
    },
    "clarification_request": {
        "label": "Clarification request",
        "description": "Information or revised text the researcher must provide before judgment.",
    },
    "no_change_required": {
        "label": "No change required",
        "description": "The submitted evidence is sufficient for this specific handoff.",
    },
}
STUDY_FINAL_ARTIFACT_MAX_CHARS = 20000
STUDY_RATIONALE_MAX_CHARS = 4000
STUDY_CONDITIONS = {"safebars_full", "general_chat"}
_STUDY_CODE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{1,63}$")
_LLM_CRITIC_SYSTEM_PROMPT = (
    "You are a bounded SafeBARS protocol critic. Inspect only the submitted passages. "
    "Do not speak as a participant and do not claim what any population thinks, feels, or will do. "
    "Do not provide ethics approval or compliance verdicts. Return valid JSON only."
)
_LLM_CRITIC_USER_INSTRUCTION = (
    "Find at most two concrete relational or procedural gaps not already obvious from a generic checklist. "
    "Each gap must cite existing passage IDs. Return a JSON array with keys: title, category, severity "
    "(high/medium/low), source_passage_ids, observation, suggestion, handoff_owner. "
    "If no passage-grounded gap is justified, return []."
)
_GENERAL_CHAT_SYSTEM_PROMPT = (
    "You are a general-purpose research planning assistant. Help the user improve the "
    "submitted research plan in response to their requests. Do not claim ethics approval "
    "or invent institutional requirements. Use ordinary conversational responses without "
    "a hidden multi-agent workflow."
)


class EncounterEngine:
    """Runs a bounded, inspectable encounter-audit workflow over research artifacts."""

    def __init__(self, db_path: Optional[str] = None, llm_client: Optional[LLMClient] = None):
        default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "safebars_v2.db")
        self.store = EncounterStore(db_path or os.getenv("SAFEBARS_V2_DB_PATH", default_path))
        self.llm_client = llm_client or LLMClient()

    def public_options(self) -> Dict[str, Any]:
        return {
            "artifact_labels": ARTIFACT_LABELS,
            "scenarios": [
                {
                    "id": item["id"],
                    "category": item["category"],
                    "title": item["title"],
                    "trigger": item["trigger"],
                    "trigger_stage": item["trigger_stage"],
                }
                for item in SCENARIO_LIBRARY
            ],
            "llm_configured": self.llm_client.is_configured(),
            "active_provider": self._active_provider_summary(),
            "sample_project": SAMPLE_PROJECT,
            "ethics_frameworks": [FRAMEWORKS[key] | {"id": key} for key in FRAMEWORKS],
            "expert_roles": [EXPERT_ROLES[key] | {"id": key} for key in EXPERT_ROLES],
            "expert_advice_types": [
                EXPERT_ADVICE_TYPES[key] | {"id": key} for key in EXPERT_ADVICE_TYPES
            ],
            "application_profiles": [
                APPLICATION_PROFILES[key] | {"id": key} for key in APPLICATION_PROFILES
            ],
        }

    def issue_access(self, session_id: str) -> Dict[str, str]:
        if not self.store.load(session_id):
            raise KeyError("Session not found.")
        return {
            "researcher_token": self.store.rotate_access(session_id, "researcher"),
            "expert_token": self.store.rotate_access(session_id, "expert"),
        }

    def rotate_expert_access(self, session_id: str) -> str:
        if not self.store.load(session_id):
            raise KeyError("Session not found.")
        return self.store.rotate_access(session_id, "expert")

    def access_role(self, session_id: str, token: str) -> Optional[str]:
        return self.store.access_role(session_id, token)

    @staticmethod
    def _human_review_started(session: Dict[str, Any]) -> bool:
        decided = any(
            item.get("decision", "pending") != "pending"
            for item in session.get("issues", [])
        )
        reviewed = any(
            item.get("review_history") or item.get("researcher_revision_history")
            for item in session.get("handoffs", [])
        )
        return decided or reviewed

    @staticmethod
    def _require_active_study_task(session: Dict[str, Any]) -> None:
        manifest = session.get("study_manifest")
        if not manifest:
            return
        status = manifest.get("task_status", "configured")
        if status == "configured":
            raise ValueError("Start the instrumented study task before changing the case.")
        if status == "completed":
            raise ValueError("This instrumented study task is complete and researcher changes are frozen.")

    @staticmethod
    def _require_safebars_condition(session: Dict[str, Any]) -> None:
        manifest = session.get("study_manifest")
        if manifest and manifest.get("condition") != "safebars_full":
            raise ValueError(
                "The general_chat condition cannot use SafeBARS maps, agents, audits, "
                "decisions, or handoff tools."
            )

    def create_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        project = payload.get("project", {})
        raw_study_manifest = payload.get("study_manifest")
        requested_condition = (
            str(raw_study_manifest.get("condition", "")).strip()
            if isinstance(raw_study_manifest, dict)
            else ""
        )
        # Formal study conditions must use the same configured provider and fixed
        # decoding settings. The participant-facing toggle is therefore ignored
        # for instrumented sessions.
        use_llm = True if raw_study_manifest is not None else bool(payload.get("use_llm", False))
        artifacts = {
            key: str(payload.get("artifacts", {}).get(key, "")).strip()
            for key in ARTIFACT_LABELS
        }
        if not any(artifacts.values()):
            raise ValueError("Add at least one research artifact before starting an audit.")

        session_id = f"encounter_{uuid.uuid4().hex[:12]}"
        created_at = utc_now()
        session = {
            "id": session_id,
            "version": "2.3",
            "status": "mapped",
            "project": {
                "title": str(project.get("title", "Untitled fieldwork plan")).strip(),
                "review_context": str(project.get("review_context", "")).strip(),
                "context": str(project.get("context", "")).strip(),
                "target_people": str(project.get("target_people", "")).strip(),
                "uses_ai": bool(project.get("uses_ai", False)),
            },
            "artifacts": artifacts,
            "intake_transcript": payload.get("intake_transcript", []),
            "passages": self._extract_passages(artifacts, project),
            "encounter_map": [],
            "framework_assessment": {},
            "tradeoff_deliberations": payload.get("tradeoff_deliberations", {}),
            "application_profile_id": str(payload.get("application_profile_id", "")).strip(),
            "application_readiness": {},
            "lineage": {
                "parent_session_id": str(payload.get("lineage", {}).get("parent_session_id", "")).strip(),
                "version_number": int(payload.get("lineage", {}).get("version_number", 1) or 1),
            },
            "selected_scenarios": payload.get("selected_scenarios", []),
            "traces": [],
            "issues": [],
            "handoffs": [],
            "agent_activity": [],
            "audit_plan": [],
            "use_llm": use_llm,
            "created_at": created_at,
            "updated_at": created_at,
        }
        study_manifest = self._build_study_manifest(
            raw_study_manifest,
            use_llm=session["use_llm"],
            created_at=created_at,
        )
        if study_manifest:
            session["study_manifest"] = study_manifest
            session["study_chat"] = []
            session["study_submission"] = {
                "final_artifact": "",
                "decision_rationales": ["", ""],
                "saved_at": "",
                "revision_number": 0,
            }
            session["study_submission_history"] = []
            session["study_llm_calls"] = []
        if study_manifest and study_manifest["condition"] == "general_chat":
            # The baseline stores the common source material but does not create
            # or expose any SafeBARS analysis output.
            session["status"] = "study_chat_ready"
        else:
            session["encounter_map"] = self._build_encounter_map(session)
            session["framework_assessment"] = build_framework_assessment(session)
            session["application_readiness"] = build_application_readiness(session)
            session["audit_plan"] = self._build_audit_plan(
                session, session.get("selected_scenarios") or None
            )
            self._activity(
                session,
                "Encounter Orchestrator",
                "completed",
                "Built an editable encounter map from submitted artifacts.",
            )
        self._save(
            session,
            "session_created",
            {
                "passage_count": len(session["passages"]),
                "planned_task_count": len(session["audit_plan"]),
            },
        )
        return session

    def _build_study_manifest(
        self,
        raw_manifest: Any,
        *,
        use_llm: bool,
        created_at: str,
    ) -> Optional[Dict[str, Any]]:
        if raw_manifest is None:
            return None
        if not isinstance(raw_manifest, dict):
            raise ValueError("Study manifest must be an object.")

        clean: Dict[str, str] = {}
        labels = {
            "study_id": "Study ID",
            "participant_id": "Participant code",
            "case_id": "Case ID",
        }
        for key, label in labels.items():
            value = str(raw_manifest.get(key, "")).strip()
            if not _STUDY_CODE_PATTERN.fullmatch(value):
                raise ValueError(
                    f"{label} must be a 2-64 character pseudonymous code using only "
                    "letters, numbers, hyphens, or underscores."
                )
            clean[key] = value

        condition = str(raw_manifest.get("condition", "")).strip()
        if condition not in STUDY_CONDITIONS:
            raise ValueError(
                "Study condition must be safebars_full or general_chat."
            )
        clean["condition"] = condition

        order = raw_manifest.get("order")
        if isinstance(order, bool):
            raise ValueError("Study order must be a positive integer.")
        try:
            order = int(order)
        except (TypeError, ValueError):
            raise ValueError("Study order must be a positive integer.") from None
        if order < 1 or order > 100:
            raise ValueError("Study order must be between 1 and 100.")
        if raw_manifest.get("consent_confirmed") is not True:
            raise ValueError(
                "Study consent must be confirmed before an instrumented session is created."
            )

        provider = self._active_provider_summary()
        if not provider:
            raise ValueError(
                "A configured LLM provider is required for both formal study "
                "conditions so safebars_full and general_chat use the same model."
            )
        model_enabled = bool(use_llm and provider)
        if condition == "general_chat":
            prompt_id = "general-research-chat-v1"
            prompt_template = _GENERAL_CHAT_SYSTEM_PROMPT
        else:
            prompt_id = STUDY_PROMPT_VERSION
            prompt_template = (
                f"{_LLM_CRITIC_SYSTEM_PROMPT}\n{_LLM_CRITIC_USER_INSTRUCTION}"
            )
        prompt_hash = hashlib.sha256(prompt_template.encode("utf-8")).hexdigest()
        commit_sha = next(
            (
                os.environ[name].strip()
                for name in ("RENDER_GIT_COMMIT", "GITHUB_SHA", "CF_PAGES_COMMIT_SHA")
                if os.environ.get(name, "").strip()
            ),
            None,
        )
        return {
            "schema_version": STUDY_MANIFEST_SCHEMA_VERSION,
            **clean,
            "order": order,
            "consent_confirmed": True,
            "consent_confirmed_at": created_at,
            "task_status": "configured",
            "task_started_at": "",
            "task_completed_at": "",
            "elapsed_seconds": None,
            "config_snapshot": {
                "app_session_version": "2.3",
                "commit_sha": commit_sha,
                "prompt": {
                    "id": prompt_id,
                    "template_sha256": prompt_hash,
                    "maximum_issues": 2,
                },
                "model": {
                    "enabled": model_enabled,
                    "requested": bool(use_llm),
                    "configured": bool(provider),
                    "provider": provider if model_enabled else None,
                    "temperature": STUDY_LLM_TEMPERATURE if model_enabled else None,
                    "max_tokens": STUDY_LLM_MAX_TOKENS if model_enabled else None,
                    "timeout_seconds": (
                        STUDY_LLM_TIMEOUT_SECONDS if model_enabled else None
                    ),
                },
            },
        }

    @staticmethod
    def _parse_timestamp(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    def _timestamp_at_or_after(value: str, reference: str) -> bool:
        """Compare ISO timestamps safely across Z/offset/precision variants."""
        try:
            current = datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
            baseline = datetime.fromisoformat(str(reference or "").replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return False
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        if baseline.tzinfo is None:
            baseline = baseline.replace(tzinfo=timezone.utc)
        return current >= baseline

    @staticmethod
    def _timestamp_after(value: str, reference: str) -> bool:
        try:
            current = datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
            baseline = datetime.fromisoformat(str(reference or "").replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return False
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        if baseline.tzinfo is None:
            baseline = baseline.replace(tzinfo=timezone.utc)
        return current > baseline

    @staticmethod
    def _latest_timestamp(values: Iterable[str]) -> str:
        parsed_values = []
        for value in values:
            try:
                parsed = datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
            except (TypeError, ValueError):
                continue
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            parsed_values.append((parsed, str(value)))
        return max(parsed_values, default=(None, ""), key=lambda item: item[0])[1]

    @staticmethod
    def _study_event_payload(manifest: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "study_id": manifest["study_id"],
            "participant_id": manifest["participant_id"],
            "condition": manifest["condition"],
            "case_id": manifest["case_id"],
            "order": manifest["order"],
        }

    @staticmethod
    def _study_events(session: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            event
            for event in session.get("event_log", [])
            if event.get("event_type") in {"study_task_start", "study_task_complete"}
        ]

    @staticmethod
    def _study_submission_complete(session: Dict[str, Any]) -> bool:
        submission = session.get("study_submission", {})
        rationales = submission.get("decision_rationales", [])
        return (
            len(str(submission.get("final_artifact", "")).strip()) >= 40
            and isinstance(rationales, list)
            and len(rationales) == 2
            and all(len(str(item).strip()) >= 10 for item in rationales)
        )

    @staticmethod
    def _general_chat_source_context(session: Dict[str, Any]) -> str:
        project = session.get("project", {})
        sections = [
            f"Project title: {project.get('title', '')}",
            f"Review context: {project.get('review_context', '')}",
            f"Project plan: {project.get('context', '')}",
            f"People and relationships: {project.get('target_people', '')}",
        ]
        for key, value in session.get("artifacts", {}).items():
            if str(value).strip():
                sections.append(f"{key.replace('_', ' ').title()}: {value}")
        return "\n\n".join(sections)[:12000]

    @staticmethod
    def _llm_usage_metrics(raw_usage: Any) -> Dict[str, int]:
        """Keep only non-sensitive numeric token usage returned by a provider."""
        if not isinstance(raw_usage, dict):
            return {}
        allowed = {
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "input_tokens",
            "output_tokens",
        }
        usage: Dict[str, int] = {}
        for key in allowed:
            value = raw_usage.get(key)
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)) and value >= 0:
                usage[key] = int(value)
        return usage

    def _record_study_llm_call(
        self,
        session: Dict[str, Any],
        *,
        call_type: str,
        result: Dict[str, Any],
        started_at: str,
        completed_at: str,
        latency_ms: float,
        input_chars: int,
    ) -> None:
        """Append an inspectable call receipt without duplicating prompt or response text."""
        if not session.get("study_manifest"):
            return
        provider = self._active_provider_summary() or {}
        response_text = str(result.get("text", ""))
        calls = session.setdefault("study_llm_calls", [])
        calls.append(
            {
                "call_index": len(calls) + 1,
                "call_type": call_type,
                "started_at": started_at,
                "completed_at": completed_at,
                "latency_ms": latency_ms,
                "ok": bool(result.get("ok")),
                "error_type": str(result.get("error_type", ""))[:80],
                "error": str(result.get("error", ""))[:300],
                "status_code": result.get("status_code"),
                "provider_id": self.llm_client.active_provider_id,
                "model": result.get("model") or provider.get("model"),
                "temperature": STUDY_LLM_TEMPERATURE,
                "max_tokens": STUDY_LLM_MAX_TOKENS,
                "usage": self._llm_usage_metrics(result.get("usage")),
                "input_chars": max(0, int(input_chars)),
                "output_chars": len(response_text),
                "response_sha256": (
                    hashlib.sha256(response_text.encode("utf-8")).hexdigest()
                    if response_text
                    else ""
                ),
            }
        )

    def study_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Return the immutable study manifest and task timing for one session."""
        session = self.get_session(session_id)
        if not session:
            return None
        manifest = session.get("study_manifest")
        if not manifest:
            raise ValueError("This is not an instrumented study session.")
        return {
            "session_id": session["id"],
            "manifest": manifest,
            "events": self._study_events(session),
        }

    def save_study_submission(
        self,
        session_id: str,
        final_artifact: str,
        decision_rationales: List[str],
    ) -> Optional[Dict[str, Any]]:
        """Save the condition-neutral final artifact required in both conditions."""
        session = self.get_session(session_id)
        if not session:
            return None
        manifest = session.get("study_manifest")
        if not manifest:
            raise ValueError("This is not an instrumented study session.")
        self._require_active_study_task(session)

        final_artifact = str(final_artifact or "").strip()
        if not isinstance(decision_rationales, list) or len(decision_rationales) != 2:
            raise ValueError("Provide exactly two decision rationales.")
        rationales = [str(item or "").strip() for item in decision_rationales]
        if len(final_artifact) < 40:
            raise ValueError("The final artifact must contain at least 40 characters.")
        if len(final_artifact) > STUDY_FINAL_ARTIFACT_MAX_CHARS:
            raise ValueError(
                f"The final artifact is limited to {STUDY_FINAL_ARTIFACT_MAX_CHARS} characters."
            )
        if any(len(item) < 10 for item in rationales):
            raise ValueError("Each decision rationale must contain at least 10 characters.")
        if any(len(item) > STUDY_RATIONALE_MAX_CHARS for item in rationales):
            raise ValueError(
                f"Each decision rationale is limited to {STUDY_RATIONALE_MAX_CHARS} characters."
            )

        now = utc_now()
        revision_number = int(
            session.get("study_submission", {}).get("revision_number", 0) or 0
        ) + 1
        submission = {
            "final_artifact": final_artifact,
            "decision_rationales": rationales,
            "saved_at": now,
            "revision_number": revision_number,
        }
        session["study_submission"] = submission
        session.setdefault("study_submission_history", []).append(dict(submission))
        session["updated_at"] = now
        self._save(
            session,
            "study_submission_saved",
            {
                **self._study_event_payload(manifest),
                "revision_number": revision_number,
                "final_artifact_chars": len(final_artifact),
                "rationale_chars": [len(item) for item in rationales],
            },
        )
        return session

    def add_study_chat_turn(
        self,
        session_id: str,
        message: str,
    ) -> Optional[Dict[str, Any]]:
        """Run and persist one bounded turn for the general-chat baseline."""
        session = self.get_session(session_id)
        if not session:
            return None
        manifest = session.get("study_manifest")
        if not manifest:
            raise ValueError("This is not an instrumented study session.")
        self._require_active_study_task(session)
        if manifest.get("condition") != "general_chat":
            raise ValueError("Study chat is available only in the general_chat condition.")

        message = str(message or "").strip()
        if not message:
            raise ValueError("Enter a message before sending.")
        if len(message) > STUDY_CHAT_MAX_INPUT_CHARS:
            raise ValueError(
                f"Study chat messages are limited to {STUDY_CHAT_MAX_INPUT_CHARS} characters."
            )
        turns = session.setdefault("study_chat", [])
        if len(turns) >= STUDY_CHAT_MAX_TURNS:
            raise ValueError(
                f"Study chat is limited to {STUDY_CHAT_MAX_TURNS} turns."
            )

        user_timestamp = utc_now()
        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    _GENERAL_CHAT_SYSTEM_PROMPT
                    + "\n\nSubmitted research materials:\n"
                    + self._general_chat_source_context(session)
                ),
            }
        ]
        for prior in turns:
            messages.append({"role": "user", "content": prior.get("user_text", "")})
            if prior.get("assistant_text"):
                messages.append(
                    {"role": "assistant", "content": prior.get("assistant_text", "")}
                )
        messages.append({"role": "user", "content": message})

        started = time.perf_counter()
        result = self.llm_client.chat_with_provider_detailed(
            self.llm_client.active_provider_id,
            messages,
            temperature=STUDY_LLM_TEMPERATURE,
            timeout=STUDY_LLM_TIMEOUT_SECONDS,
        )
        latency_ms = round((time.perf_counter() - started) * 1000, 3)
        assistant_timestamp = utc_now()
        assistant_text = str(result.get("text", ""))[:STUDY_CHAT_MAX_OUTPUT_CHARS]
        provider = self._active_provider_summary() or {}
        usage = self._llm_usage_metrics(result.get("usage"))
        turn = {
            "turn_index": len(turns) + 1,
            "user_text": message,
            "user_timestamp": user_timestamp,
            "assistant_text": assistant_text,
            "assistant_timestamp": assistant_timestamp,
            "latency_ms": latency_ms,
            "ok": bool(result.get("ok")),
            "error_type": str(result.get("error_type", ""))[:80],
            "error": str(result.get("error", ""))[:300],
            "status_code": result.get("status_code"),
            "provider_id": self.llm_client.active_provider_id,
            "model": result.get("model") or provider.get("model"),
            "temperature": STUDY_LLM_TEMPERATURE,
            "usage": usage,
            "response_sha256": (
                hashlib.sha256(assistant_text.encode("utf-8")).hexdigest()
                if assistant_text
                else ""
            ),
        }
        turns.append(turn)
        self._record_study_llm_call(
            session,
            call_type="general_chat",
            result={**result, "text": assistant_text},
            started_at=user_timestamp,
            completed_at=assistant_timestamp,
            latency_ms=latency_ms,
            input_chars=sum(len(item.get("content", "")) for item in messages),
        )
        session["updated_at"] = assistant_timestamp
        self._save(
            session,
            "study_chat_turn",
            {
                **self._study_event_payload(manifest),
                "turn_index": turn["turn_index"],
                "input_chars": len(message),
                "output_chars": len(assistant_text),
                "latency_ms": latency_ms,
                "ok": turn["ok"],
                "error_type": turn["error_type"],
            },
        )
        return session

    def start_study_task(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Start the measured task once; retries are idempotent."""
        session = self.get_session(session_id)
        if not session:
            return None
        manifest = session.get("study_manifest")
        if not manifest:
            raise ValueError("This is not an instrumented study session.")
        if manifest.get("task_status") == "completed":
            raise ValueError("This study task is already complete.")
        if manifest.get("task_started_at"):
            return session

        now = utc_now()
        manifest["task_status"] = "in_progress"
        manifest["task_started_at"] = now
        manifest["task_completed_at"] = ""
        manifest["elapsed_seconds"] = None
        session["updated_at"] = now
        self._save(
            session,
            "study_task_start",
            self._study_event_payload(manifest),
        )
        return session

    def complete_study_task(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Complete the measured task once and store server-derived elapsed time."""
        session = self.get_session(session_id)
        if not session:
            return None
        manifest = session.get("study_manifest")
        if not manifest:
            raise ValueError("This is not an instrumented study session.")
        if manifest.get("task_status") == "completed":
            return session
        started_at = manifest.get("task_started_at")
        if not started_at:
            raise ValueError("Start the study task before completing it.")
        if not self._study_submission_complete(session):
            raise ValueError(
                "Save one condition-neutral final artifact and exactly two decision "
                "rationales before completing the task."
            )

        now = utc_now()
        elapsed = max(
            0.0,
            (self._parse_timestamp(now) - self._parse_timestamp(started_at)).total_seconds(),
        )
        manifest["task_status"] = "completed"
        manifest["task_completed_at"] = now
        manifest["elapsed_seconds"] = round(elapsed, 3)
        session["updated_at"] = now
        event_payload = self._study_event_payload(manifest)
        event_payload["elapsed_seconds"] = manifest["elapsed_seconds"]
        self._save(session, "study_task_complete", event_payload)
        return session

    def study_export(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Build a pseudonymous, analysis-ready study record without free-text names."""
        session = self.get_session(session_id)
        if not session:
            return None
        manifest = session.get("study_manifest")
        if not manifest:
            raise ValueError("This is not an instrumented study session.")
        decisions = Counter(
            item.get("decision", "pending") for item in session.get("issues", [])
        )
        handoff_statuses = Counter(
            item.get("status", "open") for item in session.get("handoffs", [])
        )
        linked_issue_outputs = sum(
            bool(item.get("source_passage_ids")) for item in session.get("issues", [])
        )
        chat_turns = session.get("study_chat", [])
        llm_calls = session.get("study_llm_calls", [])
        submission = session.get("study_submission", {})
        rationales = submission.get("decision_rationales", [])
        usage_totals: Counter[str] = Counter()
        for call in llm_calls:
            usage_totals.update(self._llm_usage_metrics(call.get("usage")))
        return {
            "schema_version": STUDY_MANIFEST_SCHEMA_VERSION,
            "exported_at": utc_now(),
            "session_id": session["id"],
            "manifest": manifest,
            "task_events": self._study_events(session),
            "outcomes": {
                "session_status": session.get("status", ""),
                "passage_count": len(session.get("passages", [])),
                "trace_count": len(session.get("traces", [])),
                "issue_count": len(session.get("issues", [])),
                "issues_with_passage_evidence": linked_issue_outputs,
                "decision_counts": dict(sorted(decisions.items())),
                "handoff_count": len(session.get("handoffs", [])),
                "handoff_status_counts": dict(sorted(handoff_statuses.items())),
                "protocol_version": session.get("lineage", {}).get("version_number", 1),
                "chat_turn_count": len(chat_turns),
                "chat_input_chars": sum(
                    len(str(item.get("user_text", ""))) for item in chat_turns
                ),
                "chat_output_chars": sum(
                    len(str(item.get("assistant_text", ""))) for item in chat_turns
                ),
                "chat_error_count": sum(not item.get("ok", False) for item in chat_turns),
                "llm_call_count": len(llm_calls),
                "llm_success_count": sum(bool(item.get("ok")) for item in llm_calls),
                "llm_error_count": sum(not item.get("ok", False) for item in llm_calls),
                "llm_latency_ms_total": round(
                    sum(float(item.get("latency_ms", 0) or 0) for item in llm_calls),
                    3,
                ),
                "llm_token_usage": dict(sorted(usage_totals.items())),
                "final_artifact_submitted": self._study_submission_complete(session),
                "final_artifact_chars": len(
                    str(submission.get("final_artifact", ""))
                ),
                "decision_rationale_chars": [
                    len(str(item)) for item in rationales[:2]
                ],
                "submission_revision_count": int(
                    submission.get("revision_number", 0) or 0
                ),
            },
            "privacy_note": (
                "This record uses a pseudonymous participant code and excludes reviewer names "
                "and protocol free text. Pair it with separately governed artifacts only when "
                "the approved study protocol requires that linkage."
            ),
        }

    def create_protocol_version(self, session_id: str) -> Optional[Dict[str, Any]]:
        source = self.get_session(session_id)
        if not source:
            return None
        if source.get("study_manifest"):
            raise ValueError(
                "Instrumented study sessions are frozen. Start a separately assigned "
                "study session instead of creating an untracked protocol version."
            )
        current_version = int(source.get("lineage", {}).get("version_number", 1) or 1)
        payload = {
            "project": {**source.get("project", {}), "uses_ai": True},
            "artifacts": {
                **source.get("artifacts", {}),
                "ai_governance": "",
            },
            "intake_transcript": source.get("intake_transcript", []),
            "selected_scenarios": source.get("selected_scenarios", []),
            "use_llm": True,
            "application_profile_id": source.get("application_profile_id", ""),
            "tradeoff_deliberations": source.get("tradeoff_deliberations", {}),
            "lineage": {
                "parent_session_id": source["id"],
                "version_number": current_version + 1,
            },
        }
        version = self.create_session(payload)
        self.store.log(
            source["id"],
            "protocol_version_created",
            {"new_session_id": version["id"], "version_number": current_version + 1},
        )
        return version

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.store.load(session_id)
        if session:
            session.setdefault("tradeoff_deliberations", {})
            if not isinstance(session.get("handoffs"), list):
                session["handoffs"] = []
            handoff_defaults = {
                "advice_type": "",
                "advice_type_label": "",
                "responsible_actor": "",
                "closure_evidence": "",
                "reviewed_passage_ids": [],
                "evidence_gap_acknowledged": False,
                "evidence_reviewed": False,
                "evidence_reviewed_at": "",
                "review_history": [],
                "researcher_revision_history": [],
            }
            for handoff in session["handoffs"]:
                for key, default in handoff_defaults.items():
                    if key not in handoff or handoff[key] is None:
                        handoff[key] = list(default) if isinstance(default, list) else default
                if not isinstance(handoff.get("reviewed_passage_ids"), list):
                    handoff["reviewed_passage_ids"] = []
                if not isinstance(handoff.get("review_history"), list):
                    handoff["review_history"] = []
                if not isinstance(handoff.get("researcher_revision_history"), list):
                    handoff["researcher_revision_history"] = []
            if not session.get("audit_plan"):
                session["audit_plan"] = self._build_audit_plan(
                    session, session.get("selected_scenarios") or None
                )
            session["application_readiness"] = build_application_readiness(session)
            session["event_log"] = self.store.list_events(session_id)
        return session

    def update_map(self, session_id: str, stages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None
        self._require_active_study_task(session)
        self._require_safebars_condition(session)
        if self._human_review_started(session):
            raise ValueError("The encounter scope cannot change after human review has started. Create a new protocol version instead.")
        allowed_ids = {stage["id"] for stage in STAGE_DEFINITIONS}
        cleaned = []
        for stage in stages:
            if stage.get("id") not in allowed_ids:
                continue
            cleaned.append(
                {
                    **stage,
                    "name": str(stage.get("name", "")).strip(),
                    "notes": str(stage.get("notes", "")).strip(),
                    "included": bool(stage.get("included", True)),
                }
            )
        if cleaned:
            if session.get("status") == "audited":
                self._invalidate_audit_results(session)
            session["encounter_map"] = cleaned
            session["audit_plan"] = self._build_audit_plan(
                session, session.get("selected_scenarios") or None
            )
            session["updated_at"] = utc_now()
            self._save(
                session,
                "map_updated",
                {
                    "stage_count": len(cleaned),
                    "planned_task_count": len(session["audit_plan"]),
                },
            )
        return session

    def update_audit_plan(
        self,
        session_id: str,
        scenario_ids: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None
        self._require_active_study_task(session)
        self._require_safebars_condition(session)
        valid_ids = {item["id"] for item in SCENARIO_LIBRARY}
        selected = [item for item in (scenario_ids or []) if item in valid_ids]
        if not selected:
            raise ValueError("Select at least one bounded scenario for the audit plan.")
        if self._human_review_started(session):
            raise ValueError("The audit plan cannot change after human review has started. Create a new protocol version instead.")
        if session.get("status") == "audited":
            self._invalidate_audit_results(session)
        session["selected_scenarios"] = selected
        session["audit_plan"] = self._build_audit_plan(session, selected)
        session["status"] = "mapped"
        session["updated_at"] = utc_now()
        self._save(
            session,
            "audit_plan_updated",
            {
                "scenario_ids": selected,
                "task_order": [item["id"] for item in session["audit_plan"]],
            },
        )
        return session

    def update_application_profile(
        self,
        session_id: str,
        profile_id: str,
    ) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None
        self._require_active_study_task(session)
        self._require_safebars_condition(session)
        if profile_id not in APPLICATION_PROFILES:
            raise ValueError("Select a recognized application profile.")
        session["application_profile_id"] = profile_id
        session["updated_at"] = utc_now()
        self._save(session, "application_profile_updated", {"profile_id": profile_id})
        return session

    def update_tradeoff_deliberations(
        self,
        session_id: str,
        deliberations: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None
        self._require_active_study_task(session)
        self._require_safebars_condition(session)
        allowed = {
            item.get("id"): item
            for item in session.get("framework_assessment", {}).get("tradeoffs", [])
        }
        cleaned: Dict[str, Dict[str, Any]] = {}
        for item in deliberations or []:
            tradeoff_id = str(item.get("id", "")).strip()
            if tradeoff_id not in allowed:
                continue
            try:
                value = int(item.get("value", allowed[tradeoff_id].get("left", {}).get("value", 50)))
            except (TypeError, ValueError):
                raise ValueError("Trade-off positions must be whole numbers from 0 to 100.")
            if value < 0 or value > 100:
                raise ValueError("Trade-off positions must be between 0 and 100.")
            cleaned[tradeoff_id] = {
                "id": tradeoff_id,
                "value": value,
                "rationale": str(item.get("rationale", "")).strip()[:2000],
                "updated_at": utc_now(),
            }
        if not cleaned:
            raise ValueError("Add at least one recognized trade-off deliberation.")
        session["tradeoff_deliberations"] = {
            **session.get("tradeoff_deliberations", {}),
            **cleaned,
        }
        session["updated_at"] = utc_now()
        self._save(
            session,
            "tradeoff_deliberations_updated",
            {
                "tradeoff_ids": list(cleaned),
                "positions": {key: value["value"] for key, value in cleaned.items()},
            },
        )
        return session

    def run_audit(self, session_id: str, scenario_ids: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None
        self._require_active_study_task(session)
        self._require_safebars_condition(session)
        if self._human_review_started(session):
            raise ValueError("The audit cannot be rerun after human review has started. Create a new protocol version to preserve the review record.")

        selected = set(scenario_ids or session.get("selected_scenarios") or [])
        scenarios = [item for item in SCENARIO_LIBRARY if not selected or item["id"] in selected]
        session["selected_scenarios"] = [item["id"] for item in scenarios]
        session["audit_plan"] = self._build_audit_plan(session, session["selected_scenarios"])
        session["traces"] = []
        session["issues"] = []
        session["handoffs"] = []
        session["agent_activity"] = [
            item for item in session.get("agent_activity", []) if item.get("agent") == "Encounter Orchestrator"
        ]

        scenario_by_id = {item["id"]: item for item in scenarios}
        scenario_tasks = sorted(
            [item for item in session["audit_plan"] if item["kind"] == "scenario"],
            key=lambda item: (PRIORITY_ORDER[item["priority"]], item["id"]),
        )
        self._activity(session, "Breakdown Scenario Agent", "running", f"Tracing {len(scenario_tasks)} material-routed scenarios.")
        for task in scenario_tasks:
            scenario = scenario_by_id[task["scenario_id"]]
            self._start_task(task)
            trace = self._trace_scenario(session, scenario)
            session["traces"].append(trace)
            if trace["status"] != "covered":
                session["issues"].append(self._issue_from_trace(session, scenario, trace))
            self._finish_task(
                task,
                "paused" if trace["status"] == "not_run" else "completed",
                [trace["id"]],
                trace["first_gap"],
            )
        self._activity(session, "Breakdown Scenario Agent", "completed", f"Produced {len(session['traces'])} inspectable traces.")

        relationship_task = self._plan_task(session, "relationship")
        if relationship_task:
            self._start_task(relationship_task)
        self._activity(session, "Relationship and Power Agent", "running", "Checking support, pressure, gatekeeping, and responsibility roles.")
        relationship_issues = self._relationship_issues(session)
        session["issues"].extend(relationship_issues)
        if relationship_task:
            self._finish_task(
                relationship_task,
                "completed",
                [item["id"] for item in relationship_issues],
                f"Produced {len(relationship_issues)} relationship-specific issue(s).",
            )
        self._activity(session, "Relationship and Power Agent", "completed", "Added relationship-specific planning questions where needed.")

        llm_task = self._plan_task(session, "llm_critic")
        if session.get("use_llm") and self.llm_client.is_configured():
            if llm_task:
                self._start_task(llm_task)
            self._activity(session, "Bounded LLM Critic", "running", "Looking for up to two passage-grounded gaps beyond the scenario library.")
            llm_issues, detail = self._llm_issues(session)
            session["issues"].extend(llm_issues)
            state = "completed" if llm_issues else "fallback"
            if llm_task:
                self._finish_task(llm_task, state, [item["id"] for item in llm_issues], detail)
            self._activity(session, "Bounded LLM Critic", state, detail)

        boundary_task = self._plan_task(session, "boundary_handoff")
        if boundary_task:
            self._start_task(boundary_task)
        self._activity(session, "Boundary and Handoff Agent", "running", "Checking provenance, preserving contestation, and removing participant-proxy claims.")
        session["issues"] = self._boundary_check(session, session["issues"])
        session["issues"] = self._deduplicate_issues(session["issues"])
        session["handoffs"] = self._initial_handoffs(session["issues"])
        if boundary_task:
            self._finish_task(
                boundary_task,
                "completed",
                [item["id"] for item in session["handoffs"]],
                f"Checked {len(session['issues'])} issue(s) and prepared {len(session['handoffs'])} handoff(s).",
            )
        self._activity(
            session,
            "Boundary and Handoff Agent",
            "completed",
            f"Prepared {len(session['issues'])} contestable issues and {len(session['handoffs'])} real-person handoffs.",
        )
        session["status"] = "audited"
        session["updated_at"] = utc_now()
        self._save(
            session,
            "audit_completed",
            {
                "trace_count": len(session["traces"]),
                "issue_count": len(session["issues"]),
                "task_order": [item["id"] for item in scenario_tasks],
            },
        )
        return session

    def rerun_task(self, session_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Rerun one bounded task without silently overwriting a human decision."""
        session = self.get_session(session_id)
        if not session:
            return None
        self._require_active_study_task(session)
        self._require_safebars_condition(session)
        task = next((item for item in session.get("audit_plan", []) if item["id"] == task_id), None)
        if not task:
            raise KeyError("Audit task not found.")
        if task["kind"] in {"orchestrator", "boundary_handoff"}:
            raise ValueError("This coordination task is refreshed automatically after a specialist rerun.")

        affected = self._issues_for_task(session, task)
        decided = [item for item in affected if item.get("decision", "pending") != "pending"]
        if decided:
            raise ValueError("Reset the related human decision before rerunning this task.")

        affected_ids = {item["id"] for item in affected}
        session["issues"] = [item for item in session.get("issues", []) if item["id"] not in affected_ids]
        session["handoffs"] = [
            item for item in session.get("handoffs", []) if item.get("issue_id") not in affected_ids
        ]
        self._start_task(task)

        if task["kind"] == "scenario":
            scenario = next(item for item in SCENARIO_LIBRARY if item["id"] == task["scenario_id"])
            session["traces"] = [
                item for item in session.get("traces", []) if item.get("scenario_id") != scenario["id"]
            ]
            trace = self._trace_scenario(session, scenario)
            session["traces"].append(trace)
            if trace["status"] != "covered":
                session["issues"].append(self._issue_from_trace(session, scenario, trace))
            self._finish_task(
                task,
                "paused" if trace["status"] == "not_run" else "completed",
                [trace["id"]],
                trace["first_gap"],
            )
        elif task["kind"] == "relationship":
            issues = self._relationship_issues(session)
            session["issues"].extend(issues)
            self._finish_task(
                task,
                "completed",
                [item["id"] for item in issues],
                f"Produced {len(issues)} relationship-specific issue(s).",
            )
        elif task["kind"] == "llm_critic":
            if not session.get("use_llm") or not self.llm_client.is_configured():
                self._finish_task(task, "fallback", [], "No configured LLM provider; no model call was made.")
            else:
                issues, detail = self._llm_issues(session)
                session["issues"].extend(issues)
                self._finish_task(
                    task,
                    "completed" if issues else "fallback",
                    [item["id"] for item in issues],
                    detail,
                )

        session["issues"] = self._deduplicate_issues(
            self._boundary_check(session, session.get("issues", []))
        )
        session["handoffs"] = self._initial_handoffs(session["issues"], session.get("handoffs", []))
        boundary_task = self._plan_task(session, "boundary_handoff")
        if boundary_task:
            self._start_task(boundary_task)
            self._finish_task(
                boundary_task,
                "completed",
                [item["id"] for item in session["handoffs"]],
                "Boundary and handoff state refreshed after specialist rerun.",
            )
        session["updated_at"] = utc_now()
        self._save(session, "audit_task_rerun", {"task_id": task_id, "attempt": task["attempts"]})
        return session

    def record_decision(
        self,
        session_id: str,
        issue_id: str,
        decision: str,
        rationale: str = "",
        revised_text: str = "",
    ) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None
        self._require_active_study_task(session)
        self._require_safebars_condition(session)
        if decision not in {"accept", "edit", "reject", "defer", "pending"}:
            raise ValueError("Decision must be accept, edit, reject, defer, or pending.")
        issue = next((item for item in session.get("issues", []) if item["id"] == issue_id), None)
        if not issue:
            raise KeyError("Issue not found.")
        issue["decision"] = decision
        issue["decision_rationale"] = rationale.strip()
        issue["revised_text"] = revised_text.strip()
        issue["decided_at"] = utc_now() if decision != "pending" else ""
        if decision == "defer":
            self._ensure_handoff(session, issue)
        session["updated_at"] = utc_now()
        self._save(session, "issue_decision", {"issue_id": issue_id, "decision": decision})
        return session

    def respond_to_handoff(
        self,
        session_id: str,
        handoff_id: str,
        response: str = "",
        revised_text: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Link an expert handoff to a researcher response and protocol revision."""
        session = self.get_session(session_id)
        if not session:
            return None
        self._require_active_study_task(session)
        self._require_safebars_condition(session)
        handoff = next(
            (item for item in session.get("handoffs", []) if item.get("id") == handoff_id),
            None,
        )
        if not handoff:
            raise KeyError("Handoff not found.")
        if handoff.get("status") == "resolved":
            raise ValueError(
                "This handoff is closed. An expert must reopen it before the researcher can add another response."
            )
        response = str(response or "").strip()
        revised_text = str(revised_text or "").strip()
        if not response and not revised_text:
            raise ValueError("Add a response or revised protocol text before submitting.")

        now = utc_now()
        revision = {
            "response": response,
            "revised_text": revised_text,
            "timestamp": now,
        }
        handoff.setdefault("researcher_revision_history", []).append(revision)
        handoff["researcher_response"] = response
        handoff["researcher_revised_text"] = revised_text
        handoff["researcher_responded_at"] = now
        handoff["status"] = "researcher_revised" if revised_text else "researcher_responded"
        handoff["resolved_at"] = ""
        # A new researcher answer changes the evidence under review. Preserve the
        # earlier review in history, but require the expert to inspect the latest
        # material before another substantive action or closure.
        handoff["reviewed_passage_ids"] = []
        handoff["evidence_gap_acknowledged"] = False
        handoff["evidence_reviewed"] = False
        handoff["evidence_reviewed_at"] = ""

        issue = next(
            (item for item in session.get("issues", []) if item.get("id") == handoff.get("issue_id")),
            None,
        )
        if issue:
            if revised_text:
                issue["revised_text"] = revised_text
                issue["decision"] = "edit"
                issue["decided_at"] = now
            if response:
                issue["decision_rationale"] = response

        session["updated_at"] = now
        self._save(
            session,
            "researcher_handoff_response",
            {
                "handoff_id": handoff_id,
                "has_response": bool(response),
                "has_revision": bool(revised_text),
            },
        )
        return session

    def review_handoff(
        self,
        session_id: str,
        handoff_id: str,
        action: str,
        reviewer_role: str,
        reviewer_name: str = "",
        advice: str = "",
        rationale: str = "",
        redirect_role: str = "",
        advice_type: str = "",
        responsible_actor: str = "",
        closure_evidence: str = "",
        reviewed_passage_ids: Optional[List[str]] = None,
        evidence_gap_acknowledged: bool = False,
    ) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None
        valid_actions = {"assign", "advise", "request_clarification", "redirect", "resolve", "reopen"}
        if action not in valid_actions:
            raise ValueError("Unsupported expert-review action.")
        if reviewer_role not in EXPERT_ROLES:
            raise ValueError("Select a recognized expert role.")
        handoff = next(
            (item for item in session.get("handoffs", []) if item.get("id") == handoff_id),
            None,
        )
        if not handoff:
            raise KeyError("Handoff not found.")
        if handoff.get("status") == "resolved" and action != "reopen":
            raise ValueError("This handoff is already closed. Reopen it before recording another expert action.")
        if action == "reopen" and handoff.get("status") != "resolved":
            raise ValueError("Only a resolved handoff can be reopened.")
        if reviewed_passage_ids is not None and not isinstance(
            reviewed_passage_ids, (list, tuple, set)
        ):
            raise ValueError("Reviewed evidence must be supplied as a list of protocol passage IDs.")
        reviewer_name = str(reviewer_name or "").strip()
        substantive_actions = {"advise", "request_clarification", "resolve"}
        advice = str(advice or "").strip() or str(handoff.get("expert_advice") or "").strip()
        rationale = str(rationale or "").strip() or str(handoff.get("expert_rationale") or "").strip()
        advice_type = str(advice_type or "").strip() or str(handoff.get("advice_type") or "").strip()
        responsible_actor = (
            str(responsible_actor or "").strip()
            or str(handoff.get("responsible_actor") or "").strip()
        )
        closure_evidence = (
            str(closure_evidence or "").strip()
            or str(handoff.get("closure_evidence") or "").strip()
        )
        if action == "request_clarification":
            advice_type = "clarification_request"
        issue = next(
            (item for item in session.get("issues", []) if item.get("id") == handoff.get("issue_id")),
            {},
        )
        required_passage_ids = {
            str(item) for item in issue.get("source_passage_ids", []) if str(item).strip()
        }
        valid_passage_ids = {
            str(item.get("id")) for item in session.get("passages", []) if item.get("id")
        }
        submitted_passage_ids = {
            str(item) for item in (reviewed_passage_ids or []) if str(item).strip()
        }
        unknown_passage_ids = submitted_passage_ids - valid_passage_ids
        if unknown_passage_ids:
            raise ValueError("Reviewed evidence contains an unknown protocol passage ID.")
        stored_passage_ids = {
            str(item) for item in handoff.get("reviewed_passage_ids", []) if str(item).strip()
        }
        latest_researcher_evidence_at = str(handoff.get("researcher_responded_at") or "")
        stored_review_at = str(handoff.get("evidence_reviewed_at") or "")
        stored_evidence_is_current = not latest_researcher_evidence_at or (
            bool(stored_review_at)
            and self._timestamp_at_or_after(
                stored_review_at, latest_researcher_evidence_at
            )
        )
        effective_passage_ids = (
            submitted_passage_ids
            if submitted_passage_ids
            else (stored_passage_ids if stored_evidence_is_current else set())
        )
        evidence_reviewed = bool(
            required_passage_ids.intersection(effective_passage_ids)
            if required_passage_ids
            else (
                evidence_gap_acknowledged
                or (
                    handoff.get("evidence_gap_acknowledged")
                    and stored_evidence_is_current
                )
            )
        )
        if action in substantive_actions:
            if advice_type not in EXPERT_ADVICE_TYPES:
                raise ValueError("Classify the response as a required change, optional recommendation, clarification request, or no change required.")
            if action == "advise" and advice_type == "clarification_request":
                raise ValueError("Use Ask researcher when the response is a clarification request.")
            if len(advice) < 10:
                raise ValueError("Write a concrete expert instruction or conclusion before saving.")
            if len(rationale) < 10:
                raise ValueError("Explain the ethical rationale before saving.")
            if len(responsible_actor) < 2:
                raise ValueError("Name the person or role responsible for the next action.")
            if len(closure_evidence) < 10:
                raise ValueError("State what evidence would be sufficient to close this handoff.")
            if not evidence_reviewed:
                if required_passage_ids:
                    raise ValueError("Open Evidence and review at least one cited protocol passage before saving this expert action.")
                raise ValueError("This handoff has no cited passage. Review the evidence gap and acknowledge it before saving.")
            if action == "resolve" and not required_passage_ids and not (
                handoff.get("researcher_response")
                or handoff.get("researcher_revised_text")
                or handoff.get("researcher_revision_history")
            ):
                raise ValueError("No cited protocol passage supports closure. Ask the researcher for clarification or revised evidence first.")
            if action == "resolve":
                blocking_events = [
                    item
                    for item in handoff.get("review_history", [])
                    if item.get("action") in {"advise", "request_clarification"}
                    and (
                        item.get("advice_type")
                        in {"required_change", "clarification_request"}
                        or item.get("action") == "request_clarification"
                    )
                ]
                latest_blocking_request_at = self._latest_timestamp(
                    str(item.get("timestamp") or "") for item in blocking_events
                )
                response_at = str(handoff.get("researcher_responded_at") or "")
                if latest_blocking_request_at and (
                    not response_at
                    or not self._timestamp_after(
                        response_at, latest_blocking_request_at
                    )
                ):
                    raise ValueError(
                        "The researcher has not responded to the latest required change or clarification request. Keep this handoff open."
                    )
            if action == "resolve" and advice_type in {"required_change", "clarification_request"}:
                request_events = [
                    item
                    for item in handoff.get("review_history", [])
                    if item.get("action") in {"advise", "request_clarification"}
                    and (
                        item.get("advice_type") == advice_type
                        or (
                            advice_type == "clarification_request"
                            and item.get("action") == "request_clarification"
                        )
                    )
                ]
                latest_request_at = self._latest_timestamp(
                    str(item.get("timestamp") or "") for item in request_events
                )
                response_at = str(handoff.get("researcher_responded_at") or "")
                if not latest_request_at:
                    raise ValueError("Send this required change or clarification request to the researcher before closing the handoff.")
                if not response_at or not self._timestamp_after(
                    response_at, latest_request_at
                ):
                    raise ValueError("The researcher has not responded to the latest required change or clarification request. Keep this handoff open.")
        if action == "redirect" and redirect_role not in EXPERT_ROLES:
            raise ValueError("Select a recognized role to receive the redirected handoff.")

        now = utc_now()
        event = {
            "action": action,
            "reviewer_role": reviewer_role,
            "reviewer_role_label": EXPERT_ROLES[reviewer_role]["label"],
            "reviewer_name": reviewer_name,
            "timestamp": now,
        }
        if action in substantive_actions:
            event.update(
                {
                    "advice": advice,
                    "rationale": rationale,
                    "advice_type": advice_type,
                    "advice_type_label": EXPERT_ADVICE_TYPES[advice_type]["label"],
                    "responsible_actor": responsible_actor,
                    "closure_evidence": closure_evidence,
                    "reviewed_passage_ids": sorted(effective_passage_ids),
                    "evidence_gap_acknowledged": bool(
                        evidence_gap_acknowledged
                        or handoff.get("evidence_gap_acknowledged")
                    ),
                    "evidence_reviewed": evidence_reviewed,
                    "evidence_reviewed_at": now,
                }
            )
        handoff.setdefault("review_history", []).append(event)
        handoff["reviewer_role"] = reviewer_role
        handoff["reviewer_name"] = reviewer_name
        if action in substantive_actions:
            handoff["expert_advice"] = advice
            handoff["expert_rationale"] = rationale
            handoff["advice_type"] = advice_type
            handoff["advice_type_label"] = EXPERT_ADVICE_TYPES[advice_type]["label"]
            handoff["responsible_actor"] = responsible_actor
            handoff["closure_evidence"] = closure_evidence
            handoff["reviewed_passage_ids"] = sorted(effective_passage_ids)
            handoff["evidence_gap_acknowledged"] = bool(
                evidence_gap_acknowledged or handoff.get("evidence_gap_acknowledged")
            )
            handoff["evidence_reviewed"] = evidence_reviewed
            handoff["evidence_reviewed_at"] = now
        handoff["reviewed_at"] = now
        if action in {"advise", "request_clarification", "resolve"} and not handoff.get("assigned_role"):
            handoff["assigned_role"] = reviewer_role
            handoff["assigned_role_label"] = EXPERT_ROLES[reviewer_role]["label"]
            handoff["assigned_reviewer_name"] = reviewer_name or EXPERT_ROLES[reviewer_role]["label"]
            handoff["assigned_at"] = now
        if action == "assign":
            handoff["assigned_role"] = reviewer_role
            handoff["assigned_role_label"] = EXPERT_ROLES[reviewer_role]["label"]
            handoff["assigned_reviewer_name"] = reviewer_name or EXPERT_ROLES[reviewer_role]["label"]
            handoff["assigned_at"] = now
            handoff["status"] = "assigned"
        elif action == "advise":
            if not handoff.get("assigned_role"):
                handoff["assigned_role"] = reviewer_role
                handoff["assigned_role_label"] = EXPERT_ROLES[reviewer_role]["label"]
                handoff["assigned_reviewer_name"] = reviewer_name or EXPERT_ROLES[reviewer_role]["label"]
                handoff["assigned_at"] = now
            handoff["status"] = "advised"
        elif action == "request_clarification":
            if not handoff.get("assigned_role"):
                handoff["assigned_role"] = reviewer_role
                handoff["assigned_role_label"] = EXPERT_ROLES[reviewer_role]["label"]
                handoff["assigned_reviewer_name"] = reviewer_name or EXPERT_ROLES[reviewer_role]["label"]
                handoff["assigned_at"] = now
            handoff["status"] = "needs_clarification"
        elif action == "redirect":
            role = EXPERT_ROLES[redirect_role]
            handoff["recommended_role"] = redirect_role
            handoff["recommended_role_label"] = role["label"]
            handoff["owner"] = role["label"]
            handoff["assigned_role"] = redirect_role
            handoff["assigned_role_label"] = role["label"]
            handoff["assigned_reviewer_name"] = ""
            handoff["assigned_at"] = now
            handoff["status"] = "redirected"
            event["redirect_role"] = redirect_role
            event["redirect_role_label"] = role["label"]
        elif action == "resolve":
            handoff["status"] = "resolved"
            handoff["resolved_at"] = now
        elif action == "reopen":
            handoff["status"] = "open"
            handoff["resolved_at"] = ""
            handoff["reviewed_passage_ids"] = []
            handoff["evidence_gap_acknowledged"] = False
            handoff["evidence_reviewed"] = False
            handoff["evidence_reviewed_at"] = ""

        session["updated_at"] = now
        self._save(
            session,
            "expert_handoff_review",
            {
                "handoff_id": handoff_id,
                "action": action,
                "reviewer_role": reviewer_role,
                "advice_type": advice_type if action in substantive_actions else "",
                "reviewed_passage_ids": sorted(effective_passage_ids)
                if action in substantive_actions
                else [],
                "evidence_reviewed": evidence_reviewed
                if action in substantive_actions
                else False,
            },
        )
        return session

    def expert_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None
        issue_by_id = {item["id"]: item for item in session.get("issues", [])}
        queue = []
        for handoff in session.get("handoffs", []):
            issue = issue_by_id.get(handoff.get("issue_id"), {})
            researcher_evidence_at = str(handoff.get("researcher_responded_at") or "")
            evidence_review_at = str(handoff.get("evidence_reviewed_at") or "")
            evidence_review_current = bool(
                handoff.get("evidence_reviewed")
                and (
                    not researcher_evidence_at
                    or self._timestamp_at_or_after(
                        evidence_review_at, researcher_evidence_at
                    )
                )
            )
            closure_record_complete = bool(
                handoff.get("advice_type") in EXPERT_ADVICE_TYPES
                and len(str(handoff.get("expert_advice") or "").strip()) >= 10
                and len(str(handoff.get("expert_rationale") or "").strip()) >= 10
                and len(str(handoff.get("responsible_actor") or "").strip()) >= 2
                and len(str(handoff.get("closure_evidence") or "").strip()) >= 10
                and evidence_review_current
            )
            queue.append(
                {
                    **handoff,
                    "evidence_review_current": evidence_review_current,
                    "closure_record_complete": closure_record_complete,
                    "legacy_resolution": bool(
                        handoff.get("status") == "resolved"
                        and not closure_record_complete
                    ),
                    "issue": {
                        "title": issue.get("title", "Unresolved protocol issue"),
                        "severity": issue.get("severity", "unknown"),
                        "category": issue.get("category", "unknown"),
                        "observation": issue.get("observation", ""),
                        "suggestion": issue.get("suggestion", ""),
                        "source_passage_ids": issue.get("source_passage_ids", []),
                        "researcher_decision": issue.get("decision", "pending"),
                        "researcher_rationale": issue.get("decision_rationale", ""),
                    },
                }
            )
        priority_order = {"high": 0, "medium": 1, "standard": 2}
        queue.sort(key=lambda item: (priority_order.get(item.get("priority", "standard"), 3), item.get("status") == "resolved"))
        role_counts: Dict[str, int] = {}
        for item in queue:
            role_id = item.get("assigned_role") or item.get("recommended_role") or "unassigned"
            role_counts[role_id] = role_counts.get(role_id, 0) + 1
        return {
            "session_id": session["id"],
            "project": session.get("project", {}),
            "framework_pathway": session.get("framework_assessment", {}).get("pathway", "unassessed"),
            "framework_dimensions": session.get("framework_assessment", {}).get("dimensions", []),
            "passages": session.get("passages", []),
            "generated_at": utc_now(),
            "queue": queue,
            "counts": {
                "total": len(queue),
                "unresolved": sum(item.get("status") != "resolved" for item in queue),
                "high_priority": sum(item.get("priority") == "high" for item in queue),
                "unresolved_high_priority": sum(
                    item.get("priority") == "high" and item.get("status") != "resolved"
                    for item in queue
                ),
                "advised": sum(item.get("status") == "advised" for item in queue),
                "resolved": sum(item.get("status") == "resolved" for item in queue),
                "assigned": sum(bool(item.get("assigned_role")) or item.get("status") == "assigned" for item in queue),
                "needs_clarification": sum(item.get("status") == "needs_clarification" for item in queue),
            },
            "role_counts": role_counts,
            "boundary": "Expert advice supports institutional review; this summary is not an approval decision.",
        }

    def _build_audit_plan(
        self,
        session: Dict[str, Any],
        scenario_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Create a material-dependent, inspectable execution plan."""
        selected = set(scenario_ids or [item["id"] for item in SCENARIO_LIBRARY])
        now = utc_now()
        plan: List[Dict[str, Any]] = [
            {
                "id": "task_orchestrate",
                "kind": "orchestrator",
                "agent": "Encounter Orchestrator",
                "title": "Index materials and map the encounter",
                "goal": "Create addressable passages, stages, and a bounded specialist queue.",
                "reason": f"The submitted package contains {len(session.get('passages', []))} addressable passage(s).",
                "priority": "high",
                "status": "completed",
                "depends_on": [],
                "input_passage_ids": [item["id"] for item in session.get("passages", [])[:12]],
                "tools": ["protocol parser", "artifact inventory", "stage coverage mapper"],
                "stop_condition": "Stop for human scope confirmation before specialist tasks run.",
                "attempts": 1,
                "last_started_at": now,
                "last_completed_at": now,
                "output_ids": [item["id"] for item in session.get("encounter_map", [])],
                "result_summary": "Editable encounter map created; awaiting human scope confirmation.",
            }
        ]

        scenario_task_ids = []
        for scenario in SCENARIO_LIBRARY:
            if scenario["id"] not in selected:
                continue
            priority, reason, input_ids = self._scenario_route(session, scenario)
            task_id = f"task_scenario_{scenario['id']}"
            scenario_task_ids.append(task_id)
            plan.append(
                {
                    "id": task_id,
                    "kind": "scenario",
                    "scenario_id": scenario["id"],
                    "agent": "Breakdown Scenario Agent",
                    "title": scenario["title"],
                    "goal": "Trace the protocol response and stop at the first unsupported transition.",
                    "reason": reason,
                    "priority": priority,
                    "status": "queued",
                    "depends_on": ["task_orchestrate"],
                    "input_passage_ids": input_ids,
                    "tools": ["passage retrieval", "safeguard lookup", "transition tracer"],
                    "stop_condition": scenario["boundary_explanation"],
                    "attempts": 0,
                    "last_started_at": "",
                    "last_completed_at": "",
                    "output_ids": [],
                    "result_summary": "",
                }
            )

        relationship_reason = self._relationship_route_reason(session)
        plan.append(
            {
                "id": "task_relationship",
                "kind": "relationship",
                "agent": "Relationship and Power Agent",
                "title": "Inspect support, pressure, gatekeeping, and responsibility",
                "goal": "Map consequential relationships without generating demographic personas.",
                "reason": relationship_reason,
                "priority": "high" if "missing" in relationship_reason.lower() else "medium",
                "status": "queued",
                "depends_on": ["task_orchestrate"],
                "input_passage_ids": [
                    item["id"]
                    for item in self._passages(session, ["recruitment", "consent", "safety"])[:8]
                ],
                "tools": ["relationship term scan", "responsibility check", "role boundary rules"],
                "stop_condition": "Stop before claiming which relationships matter locally; create a real-person handoff.",
                "attempts": 0,
                "last_started_at": "",
                "last_completed_at": "",
                "output_ids": [],
                "result_summary": "",
            }
        )

        llm_enabled = bool(session.get("use_llm") and self.llm_client.is_configured())
        plan.append(
            {
                "id": "task_llm_critic",
                "kind": "llm_critic",
                "agent": "Bounded LLM Critic",
                "title": "Probe for additional passage-grounded gaps",
                "goal": "Find at most two non-checklist gaps while remaining grounded to submitted passages.",
                "reason": (
                    "The always-on AI review path found a configured provider for this bounded probe."
                    if llm_enabled
                    else "The AI critic was requested automatically, but no provider is configured; deterministic tracing remains active."
                ),
                "priority": "low",
                "status": "queued" if llm_enabled else "skipped",
                "depends_on": ["task_orchestrate"],
                "input_passage_ids": [item["id"] for item in session.get("passages", [])[:40]],
                "tools": ["bounded model call", "JSON schema validation", "passage ID validator"],
                "stop_condition": "Return no issue unless it cites an existing passage; never speak as a participant.",
                "attempts": 0,
                "last_started_at": "",
                "last_completed_at": "",
                "output_ids": [],
                "result_summary": "",
            }
        )

        specialist_dependencies = scenario_task_ids + ["task_relationship"]
        if llm_enabled:
            specialist_dependencies.append("task_llm_critic")
        plan.append(
            {
                "id": "task_boundary_handoff",
                "kind": "boundary_handoff",
                "agent": "Boundary and Handoff Agent",
                "title": "Check provenance, preserve contestation, and route unknowns",
                "goal": "Prevent participant-proxy claims and convert situated unknowns into named consultation tasks.",
                "reason": "This task is conditionally released only after the selected specialist tasks finish.",
                "priority": "high",
                "status": "blocked",
                "depends_on": specialist_dependencies,
                "input_passage_ids": [],
                "tools": ["provenance validator", "claim boundary rules", "handoff generator"],
                "stop_condition": "Do not resolve local, legal, clinical, community, or normative questions with generated text.",
                "attempts": 0,
                "last_started_at": "",
                "last_completed_at": "",
                "output_ids": [],
                "result_summary": "",
            }
        )
        return plan

    def _scenario_route(
        self,
        session: Dict[str, Any],
        scenario: Dict[str, Any],
    ) -> tuple[str, str, List[str]]:
        stage = next(
            (item for item in session.get("encounter_map", []) if item["id"] == scenario["trigger_stage"]),
            None,
        )
        relevant = self._passages(session, scenario["artifacts"])
        safeguards = self._matching_passages(relevant, scenario["safeguards"])
        input_ids = [item["id"] for item in relevant[:8]]
        if stage and not stage.get("included", True):
            return (
                "low",
                f"The triggering stage '{stage['name']}' is outside the confirmed scope; run only to document that stop.",
                input_ids,
            )
        if not relevant:
            return (
                "high",
                "No relevant artifact was submitted, so the task is routed as a missing-context probe.",
                [],
            )
        if not safeguards:
            return (
                "high",
                f"{len(relevant)} relevant passage(s) were found, but no explicit response cue matched this scenario.",
                input_ids,
            )
        return (
            "medium",
            f"{len(safeguards)} possible safeguard passage(s) were found and require responsibility-aware review.",
            input_ids,
        )

    def _relationship_route_reason(self, session: Dict[str, Any]) -> str:
        blob = " ".join(
            [session.get("project", {}).get("context", ""), session.get("project", {}).get("target_people", "")]
            + list(session.get("artifacts", {}).values())
        ).lower()
        terms = ["family", "caregiver", "helper", "community", "partner", "gatekeeper", "service"]
        found = [term for term in terms if term in blob]
        if found:
            return f"Relationship cues ({', '.join(found[:4])}) require a dedicated power and responsibility check."
        return "Relationship roles are missing from the submitted context, so the task checks this absence explicitly."

    def _plan_task(self, session: Dict[str, Any], kind: str) -> Optional[Dict[str, Any]]:
        return next((item for item in session.get("audit_plan", []) if item.get("kind") == kind), None)

    def _start_task(self, task: Dict[str, Any]) -> None:
        task["status"] = "running"
        task["attempts"] = int(task.get("attempts", 0)) + 1
        task["last_started_at"] = utc_now()
        task["result_summary"] = ""

    def _finish_task(
        self,
        task: Dict[str, Any],
        status: str,
        output_ids: List[str],
        summary: str,
    ) -> None:
        task["status"] = status
        task["last_completed_at"] = utc_now()
        task["output_ids"] = output_ids
        task["result_summary"] = summary

    def _issues_for_task(
        self,
        session: Dict[str, Any],
        task: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        if task["kind"] == "scenario":
            trace_id = f"trace_{task['scenario_id']}"
            return [item for item in session.get("issues", []) if item.get("trigger_trace_id") == trace_id]
        if task["kind"] == "relationship":
            return [
                item
                for item in session.get("issues", [])
                if item.get("agent") == "Relationship and Power Agent"
            ]
        if task["kind"] == "llm_critic":
            return [
                item for item in session.get("issues", []) if item.get("agent") == "Bounded LLM Critic"
            ]
        return []

    def _invalidate_audit_results(self, session: Dict[str, Any]) -> None:
        """Clear stale specialist outputs when an undecided plan is rescoped."""
        session["traces"] = []
        session["issues"] = []
        session["handoffs"] = []
        session["agent_activity"] = [
            item
            for item in session.get("agent_activity", [])
            if item.get("agent") == "Encounter Orchestrator"
        ]
        session["status"] = "mapped"

    def _extract_passages(
        self,
        artifacts: Dict[str, str],
        project: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        passages: List[Dict[str, str]] = []
        for artifact_type, text in artifacts.items():
            if not text:
                continue
            chunks = [chunk.strip(" -\t") for chunk in re.split(r"\r?\n+", text) if chunk.strip(" -\t")]
            if len(chunks) == 1 and len(chunks[0]) > 260:
                chunks = [
                    chunk.strip()
                    for chunk in re.split(r"(?<=[.!?])\s+", chunks[0])
                    if chunk.strip()
                ]
            prefix = artifact_type[:3].upper()
            for index, chunk in enumerate(chunks, start=1):
                passages.append(
                    {
                        "id": f"{prefix}-{index:03d}",
                        "artifact_type": artifact_type,
                        "artifact_label": ARTIFACT_LABELS[artifact_type],
                        "text": chunk,
                    }
                )
        project_sources = [
            ("review_context", "REV", "Research area and review context"),
            ("context", "CTX", "Project plan"),
            ("target_people", "PEO", "People and relationships"),
        ]
        for field, prefix, label in project_sources:
            text = str((project or {}).get(field, "") or "").strip()
            if not text:
                continue
            chunks = [
                chunk.strip(" -\t")
                for chunk in re.split(r"\r?\n+", text)
                if chunk.strip(" -\t")
            ]
            if len(chunks) == 1 and len(chunks[0]) > 260:
                chunks = [
                    chunk.strip()
                    for chunk in re.split(r"(?<=[.!?])\s+", chunks[0])
                    if chunk.strip()
                ]
            artifact_type = "review_context" if field == "review_context" else (
                "project_context" if field == "context" else "target_people"
            )
            for index, chunk in enumerate(chunks, start=1):
                passages.append(
                    {
                        "id": f"{prefix}-{index:03d}",
                        "artifact_type": artifact_type,
                        "artifact_label": label,
                        "text": chunk,
                    }
                )
        return passages

    def _build_encounter_map(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        stages = []
        for definition in STAGE_DEFINITIONS:
            artifact_passages = self._passages(session, definition["artifacts"])
            keyword_passages = self._matching_passages(artifact_passages, definition["keywords"])
            if keyword_passages:
                coverage = "covered"
            elif artifact_passages:
                coverage = "partial"
            else:
                coverage = "missing"
            stages.append(
                {
                    "id": definition["id"],
                    "name": definition["name"],
                    "included": True,
                    "coverage": coverage,
                    "source_passage_ids": [item["id"] for item in (keyword_passages or artifact_passages)[:3]],
                    "responsible_actor": "Research team" if coverage != "missing" else "Unspecified",
                    "notes": "",
                }
            )
        return stages

    def _trace_scenario(self, session: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
        relevant = self._passages(session, scenario["artifacts"])
        safeguards = self._matching_passages(relevant, scenario["safeguards"])
        trigger_source = (relevant or session["passages"][:1])[:3]
        stage = next(
            (item for item in session["encounter_map"] if item["id"] == scenario["trigger_stage"]),
            None,
        )
        included = bool(stage and stage.get("included", True))
        if not included:
            status = "not_run"
            gap = "The relevant encounter stage is excluded from the current audit scope."
        elif not relevant:
            status = "missing"
            gap = "No submitted material defines a response for this part of the encounter."
        elif safeguards:
            status = "covered"
            gap = "No missing transition was detected by the bounded keyword check; human review is still required."
        else:
            status = "gap"
            gap = "The submitted materials describe the encounter but do not specify a response to this event."

        steps = [
            {
                "order": 1,
                "label": "Trigger",
                "text": scenario["trigger"],
                "source_passage_ids": [item["id"] for item in trigger_source],
                "state": "observed",
            },
            {
                "order": 2,
                "label": "Protocol response",
                "text": (
                    "Relevant safeguard language was located."
                    if safeguards
                    else "No explicit response path was located in the submitted materials."
                ),
                "source_passage_ids": [item["id"] for item in safeguards[:3]],
                "state": "supported" if safeguards else "unsupported",
            },
            {
                "order": 3,
                "label": "Responsibility and next step",
                "text": (
                    "A researcher must inspect whether the located language assigns a workable action and owner."
                    if safeguards
                    else f"Clarify the procedure and verify it with a {scenario['handoff_owner']}."
                ),
                "source_passage_ids": [],
                "state": "review" if safeguards else "handoff",
            },
        ]
        return {
            "id": f"trace_{scenario['id']}",
            "scenario_id": scenario["id"],
            "category": scenario["category"],
            "title": scenario["title"],
            "trigger_stage": scenario["trigger_stage"],
            "status": status,
            "steps": steps,
            "first_gap": gap,
            "uncertainty": scenario["boundary_explanation"],
        }

    def _issue_from_trace(
        self,
        session: Dict[str, Any],
        scenario: Dict[str, Any],
        trace: Dict[str, Any],
    ) -> Dict[str, Any]:
        source_ids = []
        for step in trace["steps"]:
            source_ids.extend(step.get("source_passage_ids", []))
        return {
            "id": f"issue_{scenario['id']}",
            "title": scenario["title"],
            "category": scenario["category"],
            "severity": scenario["severity"],
            "agent": "Breakdown Scenario Agent",
            "source_passage_ids": list(dict.fromkeys(source_ids))[:4],
            "trigger_trace_id": trace["id"],
            "observation": trace["first_gap"],
            "evidence_type": "protocol coverage check",
            "suggestion": scenario["suggestion"],
            "uncertainty": trace["uncertainty"],
            "requires_handoff": True,
            "handoff_owner": scenario["handoff_owner"],
            "decision": "pending",
            "decision_rationale": "",
            "revised_text": "",
            "decided_at": "",
        }

    def _relationship_issues(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        blob = " ".join(
            [session["project"].get("context", ""), session["project"].get("target_people", "")]
            + list(session["artifacts"].values())
        ).lower()
        relationship_terms = ["family", "caregiver", "helper", "community", "partner", "gatekeeper"]
        responsibility_terms = ["facilitator", "researcher", "team member", "responsible", "contact"]
        issues = []
        if not any(term in blob for term in relationship_terms):
            source = self._passages(session, ["recruitment", "consent"])[:2]
            issues.append(
                {
                    "id": "issue_relationship_map",
                    "title": "Support, pressure, and gatekeeping relationships are not mapped",
                    "category": "power_relationships",
                    "severity": "medium",
                    "agent": "Relationship and Power Agent",
                    "source_passage_ids": [item["id"] for item in source],
                    "trigger_trace_id": "",
                    "observation": "The submitted materials name participants but do not identify who may enable access, influence consent, support participation, or receive disclosures.",
                    "evidence_type": "missing relationship role",
                    "suggestion": "Add a relationship map and state which roles may be present at recruitment, consent, participation, and follow-up.",
                    "uncertainty": "Only a real partner can confirm which relationships matter locally.",
                    "requires_handoff": True,
                    "handoff_owner": "community partner or participant advisory group",
                    "decision": "pending",
                    "decision_rationale": "",
                    "revised_text": "",
                    "decided_at": "",
                }
            )
        safety_text = session["artifacts"].get("safety", "").lower()
        if safety_text and not any(term in safety_text for term in responsibility_terms):
            safety_sources = self._passages(session, ["safety"])[:3]
            issues.append(
                {
                    "id": "issue_responsibility",
                    "title": "Safety actions do not have a named decision owner",
                    "category": "responsibility",
                    "severity": "high",
                    "agent": "Relationship and Power Agent",
                    "source_passage_ids": [item["id"] for item in safety_sources],
                    "trigger_trace_id": "",
                    "observation": "The safety procedure describes possible action without assigning who notices, decides, documents, or follows up.",
                    "evidence_type": "responsibility check",
                    "suggestion": "Assign an owner and escalation route for each pause, support, referral, or follow-up action.",
                    "uncertainty": "Role assignments must be checked against the real team's training and authority.",
                    "requires_handoff": True,
                    "handoff_owner": "project lead or safeguarding advisor",
                    "decision": "pending",
                    "decision_rationale": "",
                    "revised_text": "",
                    "decided_at": "",
                }
            )
        return issues

    def _boundary_check(self, session: Dict[str, Any], issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid_ids = {item["id"] for item in session["passages"]}
        for issue in issues:
            issue["source_passage_ids"] = [
                item for item in issue.get("source_passage_ids", []) if item in valid_ids
            ]
            issue["boundary_status"] = "planning_hypothesis"
            issue["boundary_note"] = "This issue concerns the submitted protocol and must not be treated as evidence about a real community."
            issue["agent_positions"] = [
                {
                    "agent": issue.get("agent", "Specialist agent"),
                    "position": issue.get("suggestion", "Revise or clarify the cited protocol passage."),
                },
                {
                    "agent": "Boundary and Handoff Agent",
                    "position": issue.get("uncertainty", "Defer the situated judgment to an appropriate real person."),
                },
            ]
            issue["contestation_status"] = (
                "human_resolution_required" if issue.get("requires_handoff") else "review_required"
            )
            issue["resolution_rule"] = "No agent vote or synthetic consensus: the researcher must accept, edit, reject, or defer."
        return issues

    def _llm_issues(self, session: Dict[str, Any]) -> tuple[List[Dict[str, Any]], str]:
        passage_lines = [
            f"{item['id']} | {item['artifact_label']} | {item['text']}"
            for item in session["passages"][:40]
        ]
        messages = [
            {
                "role": "system",
                "content": _LLM_CRITIC_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    _LLM_CRITIC_USER_INSTRUCTION
                    + "\n\n"
                    + "\n".join(passage_lines)
                ),
            },
        ]
        started_at = utc_now()
        started = time.perf_counter()
        result = self.llm_client.chat_with_provider_detailed(
            self.llm_client.active_provider_id,
            messages,
            temperature=STUDY_LLM_TEMPERATURE,
            timeout=STUDY_LLM_TIMEOUT_SECONDS,
        )
        completed_at = utc_now()
        latency_ms = round((time.perf_counter() - started) * 1000, 3)
        self._record_study_llm_call(
            session,
            call_type="safebars_critic",
            result=result,
            started_at=started_at,
            completed_at=completed_at,
            latency_ms=latency_ms,
            input_chars=sum(len(item.get("content", "")) for item in messages),
        )
        if not result.get("ok"):
            return [], f"LLM unavailable; deterministic trace remained active. {result.get('error', '')[:180]}"
        try:
            raw = result.get("text", "")
            match = re.search(r"\[.*\]", raw, flags=re.DOTALL)
            parsed = json.loads(match.group(0) if match else raw)
        except (ValueError, TypeError, AttributeError):
            return [], "LLM response was not valid structured JSON; deterministic trace remained active."

        valid_ids = {item["id"] for item in session["passages"]}
        issues = []
        for index, item in enumerate(parsed[:2]):
            source_ids = [source for source in item.get("source_passage_ids", []) if source in valid_ids]
            if not source_ids:
                continue
            observation = str(item.get("observation", "")).strip()
            if not observation:
                continue
            title = str(item.get("title", "Additional passage-grounded gap"))[:120]
            category = str(item.get("category", "additional_gap"))[:60]
            handoff_owner = str(item.get("handoff_owner", "relevant real stakeholder"))[:120]
            issues.append(
                {
                    "id": f"issue_llm_{index + 1}_{uuid.uuid4().hex[:5]}",
                    "title": title,
                    "category": category,
                    "severity": item.get("severity") if item.get("severity") in {"high", "medium", "low"} else "medium",
                    "agent": "Bounded LLM Critic",
                    "source_passage_ids": source_ids[:4],
                    "trigger_trace_id": "",
                    "observation": observation[:700],
                    "evidence_type": "LLM inference grounded to submitted passages",
                    "suggestion": str(item.get("suggestion", "Review and clarify the cited passages."))[:700],
                    "uncertainty": self._llm_boundary_explanation(title, category, handoff_owner),
                    "requires_handoff": True,
                    "handoff_owner": handoff_owner,
                    "decision": "pending",
                    "decision_rationale": "",
                    "revised_text": "",
                    "decided_at": "",
                    "boundary_status": "planning_hypothesis",
                    "boundary_note": "This issue concerns the submitted protocol and must not be treated as evidence about a real community.",
                }
            )
        return issues, f"Added {len(issues)} passage-grounded LLM issue(s) after boundary checks."

    def _llm_boundary_explanation(self, title: str, category: str, owner: str) -> str:
        topic = f"{title} {category}".lower()
        if any(term in topic for term in ["psycholog", "mental", "distress", "emotional"]):
            return (
                "This review can check whether the cited materials define a response when distress or "
                f"psychological support needs arise. It cannot determine what support is appropriate or "
                f"available in this setting; confirm that with {owner}."
            )
        if any(term in topic for term in ["data", "privacy", "security", "confidential", "record"]):
            return (
                "This review can check whether the cited materials specify access, storage, retention, and "
                f"deletion. It cannot determine whether those measures satisfy institutional or legal "
                f"requirements; confirm that with {owner}."
            )
        if any(term in topic for term in ["consent", "autonomy", "withdraw"]):
            return (
                "This review can check whether consent and withdrawal choices are written into the cited "
                f"materials. It cannot determine how those choices should work in the local relationship or "
                f"institutional context; confirm that with {owner}."
            )
        return (
            f"This review can flag that '{title}' is not clearly addressed in the cited materials. "
            f"It cannot determine the appropriate response in this study context; confirm that with {owner}."
        )

    def _deduplicate_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        result = []
        for issue in issues:
            key = (issue.get("category"), tuple(issue.get("source_passage_ids", [])))
            if key in seen:
                continue
            seen.add(key)
            result.append(issue)
        return result

    def _initial_handoffs(
        self,
        issues: List[Dict[str, Any]],
        existing: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        existing_by_id = {item.get("id"): item for item in (existing or [])}
        handoffs = []
        for issue in issues:
            if not issue.get("requires_handoff"):
                continue
            generated = self._handoff_from_issue(issue)
            prior = existing_by_id.get(generated["id"])
            if prior:
                for key in (
                    "owner", "recommended_role", "recommended_role_label", "recommended_role_scope",
                    "priority", "status", "reviewer_role", "reviewer_name", "expert_advice",
                    "expert_rationale", "reviewed_at", "resolved_at", "review_history",
                    "advice_type", "advice_type_label", "responsible_actor", "closure_evidence",
                    "reviewed_passage_ids", "evidence_gap_acknowledged", "evidence_reviewed",
                    "evidence_reviewed_at",
                    "assigned_role", "assigned_role_label", "assigned_reviewer_name", "assigned_at",
                    "researcher_response", "researcher_revised_text", "researcher_responded_at",
                    "researcher_revision_history",
                ):
                    if key in prior:
                        generated[key] = prior[key]
            handoffs.append(generated)
        return handoffs

    def _handoff_from_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        role = recommend_expert_role(issue)
        severity = issue.get("severity", "medium")
        priority = "high" if severity == "high" else ("medium" if severity == "medium" else "standard")
        triage_factors = [f"{severity} issue severity", "situated judgment required"]
        if issue.get("decision") == "defer":
            triage_factors.append("researcher explicitly deferred the issue")
        if issue.get("category") in {"consent_autonomy", "withdrawal_data", "privacy_disclosure", "distress_support"}:
            triage_factors.append("participant rights, safety, or data control may change")
        return {
            "id": f"handoff_{issue['id']}",
            "issue_id": issue["id"],
            "question": f"How should the project address: {issue['title']}?",
            "why_ai_cannot_resolve": issue.get("uncertainty") or "The answer depends on situated human judgment.",
            "owner": role["label"],
            "recommended_role": role["id"],
            "recommended_role_label": role["label"],
            "recommended_role_scope": role["scope"],
            "original_owner_suggestion": issue.get("handoff_owner", "relevant real stakeholder"),
            "priority": priority,
            "triage_factors": triage_factors,
            "suggested_method": "Review the cited passage and scenario in a short consultation before recruitment.",
            "deadline_stage": "Before recruitment or fieldwork",
            "created_at": utc_now(),
            "status": "open",
            "assigned_role": "",
            "assigned_role_label": "",
            "assigned_reviewer_name": "",
            "assigned_at": "",
            "reviewer_role": "",
            "reviewer_name": "",
            "expert_advice": "",
            "expert_rationale": "",
            "advice_type": "",
            "advice_type_label": "",
            "responsible_actor": "",
            "closure_evidence": "",
            "reviewed_passage_ids": [],
            "evidence_gap_acknowledged": False,
            "evidence_reviewed": False,
            "evidence_reviewed_at": "",
            "reviewed_at": "",
            "resolved_at": "",
            "review_history": [],
            "researcher_revision_history": [],
        }

    def _ensure_handoff(self, session: Dict[str, Any], issue: Dict[str, Any]) -> None:
        handoff_id = f"handoff_{issue['id']}"
        if not any(item["id"] == handoff_id for item in session.get("handoffs", [])):
            session.setdefault("handoffs", []).append(self._handoff_from_issue(issue))

    def _passages(self, session: Dict[str, Any], artifact_types: Iterable[str]) -> List[Dict[str, str]]:
        ordered_types = list(dict.fromkeys(artifact_types))
        passages = session.get("passages", [])
        return [
            item
            for artifact_type in ordered_types
            for item in passages
            if item["artifact_type"] == artifact_type
        ]

    def _matching_passages(
        self, passages: List[Dict[str, str]], keywords: Iterable[str]
    ) -> List[Dict[str, str]]:
        terms = [term.lower() for term in keywords]
        return [item for item in passages if any(term in item["text"].lower() for term in terms)]

    def _activity(
        self,
        session: Dict[str, Any],
        agent: str,
        status: str,
        detail: str,
    ) -> None:
        session.setdefault("agent_activity", []).append(
            {
                "agent": agent,
                "status": status,
                "detail": detail,
                "timestamp": utc_now(),
            }
        )

    def _save(self, session: Dict[str, Any], event_type: str, payload: Dict[str, Any]) -> None:
        session["application_readiness"] = build_application_readiness(session)
        self.store.save(session)
        self.store.log(session["id"], event_type, payload)
        session["event_log"] = self.store.list_events(session["id"])

    def _active_provider_summary(self) -> Optional[Dict[str, Any]]:
        provider_id = self.llm_client.active_provider_id
        if not provider_id:
            return None
        provider = self.llm_client.providers.get(provider_id)
        return provider.public_dict() if provider else None
