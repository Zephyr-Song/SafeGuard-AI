"""Explicit framework-path selector for SafeBARS intake.

The dual-path routing (traditional human-subjects review vs AI-assisted
research review) is the core "framework selector" contribution. The underlying
detection already lives in :mod:`modules.ethics_framework`, but it was an
implicit side effect of building the full assessment. This module turns that
decision into a transparent, inspectable, and testable component so researchers
and reviewers can see *which* ethics frameworks and expert-review roles a
protocol maps to, and *why*, before committing to a full audit.

This module does NOT determine ethical acceptability or approval. It explains
routing only.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .ethics_framework import (
    EXPERT_CATEGORY_ROUTES,
    EXPERT_ROLES,
    FRAMEWORKS,
    build_framework_assessment,
)

# Dimension id -> issue category used by the expert router in ethics_framework.
_DIMENSION_CATEGORY = {
    "respect": "consent_autonomy",
    "beneficence": "distress_support",
    "justice": "burden_access",
    "law_public_interest": "responsibility",
    "ai_govern": "ai_governance",
    "ai_map": "ai_measure",
    "ai_review_pathway": "responsibility",
    "ai_measure": "ai_measure",
    "ai_manage": "ai_manage",
    "value_tensions": "trust_pathways",
    "societal_review": "trust_pathways",
}

_PATHWAY_LABELS = {
    "human_subjects": "Traditional human-subjects research pathway",
    "ict_research": "ICT / digital research pathway",
    "ai_research": "AI-assisted research pathway",
}

# Roles that are always relevant for a pathway, before any issue-specific routing.
_PATHWAY_BASE_ROLES = {
    "human_subjects": ["ethics_board", "methods", "safeguarding", "accessibility"],
    "ict_research": ["ethics_board", "methods", "data_governance", "safeguarding", "accessibility"],
    "ai_research": [
        "ethics_board",
        "methods",
        "data_governance",
        "ai_governance",
        "safeguarding",
        "accessibility",
    ],
}


def _confidence_for(project: Dict[str, Any], uses_ai: bool, uses_ict: bool) -> Dict[str, Any]:
    """Explain how certain the pathway decision is.

    An explicit boolean declaration is high confidence; text-inferred signals
    are medium; a default fallback is low. This is a transparency signal for the
    researcher, not a compliance score.
    """
    explicit = isinstance(project.get("uses_ai"), bool)
    if explicit:
        declared = bool(project.get("uses_ai"))
        basis = (
            "Project declaration explicitly states AI use."
            if declared
            else "Project declaration explicitly states no AI use."
        )
        return {"level": "high", "score": 0.9, "basis": basis}
    if uses_ai or uses_ict:
        return {
            "level": "medium",
            "score": 0.6,
            "basis": "AI/ICT use inferred from submitted text; confirm during intake.",
        }
    return {
        "level": "low",
        "score": 0.3,
        "basis": "No AI/ICT signal detected; defaulting to traditional human-subjects pathway.",
    }


def _role_details(role_ids: Iterable[str]) -> List[Dict[str, str]]:
    return [
        {
            "id": rid,
            "label": EXPERT_ROLES[rid]["label"],
            "scope": EXPERT_ROLES[rid]["scope"],
        }
        for rid in role_ids
        if rid in EXPERT_ROLES
    ]


def select_framework_path(
    project: Dict[str, Any],
    *,
    passages: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Return an explicit framework-path selection for a submitted protocol.

    Parameters
    ----------
    project:
        Protocol description, typically ``{"title", "context", "target_people",
        "uses_ai", ...}``. If a non-dict is passed it is coerced to a minimal
        title-only project.
    passages:
        Optional list of ``{"id", "artifact_type", "text"}`` passages. When
        provided, coverage and source-passage references are included in the
        returned dimensions; when omitted, the dimensions only carry the
        framework routing.

    Returns
    -------
    dict with keys: ``pathway``, ``pathway_label``, ``uses_ai``, ``uses_ict``,
    ``confidence``, ``frameworks``, ``activated_expert_roles``, ``dimensions``,
    ``tradeoffs``, ``selection_rationale``, ``interpretation_boundary``.
    """
    if not isinstance(project, dict):
        project = {"title": str(project or ""), "context": "", "target_people": ""}

    session = {"project": project, "artifacts": {}, "passages": passages or []}
    assessment = build_framework_assessment(session)

    pathway = assessment["pathway"]
    uses_ai = assessment["uses_ai"]
    uses_ict = assessment["uses_ict"]

    activated_roles = list(_PATHWAY_BASE_ROLES.get(pathway, _PATHWAY_BASE_ROLES["human_subjects"]))
    for dim in assessment["dimensions"]:
        category = _DIMENSION_CATEGORY.get(dim["id"])
        role_id = EXPERT_CATEGORY_ROUTES.get(category) if category else None
        if role_id and role_id not in activated_roles:
            activated_roles.append(role_id)
    role_details = _role_details(activated_roles)

    confidence = _confidence_for(project, uses_ai, uses_ict)

    frameworks = [
        {
            "id": fw["id"],
            "name": fw["name"],
            "scope": fw["scope"],
            "citation": fw["citation"],
            "url": fw["url"],
        }
        for fw in assessment["frameworks"]
    ]

    rationale = (
        f"Detected pathway: {_PATHWAY_LABELS.get(pathway, pathway)}. "
        f"AI-assisted methods: {'yes' if uses_ai else 'no'}. "
        f"ICT/digital methods: {'yes' if uses_ict else 'no'}. "
        f"Activated frameworks: {', '.join(fw['name'] for fw in frameworks)}. "
        f"Recommended expert-review roles: {', '.join(r['label'] for r in role_details)}."
    )

    return {
        "pathway": pathway,
        "pathway_label": _PATHWAY_LABELS.get(pathway, pathway),
        "uses_ai": uses_ai,
        "uses_ict": uses_ict,
        "confidence": confidence,
        "frameworks": frameworks,
        "activated_expert_roles": role_details,
        "dimensions": assessment["dimensions"],
        "tradeoffs": assessment["tradeoffs"],
        "selection_rationale": rationale,
        "interpretation_boundary": assessment["interpretation_boundary"],
    }


def pathway_label(pathway: str) -> str:
    """Human-readable label for a known pathway id."""
    return _PATHWAY_LABELS.get(pathway, pathway)
