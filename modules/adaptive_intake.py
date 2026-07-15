"""Adaptive guided-intake question engine for SafeBARS.

This module is the single source of truth for the conversational protocol
intake described in ``research/chi2027/80_adaptive_intake_and_export_architecture.md``.

The frontend loads the question schema from this engine (via the
``POST /api/safebars/v2/adaptive-intake/plan`` endpoint) instead of hardcoding
it, so the intake is versioned, server-validated, and reproducible. Keeping the
selection logic here also lets the "adaptive" behaviour be unit-tested offline,
which matters for the CHI 2027 reproducibility contribution.

The design is deliberately faithful to doc 80:

* six core questions, always asked;
* one conditional follow-up (AI governance) when AI use is declared or detected
  in the project description.

The engine is intentionally extensible: additional conditional follow-ups can be
added by extending ``_CONDITIONAL_STEPS`` and the signal logic in
``build_intake_plan`` without touching the frontend.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

# --- AI detection -----------------------------------------------------------
# Kept consistent with the legacy client-side heuristic in safebars_v2.html so
# that the server and the browser never disagree about whether a project is
# "AI".
_AI_TERMS = re.compile(
    r"\b(ai|artificial intelligence|llm|language model|machine learning|"
    r"algorithmic|automated model)\b",
    re.IGNORECASE,
)
_NO_AI_TERMS = re.compile(
    r"\b(no ai|without ai|does not use ai|do not use ai|not using ai)\b",
    re.IGNORECASE,
)


def detect_ai_use(text: str) -> bool:
    """Return ``True`` when the text declares or implies AI use.

    Mirrors the browser heuristic: an explicit "no AI" phrase suppresses the
    detection even when AI terminology is otherwise present.
    """
    normalized = text or ""
    if _NO_AI_TERMS.search(normalized):
        return False
    return bool(_AI_TERMS.search(normalized))


# --- Question schema --------------------------------------------------------
# Each entry matches the field names the frontend already consumes
# (id, question, hint, min, target, sections, appendTarget, detectAi), so the
# server schema drops straight into the existing intake UI.
CORE_INTAKE_STEPS: List[Dict[str, Any]] = [
    {
        "id": "context",
        "target": "projectContext",
        "question": "What are you studying, where and how will the research happen, and does AI play any role?",
        "hint": "Include the aim, setting, method, why human participation is needed, and either describe the AI role or write 'No AI'.",
        "min": 30,
        "detectAi": True,
    },
    {
        "id": "people_recruitment",
        "question": "Who is involved and how will participants be recruited?",
        "hint": "Use two lines if possible:\nPeople/relationships: participants, helpers, gatekeepers, affected communities.\nRecruitment: contact, eligibility, compensation, and pressure safeguards.",
        "min": 30,
        "sections": [
            {"target": "targetPeople", "labels": ["people", "participants", "relationships"]},
            {"target": "artifactRecruitment", "labels": ["recruitment", "eligibility", "contact"]},
        ],
    },
    {
        "id": "consent",
        "target": "artifactConsent",
        "question": "What information and choices will participants receive before agreeing?",
        "hint": "Cover comprehension, voluntariness, recording, data use, skipping, withdrawal stages, and a contact for questions.",
        "min": 25,
    },
    {
        "id": "procedures",
        "question": "What will participants be asked and what will they do?",
        "hint": "Use two sections if possible:\nQuestions/prompts: sensitive or decision-relevant questions.\nActivities: tasks, duration, technologies, breaks, accessibility, and alternatives.",
        "min": 30,
        "sections": [
            {"target": "artifactInterview", "labels": ["questions", "prompts", "interview"]},
            {"target": "artifactActivity", "labels": ["activities", "activity", "tasks", "procedures"]},
        ],
    },
    {
        "id": "safety",
        "target": "artifactSafety",
        "question": "What happens if there is distress, unexpected disclosure, privacy loss, or another safeguarding concern?",
        "hint": "Name triggers, pause or stop actions, responsible staff, escalation limits, and real support routes.",
        "min": 25,
    },
    {
        "id": "follow_up",
        "target": "artifactFollowUp",
        "question": "What happens after participation and to the research data?",
        "hint": "Cover debriefing, complaints, follow-up, access, storage, security, retention, deletion, reporting, and withdrawal after collection.",
        "min": 30,
    },
]

AI_GOVERNANCE_STEP: Dict[str, Any] = {
    "id": "ai_governance",
    "appendTarget": "projectContext",
    "question": "Because this project uses AI, what needs human oversight and what happens when the AI is wrong?",
    "hint": "Describe the model/provider, prompts or outputs, participant disclosure, human review and override, data/training use, monitoring, fallback, correction, and complaints.",
    "min": 30,
}

# Conditional follow-ups keyed by a stable signal id. Extend here to add more
# adaptive branches without changing the frontend.
_CONDITIONAL_STEPS: Dict[str, Dict[str, Any]] = {
    "ai": AI_GOVERNANCE_STEP,
}


def build_intake_plan(project: Dict[str, Any]) -> Dict[str, Any]:
    """Return the adaptive intake plan for a project description.

    Parameters
    ----------
    project:
        Mapping with optional keys ``title``, ``context``, ``target_people``,
        and ``uses_ai``. Any of them may be missing.

    Returns
    -------
    dict with keys:
        ``core`` (list of the six always-asked questions),
        ``conditional`` (list of follow-ups triggered by detected signals),
        ``uses_ai_detected`` (bool, heuristic result from the text),
        ``rationale`` (human-readable reason for the conditional set).
    """
    title = str(project.get("title", "") or "")
    context = str(project.get("context", "") or "")
    people = str(project.get("target_people", "") or "")
    uses_ai = bool(project.get("uses_ai", False))

    text_blob = f"{title}\n{context}\n{people}"
    ai_detected = detect_ai_use(text_blob)

    conditional: List[Dict[str, Any]] = []
    if uses_ai or ai_detected:
        conditional.append(_CONDITIONAL_STEPS["ai"])

    if conditional:
        rationale = (
            "AI governance follow-up included because AI use was declared or "
            "detected in the project description."
        )
    else:
        rationale = "No AI signals; only the six core questions are required."

    return {
        "core": CORE_INTAKE_STEPS,
        "conditional": conditional,
        "uses_ai_detected": ai_detected,
        "rationale": rationale,
    }
