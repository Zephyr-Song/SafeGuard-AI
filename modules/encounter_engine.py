"""Artifact-centered encounter stress testing for SafeBARS v2."""

from __future__ import annotations

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
from typing import Any, Dict, Iterable, List, Optional
import uuid

from .llm_client import LLMClient
from .ethics_framework import (
    EXPERT_ROLES,
    FRAMEWORKS,
    build_framework_assessment,
    recommend_expert_role,
)
from .ethics_application import APPLICATION_PROFILES, build_application_readiness


ARTIFACT_LABELS = {
    "recruitment": "Recruitment message",
    "consent": "Consent language",
    "interview": "Interview questions",
    "activity": "Workshop or activity plan",
    "safety": "Safety and escalation procedure",
    "follow_up": "Debrief, follow-up, and data use",
}


STAGE_DEFINITIONS = [
    {
        "id": "outreach",
        "name": "Outreach and recruitment",
        "artifacts": ["recruitment"],
        "keywords": ["invite", "recruit", "contact", "voluntary"],
    },
    {
        "id": "gatekeeping",
        "name": "Eligibility and gatekeeping",
        "artifacts": ["recruitment"],
        "keywords": ["eligible", "eligibility", "screen", "gatekeeper", "partner"],
    },
    {
        "id": "consent",
        "name": "Information and consent",
        "artifacts": ["consent"],
        "keywords": ["consent", "voluntary", "decline", "questions"],
    },
    {
        "id": "activity",
        "name": "Interview, workshop, or activity",
        "artifacts": ["interview", "activity"],
        "keywords": ["question", "interview", "workshop", "activity"],
    },
    {
        "id": "disclosure",
        "name": "Sensitive disclosure",
        "artifacts": ["interview", "safety"],
        "keywords": ["sensitive", "disclosure", "loss", "personal", "private"],
    },
    {
        "id": "pause_withdrawal",
        "name": "Pause, skip, or withdrawal",
        "artifacts": ["consent", "safety"],
        "keywords": ["pause", "skip", "withdraw", "stop", "not answer"],
    },
    {
        "id": "escalation",
        "name": "Safeguarding and escalation",
        "artifacts": ["safety"],
        "keywords": ["distress", "support", "referral", "escalat", "responsible"],
    },
    {
        "id": "debrief",
        "name": "Debrief and immediate support",
        "artifacts": ["safety", "follow_up"],
        "keywords": ["debrief", "support", "resource", "check-in", "after"],
    },
    {
        "id": "follow_up",
        "name": "Follow-up, data use, and reporting",
        "artifacts": ["follow_up", "consent"],
        "keywords": ["follow-up", "follow up", "data", "record", "report", "delete"],
    },
]


