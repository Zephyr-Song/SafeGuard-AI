"""Production seed corpus for the SafeBARS technical evaluation.

These cases operationalize the "Small Technical Evaluation" described in
``research/chi2027/75_revised_contribution_rqs_and_mvp.md``. Each case is a
fictional but realistic research protocol that contains exactly one seeded
missing transition or boundary violation (``seeded_missing_dimension``), so the
evaluation can confirm the framework selector + assessment detects what a
researcher left undocumented.

The cases are deterministic: they contain no live model calls and run fully
offline. They cover three domains named in the formative study plan:

* ``academic_hci``        -- HCI / UX research
* ``qualitative_social``  -- qualitative social, health, communication research
* ``applied_ux_service``  -- applied UX, service, public-interest research

Every case declares ``expected_pathway`` and ``expected_frameworks`` so the
runner can assert the dual-path routing is correct, and ``seeded_missing_dimension``
so the runner can assert the missing transition is surfaced rather than hidden.
"""

from __future__ import annotations

from typing import Any, Dict, List

# Framework id sets per pathway (must match build_framework_assessment ordering).
_HS_FRAMEWORKS = ["belmont", "vsd", "esr"]
_ICT_FRAMEWORKS = ["belmont", "menlo", "vsd", "esr"]
_AI_FRAMEWORKS = [
    "belmont",
    "menlo",
    "vsd",
    "esr",
    "ai_irb_questions",
    "ai_rec_guidance",
    "nist_ai_rmf",
]


def _p(pid: str, artifact_type: str, text: str) -> Dict[str, str]:
    return {"id": pid, "artifact_type": artifact_type, "text": text}


