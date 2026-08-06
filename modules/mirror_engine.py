"""Core engine for the SafeBARS Ethical Mirror MVP.

The engine deliberately produces a complete deterministic analysis before any
optional LLM call.  An LLM may add a clearly labelled supplementary probe, but
it cannot decide evidence states, block the workflow, or impersonate a real
stakeholder.
"""

from __future__ import annotations

from copy import deepcopy
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import hashlib
import json
import os
import re
import secrets
import threading

from .mirror_literature import (
    EVIDENCE_STATE_NOTICE,
    LENS_SYNTHESIS_NOTICE,
    lens_registry,
    lens_specs,
    literature_by_id,
    literature_registry,
)
from .mirror_store import MirrorStore, utc_now


SCHEMA_VERSION = "safebars-mirror.v1"
BOUNDARY_NOTICE = (
    "SafeBARS Ethical Mirror is an early research-design reflection aid. "
    "Its evidence states are not an ethics score or institutional approval. "
    "Synthetic role-play is a hypothesis-generating probe, not stakeholder "
    "testimony; consequential claims must be checked with literature, real "
    "affected people, domain experts, and the applicable review process."
)
SYNTHETIC_ROLE_NOTICE = (
    "Synthetic perspective probe — not testimony, lived experience, population "
    "evidence, or a substitute for participation by real affected people."
)

EVIDENCE_STATES: Tuple[Tuple[str, str, int], ...] = (
    ("missing", "Missing", 0),
    ("claimed", "Claimed", 1),
    ("reasoned", "Reasoned", 2),
    ("action_linked", "Action-linked", 3),
)
_STATE_BY_ID = {item[0]: {"id": item[0], "label": item[1], "rank": item[2]} for item in EVIDENCE_STATES}
_STATE_RANK = {item[1]: item[2] for item in EVIDENCE_STATES}

MAX_PLAN_CHARS = 30000
MAX_TITLE_CHARS = 160
MAX_COMMITMENTS = 5
MAX_COMMITMENT_CHARS = 320
MAX_PASSAGES = 80
MAX_REVISIONS = 30
MAX_REPLAY_HISTORY = 30
INTAKE_FIELDS: Tuple[str, ...] = (
    "research_context",
    "intended_change",
    "direct_users",
    "ai_role",
    "data_materials",
    "sensitive_data_justification",
    "affected_others",
    "value_commitment",
    "stop_condition",
    "optional_perspective_context",
)

_REASON_MARKERS = (
    "because", "so that", "therefore", "to avoid", "to prevent", "in order to",
    "could lead", "may cause", "may affect", "which means", "as a result",
    "rather than", "while", "whereas", "due to", "given that", "so participants",
    "because of", "以避免", "因为", "因此", "可能导致",
)
_ACTION_MARKERS = (
    "we will", "the team will", "researchers will", "must", "shall", "require",
    "add", "remove", "limit", "disable", "monitor", "audit", "notify", "obtain",
    "consult", "evaluate", "test", "stop", "pause", "fallback", "allow users",
    "document", "assign", "review", "implement", "provide an appeal",
    "我们将", "必须", "停止", "监测", "审查", "限制",
)
_SPECIFICITY_MARKERS = (
    "before", "after", "when", "if ", "unless", "within", "weekly", "monthly",
    "at each", "for every", "threshold", "metric", "owner", "principal investigator",
    "supervisor", "moderator", "reviewer", "named", "responsible for", "trigger",
    "prior to", "no later than", "一旦", "之前", "之后", "负责人", "阈值",
)
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "have", "in", "is", "it", "of", "on", "or", "our", "research", "study",
    "that", "the", "their", "this", "to", "use", "uses", "using", "we", "will",
    "with", "should", "must", "value",
}


_ROLE_SPECS: List[Dict[str, Any]] = [
    {
        "id": "direct_user",
        "label": "Direct user",
        "objective": (
            "Experience one consequential interaction with the proposed app and "
            "surface an agency, comprehension, access, or contestability tension."
        ),
        "lens_ids": [
            "affected_parties_distribution",
            "responsibility_oversight_contestability",
            "benefit_harm_assumptions",
        ],
        "max_scenarios": 1,
    },
    {
        "id": "affected_non_user",
        "label": "Affected non-user",
        "objective": (
            "Trace how a person who did not directly choose the app could still "
            "be represented, inferred about, excluded, or burdened."
        ),
        "lens_ids": [
            "affected_parties_distribution",
            "perspective_participation",
            "benefit_harm_assumptions",
        ],
        "max_scenarios": 1,
    },
    {
        "id": "downstream_deployer",
        "label": "Downstream deployer",
        "objective": (
            "Move the research prototype into a different context or larger "
            "scale and inspect which assumptions and safeguards stop transferring."
        ),
        "lens_ids": [
            "downstream_use_misuse_scale",
            "lifecycle_integration",
            "mitigation_design_commitment",
        ],
        "max_scenarios": 1,
    },
    {
        "id": "adversarial_reuser",
        "label": "Adversarial reuser",
        "objective": (
            "Probe one plausible misuse or repurposing path without providing "
            "operational instructions for abuse."
        ),
        "lens_ids": [
            "downstream_use_misuse_scale",
            "mitigation_design_commitment",
            "evidence_analogues_horizon",
        ],
        "max_scenarios": 1,
    },
    {
        "id": "maintainer_auditor",
        "label": "Maintainer / auditor",
        "objective": (
            "Inspect a later model, data, or context change and ask who detects "
            "failure, acts, documents the decision, and supports redress."
        ),
        "lens_ids": [
            "monitoring_learning_redress",
            "responsibility_oversight_contestability",
            "evidence_analogues_horizon",
        ],
        "max_scenarios": 1,
    },
]

_ROLE_SCENARIO_TEXT: Dict[str, Dict[str, str]] = {
    "direct_user": {
        "affected_party": "A person using the proposed app in a consequential moment",
        "situation": (
            "A direct user receives an AI-mediated recommendation or classification "
            "and must decide whether to rely on it."
        ),
        "consequence": (
            "The output may shape the user's choice while its basis, uncertainty, "
            "or route to challenge the result remains unclear."
        ),
        "voice": (
            "I can see what the app recommends, but I need to know what it used, "
            "what it may have missed, and how I can reject or correct the result."
        ),
        "assumption": "A useful or accurate-looking output automatically preserves user agency.",
        "intervention": "Make uncertainty, human authority, correction, and appeal visible at the decision point.",
    },
    "affected_non_user": {
        "affected_party": "A person represented in, inferred from, or indirectly affected by the system",
        "situation": (
            "The app's data or output influences someone who never directly used "
            "the prototype or agreed to its decision context."
        ),
        "consequence": (
            "Benefits may accrue to direct users while an unconsulted non-user "
            "bears privacy, exclusion, stigma, or allocation burdens."
        ),
        "voice": (
            "I was not the person using this app, but its assumptions or data "
            "still shaped how another person or institution treated me."
        ),
        "assumption": "Studying direct users captures everyone materially affected by the research output.",
        "intervention": "Validate the affected-party map with real representatives and revise scope or safeguards.",
    },
    "downstream_deployer": {
        "affected_party": "A later operator deploying the prototype outside the original study",
        "situation": (
            "A downstream team reuses the prototype with a different population, "
            "institutional incentive, or level of scale."
        ),
        "consequence": (
            "Safeguards and validity assumptions tied to the study context may "
            "disappear while the output gains greater authority or reach."
        ),
        "voice": (
            "The prototype looks ready to reuse, but I cannot tell which claims, "
            "populations, or safeguards were limited to the original study."
        ),
        "assumption": "A design that is acceptable in a bounded study transfers safely to later contexts.",
        "intervention": "Encode scope limits, deployment conditions, and reassessment triggers in the artefact.",
    },
    "adversarial_reuser": {
        "affected_party": "People exposed to a deliberately repurposed or misused version of the app",
        "situation": (
            "A reuser seeks to turn an intended capability, data flow, or output "
            "toward surveillance, manipulation, exclusion, or another harmful end."
        ),
        "consequence": (
            "A capability designed for benefit may lower the cost of harmful use "
            "or allow misuse to scale beyond the research team's control."
        ),
        "voice": (
            "The same capability can serve a different goal when access, data, "
            "or deployment constraints are removed."
        ),
        "assumption": "Stating the intended use meaningfully constrains how the research output can be reused.",
        "intervention": "Reduce unnecessary capability, gate access, test abuse paths, and define a stop or response rule.",
    },
    "maintainer_auditor": {
        "affected_party": "Future users and affected people after a model, data, or context change",
        "situation": (
            "A model update, new data source, or changed deployment context alters "
            "behavior after the initial evaluation."
        ),
        "consequence": (
            "A previously acceptable result may drift or fail without a named "
            "monitoring trigger, decision owner, correction route, or remedy."
        ),
        "voice": (
            "I can observe that the system changed, but I need a threshold for "
            "action, a responsible owner, and a way to repair affected outcomes."
        ),
        "assumption": "Initial evaluation remains sufficient as models, data, and contexts change.",
        "intervention": "Bind monitoring indicators to an owner, review cadence, rollback, correction, and redress.",
    },
}


