"""Artifact-centered encounter stress testing for SafeBARS v2."""

from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import json
import os
import re
import sqlite3
import threading
from typing import Any, Dict, Iterable, List, Optional
import uuid

from .llm_client import LLMClient


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
    },
]


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
        }

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
            "version": "2.0",
            "status": "mapped",
            "project": {
                "title": str(project.get("title", "Untitled fieldwork plan")).strip(),
                "context": str(project.get("context", "")).strip(),
                "target_people": str(project.get("target_people", "")).strip(),
            },
            "artifacts": artifacts,
            "passages": self._extract_passages(artifacts),
            "encounter_map": [],
            "selected_scenarios": payload.get("selected_scenarios", []),
            "traces": [],
            "issues": [],
            "handoffs": [],
            "agent_activity": [],
            "use_llm": bool(payload.get("use_llm", False)),
            "created_at": created_at,
            "updated_at": created_at,
        }
        session["encounter_map"] = self._build_encounter_map(session)
        self._activity(session, "Encounter Orchestrator", "completed", "Built an editable encounter map from submitted artifacts.")
        self._save(session, "session_created", {"passage_count": len(session["passages"])})
        return session

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.store.load(session_id)
        if session:
            session["event_log"] = self.store.list_events(session_id)
        return session

    def update_map(self, session_id: str, stages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None
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
            session["encounter_map"] = cleaned
            session["updated_at"] = utc_now()
            self._save(session, "map_updated", {"stage_count": len(cleaned)})
        return session

    def run_audit(self, session_id: str, scenario_ids: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None

        selected = set(scenario_ids or session.get("selected_scenarios") or [])
        scenarios = [item for item in SCENARIO_LIBRARY if not selected or item["id"] in selected]
        session["selected_scenarios"] = [item["id"] for item in scenarios]
        session["traces"] = []
        session["issues"] = []
        session["handoffs"] = []
        session["agent_activity"] = [
            item for item in session.get("agent_activity", []) if item.get("agent") == "Encounter Orchestrator"
        ]

        self._activity(session, "Breakdown Scenario Agent", "running", f"Tracing {len(scenarios)} bounded scenarios.")
        for scenario in scenarios:
            trace = self._trace_scenario(session, scenario)
            session["traces"].append(trace)
            if trace["status"] != "covered":
                session["issues"].append(self._issue_from_trace(session, scenario, trace))
        self._activity(session, "Breakdown Scenario Agent", "completed", f"Produced {len(session['traces'])} inspectable traces.")

        self._activity(session, "Relationship and Power Agent", "running", "Checking support, pressure, gatekeeping, and responsibility roles.")
        session["issues"].extend(self._relationship_issues(session))
        self._activity(session, "Relationship and Power Agent", "completed", "Added relationship-specific planning questions where needed.")

        self._activity(session, "Boundary and Handoff Agent", "running", "Checking provenance and removing participant-proxy claims.")
        session["issues"] = self._boundary_check(session, session["issues"])

        if session.get("use_llm") and self.llm_client.is_configured():
            self._activity(session, "Bounded LLM Critic", "running", "Looking for up to two passage-grounded gaps beyond the scenario library.")
            llm_issues, detail = self._llm_issues(session)
            session["issues"].extend(llm_issues)
            state = "completed" if llm_issues else "fallback"
            self._activity(session, "Bounded LLM Critic", state, detail)

        session["issues"] = self._deduplicate_issues(session["issues"])
        session["handoffs"] = self._initial_handoffs(session["issues"])
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
            {"trace_count": len(session["traces"]), "issue_count": len(session["issues"])},
        )
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
            "uncertainty": "This trace tests protocol coverage; it does not predict how a real person will respond.",
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
                    "(high/medium/low), source_passage_ids, observation, suggestion, uncertainty, handoff_owner. "
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
            issues.append(
                {
                    "id": f"issue_llm_{index + 1}_{uuid.uuid4().hex[:5]}",
                    "title": str(item.get("title", "Additional passage-grounded gap"))[:120],
                    "category": str(item.get("category", "additional_gap"))[:60],
                    "severity": item.get("severity") if item.get("severity") in {"high", "medium", "low"} else "medium",
                    "agent": "Bounded LLM Critic",
                    "source_passage_ids": source_ids[:4],
                    "trigger_trace_id": "",
                    "observation": observation[:700],
                    "evidence_type": "LLM inference grounded to submitted passages",
                    "suggestion": str(item.get("suggestion", "Review and clarify the cited passages."))[:700],
                    "uncertainty": str(item.get("uncertainty", "Verify this inference with a real stakeholder."))[:500],
                    "requires_handoff": True,
                    "handoff_owner": str(item.get("handoff_owner", "relevant real stakeholder"))[:120],
                    "decision": "pending",
                    "decision_rationale": "",
                    "revised_text": "",
                    "decided_at": "",
                    "boundary_status": "planning_hypothesis",
                    "boundary_note": "This issue concerns the submitted protocol and must not be treated as evidence about a real community.",
                }
            )
        return issues, f"Added {len(issues)} passage-grounded LLM issue(s) after boundary checks."

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

    def _initial_handoffs(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        handoffs = []
        for issue in issues:
            if not issue.get("requires_handoff"):
                continue
            handoffs.append(self._handoff_from_issue(issue))
        return handoffs

    def _handoff_from_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": f"handoff_{issue['id']}",
            "issue_id": issue["id"],
            "question": f"How should the project address: {issue['title']}?",
            "why_ai_cannot_resolve": issue.get("uncertainty") or "The answer depends on situated human judgment.",
            "owner": issue.get("handoff_owner", "relevant real stakeholder"),
            "suggested_method": "Review the cited passage and scenario in a short consultation before recruitment.",
            "deadline_stage": "Before recruitment or fieldwork",
            "status": "open",
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
        self.store.save(session)
        self.store.log(session["id"], event_type, payload)
        session["event_log"] = self.store.list_events(session["id"])

    def _active_provider_summary(self) -> Optional[Dict[str, Any]]:
        provider_id = self.llm_client.active_provider_id
        if not provider_id:
            return None
        provider = self.llm_client.providers.get(provider_id)
        return provider.public_dict() if provider else None