SCENARIO_LIBRARY = [
    {
        "id": "family_pressure",
        "category": "consent_autonomy",
        "title": "Consent under helper or gatekeeper pressure",
        "trigger_stage": "consent",
        "trigger": "A helper or gatekeeper is present and influences whether the person agrees.",
        "artifacts": ["recruitment", "consent", "safety"],
        "safeguards": ["private", "alone", "voluntary", "decline", "no effect", "without"],
        "severity": "high",
        "suggestion": "Add a private consent check and state that declining will not affect services, relationships, or compensation.",
        "handoff_owner": "community partner or participant advisory group",
        "boundary_explanation": "This trace can check whether private, voluntary consent is written into the protocol. It cannot tell how a particular helper relationship affects someone's choice; review that question with a community partner or participant advisor.",
    },
    {
        "id": "unexpected_disclosure",
        "category": "privacy_disclosure",
        "title": "Unexpected identifying or sensitive disclosure",
        "trigger_stage": "disclosure",
        "trigger": "The session surfaces identifying financial, health, safety, or family information that the protocol did not request.",
        "artifacts": ["interview", "consent", "safety", "follow_up"],
        "safeguards": ["confidential", "privacy", "access", "redact", "recording", "delete", "data"],
        "severity": "high",
        "suggestion": "Specify how unrequested sensitive information will be handled, who can access it, and whether it can be redacted or deleted.",
        "handoff_owner": "data protection or ethics reviewer",
        "boundary_explanation": "This trace can check the protocol's rules for unexpected disclosures. It cannot anticipate what people may disclose or decide which handling is acceptable in context; confirm that with a data protection or ethics reviewer.",
    },
    {
        "id": "participant_distress",
        "category": "distress_support",
        "title": "Distress during a sensitive question or activity",
        "trigger_stage": "activity",
        "trigger": "A question or activity produces visible discomfort, shame, or distress.",
        "artifacts": ["interview", "activity", "safety", "follow_up"],
        "safeguards": ["pause", "stop", "break", "support", "referral", "distress", "check-in"],
        "severity": "high",
        "suggestion": "Add an observable pause rule, a neutral check-in script, and a named support or referral action with a responsible team member.",
        "handoff_owner": "safeguarding or domain advisor",
        "boundary_explanation": "This trace can check whether pause and support actions are defined. It cannot identify how a particular person will show distress or what support will be appropriate; confirm that with a safeguarding or domain advisor.",
    },
    {
        "id": "partial_withdrawal",
        "category": "withdrawal_data",
        "title": "Partial withdrawal after data collection begins",
        "trigger_stage": "pause_withdrawal",
        "trigger": "A person wants to skip one part or withdraw after some notes or recordings already exist.",
        "artifacts": ["consent", "safety", "follow_up"],
        "safeguards": ["withdraw", "skip", "not answer", "delete", "retain", "already collected"],
        "severity": "high",
        "suggestion": "Explain partial participation and what happens to notes, recordings, and quotations after withdrawal at different stages.",
        "handoff_owner": "ethics reviewer or data governance lead",
        "boundary_explanation": "This trace can check whether withdrawal and data handling are specified. It cannot decide what participants will expect or what retention rules permit; confirm that with an ethics reviewer or data governance lead.",
    },
    {
        "id": "institutional_distrust",
        "category": "trust_pathways",
        "title": "The named reporting or support pathway is not trusted",
        "trigger_stage": "escalation",
        "trigger": "The protocol directs a person to an authority, platform, bank, clinic, or service they may not trust.",
        "artifacts": ["safety", "follow_up", "consent"],
        "safeguards": ["alternative", "choice", "community", "trusted", "different service", "option"],
        "severity": "medium",
        "suggestion": "Offer more than one support pathway and ask a real partner which options are locally credible and accessible.",
        "handoff_owner": "local service partner or community organization",
        "boundary_explanation": "This trace can check whether the protocol offers alternative support pathways. It cannot know which services are trusted or accessible locally; ask a local service partner or community organization.",
    },
    {
        "id": "access_burden",
        "category": "burden_access",
        "title": "Session burden or access assumptions fail",
        "trigger_stage": "activity",
        "trigger": "The planned duration, digital task, language, travel, or format becomes difficult to complete.",
        "artifacts": ["recruitment", "activity", "safety", "follow_up"],
        "safeguards": ["break", "shorter", "accessible", "language", "support", "alternative format", "remote"],
        "severity": "medium",
        "suggestion": "Add lower-burden alternatives, breaks, accessible formats, and a way to continue without completing every activity.",
        "handoff_owner": "accessibility advisor or target-user representative",
        "boundary_explanation": "This trace can check whether breaks and accessible alternatives are written into the plan. It cannot know which burdens people will actually face; review the plan with an accessibility advisor or target-user representative.",
    },
]


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