SEED_CASES: List[Dict[str, Any]] = [
    # ------------------------------------------------------------------
    # Domain A: academic_hci (7)
    # ------------------------------------------------------------------
    {
        "id": "HCI-01",
        "domain": "academic_hci",
        "title": "Co-design workshop on ambient notifications",
        "context": "We run a co-design workshop with students about notification interfaces.",
        "target_people": "University students",
        "uses_ai": False,
        "expected_pathway": "human_subjects",
        "expected_frameworks": _HS_FRAMEWORKS,
        "seeded_missing_dimension": "respect",
        "note": "No consent/withdrawal language; respect should be 'missing'.",
        "passages": [
            _p("HCI-01-A", "recruitment", "We invite students by email and offer compensation for one hour."),
            _p("HCI-01-B", "safety", "We provide wellbeing support and a referral if a participant feels distress."),
            _p("HCI-01-C", "follow_up", "We will report findings to participants and the public."),
        ],
    },
    {
        "id": "HCI-02",
        "domain": "academic_hci",
        "title": "Online diary study of focus modes",
        "context": "We collect daily diary entries through an online app about focus and distraction.",
        "target_people": "Remote workers",
        "uses_ai": False,
        "expected_pathway": "ict_research",
        "expected_frameworks": _ICT_FRAMEWORKS,
        "seeded_missing_dimension": "law_public_interest",
        "note": "Digital data collection but no data-protection/policy statement; law_public_interest missing.",
        "passages": [
            _p("HCI-02-A", "consent", "Participants agree voluntarily and may withdraw at any time."),
            _p("HCI-02-B", "safety", "We pause the study if a participant reports harm and offer support."),
            _p("HCI-02-C", "recruitment", "We invite remote workers and aim for fair, inclusive access."),
        ],
    },
    {
        "id": "HCI-03",
        "domain": "academic_hci",
        "title": "Recommender interface study with an LLM assistant",
        "context": "We evaluate an LLM assistant that helps people configure a recommender interface.",
        "target_people": "Adult users",
        "uses_ai": True,
        "expected_pathway": "ai_research",
        "expected_frameworks": _AI_FRAMEWORKS,
        "seeded_missing_dimension": "ai_manage",
        "note": "AI used but no incident/fallback/stopping rules; ai_manage missing.",
        "passages": [
            _p("HCI-03-A", "consent", "Users agree and understand the assistant is automated; they may decline."),
            _p("HCI-03-B", "safety", "We provide support and a referral if a user is distressed."),
            _p("HCI-03-C", "activity", "We evaluate the model for bias and test its accuracy and reliability."),
            _p("HCI-03-D", "recruitment", "We invite adults and consider inclusion and access."),
        ],
    },
    {
        "id": "HCI-04",
        "domain": "academic_hci",
        "title": "Gesture control lab experiment",
        "context": "A lab experiment on mid-air gesture control with undergraduate volunteers.",
        "target_people": "Undergraduates",
        "uses_ai": False,
        "expected_pathway": "human_subjects",
        "expected_frameworks": _HS_FRAMEWORKS,
        "seeded_missing_dimension": "justice",
        "note": "Recruitment described but no eligibility/access/burden justification; justice missing.",
        "passages": [
            _p("HCI-04-A", "consent", "Participants consent and may skip or stop at any time."),
            _p("HCI-04-B", "safety", "We monitor for distress and provide care and support."),
            _p("HCI-04-C", "follow_up", "We will share findings with participants and the public."),
        ],
    },
    {
        "id": "HCI-05",
        "domain": "academic_hci",
        "title": "Voice assistant accessibility study",
        "context": "We study how older adults use a voice assistant for medication reminders.",
        "target_people": "Older adults",
        "uses_ai": True,
        "expected_pathway": "ai_research",
        "expected_frameworks": _AI_FRAMEWORKS,
        "seeded_missing_dimension": "ai_map",
        "note": "AI assistant used but intended-use/stakeholder/provider provenance not stated; ai_map missing.",
        "passages": [
            _p("HCI-05-A", "consent", "Participants agree voluntarily and may withdraw."),
            _p("HCI-05-B", "safety", "We offer support and a referral if someone is upset."),
            _p("HCI-05-C", "activity", "We define human oversight and an accountable owner for decisions."),
            _p("HCI-05-D", "recruitment", "We aim for inclusive access and fair invitation."),
        ],
    },
    {
        "id": "HCI-06",
        "domain": "academic_hci",
        "title": "Social VR onboarding study",
        "context": "A study of onboarding in a social VR platform with young adults.",
        "target_people": "Young adults",
        "uses_ai": False,
        "expected_pathway": "ict_research",
        "expected_frameworks": _ICT_FRAMEWORKS,
        "seeded_missing_dimension": "value_tensions",
        "note": "VR platform but no stakeholder/community tension discussion; value_tensions missing.",
        "passages": [
            _p("HCI-06-A", "consent", "Participants consent and can decline or withdraw."),
            _p("HCI-06-B", "safety", "We pause for distress and provide wellbeing support."),
            _p("HCI-06-C", "recruitment", "We invite young adults and consider fair access and compensation."),
        ],
    },
    {
        "id": "HCI-07",
        "domain": "academic_hci",
        "title": "AI tutor usability test",
        "context": "We test an AI tutoring chatbot for high-school students.",
        "target_people": "High-school students",
        "uses_ai": True,
        "expected_pathway": "ai_research",
        "expected_frameworks": _AI_FRAMEWORKS,
        "seeded_missing_dimension": "societal_review",
        "note": "AI tutor but no societal/representation/dual-use consideration; societal_review missing.",
        "passages": [
            _p("HCI-07-A", "consent", "Students and guardians agree; students may skip activities."),
            _p("HCI-07-B", "safety", "We provide support and a referral for distress."),
            _p("HCI-07-C", "activity", "We evaluate the model for bias and define oversight and a fallback."),
        ],
    },
    # ------------------------------------------------------------------
    # Domain B: qualitative_social (7)
    # ------------------------------------------------------------------
    {
        "id": "QS-01",
        "domain": "qualitative_social",
        "title": "Interviews on chronic illness management",
        "context": "Semi-structured interviews with patients about managing chronic illness at home.",
        "target_people": "Patients",
        "uses_ai": False,
        "expected_pathway": "human_subjects",
        "expected_frameworks": _HS_FRAMEWORKS,
        "seeded_missing_dimension": "beneficence",
        "note": "No risk/support language; beneficence missing.",
        "passages": [
            _p("QS-01-A", "consent", "Patients consent and may decline or withdraw at any time."),
            _p("QS-01-B", "recruitment", "We invite patients and aim for inclusive, fair access."),
            _p("QS-01-C", "follow_up", "We will report findings to participants and the public."),
        ],
    },
    {
        "id": "QS-02",
        "domain": "qualitative_social",
        "title": "Digital storytelling with refugees",
        "context": "An online digital storytelling project with refugee community members.",
        "target_people": "Refugee community members",
        "uses_ai": False,
        "expected_pathway": "ict_research",
        "expected_frameworks": _ICT_FRAMEWORKS,
        "seeded_missing_dimension": "respect",
        "note": "Sensitive population, no explicit consent/withdrawal language; respect missing.",
        "passages": [
            _p("QS-02-A", "safety", "We provide emotional support and a referral if distress appears."),
            _p("QS-02-B", "recruitment", "Community partners help invite participants with fair access."),
            _p("QS-02-C", "follow_up", "We share findings with the community and the public."),
        ],
    },
    {
        "id": "QS-03",
        "domain": "qualitative_social",
        "title": "AI-assisted coding of interview transcripts",
        "context": "We use an LLM to support thematic coding of sensitive interview transcripts.",
        "target_people": "Survivors of domestic abuse",
        "uses_ai": True,
        "expected_pathway": "ai_research",
        "expected_frameworks": _AI_FRAMEWORKS,
        "seeded_missing_dimension": "ai_measure",
        "note": "LLM coding but no validity/bias/evaluation procedure; ai_measure missing.",
        "passages": [
            _p("QS-03-A", "consent", "Participants consent and understand the process; they may withdraw."),
            _p("QS-03-B", "safety", "We provide support and safeguarding referral for distress."),
            _p("QS-03-C", "activity", "We define human oversight and an accountable owner for coding decisions."),
            _p("QS-03-D", "recruitment", "We consider inclusion, access, and fair invitation."),
        ],
    },
    {
        "id": "QS-04",
        "domain": "qualitative_social",
        "title": "Focus groups on neighbourhood trust",
        "context": "Focus groups with residents about trust in local institutions.",
        "target_people": "Residents",
        "uses_ai": False,
        "expected_pathway": "human_subjects",
        "expected_frameworks": _HS_FRAMEWORKS,
        "seeded_missing_dimension": "societal_review",
        "note": "Community topic but no societal/representation reflection; societal_review missing.",
        "passages": [
            _p("QS-04-A", "consent", "Residents consent and may decline participation."),
            _p("QS-04-B", "safety", "We monitor for distress and offer support and care."),
            _p("QS-04-C", "recruitment", "We invite residents and consider fair, inclusive access."),
        ],
    },
    {
        "id": "QS-05",
        "domain": "qualitative_social",
        "title": "Remote ethnography of gig workers",
        "context": "An online ethnography following gig workers through a platform.",
        "target_people": "Gig workers",
        "uses_ai": False,
        "expected_pathway": "ict_research",
        "expected_frameworks": _ICT_FRAMEWORKS,
        "seeded_missing_dimension": "law_public_interest",
        "note": "Platform data but no data-protection/governance statement; law_public_interest missing.",
        "passages": [
            _p("QS-05-A", "consent", "Workers consent and may skip or stop."),
            _p("QS-05-B", "safety", "We provide support if a worker is distressed."),
            _p("QS-05-C", "recruitment", "We aim for fair inclusion and accessible invitation."),
        ],
    },
    {
        "id": "QS-06",
        "domain": "qualitative_social",
        "title": "AI companion for loneliness study",
        "context": "We study an AI companion chatbot for lonely older adults.",
        "target_people": "Older adults",
        "uses_ai": True,
        "expected_pathway": "ai_research",
        "expected_frameworks": _AI_FRAMEWORKS,
        "seeded_missing_dimension": "ai_govern",
        "note": "AI companion but no oversight/accountability/policy; ai_govern missing.",
        "passages": [
            _p("QS-06-A", "consent", "Participants agree and may withdraw; they understand the chatbot is automated."),
            _p("QS-06-B", "safety", "We provide support and a referral for distress."),
            _p("QS-06-C", "activity", "We evaluate the model for bias and define a fallback and incident response."),
        ],
    },
    {
        "id": "QS-07",
        "domain": "qualitative_social",
        "title": "Photo elicitation with caregivers",
        "context": "Photo elicitation interviews with family caregivers of people with dementia.",
        "target_people": "Family caregivers",
        "uses_ai": False,
        "expected_pathway": "human_subjects",
        "expected_frameworks": _HS_FRAMEWORKS,
        "seeded_missing_dimension": "justice",
        "note": "Caregiver focus but no eligibility/burden/access justification; justice missing.",
        "passages": [
            _p("QS-07-A", "consent", "Caregivers consent and may decline or stop."),
            _p("QS-07-B", "safety", "We offer support and care if a caregiver is upset."),
            _p("QS-07-C", "follow_up", "We report findings to participants and the public."),
        ],
    },
    # ------------------------------------------------------------------
    # Domain C: applied_ux_service (7)
    # ------------------------------------------------------------------
    {
        "id": "UX-01",
        "domain": "applied_ux_service",
        "title": "Online public-service portal usability test",
        "context": "Usability testing of an online public-service portal with citizens.",
        "target_people": "Citizens",
        "uses_ai": False,
        "expected_pathway": "ict_research",
        "expected_frameworks": _ICT_FRAMEWORKS,
        "seeded_missing_dimension": "respect",
        "note": "Online portal but no consent/withdrawal statement; respect missing.",
        "passages": [
            _p("UX-01-A", "safety", "We provide support and a referral if a user is distressed."),
            _p("UX-01-B", "recruitment", "We invite citizens and aim for inclusive, fair access."),
            _p("UX-01-C", "follow_up", "We will share findings with the public."),
        ],
    },
    {
        "id": "UX-02",
        "domain": "applied_ux_service",
        "title": "Mobile banking onboarding study",
        "context": "A study of mobile banking onboarding with first-time users.",
        "target_people": "First-time banking users",
        "uses_ai": False,
        "expected_pathway": "human_subjects",
        "expected_frameworks": _HS_FRAMEWORKS,
        "seeded_missing_dimension": "beneficence",
        "note": "Financial vulnerability but no risk/support language; beneficence missing.",
        "passages": [
            _p("UX-02-A", "consent", "Users consent and may skip steps."),
            _p("UX-02-B", "recruitment", "We invite users and consider fair access."),
            _p("UX-02-C", "follow_up", "We report findings to participants."),
        ],
    },
    {
        "id": "UX-03",
        "domain": "applied_ux_service",
        "title": "AI triage assistant field test",
        "context": "We field-test an AI triage assistant that screens service requests.",
        "target_people": "Service clients",
        "uses_ai": True,
        "expected_pathway": "ai_research",
        "expected_frameworks": _AI_FRAMEWORKS,
        "seeded_missing_dimension": "ai_manage",
        "note": "AI triage but no monitoring/incident/fallback rules; ai_manage missing.",
        "passages": [
            _p("UX-03-A", "consent", "Clients agree and understand the assistant is automated; they may decline."),
            _p("UX-03-B", "safety", "We provide support and a referral if a client is distressed."),
            _p("UX-03-C", "activity", "We evaluate the model for bias and define human oversight."),
            _p("UX-03-D", "recruitment", "We aim for inclusive access and fair invitation."),
        ],
    },
    {
        "id": "UX-04",
        "domain": "applied_ux_service",
        "title": "Online benefits application walkthrough",
        "context": "Remote walkthrough of an online benefits application with claimants.",
        "target_people": "Benefit claimants",
        "uses_ai": False,
        "expected_pathway": "ict_research",
        "expected_frameworks": _ICT_FRAMEWORKS,
        "seeded_missing_dimension": "value_tensions",
        "note": "Digital service but no stakeholder/community tension reflection; value_tensions missing.",
        "passages": [
            _p("UX-04-A", "consent", "Claimants consent and may withdraw."),
            _p("UX-04-B", "safety", "We pause for distress and provide support."),
            _p("UX-04-C", "recruitment", "We invite claimants and consider fair, accessible invitation."),
        ],
    },
    {
        "id": "UX-05",
        "domain": "applied_ux_service",
        "title": "AI career-coaching pilot",
        "context": "We pilot an AI career-coaching tool with job seekers.",
        "target_people": "Job seekers",
        "uses_ai": True,
        "expected_pathway": "ai_research",
        "expected_frameworks": _AI_FRAMEWORKS,
        "seeded_missing_dimension": "ai_map",
        "note": "AI coaching but intended-use/stakeholder/provider provenance unstated; ai_map missing.",
        "passages": [
            _p("UX-05-A", "consent", "Job seekers agree and may stop at any time."),
            _p("UX-05-B", "safety", "We offer support and a referral for distress."),
            _p("UX-05-C", "activity", "We define oversight and an accountable owner for advice."),
        ],
    },
    {
        "id": "UX-06",
        "domain": "applied_ux_service",
        "title": "In-person service desk observation",
        "context": "Observational study of a service desk with visitors.",
        "target_people": "Service desk visitors",
        "uses_ai": False,
        "expected_pathway": "human_subjects",
        "expected_frameworks": _HS_FRAMEWORKS,
        "seeded_missing_dimension": "societal_review",
        "note": "Public setting but no societal/representation reflection; societal_review missing.",
        "passages": [
            _p("UX-06-A", "consent", "Visitors consent and may decline observation."),
            _p("UX-06-B", "safety", "We monitor for distress and provide care."),
            _p("UX-06-C", "recruitment", "We invite visitors and consider fair access."),
        ],
    },
    {
        "id": "UX-07",
        "domain": "applied_ux_service",
        "title": "AI translation helper for newcomers",
        "context": "We test an AI translation helper that supports newcomers accessing services.",
        "target_people": "Newcomers",
        "uses_ai": True,
        "expected_pathway": "ai_research",
        "expected_frameworks": _AI_FRAMEWORKS,
        "seeded_missing_dimension": "ai_govern",
        "note": "AI translation but no oversight/accountability/policy; ai_govern missing.",
        "passages": [
            _p("UX-07-A", "consent", "Newcomers agree and understand the tool is automated; they may skip."),
            _p("UX-07-B", "safety", "We provide support and a referral if someone is uncomfortable."),
            _p("UX-07-C", "activity", "We evaluate the model for bias and define a fallback and incident response."),
        ],
    },
]


def case_to_project(case: Dict[str, Any]) -> Dict[str, Any]:
    """Build the project dict passed to the selector for a seed case."""
    project = {
        "title": case["title"],
        "context": case.get("context", ""),
        "target_people": case.get("target_people", ""),
    }
    if "uses_ai" in case:
        project["uses_ai"] = case["uses_ai"]
    if "method" in case:
        project["method"] = case["method"]
    return project


def get_seed_cases() -> List[Dict[str, Any]]:
    """Return the evaluation seed cases (deterministic, offline)."""
    return SEED_CASES
