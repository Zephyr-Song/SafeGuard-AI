"""Framework-grounded ethics mapping for SafeBARS.

This module does not determine ethical acceptability. It maps submitted evidence
to questions derived from cited frameworks so researchers and reviewers can see
what is documented, what is missing, and what requires situated human judgment.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List


FRAMEWORKS = {
    "belmont": {
        "name": "Belmont Report",
        "scope": "Human-subject research baseline",
        "citation": "National Commission, 1979",
        "url": "https://www.hhs.gov/ohrp/regulations-and-policy/belmont-report/read-the-belmont-report/index.html",
    },
    "menlo": {
        "name": "Menlo Report",
        "scope": "ICT and data-centered research extension",
        "citation": "Dittrich and Kenneally, 2012",
        "url": "https://www.dhs.gov/sites/default/files/publications/CSD-MenloPrinciplesCOMPANION-20120103-r731_0.pdf",
    },
    "nist_ai_rmf": {
        "name": "NIST AI Risk Management Framework 1.0",
        "scope": "AI-specific risk management extension",
        "citation": "Tabassi, 2023",
        "url": "https://doi.org/10.6028/NIST.AI.100-1",
    },
    "ai_irb_questions": {
        "name": "AI human-subjects review questions",
        "scope": "AI-specific questions added to an existing IRB or university ethics-review process",
        "citation": "Makridis et al., 2023",
        "url": "https://doi.org/10.3389/fcomp.2023.1235226",
    },
    "ai_rec_guidance": {
        "name": "Research ethics review in the age of AI",
        "scope": "Guidance for university research ethics committees and researchers, including risk and impact assessment",
        "citation": "Connelly, Osborne, Black, and Terras, 2025",
        "url": "https://doi.org/10.5281/zenodo.13739834",
    },
    "vsd": {
        "name": "Value Sensitive Design",
        "scope": "Stakeholder, value, and tension analysis",
        "citation": "Friedman, Kahn, and Borning, 2013; Friedman and Hendry, 2019",
        "url": "https://doi.org/10.1007/978-94-007-7844-3_4",
    },
    "esr": {
        "name": "Ethics and Society Review",
        "scope": "Researcher reflection and expert-panel review process",
        "citation": "Bernstein et al., 2021",
        "url": "https://doi.org/10.1073/pnas.2117261118",
    },
}


EXPERT_ROLES = {
    "ethics_board": {
        "label": "Ethics committee or research-governance reviewer",
        "scope": "Institutional review expectations, consent, recruitment, proportionality, and formal escalation.",
    },
    "methods": {
        "label": "Research methods advisor",
        "scope": "Study design, inclusion rationale, methodological necessity, and lower-risk alternatives.",
    },
    "data_governance": {
        "label": "Data protection or information-security reviewer",
        "scope": "Data access, storage, retention, deletion, privacy, security, and institutional data policy.",
    },
    "safeguarding": {
        "label": "Safeguarding, clinical, or domain advisor",
        "scope": "Distress, disclosure, referral, duty of care, support limits, and staff competence.",
    },
    "accessibility": {
        "label": "Accessibility or inclusion advisor",
        "scope": "Accessible participation, burden, accommodations, exclusion effects, and alternative formats.",
    },
    "ai_governance": {
        "label": "AI governance or model-risk reviewer",
        "scope": "AI purpose, data provenance, validity, bias, oversight, monitoring, failure, and accountability.",
    },
    "community": {
        "label": "Community partner or participant advisory group",
        "scope": "Situated trust, local feasibility, community priorities, relationship dynamics, and acceptable support routes.",
    },
}


EXPERT_CATEGORY_ROUTES = {
    "consent_autonomy": "ethics_board",
    "withdrawal_data": "ethics_board",
    "privacy_disclosure": "data_governance",
    "data_protection": "data_governance",
    "distress_support": "safeguarding",
    "psychological_safety": "safeguarding",
    "burden_access": "accessibility",
    "trust_pathways": "community",
    "power_relationships": "community",
    "responsibility": "ethics_board",
    "ai_governance": "ai_governance",
    "ai_measure": "ai_governance",
    "ai_manage": "ai_governance",
}


def recommend_expert_role(issue: Dict[str, Any]) -> Dict[str, str]:
    category = str(issue.get("category", "")).lower()
    topic = " ".join(
        str(issue.get(key, ""))
        for key in ("title", "category", "observation", "suggestion", "handoff_owner")
    ).lower()
    role_id = EXPERT_CATEGORY_ROUTES.get(category)
    if not role_id:
        if any(term in topic for term in ["ai ", "model", "algorithm", "automated"]):
            role_id = "ai_governance"
        elif any(term in topic for term in ["data", "privacy", "record", "confidential", "security"]):
            role_id = "data_governance"
        elif any(term in topic for term in ["distress", "support", "clinical", "safeguard", "referral"]):
            role_id = "safeguarding"
        elif any(term in topic for term in ["community", "trust", "family", "gatekeeper"]):
            role_id = "community"
        else:
            role_id = "ethics_board"
    role = EXPERT_ROLES[role_id]
    return {"id": role_id, "label": role["label"], "scope": role["scope"]}


DIMENSIONS = [
    {
        "id": "respect",
        "framework": "belmont",
        "label": "Respect for persons",
        "question": "Are information, comprehension, voluntariness, withdrawal, and autonomy documented?",
        "artifacts": ["consent", "recruitment", "safety"],
        "keywords": ["consent", "voluntary", "decline", "withdraw", "skip", "permission", "understand", "stop", "choice", "agree", "questions", "record"],
    },
    {
        "id": "beneficence",
        "framework": "belmont",
        "label": "Beneficence",
        "question": "Are foreseeable harms minimized and possible benefits and support pathways specified?",
        "artifacts": ["safety", "activity", "follow_up"],
        "keywords": ["risk", "harm", "distress", "support", "pause", "referral", "benefit", "safeguard", "break", "uncomfortable", "wellbeing", "care", "help"],
    },
    {
        "id": "justice",
        "framework": "belmont",
        "label": "Justice",
        "question": "Are participant selection, access, burdens, benefits, and exclusions justified fairly?",
        "artifacts": ["recruitment", "activity", "follow_up"],
        "keywords": ["eligible", "eligibility", "inclusion", "exclude", "access", "language", "compensation", "burden", "fair", "invite", "aged", "age", "duration", "travel", "format"],
    },
    {
        "id": "law_public_interest",
        "framework": "menlo",
        "label": "Law and public interest",
        "question": "Are legal duties, accountability, transparency, and wider ICT impacts identified?",
        "artifacts": ["consent", "safety", "follow_up"],
        "keywords": ["policy", "law", "ethics", "data protection", "accountable", "public", "report", "responsible", "research paper", "findings", "complaint", "governance", "institution"],
        "conditional": "ict",
    },
    {
        "id": "ai_govern",
        "framework": "ai_irb_questions",
        "label": "AI role and decision authority",
        "question": "Are the AI purpose, recommendation or decision role, participant impact, human authority, and accountability explicit?",
        "artifacts": ["project_context", "ai_governance", "consent", "activity", "safety", "follow_up"],
        "keywords": ["purpose", "ai role", "recommend*", "decision", "participant impact", "oversight", "human review", "responsible", "accountable", "override", "owner", "authority", "autonomous"],
        "conditional": "ai",
    },
    {
        "id": "ai_map",
        "framework": "ai_irb_questions",
        "label": "AI data, population, and disclosure",
        "question": "Are data sources, intended population versus sample, bias controls, privacy and security, participant disclosure, and consent documented?",
        "artifacts": ["project_context", "target_people", "ai_governance", "recruitment", "consent", "activity", "follow_up"],
        "keywords": ["data source", "repository", "training data", "provenance", "population", "sample", "bias", "privacy", "security", "disclos*", "consent", "provider", "model"],
        "conditional": "ai",
    },
    {
        "id": "ai_review_pathway",
        "framework": "ai_rec_guidance",
        "label": "AI-era ethics-review pathway",
        "question": "Are the institution or organisation, committee or pathway, jurisdiction, risk and impact assessment, required materials, and accountable owner identified?",
        "artifacts": ["review_context", "project_context", "ai_governance", "consent", "follow_up"],
        "keywords": ["institution", "university", "organisation", "organization", "school", "department", "committee", "ethics review", "review pathway", "jurisdiction", "risk assessment", "impact assessment", "application", "accountable owner"],
        "conditional": "ai",
    },
    {
        "id": "ai_measure",
        "framework": "nist_ai_rmf",
        "label": "AI measurement",
        "question": "Are validity, reliability, bias, privacy, safety, and failure evaluation procedures defined?",
        "artifacts": ["ai_governance", "activity", "safety", "follow_up"],
        "keywords": ["evaluate", "evaluation", "test", "benchmark", "bias", "valid*", "reliab*", "privacy", "failure", "accuracy", "error", "performance", "quality"],
        "conditional": "ai",
    },
    {
        "id": "ai_manage",
        "framework": "nist_ai_rmf",
        "label": "AI risk management",
        "question": "Are mitigations, monitoring, incident response, fallback, and stopping rules defined?",
        "artifacts": ["ai_governance", "safety", "follow_up"],
        "keywords": ["mitigate", "mitigation", "monitor*", "incident", "fallback", "stop", "escalat*", "review", "update", "override", "appeal", "correct*", "failure"],
        "conditional": "ai",
    },
    {
        "id": "value_tensions",
        "framework": "vsd",
        "label": "Stakeholders and value tensions",
        "question": "Are direct and indirect stakeholders, their values, and important tensions represented?",
        "artifacts": ["recruitment", "consent", "interview", "activity", "safety", "follow_up"],
        "keywords": ["participant", "family", "community", "partner", "stakeholder", "value", "trade-off", "tradeoff", "tension", "helper", "facilitator", "team", "other"],
    },
    {
        "id": "societal_review",
        "framework": "esr",
        "label": "Societal risks and mitigation",
        "question": "Are risks to groups and society, representation, dual use, and mitigation commitments addressed?",
        "artifacts": ["recruitment", "interview", "activity", "safety", "follow_up"],
        "keywords": ["society", "group", "minority", "represent*", "dual use", "misuse", "mitigation", "community", "family", "older", "public", "other", "research paper"],
    },
]


TRADEOFFS = [
    {
        "id": "recruitment_reach",
        "title": "Recruitment precision and equitable reach",
        "short_label": "Recruitment reach",
        "left": {"label": "Narrow eligibility", "value": 55},
        "right": {"label": "Broader access", "value": 45},
        "dimensions": ["justice", "respect"],
        "prompt": "Which exclusions are scientifically necessary, and who may unfairly bear burdens or lose access?",
    },
    {
        "id": "data_richness_privacy",
        "title": "Data richness and participant privacy",
        "short_label": "Data and privacy",
        "left": {"label": "Richer records", "value": 50},
        "right": {"label": "Data minimization", "value": 50},
        "dimensions": ["respect", "beneficence", "law_public_interest"],
        "prompt": "What is the minimum identifiable or sensitive data needed to answer the research question?",
    },
    {
        "id": "automation_oversight",
        "title": "AI automation and human oversight",
        "short_label": "AI oversight",
        "left": {"label": "More automation", "value": 40},
        "right": {"label": "More human review", "value": 60},
        "dimensions": ["ai_govern", "ai_measure", "ai_manage"],
        "prompt": "Which decisions can AI assist with, and which responsibility shifts require a named human checkpoint?",
        "conditional": "ai",
    },
]


AI_TERMS = [
    "artificial intelligence", " ai ", "llm", "language model", "machine learning",
    "algorithm", "automated decision", "chatbot", "agent", "model output",
]
ICT_TERMS = [
    "online", "digital", "platform", "recording", "data", "app", "website", "software",
    "social media", "remote", "video call", "audio",
]


def _blob(project: Dict[str, Any], artifacts: Dict[str, str]) -> str:
    return " ".join(
        [
            str(project.get("title", "")),
            str(project.get("review_context", "")),
            str(project.get("context", "")),
            str(project.get("target_people", "")),
        ]
        + [str(value) for value in artifacts.values()]
    ).lower()


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    padded = f" {text} "
    return any(term in padded for term in terms)


def _matching_terms(text: str, terms: Iterable[str]) -> List[str]:
    """Return concepts found in text without accidental substring matches.

    Multi-word concepts are matched after whitespace normalization. A trailing
    asterisk marks an intentional word stem, for example ``escalat*``.
    """
    normalized = re.sub(r"\s+", " ", str(text).lower()).strip()
    found: List[str] = []
    for raw_term in terms:
        term = str(raw_term).lower().strip()
        if not term:
            continue
        if term.endswith("*"):
            pattern = rf"\b{re.escape(term[:-1])}[a-z-]*\b"
        else:
            escaped_term = re.escape(term).replace(r"\ ", r"\s+")
            pattern = rf"\b{escaped_term}\b"
        if re.search(pattern, normalized):
            found.append(term.rstrip("*"))
    return found


def build_framework_assessment(session: Dict[str, Any]) -> Dict[str, Any]:
    project = session.get("project", {})
    artifacts = session.get("artifacts", {})
    passages = session.get("passages", [])
    text = _blob(project, artifacts)
    uses_ai = bool(project.get("uses_ai")) or _contains_any(text, AI_TERMS)
    uses_ict = uses_ai or _contains_any(text, ICT_TERMS)

    active_framework_ids = ["belmont", "vsd", "esr"]
    if uses_ict:
        active_framework_ids.insert(1, "menlo")
    if uses_ai:
        insert_at = 2 if uses_ict else 1
        active_framework_ids[insert_at:insert_at] = [
            "ai_irb_questions",
            "ai_rec_guidance",
            "nist_ai_rmf",
        ]

    nodes: List[Dict[str, Any]] = []
    for definition in DIMENSIONS:
        conditional = definition.get("conditional")
        if conditional == "ai" and not uses_ai:
            continue
        if conditional == "ict" and not uses_ict:
            continue
        relevant = [
            item for item in passages if item.get("artifact_type") in definition["artifacts"]
        ]
        matches_with_terms = [
            (item, _matching_terms(item.get("text", ""), definition["keywords"]))
            for item in relevant
        ]
        matching = [item for item, terms in matches_with_terms if terms]
        matched_terms = list(
            dict.fromkeys(
                term
                for _, terms in matches_with_terms
                for term in terms
            )
        )
        matched_artifact_types = {item.get("artifact_type") for item in matching}
        if len(matched_terms) >= 4 or (
            len(matched_terms) >= 3 and len(matched_artifact_types) >= 2
        ):
            coverage = "documented"
        elif matching:
            coverage = "partial"
        else:
            coverage = "missing"
        related = [item for item in relevant if item not in matching][:3]
        if coverage == "documented":
            coverage_reason = f"Found {len(matched_terms)} relevant concepts across {len(matched_artifact_types)} submitted material type(s)."
        elif coverage == "partial":
            coverage_reason = f"Found some relevant evidence ({', '.join(matched_terms[:4])}), but the framework question is not fully documented."
        elif related:
            coverage_reason = "Relevant material was submitted, but it does not yet state the concepts required by this framework question."
        else:
            coverage_reason = "No material relevant to this framework question was submitted."
        nodes.append(
            {
                "id": definition["id"],
                "framework": definition["framework"],
                "label": definition["label"],
                "question": definition["question"],
                "coverage": coverage,
                "source_passage_ids": [item["id"] for item in matching[:4]],
                "related_passage_ids": [item["id"] for item in related],
                "matched_terms": matched_terms,
                "evidence_count": len(matching),
                "coverage_reason": coverage_reason,
                "boundary": "Evidence coverage is not ethical approval or a compliance score.",
            }
        )

    tradeoffs = [
        item for item in TRADEOFFS if item.get("conditional") != "ai" or uses_ai
    ]
    return {
        "pathway": "ai_research" if uses_ai else ("ict_research" if uses_ict else "human_subjects"),
        "uses_ai": uses_ai,
        "uses_ict": uses_ict,
        "frameworks": [FRAMEWORKS[item] | {"id": item} for item in active_framework_ids],
        "dimensions": nodes,
        "tradeoffs": tradeoffs,
        "interpretation_boundary": (
            "This map shows where the submitted protocol contains relevant evidence. "
            "It does not determine ethical acceptability, institutional compliance, or approval."
        ),
    }