SAMPLE_PROJECT = {
    "project": {
        "title": "Community workshop on online fraud prevention",
        "context": "A research team plans interviews and a workshop with older adults who have encountered suspicious online messages.",
        "target_people": "Older adults, family helpers, and a community facilitator",
    },
    "artifacts": {
        "recruitment": "We invite adults aged 60+ who have received suspicious online messages to join a 75-minute workshop.",
        "consent": "Participation is voluntary. You may stop the session at any time. We will audio-record the interview with your permission.",
        "interview": "1. How much money did you lose?\n2. Why did you believe the message?\n3. Did your family help you report it?",
        "activity": "Participants review three scam messages, explain their decisions, and develop advice for other older adults.",
        "safety": "The facilitator may offer a short break if a participant becomes uncomfortable.",
        "follow_up": "The team will summarize workshop findings in a research paper.",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class EncounterStore:
    """Small SQLite JSON store for restart-safe study sessions and event logs."""

    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=20)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS encounter_sessions (
                        id TEXT PRIMARY KEY,
                        payload TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS encounter_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS encounter_access (
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        token_hash TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        PRIMARY KEY (session_id, role)
                    )
                    """
                )

    def save(self, session: Dict[str, Any]) -> None:
        serialized = json.dumps(session, ensure_ascii=True)
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO encounter_sessions (id, payload, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at
                    """,
                    (session["id"], serialized, session["created_at"], session["updated_at"]),
                )

    def load(self, session_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT payload FROM encounter_sessions WHERE id = ?", (session_id,)
            ).fetchone()
        return json.loads(row["payload"]) if row else None

    def log(self, session_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO encounter_events (session_id, event_type, payload, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (session_id, event_type, json.dumps(payload, ensure_ascii=True), utc_now()),
                )

    def list_events(self, session_id: str) -> List[Dict[str, Any]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT id, event_type, payload, created_at
                FROM encounter_events
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "event_type": row["event_type"],
                "payload": json.loads(row["payload"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    @staticmethod
    def _token_hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def rotate_access(self, session_id: str, role: str) -> str:
        if role not in {"researcher", "expert"}:
            raise ValueError("Access role must be researcher or expert.")
        token = secrets.token_urlsafe(32)
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO encounter_access (session_id, role, token_hash, created_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(session_id, role)
                    DO UPDATE SET token_hash=excluded.token_hash, created_at=excluded.created_at
                    """,
                    (session_id, role, self._token_hash(token), utc_now()),
                )
        return token

    def access_role(self, session_id: str, token: str) -> Optional[str]:
        if not token:
            return None
        candidate = self._token_hash(token)
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT role, token_hash FROM encounter_access WHERE session_id = ?",
                (session_id,),
            ).fetchall()
        for row in rows:
            if hmac.compare_digest(candidate, row["token_hash"]):
                return row["role"]
        return None


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
                }
                for item in SCENARIO_LIBRARY
            ],
            "llm_configured": self.llm_client.is_configured(),
            "active_provider": self._active_provider_summary(),
            "sample_project": SAMPLE_PROJECT,
            "ethics_frameworks": [FRAMEWORKS[key] | {"id": key} for key in FRAMEWORKS],
            "expert_roles": [EXPERT_ROLES[key] | {"id": key} for key in EXPERT_ROLES],
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

    def create_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        project = payload.get("project", {})
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
            "version": "2.1",
            "status": "mapped",
            "project": {
                "title": str(project.get("title", "Untitled fieldwork plan")).strip(),
                "context": str(project.get("context", "")).strip(),
                "target_people": str(project.get("target_people", "")).strip(),
                "uses_ai": bool(project.get("uses_ai", False)),
            },
            "artifacts": artifacts,
            "intake_transcript": payload.get("intake_transcript", []),
            "passages": self._extract_passages(artifacts),
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
            "use_llm": bool(payload.get("use_llm", False)),
            "created_at": created_at,
            "updated_at": created_at,
        }
        session["encounter_map"] = self._build_encounter_map(session)
        session["framework_assessment"] = build_framework_assessment(session)
        session["application_readiness"] = build_application_readiness(session)
        session["audit_plan"] = self._build_audit_plan(
            session, session.get("selected_scenarios") or None
        )
        self._activity(session, "Encounter Orchestrator", "completed", "Built an editable encounter map from submitted artifacts.")
        self._save(
            session,
            "session_created",
            {
                "passage_count": len(session["passages"]),
                "planned_task_count": len(session["audit_plan"]),
            },
        )
        return session

    def create_protocol_version(self, session_id: str) -> Optional[Dict[str, Any]]:
        source = self.get_session(session_id)
        if not source:
            return None
        current_version = int(source.get("lineage", {}).get("version_number", 1) or 1)
        payload = {
            "project": source.get("project", {}),
            "artifacts": source.get("artifacts", {}),
            "intake_transcript": source.get("intake_transcript", []),
            "selected_scenarios": source.get("selected_scenarios", []),
            "use_llm": source.get("use_llm", False),
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
        handoff = next(
            (item for item in session.get("handoffs", []) if item.get("id") == handoff_id),
            None,
        )
        if not handoff:
            raise KeyError("Handoff not found.")
        response = response.strip()
        revised_text = revised_text.strip()
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
        if action in {"advise", "request_clarification"} and not advice.strip():
            raise ValueError("Add advice or a clarification request before saving this action.")
        if action == "redirect" and redirect_role not in EXPERT_ROLES:
            raise ValueError("Select a recognized role to receive the redirected handoff.")

        now = utc_now()
        event = {
            "action": action,
            "reviewer_role": reviewer_role,
            "reviewer_role_label": EXPERT_ROLES[reviewer_role]["label"],
            "reviewer_name": reviewer_name.strip(),
            "advice": advice.strip(),
            "rationale": rationale.strip(),
            "timestamp": now,
        }
        handoff.setdefault("review_history", []).append(event)
        handoff["reviewer_role"] = reviewer_role
        handoff["reviewer_name"] = reviewer_name.strip()
        handoff["expert_advice"] = advice.strip() or handoff.get("expert_advice", "")
        handoff["expert_rationale"] = rationale.strip() or handoff.get("expert_rationale", "")
        handoff["reviewed_at"] = now
        if action == "assign":
            handoff["status"] = "assigned"
        elif action == "advise":
            handoff["status"] = "advised"
        elif action == "request_clarification":
            handoff["status"] = "needs_clarification"
        elif action == "redirect":
            role = EXPERT_ROLES[redirect_role]
            handoff["recommended_role"] = redirect_role
            handoff["recommended_role_label"] = role["label"]
            handoff["owner"] = role["label"]
            handoff["status"] = "redirected"
            event["redirect_role"] = redirect_role
            event["redirect_role_label"] = role["label"]
        elif action == "resolve":
            handoff["status"] = "resolved"
            handoff["resolved_at"] = now
        elif action == "reopen":
            handoff["status"] = "open"
            handoff["resolved_at"] = ""

        session["updated_at"] = now
        self._save(
            session,
            "expert_handoff_review",
            {"handoff_id": handoff_id, "action": action, "reviewer_role": reviewer_role},
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
            queue.append(
                {
                    **handoff,
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
            },
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
                    "A provider is configured and the researcher enabled this optional probe."
                    if llm_enabled
                    else "Skipped because no configured provider was enabled; deterministic tracing remains active."
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

    def _extract_passages(self, artifacts: Dict[str, str]) -> List[Dict[str, str]]:
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
                "content": (
                    "You are a bounded SafeBARS protocol critic. Inspect only the submitted passages. "
                    "Do not speak as a participant and do not claim what any population thinks, feels, or will do. "
                    "Do not provide ethics approval or compliance verdicts. Return valid JSON only."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Find at most two concrete relational or procedural gaps not already obvious from a generic checklist. "
                    "Each gap must cite existing passage IDs. Return a JSON array with keys: title, category, severity "
                    "(high/medium/low), source_passage_ids, observation, suggestion, handoff_owner. "
                    "If no passage-grounded gap is justified, return [].\n\n"
                    + "\n".join(passage_lines)
                ),
            },
        ]
        result = self.llm_client.chat_with_provider_detailed(
            self.llm_client.active_provider_id,
            messages,
            temperature=0.15,
            timeout=25,
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
            "status": "open",
            "reviewer_role": "",
            "reviewer_name": "",
            "expert_advice": "",
            "expert_rationale": "",
            "reviewed_at": "",
            "resolved_at": "",
            "review_history": [],
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
