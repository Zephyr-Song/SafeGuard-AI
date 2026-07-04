"""Configurable application-draft profiles and submission-readiness checks.

These profiles are scaffolds, not replicas of any institution's current form.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


APPLICATION_PROFILES: Dict[str, Dict[str, Any]] = {
    "generic_human_research": {
        "label": "Generic human-research application",
        "description": "A portable core structure that must be mapped to the institution's current form.",
        "official": False,
        "ai_extension": False,
    },
    "generic_ai_research": {
        "label": "Generic AI-enabled human-research application",
        "description": "The human-research core plus AI role, oversight, data, failure, and redress prompts.",
        "official": False,
        "ai_extension": True,
    },
}


CORE_FIELDS = [
    {
        "id": "project_title",
        "label": "Project title",
        "sources": [("project", "title")],
        "minimum_chars": 5,
        "prompt": "Give the study a specific working title.",
    },
    {
        "id": "purpose_context",
        "label": "Purpose, setting, and method",
        "sources": [("project", "context")],
        "minimum_chars": 80,
        "prompt": "Explain the research question, setting, method, and why human participation is needed.",
    },
    {
        "id": "participants_relationships",
        "label": "Participants and affected relationships",
        "sources": [("project", "target_people")],
        "minimum_chars": 50,
        "prompt": "Identify direct and indirect stakeholders, helpers, gatekeepers, and power relationships.",
    },
    {
        "id": "recruitment_selection",
        "label": "Recruitment, eligibility, and compensation",
        "sources": [("artifacts", "recruitment")],
        "minimum_chars": 100,
        "prompt": "Document contact, eligibility, gatekeepers, compensation, fair access, and pressure safeguards.",
    },
    {
        "id": "consent_withdrawal",
        "label": "Consent, recording, and withdrawal",
        "sources": [("artifacts", "consent")],
        "minimum_chars": 120,
        "prompt": "Cover comprehension, voluntariness, recordings, skipping, withdrawal stages, and contacts.",
    },
    {
        "id": "procedures",
        "label": "Research procedures and participant activities",
        "sources": [("artifacts", "interview"), ("artifacts", "activity")],
        "minimum_chars": 120,
        "prompt": "Describe questions, tasks, duration, locations, technologies, breaks, and alternatives.",
    },
    {
        "id": "risk_safeguarding",
        "label": "Risk, safeguarding, and support",
        "sources": [("artifacts", "safety")],
        "minimum_chars": 120,
        "prompt": "Name foreseeable harms, triggers, responsible staff, stop rules, escalation limits, and support.",
    },
    {
        "id": "data_confidentiality",
        "label": "Data management and confidentiality",
        "sources": [("artifacts", "follow_up")],
        "minimum_chars": 140,
        "keywords": ["access", "retention", "delete", "storage", "confidential"],
        "prompt": "Specify data types, access, transfer, storage, security, retention, deletion, quotations, and reporting.",
    },
    {
        "id": "debrief_follow_up",
        "label": "Debrief, follow-up, and complaints",
        "sources": [("artifacts", "follow_up"), ("artifacts", "safety")],
        "minimum_chars": 100,
        "keywords": ["debrief", "follow", "support", "complaint", "contact"],
        "prompt": "Explain debriefing, follow-up, support, complaints, and how participants can contact the team.",
    },
]


AI_FIELDS = [
    {
        "id": "ai_role_disclosure",
        "label": "AI role and participant disclosure",
        "sources": [("project", "context"), ("artifacts", "consent")],
        "minimum_chars": 100,
        "keywords": ["ai", "model", "algorithm", "automated"],
        "prompt": "Explain where AI is used, what participants are told, and which outputs may affect them.",
    },
    {
        "id": "ai_human_oversight",
        "label": "Human oversight and decision authority",
        "sources": [("artifacts", "activity"), ("artifacts", "safety"), ("artifacts", "follow_up")],
        "minimum_chars": 100,
        "keywords": ["human", "review", "override", "responsible", "approval"],
        "prompt": "Name who reviews, overrides, pauses, and remains accountable for AI-supported actions.",
    },
    {
        "id": "ai_data_model_governance",
        "label": "AI data and model governance",
        "sources": [("artifacts", "follow_up"), ("artifacts", "consent")],
        "minimum_chars": 120,
        "keywords": ["training", "provider", "model", "retention", "access", "data"],
        "prompt": "Describe provider access, training use, prompts/outputs, model version, retention, security, and monitoring.",
    },
    {
        "id": "ai_failure_redress",
        "label": "AI failure, contestability, and redress",
        "sources": [("artifacts", "safety"), ("artifacts", "follow_up")],
        "minimum_chars": 100,
        "keywords": ["error", "failure", "appeal", "contest", "complaint", "correct"],
        "prompt": "Define foreseeable failures, detection, fallback, correction, explanation, complaints, and redress.",
    },
]


def _source_value(session: Dict[str, Any], path: Iterable[str]) -> str:
    value: Any = session
    for key in path:
        if not isinstance(value, dict):
            return ""
        value = value.get(key, "")
    return str(value or "").strip()


def _assess_field(session: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
    evidence: List[Dict[str, str]] = []
    for group, key in spec["sources"]:
        value = _source_value(session, (group, key))
        if value:
            evidence.append({"source": f"{group}.{key}", "text": value})
    combined = "\n".join(item["text"] for item in evidence)
    found_keywords = [
        keyword for keyword in spec.get("keywords", [])
        if keyword in combined.lower()
    ]
    if not combined:
        status = "missing"
    elif len(combined) < spec["minimum_chars"]:
        status = "partial"
    elif spec.get("keywords") and len(found_keywords) < min(2, len(spec["keywords"])):
        status = "partial"
    else:
        status = "documented"
    return {
        "id": spec["id"],
        "label": spec["label"],
        "status": status,
        "prompt": spec["prompt"],
        "evidence": evidence,
        "character_count": len(combined),
        "minimum_chars": spec["minimum_chars"],
        "found_keywords": found_keywords,
    }


def select_application_profile(session: Dict[str, Any]) -> str:
    requested = session.get("application_profile_id")
    if requested in APPLICATION_PROFILES:
        return requested
    uses_ai = bool(
        session.get("project", {}).get("uses_ai")
        or session.get("framework_assessment", {}).get("uses_ai")
    )
    return "generic_ai_research" if uses_ai else "generic_human_research"


def build_application_readiness(session: Dict[str, Any]) -> Dict[str, Any]:
    profile_id = select_application_profile(session)
    profile = APPLICATION_PROFILES[profile_id]
    specs = CORE_FIELDS + (AI_FIELDS if profile["ai_extension"] else [])
    fields = [_assess_field(session, spec) for spec in specs]
    counts = {status: sum(item["status"] == status for item in fields) for status in ("documented", "partial", "missing")}
    unresolved = [
        item for item in session.get("handoffs", [])
        if item.get("status") != "resolved"
    ]
    return {
        "profile_id": profile_id,
        "profile": profile,
        "fields": fields,
        "counts": counts,
        "completion_percent": round(100 * counts["documented"] / len(fields)) if fields else 0,
        "unresolved_handoff_count": len(unresolved),
        "submission_ready": counts["missing"] == 0 and counts["partial"] == 0 and not unresolved,
        "boundary": (
            "This is a completeness check for a generic draft, not an ethics verdict. "
            "Map it to the institution's current form and obtain formal approval before recruitment or data collection."
        ),
    }
