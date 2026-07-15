"""Scenario library, stage definitions, and sample data for SafeBARS v2.

This module holds the pure-data building blocks the encounter engine routes
research artifacts against: artifact labels, the nine encounter stages, the
breakdown scenario library, priority ordering, and a sample project used by
the test-suite and quick-start demos.
"""

from __future__ import annotations

from datetime import datetime, timezone

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