def _default_db_path() -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.getenv(
        "SAFEBARS_MIRROR_DB",
        # ``data/*.db`` is already ignored by the repository, preventing local
        # sessions created by imports, tests, or development from being committed.
        os.path.join(root, "data", "safebars_mirror.db"),
    )


def _clean_text(value: Any, max_chars: int) -> str:
    if value is None:
        return ""
    text = str(value).replace("\x00", " ")
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    return text.strip()[:max_chars]


def _title_from_plan(plan: str) -> str:
    first = re.split(r"[\n.!?。！？]", plan, maxsplit=1)[0].strip()
    if not first:
        return "Untitled Ethical Mirror session"
    return first[:MAX_TITLE_CHARS].rstrip()


def _contains_term(text: str, term: str) -> bool:
    lowered = text.lower()
    needle = term.lower()
    if " " in needle or "-" in needle or not needle.isascii():
        return needle in lowered
    return bool(re.search(rf"\b{re.escape(needle)}(?:s|es|ed|ing)?\b", lowered))


def _matched_terms(text: str, terms: Iterable[str]) -> List[str]:
    return [term for term in terms if _contains_term(text, term)]


def _has_any(text: str, markers: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in markers)


def _token_set(text: str) -> set:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
    return {word for word in words if word not in _STOPWORDS}


def _short(text: str, limit: int = 360) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _split_units(text: str) -> List[str]:
    units = re.split(r"(?<=[.!?。！？])\s+|\n+", text)
    return [re.sub(r"\s+", " ", item).strip() for item in units if item.strip()]


class MirrorEngine:
    """Deterministic Ethical Mirror analysis, revision, and replay service."""

    def __init__(self, db_path: Optional[str] = None, llm_client: Optional[Any] = None):
        self.store = MirrorStore(db_path or _default_db_path())
        self._lock = threading.RLock()
        self.llm_client = llm_client
        if self.llm_client is None:
            try:
                from .llm_client import LLMClient
                self.llm_client = LLMClient()
            except Exception:
                self.llm_client = None
        configured = bool(
            self.llm_client
            and getattr(self.llm_client, "is_configured", lambda: False)()
        )
        feature_setting = os.getenv("SAFEBARS_MIRROR_ENABLE_LLM")
        self._llm_feature_enabled = (
            feature_setting != "0" if feature_setting is not None else configured
        )
        self._preferred_llm_provider_id = (
            os.getenv("SAFEBARS_MIRROR_LLM_PROVIDER") or None
        )

    # ------------------------------------------------------------------
    # Public metadata
    # ------------------------------------------------------------------

    def public_config(self) -> Dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "lenses": lens_registry(),
            "evidence_states": [
                {"id": state_id, "label": label, "rank": rank}
                for state_id, label, rank in EVIDENCE_STATES
            ],
            "roles": self.role_specs(),
            "limits": {
                "research_plan_chars": MAX_PLAN_CHARS,
                "value_commitments": MAX_COMMITMENTS,
                "value_commitment_chars": MAX_COMMITMENT_CHARS,
                "synthetic_scenarios_per_role": 1,
            },
            "interpretation_boundary": EVIDENCE_STATE_NOTICE,
            "lens_synthesis_notice": LENS_SYNTHESIS_NOTICE,
            "boundary_notice": BOUNDARY_NOTICE,
            "llm": {
                "optional": True,
                "enabled_by_server": self._llm_feature_enabled,
                "required_for_analysis": False,
                "affects_evidence_states": False,
            },
        }

    @staticmethod
    def role_specs() -> List[Dict[str, Any]]:
        roles = deepcopy(_ROLE_SPECS)
        for role in roles:
            role["synthetic"] = True
            role["boundary_notice"] = SYNTHETIC_ROLE_NOTICE
            role["stopping_rule"] = (
                "Locate one plan passage, construct one consequence probe, "
                "offer revision levers, then stop."
            )
        return roles

    @staticmethod
    def literature() -> List[Dict[str, Any]]:
        return literature_registry()

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def create_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        title, plan, commitments = self._validate_create_payload(payload)
        intake_answers = self._sanitize_intake_answers(payload.get("intake_answers"))
        now = utc_now()
        session: Dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            # The MVP does not expose a separate access token, so the public
            # session identifier itself must be impractical to enumerate.
            "id": f"mirror_{secrets.token_hex(12)}",
            "title": title,
            "original_research_plan": plan,
            "research_plan": plan,
            "current_version": 0,
            "value_commitments": commitments,
            "intake_answers": intake_answers,
            "passages": [],
            "lenses": [],
            "coverage": {},
            "scenarios": [],
            "dissonance_edges": [],
            "dissonance_visualization": {},
            "revisions": [],
            "pending_revision_id": None,
            "replay_history": [],
            "ledger": [],
            "analysis_mode": {},
            "boundary_notice": BOUNDARY_NOTICE,
            "lens_synthesis_notice": LENS_SYNTHESIS_NOTICE,
            "created_at": now,
            "updated_at": now,
        }
        self._append_ledger(
            session,
            "session_created",
            "researcher",
            {
                "title": title,
                "commitment_count": len(commitments),
                "plan_fingerprint": self._fingerprint(plan),
            },
        )
        bundle = self._analyze(plan, commitments, use_llm=False)
        self._apply_bundle(session, bundle)
        self._append_ledger(
            session,
            "analysis_completed",
            "system",
            self._analysis_event_payload(session),
        )
        self._touch(session)
        with self._lock:
            self.store.save(session)
            self.store.log(
                session["id"],
                "session_created",
                session["ledger"][0]["details"],
            )
            self.store.log(
                session["id"],
                "analysis_completed",
                session["ledger"][1]["details"],
            )
        return session

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.store.load(_clean_text(session_id, 100))

    def analyze_session(self, session_id: str, use_llm: bool = False) -> Optional[Dict[str, Any]]:
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return None
            bundle = self._analyze(
                session["research_plan"],
                session["value_commitments"],
                use_llm=bool(use_llm),
            )
            self._apply_bundle(session, bundle)
            self._append_ledger(
                session,
                "analysis_completed",
                "system",
                self._analysis_event_payload(session),
            )
            self._touch(session)
            self.store.save(session)
            self.store.log(
                session["id"],
                "analysis_completed",
                session["ledger"][-1]["details"],
            )
            return session

    def add_revision(
        self,
        session_id: str,
        revised_plan: str,
        resolutions: Optional[Any] = None,
    ) -> Optional[Dict[str, Any]]:
        revised = _clean_text(revised_plan, MAX_PLAN_CHARS)
        if len(revised) < 20:
            raise ValueError("revised_plan must contain at least 20 characters.")
        normalized_resolutions = self._normalize_resolutions(resolutions)
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return None
            if len(session.get("revisions", [])) >= MAX_REVISIONS:
                raise ValueError(f"A session can contain at most {MAX_REVISIONS} revisions.")
            known_edges = {edge["id"] for edge in session.get("dissonance_edges", [])}
            unknown = [
                item["edge_id"]
                for item in normalized_resolutions
                if item["edge_id"] not in known_edges
            ]
            if unknown:
                raise ValueError(f"Unknown dissonance edge id: {unknown[0]}")
            revision_id = f"REV-{len(session.get('revisions', [])) + 1:03d}"
            revision = {
                "id": revision_id,
                "status": "pending_replay",
                "base_version": session.get("current_version", 0),
                "base_plan": session["research_plan"],
                "revised_plan": revised,
                "resolutions": normalized_resolutions,
                "diff": self._build_diff(session["research_plan"], revised),
                "before_snapshot": self._snapshot(session),
                "after_snapshot": None,
                "replay": None,
                "created_at": utc_now(),
                "updated_at": utc_now(),
                "boundary_notice": (
                    "A saved revision records a researcher decision. It is not "
                    "evidence that a consequence has been eliminated."
                ),
            }
            session.setdefault("revisions", []).append(revision)
            session["pending_revision_id"] = revision_id
            self._append_ledger(
                session,
                "revision_added",
                "researcher",
                {
                    "revision_id": revision_id,
                    "resolution_count": len(normalized_resolutions),
                    "base_fingerprint": self._fingerprint(session["research_plan"]),
                    "candidate_fingerprint": self._fingerprint(revised),
                },
            )
            self._touch(session)
            self.store.save(session)
            self.store.log(
                session["id"],
                "revision_added",
                session["ledger"][-1]["details"],
            )
            return session

    def replay_session(
        self,
        session_id: str,
        revision_id: Optional[str] = None,
        use_llm: bool = False,
    ) -> Optional[Dict[str, Any]]:
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return None
            revision = self._select_revision(session, revision_id)
            before_snapshot = self._snapshot(session)
            candidate_plan = session["research_plan"]
            resolutions: List[Dict[str, Any]] = []
            if revision:
                if revision.get("status") == "replayed":
                    before_snapshot = revision.get("before_snapshot") or before_snapshot
                else:
                    before_snapshot = revision.get("before_snapshot") or before_snapshot
                candidate_plan = revision["revised_plan"]
                resolutions = revision.get("resolutions", [])

            bundle = self._analyze(
                candidate_plan,
                session["value_commitments"],
                use_llm=bool(use_llm),
            )
            self._apply_resolution_statuses(
                bundle["dissonance_edges"],
                resolutions,
                before_snapshot,
                bundle,
            )
            bundle["dissonance_visualization"] = self._build_dissonance_visualization(
                bundle["dissonance_edges"]
            )
            replay = self._build_replay(
                revision["id"] if revision else None,
                before_snapshot,
                bundle,
            )

            session["research_plan"] = candidate_plan
            self._apply_bundle(session, bundle)
            session["current_version"] = (
                max(session.get("current_version", 0), revision.get("base_version", 0)) + 1
                if revision and revision.get("status") != "replayed"
                else session.get("current_version", 0)
            )
            session.setdefault("replay_history", []).append(replay)
            session["replay_history"] = session["replay_history"][-MAX_REPLAY_HISTORY:]

            if revision:
                revision["status"] = "replayed"
                revision["after_snapshot"] = self._snapshot(session)
                revision["replay"] = replay
                revision["updated_at"] = utc_now()
                if session.get("pending_revision_id") == revision["id"]:
                    session["pending_revision_id"] = None

            self._append_ledger(
                session,
                "replay_completed",
                "system",
                {
                    "revision_id": replay["revision_id"],
                    "changed_lens_count": replay["summary"]["changed_lens_count"],
                    "resolved_edges": replay["summary"]["resolved_edges"],
                    "transferred_edges": replay["summary"]["transferred_edges"],
                    "open_edges": replay["summary"]["open_edges"],
                    "after_fingerprint": self._fingerprint(candidate_plan),
                },
            )
            self._touch(session)
            self.store.save(session)
            self.store.log(
                session["id"],
                "replay_completed",
                session["ledger"][-1]["details"],
            )
            return session

    # ------------------------------------------------------------------
    # Deterministic analysis
    # ------------------------------------------------------------------

    def _analyze(
        self,
        plan: str,
        commitments: Sequence[str],
        use_llm: bool = False,
    ) -> Dict[str, Any]:
        passages = self._build_passages(plan)
        lenses = self._assess_lenses(passages)
        lens_llm = self._assess_lenses_with_llm(plan, lenses, bool(use_llm))
        self._apply_llm_lens_states(lenses, lens_llm)
        scenarios = self._build_scenarios(plan, passages, lenses)
        analysis_mode = self._optional_llm_probe(plan, scenarios, bool(use_llm))
        self._apply_llm_role_probes(scenarios, analysis_mode)
        edges = self._build_dissonance_edges(commitments, passages, lenses, scenarios)
        if lens_llm.get("llm_used"):
            analysis_mode["llm_affects_evidence_states"] = True
        return {
            "passages": passages,
            "lenses": lenses,
            "coverage": self._coverage_summary(lenses),
            "scenarios": scenarios,
            "dissonance_edges": edges,
            "dissonance_visualization": self._build_dissonance_visualization(edges),
            "analysis_mode": analysis_mode,
            "lens_assessment_mode": lens_llm,
        }

    @staticmethod
    def _build_passages(plan: str) -> List[Dict[str, Any]]:
        units = _split_units(plan)
        if not units:
            units = [plan]
        passages: List[Dict[str, Any]] = []
        for index, unit in enumerate(units[:MAX_PASSAGES], start=1):
            passages.append(
                {
                    "id": f"P-{index:03d}",
                    "text": unit,
                    "fingerprint": MirrorEngine._fingerprint(unit),
                }
            )
        if len(units) > MAX_PASSAGES:
            remainder = " ".join(units[MAX_PASSAGES - 1 :])
            passages[-1]["text"] = _short(remainder, 1200)
            passages[-1]["fingerprint"] = MirrorEngine._fingerprint(passages[-1]["text"])
        return passages

    def _assess_lenses(self, passages: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for spec in lens_specs():
            evidence: List[Dict[str, Any]] = []
            for passage in passages:
                hits = _matched_terms(passage["text"], spec["keywords"])
                if hits:
                    evidence.append(
                        {
                            "passage_id": passage["id"],
                            "quote": _short(passage["text"]),
                            "matched_terms": hits,
                        }
                    )
            evidence.sort(
                key=lambda item: (-len(item["matched_terms"]), item["passage_id"])
            )
            evidence = evidence[:3]
            state_id, rationale = self._classify_evidence(evidence)
            state = _STATE_BY_ID[state_id]
            result = {
                "id": spec["id"],
                "label": spec["label"],
                "prompt": spec["prompt"],
                "operational_definition": spec["operational_definition"],
                "source_ids": spec["source_ids"],
                "boundary": spec["boundary"],
                "state": state["label"],
                "state_id": state["id"],
                "state_rank": state["rank"],
                "evidence": evidence,
                "rationale": rationale,
                "next_action": self._next_action(spec, state_id),
                "interpretation_boundary": EVIDENCE_STATE_NOTICE,
            }
            results.append(result)
        return results

    @staticmethod
    def _classify_evidence(evidence: Sequence[Dict[str, Any]]) -> Tuple[str, str]:
        if not evidence:
            return (
                "missing",
                "No plan passage matched this lens. Absence is a prompt for review, not proof of neglect.",
            )
        joined = " ".join(item["quote"] for item in evidence)
        distinct_terms = {
            term.lower()
            for item in evidence
            for term in item.get("matched_terms", [])
        }
        has_action = _has_any(joined, _ACTION_MARKERS)
        has_specificity = _has_any(joined, _SPECIFICITY_MARKERS)
        has_reason = _has_any(joined, _REASON_MARKERS)
        if has_action and has_specificity and len(distinct_terms) >= 2:
            return (
                "action_linked",
                "The plan links this concern to an action plus a condition, owner, timing cue, or trigger.",
            )
        if has_reason or len(distinct_terms) >= 3:
            return (
                "reasoned",
                "The plan provides a mechanism, trade-off, or sufficiently specific account beyond a principle label.",
            )
        return (
            "claimed",
            "The plan mentions the topic, but does not yet connect it to a mechanism and actionable decision.",
        )

    def _assess_lenses_with_llm(
        self,
        plan: str,
        lenses: Sequence[Dict[str, Any]],
        requested: bool,
    ) -> Dict[str, Any]:
        """Batch-classify all lens evidence states with one LLM call.

        Mirrors the provider-selection / retry / JSON-parse pattern of
        ``_optional_llm_probe``. On any failure (no provider, transport error,
        malformed payload, missing lens ids) it returns ``llm_used=False`` so
        the caller falls back to the deterministic keyword heuristic.
        """
        result: Dict[str, Any] = {
            "llm_requested": requested,
            "llm_used": False,
            "llm_affects_evidence_states": False,
            "llm_status": "not_requested",
            "execution_model": "deterministic_keyword_fallback",
            "lens_assessments": [],
        }
        if not requested:
            return result
        if not self._llm_feature_enabled:
            result["llm_status"] = "disabled_by_server"
            return result
        client = self.llm_client
        if not client or not getattr(client, "is_configured", lambda: False)():
            result["llm_status"] = "not_configured"
            return result
        provider_id = (
            self._preferred_llm_provider_id
            or getattr(client, "active_provider_id", None)
        )
        if not provider_id:
            result["llm_status"] = "not_configured"
            return result
        provider_ids = [provider_id]
        configured_summaries = getattr(
            client, "configured_provider_summaries", lambda: []
        )()
        for provider in configured_summaries:
            candidate = provider.get("id") if isinstance(provider, dict) else None
            if candidate and candidate not in provider_ids:
                provider_ids.append(candidate)
        max_attempts = min(
            4,
            max(1, int(os.getenv("SAFEBARS_MIRROR_LLM_PROVIDER_ATTEMPTS", "4"))),
        )
        provider_ids = provider_ids[:max_attempts]

        lens_contracts = [
            {
                "lens_id": lens["id"],
                "label": lens["label"],
                "operational_definition": lens.get("operational_definition", ""),
                "prompt": lens.get("prompt", ""),
            }
            for lens in lenses
        ]
        prompt = (
            "You assess a research plan against named ethics lenses. For each "
            "lens, judge how deeply the plan addresses it on this four-level "
            "scale:\n"
            "- missing: the plan does not address this lens at all\n"
            "- claimed: the plan mentions the topic but gives no mechanism or "
            "action\n"
            "- reasoned: the plan gives a mechanism, trade-off, or specific "
            "account beyond a label\n"
            "- action_linked: the plan binds the concern to a concrete action "
            "with a condition, owner, timing cue, or trigger\n\n"
            "Return JSON only with this schema:\n"
            '{"lens_assessments":[{"lens_id":"exact id supplied",'
            '"state":"missing|claimed|reasoned|action_linked",'
            '"rationale":"one sentence",'
            '"quote":"short verbatim plan excerpt or empty string",'
            '"concern":"for missing/claimed lenses, one or two sentences stating '
            "the concrete ethical risk the plan's gap creates in THIS project, "
            'grounded in the plan; for reasoned/action_linked lenses, what still '
            'deserves verification; empty only if genuinely nothing to add",'
            '"reflection_question":"one open question the researcher should ask '
            'themselves about this lens"}]}\n\n'
            "Rules: state must be one of the four lowercase values; quote must "
            "be copied verbatim from the plan or empty; concern and "
            "reflection_question must be grounded in the plan and its gaps, not "
            "generic restatements; do not invent facts or stakeholders not "
            "implied by the plan; do not assign an ethics score, approval, or "
            "moral verdict; assess every supplied lens_id exactly once.\n\nLENSES:\n"
            f"{json.dumps(lens_contracts, ensure_ascii=False)}\n\nPLAN:\n"
            f"{plan[:7000]}"
        )
        # Lens assessment is a judgement task, not open generation, so prefer
        # determinism.  Reuse the same bounded timeout as role probes.
        timeout = min(40, max(8, int(os.getenv("SAFEBARS_MIRROR_LLM_TIMEOUT", "30"))))
        messages = [
            {
                "role": "system",
                "content": (
                    "You help a researcher recognize the ethical considerations "
                    "in their own plan. You classify evidence coverage against "
                    "named ethics lenses AND articulate the specific ethical risk "
                    "the plan's gaps or choices create for this project. Follow "
                    "the JSON contract exactly. Never decide whether a project or "
                    "person is ethical; never invent facts not implied by the plan."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        expected_ids = {lens["id"] for lens in lenses}
        valid_states = {item[0] for item in EVIDENCE_STATES}
        provider_attempts: List[Dict[str, str]] = []
        saw_invalid_response = False
        response: Dict[str, Any] = {}
        assessments: List[Dict[str, str]] = []
        for candidate in provider_ids:
            try:
                candidate_response = client.chat_with_provider_detailed(
                    candidate,
                    messages,
                    temperature=0.0,
                    timeout=timeout,
                )
            except Exception:
                provider_attempts.append(
                    {"provider_id": candidate, "status": "transport_error"}
                )
                continue
            if not candidate_response.get("ok"):
                provider_attempts.append(
                    {"provider_id": candidate, "status": "provider_error"}
                )
                continue
            candidate_payload = self._parse_role_probe_payload(
                candidate_response.get("text", "")
            )
            candidate_assessments: List[Dict[str, str]] = []
            seen = set()
            for item in candidate_payload.get("lens_assessments", []):
                if not isinstance(item, dict):
                    continue
                lens_id = _clean_text(item.get("lens_id"), 80)
                if lens_id not in expected_ids or lens_id in seen:
                    continue
                state = _clean_text(item.get("state"), 40).lower().strip()
                if state not in valid_states:
                    continue
                candidate_assessments.append(
                    {
                        "lens_id": lens_id,
                        "state": state,
                        "rationale": _clean_text(item.get("rationale"), 600),
                        "quote": _clean_text(item.get("quote"), 600),
                        "concern": _clean_text(item.get("concern"), 600),
                        "reflection_question": _clean_text(
                            item.get("reflection_question"), 600
                        ),
                    }
                )
                seen.add(lens_id)
            # Accept a provider as long as it returns at least one valid lens
            # assessment. A partial response still helps researchers (the
            # remaining lenses keep their deterministic heuristic), and a single
            # malformed lens must not discard the useful ones.
            if not candidate_assessments:
                saw_invalid_response = True
                provider_attempts.append(
                    {"provider_id": candidate, "status": "invalid_response"}
                )
                continue
            provider_id = candidate
            self._preferred_llm_provider_id = candidate
            response = candidate_response
            assessments = candidate_assessments
            provider_attempts.append(
                {
                    "provider_id": candidate,
                    "status": "used_partial" if seen != expected_ids else "used",
                }
            )
            break
        result["provider_attempts"] = provider_attempts
        if not response.get("ok"):
            result["llm_status"] = (
                "fallback_after_invalid_response"
                if saw_invalid_response
                else "fallback_after_error"
            )
            return result
        result.update(
            {
                "llm_used": True,
                "llm_affects_evidence_states": True,
                "llm_status": "lens_states_available",
                "execution_model": "single_batched_call_temperature_zero",
                "provider_id": provider_id,
                "model": response.get("model"),
                "lens_assessments": assessments,
                "interpretation_boundary": EVIDENCE_STATE_NOTICE,
            }
        )
        return result

    @staticmethod
    def _apply_llm_lens_states(
        lenses: Sequence[Dict[str, Any]],
        lens_llm: Dict[str, Any],
    ) -> None:
        """Merge LLM lens states in place, preserving the heuristic baseline.

        Mirrors ``_apply_llm_role_probes``: when the LLM batch succeeded, the
        original keyword-heuristic state is retained as ``heuristic_state`` and
        the LLM judgement overwrites the live ``state``/``rationale`` fields so
        downstream coverage, scenarios, and dissonance edges all reflect the
        semantic judgement. The deterministic evidence list is left untouched.
        """
        if not lens_llm.get("llm_used"):
            return
        by_id = {
            item["lens_id"]: item
            for item in lens_llm.get("lens_assessments", [])
            if isinstance(item, dict) and item.get("lens_id")
        }
        for lens in lenses:
            ll = by_id.get(lens.get("id"))
            if not ll:
                continue
            lens["heuristic_state"] = lens.get("state")
            lens["heuristic_state_id"] = lens.get("state_id")
            lens["heuristic_rationale"] = lens.get("rationale")
            state_info = _STATE_BY_ID.get(ll["state"])
            if not state_info:
                continue
            lens["state"] = state_info["label"]
            lens["state_id"] = state_info["id"]
            lens["state_rank"] = state_info["rank"]
            if ll.get("rationale"):
                lens["rationale"] = ll["rationale"]
            if ll.get("concern"):
                lens["concern"] = ll["concern"]
            if ll.get("reflection_question"):
                lens["reflection_question"] = ll["reflection_question"]
            lens["assessment_source"] = "llm"

    @staticmethod
    def _next_action(spec: Dict[str, Any], state_id: str) -> str:
        if state_id == "missing":
            return f"Add a plan passage that answers: {spec['prompt']}"
        if state_id == "claimed":
            return "Explain who is affected, the causal mechanism, and which assumption may fail."
        if state_id == "reasoned":
            return "Bind the reasoning to a named design change, owner, trigger, or stopping condition."
        return "Verify the action with evidence or real stakeholders and record what would trigger revision."

    @staticmethod
    def _coverage_summary(lenses: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        counts = {label: 0 for _, label, _ in EVIDENCE_STATES}
        for lens in lenses:
            counts[lens["state"]] += 1
        return {
            "type": "evidence_coverage_not_ethics_score",
            "lens_count": len(lenses),
            "state_counts": counts,
            "interpretation_boundary": EVIDENCE_STATE_NOTICE,
            "is_ethics_score": False,
        }

    def _build_scenarios(
        self,
        plan: str,
        passages: Sequence[Dict[str, Any]],
        lenses: Sequence[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        lens_map = {lens["id"]: lens for lens in lenses}
        source_map = literature_by_id()
        system_label = self._system_label(plan)
        scenarios: List[Dict[str, Any]] = []
        for index, role in enumerate(_ROLE_SPECS, start=1):
            content = _ROLE_SCENARIO_TEXT[role["id"]]
            plan_evidence = self._best_role_evidence(role, passages, lens_map)
            source_ids: List[str] = []
            for lens_id in role["lens_ids"]:
                for source_id in lens_map[lens_id]["source_ids"]:
                    if source_id not in source_ids:
                        source_ids.append(source_id)
            scenario_id = f"SCN-{index:03d}"
            scenario = {
                "id": scenario_id,
                "agent_id": role["id"],
                "agent_label": role["label"],
                "role_id": role["id"],
                "role_label": role["label"],
                "synthetic": True,
                "boundary_notice": SYNTHETIC_ROLE_NOTICE,
                "objective": role["objective"],
                "affected_party": content["affected_party"],
                "situation": f"{content['situation']} The object under review is {system_label}.",
                "consequence": content["consequence"],
                "first_person_probe": content["voice"],
                "assumption_challenged": content["assumption"],
                "revision_lever": content["intervention"],
                "plan_evidence": plan_evidence,
                "lens_ids": role["lens_ids"],
                "source_ids": source_ids,
                "source_links": [
                    {"id": source_id, "url": source_map[source_id]["url"]}
                    for source_id in source_ids
                    if source_id in source_map
                ],
                "epistemic_status": "synthetic_hypothesis",
                "generation_mode": "deterministic_bounded_fallback",
                "bounded_trace": [
                    {
                        "step": 1,
                        "action": "Locate one relevant plan passage",
                        "result": plan_evidence["passage_id"],
                    },
                    {
                        "step": 2,
                        "action": "Apply one bounded affected-party perspective",
                        "result": role["label"],
                    },
                    {
                        "step": 3,
                        "action": "Construct one consequence and one intervention point",
                        "result": scenario_id,
                    },
                    {
                        "step": 4,
                        "action": "Stop and return control to the researcher",
                        "result": "stopped",
                    },
                ],
                "visualization": {
                    "kind": "scenario_storyboard",
                    "frames": [
                        {
                            "id": f"{scenario_id}-F1",
                            "type": "research_design",
                            "label": "Plan",
                            "text": plan_evidence["quote"],
                        },
                        {
                            "id": f"{scenario_id}-F2",
                            "type": "encounter",
                            "label": "Encounter",
                            "text": content["situation"],
                        },
                        {
                            "id": f"{scenario_id}-F3",
                            "type": "affected_voice",
                            "label": "Synthetic perspective",
                            "text": content["voice"],
                        },
                        {
                            "id": f"{scenario_id}-F4",
                            "type": "intervention",
                            "label": "Possible design lever",
                            "text": content["intervention"],
                        },
                    ],
                },
            }
            scenarios.append(scenario)
        return scenarios

    @staticmethod
    def _best_role_evidence(
        role: Dict[str, Any],
        passages: Sequence[Dict[str, Any]],
        lens_map: Dict[str, Dict[str, Any]],
    ) -> Dict[str, str]:
        for lens_id in role["lens_ids"]:
            evidence = lens_map[lens_id].get("evidence", [])
            if evidence:
                return {
                    "passage_id": evidence[0]["passage_id"],
                    "quote": evidence[0]["quote"],
                }
        fallback = passages[0] if passages else {"id": "P-000", "text": "No plan passage supplied."}
        return {
            "passage_id": fallback["id"],
            "quote": _short(fallback["text"]),
        }

    @staticmethod
    def _system_label(plan: str) -> str:
        lowered = plan.lower()
        if any(term in lowered for term in ("llm", "large language model", "generative ai")):
            return "the proposed LLM-enabled research app"
        if any(term in lowered for term in ("artificial intelligence", " ai ", "machine learning", "model")):
            return "the proposed AI-enabled research app"
        return "the proposed research app"

    def _build_dissonance_edges(
        self,
        commitments: Sequence[str],
        passages: Sequence[Dict[str, Any]],
        lenses: Sequence[Dict[str, Any]],
        scenarios: Sequence[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        lens_map = {lens["id"]: lens for lens in lenses}
        edges: List[Dict[str, Any]] = []
        for index, commitment_text in enumerate(commitments, start=1):
            scenario = self._scenario_for_commitment(commitment_text, scenarios, index - 1)
            plan_passage = self._passage_for_commitment(
                commitment_text,
                passages,
                scenario["plan_evidence"],
            )
            lens_ids = scenario["lens_ids"]
            literature_ids: List[str] = []
            for lens_id in lens_ids:
                for source_id in lens_map[lens_id]["source_ids"]:
                    if source_id not in literature_ids:
                        literature_ids.append(source_id)
            linked_lenses = [lens_map[lens_id] for lens_id in lens_ids]
            attention_lenses = [
                lens for lens in linked_lenses if lens.get("state_id") != "action_linked"
            ]
            attention_required = bool(linked_lenses) and not any(
                lens.get("state_id") == "action_linked" for lens in linked_lenses
            )
            attention_lens_ids = [lens["id"] for lens in attention_lenses]
            if attention_required:
                attention_basis = (
                    f"None of the {len(linked_lenses)} linked literature lenses contains "
                    "Action-linked plan evidence: an action plus a condition, owner, "
                    "timing cue, or trigger. This transparent coverage rule flags the "
                    "path for closer inspection; it is not an ethics or severity score."
                )
            else:
                attention_basis = (
                    "At least one linked literature lens contains Action-linked plan "
                    "evidence, so this path remains inspectable without an evidence-"
                    "coverage flag. This is not an ethics or severity score."
                )
            edge_id = f"EDGE-{index:03d}"
            design_choice = {
                "passage_id": plan_passage["passage_id"],
                "quote": plan_passage["quote"],
                "interpretation": (
                    "This passage is treated as the current design evidence to "
                    "inspect, not as a definitive statement of intent."
                ),
            }
            edge = {
                "id": edge_id,
                "commitment": {
                    "id": f"COM-{index:03d}",
                    "text": commitment_text,
                },
                "design_choice": design_choice,
                "scenario": {
                    "id": scenario["id"],
                    "agent_id": scenario["agent_id"],
                    "situation": scenario["situation"],
                    "synthetic": True,
                },
                "consequence": scenario["consequence"],
                "affected_party": scenario["affected_party"],
                "relation": "evidence_gap" if attention_required else "context_to_inspect",
                "attention_required": attention_required,
                "attention_rule": "no_linked_lens_has_action_linked_evidence",
                "attention_lens_ids": attention_lens_ids,
                "attention_basis": attention_basis,
                "tension": (
                    f"You committed to “{commitment_text}”. Inspect whether the "
                    f"current design passage remains consistent with that commitment "
                    f"when {scenario['affected_party'].lower()} experiences this scenario."
                ),
                "status": "open",
                "decision": None,
                "status_reason": "No researcher resolution has been replayed yet.",
                "provenance": {
                    "source_passage": deepcopy(design_choice),
                    "lens_ids": lens_ids,
                    "literature_ids": literature_ids,
                },
                "epistemic_status": "researcher_commitment_plus_synthetic_probe",
                "boundary_notice": (
                    "This visible mismatch is an invitation to inspect and choose, "
                    "not a diagnosis that the researcher or project is unethical."
                ),
                "response_options": [
                    {
                        "id": "revise",
                        "label": "Revise the design",
                        "description": "Change a feature, scope, method, safeguard, or stopping rule.",
                    },
                    {
                        "id": "contest_with_evidence",
                        "label": "Contest with evidence",
                        "description": "Explain why the scenario does not fit and cite inspectable evidence.",
                    },
                    {
                        "id": "consult_stakeholder",
                        "label": "Consult real stakeholders",
                        "description": "Transfer the unresolved assumption to people with relevant lived or domain knowledge.",
                    },
                    {
                        "id": "retain_with_rationale",
                        "label": "Retain with rationale",
                        "description": "Keep the design choice while recording the trade-off and reassessment trigger.",
                    },
                ],
                "visual_path": [
                    {"type": "commitment", "label": "My commitment", "text": commitment_text},
                    {"type": "design", "label": "Current design evidence", "text": plan_passage["quote"]},
                    {"type": "scenario", "label": "Synthetic encounter", "text": scenario["situation"]},
                    {"type": "party", "label": "Affected party", "text": scenario["affected_party"]},
                    {"type": "consequence", "label": "Possible consequence", "text": scenario["consequence"]},
                    {"type": "choice", "label": "Researcher decision", "text": "Open"},
                ],
            }
            edges.append(edge)
        return edges

    @staticmethod
    def _scenario_for_commitment(
        commitment: str,
        scenarios: Sequence[Dict[str, Any]],
        fallback_index: int,
    ) -> Dict[str, Any]:
        lowered = commitment.lower()
        preferences: List[Tuple[Tuple[str, ...], str]] = [
            # A researcher-authored pause/redesign threshold is a lifecycle
            # monitoring commitment. Match it before words such as "appeal"
            # so it does not collapse onto the same direct-user probe as the
            # value commitment that preceded it in guided intake.
            (("pause", "redesign", "stopping", "stop condition", "trigger"), "maintainer_auditor"),
            (("autonomy", "choice", "contest", "appeal", "transparent", "explain"), "direct_user"),
            (("fair", "equity", "equal", "access", "exclude", "inclusive"), "affected_non_user"),
            (("privacy", "data", "confidential", "consent"), "affected_non_user"),
            (("safe", "harm", "misuse", "abuse"), "adversarial_reuser"),
            (("account", "oversight", "responsib", "monitor", "redress"), "maintainer_auditor"),
            (("scale", "downstream", "deploy"), "downstream_deployer"),
        ]
        for terms, agent_id in preferences:
            if any(term in lowered for term in terms):
                for scenario in scenarios:
                    if scenario["agent_id"] == agent_id:
                        return scenario
        return scenarios[fallback_index % len(scenarios)]

    @staticmethod
    def _passage_for_commitment(
        commitment: str,
        passages: Sequence[Dict[str, Any]],
        fallback: Dict[str, str],
    ) -> Dict[str, str]:
        commitment_tokens = _token_set(commitment)
        best: Optional[Dict[str, Any]] = None
        best_overlap = 0
        for passage in passages:
            overlap = len(commitment_tokens & _token_set(passage["text"]))
            if overlap > best_overlap:
                best = passage
                best_overlap = overlap
        if best and best_overlap:
            return {"passage_id": best["id"], "quote": _short(best["text"])}
        return deepcopy(fallback)

    @staticmethod
    def _build_dissonance_visualization(edges: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        nodes: List[Dict[str, Any]] = []
        links: List[Dict[str, str]] = []
        for edge in edges:
            prefix = edge["id"]
            path_nodes: List[str] = []
            for index, item in enumerate(edge["visual_path"], start=1):
                node_id = f"{prefix}-N{index}"
                nodes.append(
                    {
                        "id": node_id,
                        "edge_id": prefix,
                        "type": item["type"],
                        "label": item["label"],
                        "text": item["text"],
                    }
                )
                path_nodes.append(node_id)
            for source, target in zip(path_nodes, path_nodes[1:]):
                links.append({"source": source, "target": target, "edge_id": prefix})
        return {
            "kind": "commitment_consequence_graph",
            "nodes": nodes,
            "links": links,
            "interaction_hint": (
                "Select any node to inspect its plan passage, synthetic scenario, "
                "lens, literature provenance, and available researcher decisions."
            ),
            "interpretation_boundary": (
                "Graph links are deliberation paths, not causal estimates or ethics scores."
            ),
        }

    # ------------------------------------------------------------------
    # Revision and replay helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_resolutions(raw: Optional[Any]) -> List[Dict[str, Any]]:
        if raw in (None, ""):
            return []
        if isinstance(raw, dict):
            if "edge_id" in raw:
                items = [raw]
            else:
                items = [
                    {"edge_id": edge_id, **(value if isinstance(value, dict) else {"decision": value})}
                    for edge_id, value in raw.items()
                ]
        elif isinstance(raw, list):
            items = raw
        else:
            raise ValueError("resolutions must be a list or object.")
        aliases = {
            "revise": "revise",
            "revise_design": "revise",
            "add_safeguard": "revise",
            "narrow_capability": "revise",
            "contest": "contest_with_evidence",
            "contest_with_evidence": "contest_with_evidence",
            "consult": "consult_stakeholder",
            "handoff": "consult_stakeholder",
            "consult_stakeholders": "consult_stakeholder",
            "consult_stakeholder": "consult_stakeholder",
            "retain": "retain_with_rationale",
            "retain_with_rationale": "retain_with_rationale",
        }
        normalized: List[Dict[str, Any]] = []
        seen = set()
        for raw_item in items:
            if not isinstance(raw_item, dict):
                raise ValueError("Each resolution must be an object.")
            edge_id = _clean_text(raw_item.get("edge_id"), 40).upper()
            decision_raw = _clean_text(
                raw_item.get("decision") or raw_item.get("resolution_type"),
                80,
            ).lower().replace(" ", "_")
            decision = aliases.get(decision_raw)
            if not edge_id or not decision:
                raise ValueError(
                    "Each resolution requires an edge_id and one of: revise, "
                    "contest_with_evidence, consult_stakeholder, retain_with_rationale."
                )
            if edge_id in seen:
                raise ValueError(f"Duplicate resolution for {edge_id}.")
            seen.add(edge_id)
            item = {
                "edge_id": edge_id,
                "decision": decision,
                "rationale": _clean_text(raw_item.get("rationale"), 1200),
            }
            follow_up = _clean_text(raw_item.get("follow_up"), 1200)
            if follow_up:
                item["follow_up"] = follow_up
            normalized.append(item)
        return normalized

    @staticmethod
    def _build_diff(before: str, after: str) -> Dict[str, Any]:
        before_units = _split_units(before)
        after_units = _split_units(after)
        matcher = SequenceMatcher(a=before_units, b=after_units, autojunk=False)
        changes: List[Dict[str, Any]] = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            changes.append(
                {
                    "type": tag,
                    "before": before_units[i1:i2],
                    "after": after_units[j1:j2],
                }
            )
        return {
            "changes": changes[:30],
            "truncated": len(changes) > 30,
            "before_chars": len(before),
            "after_chars": len(after),
            "changed": before.strip() != after.strip(),
        }

    @staticmethod
    def _snapshot(session_or_bundle: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "research_plan": session_or_bundle.get("research_plan", ""),
            "plan_fingerprint": MirrorEngine._fingerprint(
                session_or_bundle.get("research_plan", "")
            ),
            "lens_states": {
                lens["id"]: {
                    "state": lens["state"],
                    "state_id": lens["state_id"],
                    "state_rank": lens["state_rank"],
                }
                for lens in session_or_bundle.get("lenses", [])
            },
            "scenario_evidence": {
                scenario["agent_id"]: {
                    "scenario_id": scenario["id"],
                    "passage_id": scenario["plan_evidence"]["passage_id"],
                    "quote": scenario["plan_evidence"]["quote"],
                }
                for scenario in session_or_bundle.get("scenarios", [])
            },
            "edge_statuses": {
                edge["id"]: edge.get("status", "open")
                for edge in session_or_bundle.get("dissonance_edges", [])
            },
            "captured_at": utc_now(),
        }

    @staticmethod
    def _select_revision(
        session: Dict[str, Any],
        revision_id: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        revisions = session.get("revisions", [])
        target = _clean_text(revision_id, 40).upper() if revision_id else None
        if target:
            for revision in revisions:
                if revision["id"].upper() == target:
                    return revision
            raise ValueError(f"Revision not found: {target}")
        pending_id = session.get("pending_revision_id")
        if pending_id:
            for revision in revisions:
                if revision["id"] == pending_id:
                    return revision
        return None

    @staticmethod
    def _apply_resolution_statuses(
        edges: List[Dict[str, Any]],
        resolutions: Sequence[Dict[str, Any]],
        before_snapshot: Dict[str, Any],
        after_bundle: Dict[str, Any],
    ) -> None:
        resolution_map = {item["edge_id"]: item for item in resolutions}
        before_states = before_snapshot.get("lens_states", {})
        after_states = {
            lens["id"]: lens for lens in after_bundle.get("lenses", [])
        }
        for edge in edges:
            resolution = resolution_map.get(edge["id"])
            if not resolution:
                continue
            decision = resolution["decision"]
            edge["decision"] = deepcopy(resolution)
            relevant_lenses = edge["provenance"]["lens_ids"]
            improved = any(
                after_states.get(lens_id, {}).get("state_rank", 0)
                > before_states.get(lens_id, {}).get("state_rank", 0)
                for lens_id in relevant_lenses
            )
            if decision == "consult_stakeholder":
                edge["status"] = "transferred"
                edge["status_reason"] = (
                    "The researcher transferred this unresolved assumption to "
                    "real stakeholder or domain-expert consultation."
                )
            elif decision == "revise" and improved:
                edge["status"] = "resolved"
                edge["status_reason"] = (
                    "The linked plan evidence became more actionable after the "
                    "researcher-recorded revision. This does not prove the risk is eliminated."
                )
            elif decision == "revise":
                edge["status"] = "open"
                edge["status_reason"] = (
                    "A revision was recorded, but linked evidence coverage did "
                    "not become more actionable; inspect and revise again or justify."
                )
            elif decision == "contest_with_evidence" and len(resolution.get("rationale", "")) >= 40:
                edge["status"] = "resolved"
                edge["status_reason"] = (
                    "The researcher recorded a substantive contesting rationale. "
                    "Its cited evidence still requires human inspection."
                )
            else:
                edge["status"] = "open"
                edge["status_reason"] = (
                    "The researcher retained the choice or supplied insufficient "
                    "inspectable evidence; the tension remains visible."
                )
            edge["visual_path"][-1]["text"] = (
                f"{decision.replace('_', ' ').title()} · {edge['status'].title()}"
            )

    @staticmethod
    def _build_replay(
        revision_id: Optional[str],
        before_snapshot: Dict[str, Any],
        after_bundle: Dict[str, Any],
    ) -> Dict[str, Any]:
        after_lenses = {lens["id"]: lens for lens in after_bundle["lenses"]}
        lens_changes: List[Dict[str, Any]] = []
        for lens_id, after in after_lenses.items():
            before = before_snapshot.get("lens_states", {}).get(
                lens_id,
                {"state": "Missing", "state_rank": 0},
            )
            delta = after["state_rank"] - int(before.get("state_rank", 0))
            lens_changes.append(
                {
                    "lens_id": lens_id,
                    "before": before.get("state", "Missing"),
                    "after": after["state"],
                    "direction": (
                        "more_actionable_evidence"
                        if delta > 0
                        else "less_actionable_evidence"
                        if delta < 0
                        else "unchanged_state"
                    ),
                    "rank_delta": delta,
                }
            )
        before_scenarios = before_snapshot.get("scenario_evidence", {})
        scenario_changes: List[Dict[str, Any]] = []
        for scenario in after_bundle["scenarios"]:
            before = before_scenarios.get(scenario["agent_id"], {})
            quote_changed = before.get("quote") != scenario["plan_evidence"]["quote"]
            scenario_changes.append(
                {
                    "agent_id": scenario["agent_id"],
                    "scenario_id": scenario["id"],
                    "plan_evidence_changed": quote_changed,
                    "status": "reframed" if quote_changed else "persistent_probe",
                    "boundary_notice": (
                        "A persistent or reframed synthetic probe does not estimate "
                        "whether the consequence will occur."
                    ),
                }
            )
        statuses = [edge.get("status", "open") for edge in after_bundle["dissonance_edges"]]
        return {
            "id": f"REPLAY-{secrets.token_hex(4)}",
            "revision_id": revision_id,
            "created_at": utc_now(),
            "lens_changes": lens_changes,
            "scenario_changes": scenario_changes,
            "summary": {
                "changed_lens_count": sum(
                    1 for item in lens_changes if item["direction"] != "unchanged_state"
                ),
                "resolved_edges": statuses.count("resolved"),
                "transferred_edges": statuses.count("transferred"),
                "open_edges": statuses.count("open"),
            },
            "interpretation_boundary": (
                "Replay compares plan evidence and synthetic probes before and "
                "after a revision. It is not proof that harm was prevented."
            ),
        }

    # ------------------------------------------------------------------
    # Optional supplementary LLM probe
    # ------------------------------------------------------------------

    def _optional_llm_probe(
        self,
        plan: str,
        scenarios: Sequence[Dict[str, Any]],
        requested: bool,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "deterministic_analysis_completed": True,
            "llm_requested": requested,
            "llm_used": False,
            "llm_affects_evidence_states": False,
            "llm_status": "not_requested",
            "execution_model": "deterministic_bounded_fallback",
            "role_probes": [],
        }
        if not requested:
            return result
        if not self._llm_feature_enabled:
            result["llm_status"] = "disabled_by_server"
            return result
        client = self.llm_client
        if not client or not getattr(client, "is_configured", lambda: False)():
            result["llm_status"] = "not_configured"
            return result
        provider_id = (
            self._preferred_llm_provider_id
            or getattr(client, "active_provider_id", None)
        )
        if not provider_id:
            result["llm_status"] = "not_configured"
            return result
        provider_ids = [provider_id]
        configured_summaries = getattr(
            client, "configured_provider_summaries", lambda: []
        )()
        for provider in configured_summaries:
            candidate = provider.get("id") if isinstance(provider, dict) else None
            if candidate and candidate not in provider_ids:
                provider_ids.append(candidate)
        max_attempts = min(
            4,
            max(1, int(os.getenv("SAFEBARS_MIRROR_LLM_PROVIDER_ATTEMPTS", "4"))),
        )
        provider_ids = provider_ids[:max_attempts]
        role_contract = [
            {
                "agent_id": item["agent_id"],
                "role": item["agent_label"],
                "objective": item["objective"],
                "plan_evidence": item["plan_evidence"]["quote"],
                "seed_situation": item["situation"],
                "seed_consequence": item["consequence"],
            }
            for item in scenarios[:5]
        ]
        prompt = (
            "Act as an orchestrator for five bounded synthetic role probes about "
            "an AI-app research plan. Produce one distinct probe for every exact "
            "agent_id supplied below. The roles are analytical standpoints, not "
            "real people and not demographic impersonations.\n\n"
            "Return JSON only with this schema:\n"
            '{"role_probes":[{"agent_id":"exact id","first_person_probe":"max 55 '
            'words","consequence":"max 55 words","question_for_real_people":"max '
            '35 words","revision_lever":"max 35 words"}],"cross_role_questions":'
            '["max 35 words"]}\n\n'
            "Rules: keep every output specific to a submitted plan passage; do "
            "not invent a person's age, race, gender, disability, family status, "
            "or lived experience; do not claim testimony, consensus, probability, "
            "an ethics score, approval, diagnosis, or moral verdict; do not add "
            "operational abuse instructions; return at most two cross-role "
            "questions.\n\nPLAN:\n"
            f"{plan[:7000]}\n\nROLE CONTRACTS:\n"
            f"{json.dumps(role_contract, ensure_ascii=False)}"
        )
        # Five role probes are requested in one bounded call.  Some configured
        # providers need slightly longer than a chat-style single sentence, so
        # use the existing hard cap as the default instead of timing out early.
        timeout = min(18, max(4, int(os.getenv("SAFEBARS_MIRROR_LLM_TIMEOUT", "18"))))
        messages = [
            {
                "role": "system",
                "content": (
                    "You generate bounded synthetic perspective questions "
                    "for research-design reflection. Follow the JSON contract "
                    "and never decide whether a project or person is ethical."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        response: Dict[str, Any] = {}
        payload: Dict[str, Any] = {}
        probes: List[Dict[str, str]] = []
        saw_invalid_response = False
        expected_ids = {item["agent_id"] for item in scenarios[:5]}
        provider_attempts: List[Dict[str, str]] = []
        for candidate in provider_ids:
            try:
                candidate_response = client.chat_with_provider_detailed(
                    candidate,
                    messages,
                    temperature=0.2,
                    timeout=timeout,
                )
            except Exception:
                provider_attempts.append(
                    {"provider_id": candidate, "status": "transport_error"}
                )
                continue
            if not candidate_response.get("ok"):
                provider_attempts.append(
                    {"provider_id": candidate, "status": "provider_error"}
                )
                continue

            candidate_payload = self._parse_role_probe_payload(
                candidate_response.get("text", "")
            )
            candidate_probes: List[Dict[str, str]] = []
            seen = set()
            for item in candidate_payload.get("role_probes", []):
                if not isinstance(item, dict):
                    continue
                agent_id = _clean_text(item.get("agent_id"), 80)
                if agent_id not in expected_ids or agent_id in seen:
                    continue
                probe = {
                    "agent_id": agent_id,
                    "first_person_probe": _clean_text(
                        item.get("first_person_probe"), 520
                    ),
                    "consequence": _clean_text(item.get("consequence"), 520),
                    "question_for_real_people": _clean_text(
                        item.get("question_for_real_people"), 360
                    ),
                    "revision_lever": _clean_text(
                        item.get("revision_lever"), 360
                    ),
                }
                if probe["first_person_probe"] and probe["consequence"]:
                    candidate_probes.append(probe)
                    seen.add(agent_id)

            # A transport-level success is not enough.  Remember a provider only
            # after it satisfies the complete five-role contract; otherwise a
            # malformed response would poison later failover attempts.
            if seen != expected_ids:
                saw_invalid_response = True
                provider_attempts.append(
                    {"provider_id": candidate, "status": "invalid_response"}
                )
                continue

            provider_id = candidate
            self._preferred_llm_provider_id = candidate
            response = candidate_response
            payload = candidate_payload
            probes = candidate_probes
            provider_attempts.append(
                {"provider_id": candidate, "status": "used"}
            )
            break
        result["provider_attempts"] = provider_attempts
        if not response.get("ok"):
            result["llm_status"] = (
                "fallback_after_invalid_response"
                if saw_invalid_response
                else "fallback_after_error"
            )
            if not saw_invalid_response:
                result["llm_error"] = (
                    "Configured model providers were unavailable; the bounded "
                    "deterministic fallback was used."
                )
            return result
        cross_role_questions = [
            _clean_text(item, 360)
            for item in payload.get("cross_role_questions", [])[:2]
            if _clean_text(item, 360)
        ]
        result.update(
            {
                "llm_used": True,
                "llm_status": "bounded_role_probes_available",
                "execution_model": "single_batched_call_with_separate_role_contracts",
                "provider_id": provider_id,
                "model": response.get("model"),
                "role_probes": probes,
                "role_probe_count": len(probes),
                "cross_role_questions": cross_role_questions,
                "supplement_boundary": (
                    "Unverified model-generated synthetic role probes. They are "
                    "not independent stakeholder agents or testimony; inspect the "
                    "linked plan evidence and validate with real people."
                ),
            }
        )
        return result

    @staticmethod
    def _parse_role_probe_payload(raw: Any) -> Dict[str, Any]:
        text = str(raw or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
        try:
            payload = json.loads(text)
        except (TypeError, ValueError, json.JSONDecodeError):
            start = text.find("{")
            end = text.rfind("}")
            if start < 0 or end <= start:
                return {}
            try:
                payload = json.loads(text[start : end + 1])
            except (TypeError, ValueError, json.JSONDecodeError):
                return {}
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _apply_llm_role_probes(
        scenarios: Sequence[Dict[str, Any]],
        analysis_mode: Dict[str, Any],
    ) -> None:
        if not analysis_mode.get("llm_used"):
            return
        by_agent = {
            item["agent_id"]: item
            for item in analysis_mode.get("role_probes", [])
            if isinstance(item, dict) and item.get("agent_id")
        }
        for scenario in scenarios:
            probe = by_agent.get(scenario.get("agent_id"))
            if not probe:
                continue
            scenario["deterministic_seed"] = {
                "consequence": scenario["consequence"],
                "first_person_probe": scenario["first_person_probe"],
                "revision_lever": scenario["revision_lever"],
            }
            scenario["consequence"] = probe["consequence"]
            scenario["first_person_probe"] = probe["first_person_probe"]
            if probe.get("question_for_real_people"):
                scenario["question_for_real_people"] = probe[
                    "question_for_real_people"
                ]
                scenario["question"] = probe["question_for_real_people"]
            if probe.get("revision_lever"):
                scenario["revision_lever"] = probe["revision_lever"]
            scenario["generation_mode"] = "llm_batched_bounded_role_probe"
            scenario["model_enrichment"] = {
                "provider_id": analysis_mode.get("provider_id"),
                "model": analysis_mode.get("model"),
                "execution_model": analysis_mode.get("execution_model"),
            }
            frames = scenario.get("visualization", {}).get("frames", [])
            for frame in frames:
                if frame.get("type") == "affected_voice":
                    frame["text"] = scenario["first_person_probe"]
                elif frame.get("type") == "intervention":
                    frame["text"] = scenario["revision_lever"]

    # ------------------------------------------------------------------
    # General helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_create_payload(payload: Dict[str, Any]) -> Tuple[str, str, List[str]]:
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")
        plan = _clean_text(payload.get("research_plan"), MAX_PLAN_CHARS)
        if len(plan) < 20:
            raise ValueError("research_plan must contain at least 20 characters.")
        raw_commitments = payload.get("value_commitments")
        if isinstance(raw_commitments, str):
            raw_commitments = [raw_commitments]
        if not isinstance(raw_commitments, list):
            raise ValueError("value_commitments must be a list of one to five statements.")
        commitments: List[str] = []
        seen = set()
        for raw in raw_commitments:
            value = _clean_text(raw, MAX_COMMITMENT_CHARS)
            if not value:
                continue
            key = value.casefold()
            if key not in seen:
                seen.add(key)
                commitments.append(value)
        if not commitments:
            raise ValueError("At least one value commitment is required.")
        if len(commitments) > MAX_COMMITMENTS:
            raise ValueError(f"At most {MAX_COMMITMENTS} value commitments are allowed.")
        title = _clean_text(payload.get("title"), MAX_TITLE_CHARS) or _title_from_plan(plan)
        return title, plan, commitments

    @staticmethod
    def _sanitize_intake_answers(raw: Any) -> Dict[str, str]:
        """Persist only the bounded, documented guided-intake fields."""

        if raw is None:
            return {}
        if not isinstance(raw, dict):
            raise ValueError("intake_answers must be a JSON object when provided.")
        answers: Dict[str, str] = {}
        for field in INTAKE_FIELDS:
            limit = 700 if field == "optional_perspective_context" else 1400
            value = _clean_text(raw.get(field), limit)
            if value:
                answers[field] = value
        return answers

    @staticmethod
    def _apply_bundle(session: Dict[str, Any], bundle: Dict[str, Any]) -> None:
        for key in (
            "passages",
            "lenses",
            "coverage",
            "scenarios",
            "dissonance_edges",
            "dissonance_visualization",
            "analysis_mode",
            "lens_assessment_mode",
        ):
            session[key] = bundle[key]

    @staticmethod
    def _analysis_event_payload(session: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "version": session.get("current_version", 0),
            "plan_fingerprint": MirrorEngine._fingerprint(session["research_plan"]),
            "lens_state_counts": session["coverage"]["state_counts"],
            "scenario_count": len(session.get("scenarios", [])),
            "edge_count": len(session.get("dissonance_edges", [])),
            "llm_status": session.get("analysis_mode", {}).get("llm_status"),
            "not_an_ethics_score": True,
        }

    @staticmethod
    def _append_ledger(
        session: Dict[str, Any],
        event_type: str,
        actor: str,
        details: Dict[str, Any],
    ) -> None:
        ledger = session.setdefault("ledger", [])
        ledger.append(
            {
                "id": f"LED-{len(ledger) + 1:04d}",
                "event_type": event_type,
                "actor": actor,
                "details": details,
                "created_at": utc_now(),
            }
        )

    @staticmethod
    def _touch(session: Dict[str, Any]) -> None:
        session["updated_at"] = utc_now()

    @staticmethod
    def _fingerprint(text: str) -> str:
        return hashlib.sha256(str(text).encode("utf-8")).hexdigest()[:16]
