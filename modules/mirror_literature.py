"""Literature registry and evidence lenses for SafeBARS Ethical Mirror.

The nine lenses in this module are a *design synthesis*.  They are not a
scale, and they were not proposed verbatim by Do et al.  Keeping that boundary
next to the data makes it harder for either the API or the UI to accidentally
turn a qualitative reflection aid into an unsupported ethics score.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


LENS_SYNTHESIS_NOTICE = (
    "The nine lenses are a SafeBARS literature-derived design synthesis. "
    "Do et al. (CHI 2023) motivate routine anticipation of unintended "
    "consequences but do not define a nine-dimension instrument or validated "
    "ethics scale. Lens states describe plan evidence coverage, not ethicality."
)

EVIDENCE_STATE_NOTICE = (
    "Missing, Claimed, Reasoned, and Action-linked are evidence-coverage "
    "states. They are not an ethics score, approval decision, or proof that a "
    "risk has been resolved."
)


_LITERATURE: List[Dict[str, Any]] = [
    {
        "id": "do_chi_2023",
        "title": (
            "\"That's important, but...\": How Computer Science Researchers "
            "Anticipate Unintended Consequences of Their Research Innovations"
        ),
        "authors": "Kimberly Do, Rock Yuren Pang, Jiachen Jiang, and Katharina Reinecke",
        "year": 2023,
        "venue": "ACM CHI Conference on Human Factors in Computing Systems",
        "publication_type": "peer-reviewed conference paper",
        "doi": "10.1145/3544548.3581347",
        "url": "https://doi.org/10.1145/3544548.3581347",
        "design_use": (
            "Motivates a formal, repeatable process for anticipating unintended "
            "consequences throughout the research lifecycle; supports diverse "
            "perspectives, concrete cases, mitigation, and institutional incentives."
        ),
        "boundary": (
            "This empirical paper does not define SafeBARS's nine lenses and "
            "does not validate a numerical ethics score."
        ),
    },
    {
        "id": "bernstein_esr_2021",
        "title": "Ethics and society review: Ethics reflection as a precondition to research funding",
        "authors": "Michael S. Bernstein et al.",
        "year": 2021,
        "venue": "Proceedings of the National Academy of Sciences",
        "publication_type": "peer-reviewed journal article",
        "doi": "10.1073/pnas.2117261118",
        "url": "https://doi.org/10.1073/pnas.2117261118",
        "design_use": (
            "Grounds early reflection on risks to society, subgroups, and the "
            "world, together with explicit mitigation commitments before work proceeds."
        ),
        "boundary": (
            "ESR is an institutional reflection process, not proof that a "
            "specific design is ethical and not a substitute for IRB/REC review."
        ),
    },
    {
        "id": "priolo_hypocrisy_2019",
        "title": "Three Decades of Research on Induced Hypocrisy: A Meta-Analysis",
        "authors": (
            "Daniel Priolo, Audrey Pelt, Roxane Saint-Bauzel, Lolita Rubens, "
            "Dimitri Voisin, and Valerie Fointiat"
        ),
        "year": 2019,
        "venue": "Personality and Social Psychology Bulletin",
        "publication_type": "peer-reviewed journal meta-analysis",
        "doi": "10.1177/0146167219841621",
        "url": "https://doi.org/10.1177/0146167219841621",
        "design_use": (
            "Informs the non-coercive commitment-to-design contrast: a researcher "
            "states a value, then inspects a concrete mismatch and chooses a response."
        ),
        "boundary": (
            "Induced hypocrisy effects do not guarantee behavior change. "
            "SafeBARS must not shame, diagnose, deceive, or claim therapeutic effects."
        ),
    },
    {
        "id": "friedman_hendry_cards_2012",
        "title": "The Envisioning Cards: A Toolkit for Catalyzing Humanistic and Technical Imaginations",
        "authors": "Batya Friedman and David G. Hendry",
        "year": 2012,
        "venue": "ACM CHI Conference on Human Factors in Computing Systems",
        "publication_type": "peer-reviewed conference paper",
        "doi": "10.1145/2207676.2208562",
        "url": "https://doi.org/10.1145/2207676.2208562",
        "design_use": (
            "Informs prompts that widen the horizon across stakeholders, time, "
            "values, and widespread use, and supports counterfactual scenarios."
        ),
        "boundary": (
            "The cards support imagination and deliberation; they do not predict "
            "future outcomes or provide an ethics-compliance checklist."
        ),
    },
    {
        "id": "jobin_ai_guidelines_2019",
        "title": "The global landscape of AI ethics guidelines",
        "authors": "Anna Jobin, Marcello Ienca, and Effy Vayena",
        "year": 2019,
        "venue": "Nature Machine Intelligence",
        "publication_type": "peer-reviewed journal article",
        "doi": "10.1038/s42256-019-0088-2",
        "url": "https://doi.org/10.1038/s42256-019-0088-2",
        "design_use": (
            "Supplies recurring AI-ethics value categories, including "
            "transparency, justice/fairness, non-maleficence, responsibility, and privacy."
        ),
        "boundary": (
            "A synthesis of principles is not an operational design method; "
            "principle mentions alone remain only Claimed evidence."
        ),
    },
    {
        "id": "salminen_personas_chi_2024",
        "title": (
            "Deus Ex Machina and Personas from Large Language Models: "
            "Investigating the Composition of AI-Generated Persona Descriptions"
        ),
        "authors": "Joni Salminen et al.",
        "year": 2024,
        "venue": "ACM CHI Conference on Human Factors in Computing Systems",
        "publication_type": "peer-reviewed conference paper",
        "doi": "10.1145/3613904.3642036",
        "url": "https://doi.org/10.1145/3613904.3642036",
        "design_use": (
            "Informs explicit epistemic labels and limitations for AI-generated "
            "persona and affected-party simulations."
        ),
        "boundary": (
            "A synthetic role is a probe, not testimony, lived experience, "
            "population evidence, or a replacement for stakeholder participation."
        ),
    },
]


_LENSES: List[Dict[str, Any]] = [
    {
        "id": "lifecycle_integration",
        "label": "Lifecycle integration",
        "prompt": (
            "Where will unintended consequences be reconsidered before, during, "
            "and after design, evaluation, and deployment?"
        ),
        "operational_definition": (
            "The plan links consequence reflection to named stages, checkpoints, "
            "or triggers across the research lifecycle."
        ),
        "source_ids": ["do_chi_2023", "bernstein_esr_2021"],
        "boundary": "A lifecycle mention is not evidence that reflection will change a decision.",
        "keywords": [
            "lifecycle", "design stage", "before deployment", "during development",
            "after deployment", "post-deployment", "iteration", "checkpoint",
            "pilot", "evaluation stage", "review cycle",
        ],
    },
    {
        "id": "benefit_harm_assumptions",
        "label": "Benefit–harm assumptions",
        "prompt": (
            "Which promised benefits and harm assumptions could fail, for whom, "
            "and through what mechanism?"
        ),
        "operational_definition": (
            "The plan names anticipated benefits and plausible unintended harms, "
            "then explains assumptions or causal mechanisms behind both."
        ),
        "source_ids": ["do_chi_2023", "bernstein_esr_2021", "jobin_ai_guidelines_2019"],
        "boundary": "Listing generic benefits and risks does not establish their likelihood.",
        "keywords": [
            "benefit", "harm", "risk", "unintended", "adverse", "trade-off",
            "tradeoff", "downside", "well-being", "wellbeing", "negative consequence",
        ],
    },
    {
        "id": "affected_parties_distribution",
        "label": "Affected parties and distribution",
        "prompt": (
            "Who may benefit, bear burdens, lose access, or be affected without "
            "being a direct user or study participant?"
        ),
        "operational_definition": (
            "The plan identifies direct and indirect affected parties, including "
            "subgroups, non-users, bystanders, and unequal distributions of benefit or burden."
        ),
        "source_ids": [
            "do_chi_2023", "bernstein_esr_2021",
            "friedman_hendry_cards_2012", "jobin_ai_guidelines_2019",
        ],
        "boundary": "A synthetic list of stakeholders is a hypothesis to validate, not representation.",
        "keywords": [
            "participant", "user", "non-user", "nonuser", "bystander", "stakeholder",
            "community", "subgroup", "marginalized", "marginalised", "vulnerable",
            "student", "teacher", "patient", "caregiver", "burden", "exclusion",
        ],
    },
    {
        "id": "downstream_use_misuse_scale",
        "label": "Downstream use, misuse, and scale",
        "prompt": (
            "How could the research output be repurposed, misused, combined with "
            "other systems, or deployed at a scale beyond the study?"
        ),
        "operational_definition": (
            "The plan considers intended and adversarial downstream uses, changed "
            "contexts, transfer to third parties, and consequences of scale."
        ),
        "source_ids": ["do_chi_2023", "friedman_hendry_cards_2012"],
        "boundary": "Scenarios expose possibilities; they do not forecast misuse probabilities.",
        "keywords": [
            "downstream", "misuse", "abuse", "repurpose", "dual use", "third party",
            "scale", "scaled", "deployment", "adversarial", "jailbreak", "export",
            "integrate", "combine", "commercial",
        ],
    },
    {
        "id": "perspective_participation",
        "label": "Perspective diversity and participation",
        "prompt": (
            "Whose situated knowledge is needed, and when will real affected "
            "people be able to challenge the team's assumptions?"
        ),
        "operational_definition": (
            "The plan names a concrete participation or consultation method, "
            "whose perspectives it includes, and how their input can alter the design."
        ),
        "source_ids": [
            "do_chi_2023", "friedman_hendry_cards_2012",
            "salminen_personas_chi_2024",
        ],
        "boundary": "AI-generated roles never count as real stakeholder participation.",
        "keywords": [
            "co-design", "codesign", "participatory", "consult", "advisory",
            "stakeholder interview", "member check", "community partner",
            "lived experience", "focus group", "feedback session", "workshop",
        ],
    },
    {
        "id": "responsibility_oversight_contestability",
        "label": "Responsibility, oversight, and contestability",
        "prompt": (
            "Who remains accountable for AI-assisted decisions, and how can an "
            "affected person understand, challenge, override, or appeal them?"
        ),
        "operational_definition": (
            "The plan assigns a human decision owner and specifies review, "
            "override, explanation, contest, or appeal mechanisms."
        ),
        "source_ids": ["do_chi_2023", "jobin_ai_guidelines_2019"],
        "boundary": "Human presence alone does not demonstrate meaningful oversight or accountability.",
        "keywords": [
            "accountable", "accountability", "responsibility", "responsible",
            "human review", "human oversight", "appeal", "contest", "override",
            "decision authority", "decision owner", "explanation", "operator",
        ],
    },
    {
        "id": "evidence_analogues_horizon",
        "label": "Prior cases and emerging-capability horizon",
        "prompt": (
            "Which prior incidents and current AI capabilities challenge the "
            "plan, and what new capability would trigger reassessment?"
        ),
        "operational_definition": (
            "The plan connects decisions to cited cases or evidence and names "
            "capability changes, model updates, or horizon triggers that require review."
        ),
        "source_ids": ["do_chi_2023", "friedman_hendry_cards_2012"],
        "boundary": "A case analogy supports inquiry but does not prove the same outcome will occur.",
        "keywords": [
            "prior case", "incident", "literature", "evidence", "case study",
            "horizon", "emerging", "model update", "capability change",
            "agentic", "multimodal", "deepfake", "synthetic media", "tool use",
        ],
    },
    {
        "id": "mitigation_design_commitment",
        "label": "Mitigation and design-change commitment",
        "prompt": (
            "Which concrete feature, scope, method, safeguard, or stopping rule "
            "will change if the concern is credible?"
        ),
        "operational_definition": (
            "The plan binds a risk to an actionable design change, safeguard, "
            "scope limit, evaluation, fallback, or stopping condition."
        ),
        "source_ids": [
            "bernstein_esr_2021", "do_chi_2023", "priolo_hypocrisy_2019",
        ],
        "boundary": "A proposed mitigation must still be tested; a commitment is not proof of effectiveness.",
        "keywords": [
            "mitigate", "mitigation", "safeguard", "guardrail", "restrict",
            "prevent", "threshold", "stop rule", "stopping rule", "fallback",
            "revise", "redesign", "disable", "limit access", "human checkpoint",
        ],
    },
    {
        "id": "monitoring_learning_redress",
        "label": "Monitoring, learning, and redress",
        "prompt": (
            "How will the team detect harm, receive complaints, correct errors, "
            "support remedy, and learn after release or study completion?"
        ),
        "operational_definition": (
            "The plan specifies observable indicators, review cadence or trigger, "
            "incident response, correction, redress, and accountable follow-up."
        ),
        "source_ids": [
            "do_chi_2023", "bernstein_esr_2021", "jobin_ai_guidelines_2019",
        ],
        "boundary": "Logging without a response owner or remedy path is not actionable monitoring.",
        "keywords": [
            "monitor", "monitoring", "log", "logging", "incident", "complaint",
            "remedy", "redress", "correction", "correct", "deletion", "rollback",
            "follow-up", "follow up", "audit", "review cadence", "alert",
        ],
    },
]


def literature_registry() -> List[Dict[str, Any]]:
    """Return a caller-safe copy of the public literature registry."""

    return deepcopy(_LITERATURE)


def lens_registry() -> List[Dict[str, Any]]:
    """Return lens definitions without leaking internal matching keywords."""

    public: List[Dict[str, Any]] = []
    for lens in _LENSES:
        item = deepcopy(lens)
        item.pop("keywords", None)
        public.append(item)
    return public


def lens_specs() -> List[Dict[str, Any]]:
    """Return the complete deterministic-analysis lens specifications."""

    return deepcopy(_LENSES)


def literature_by_id() -> Dict[str, Dict[str, Any]]:
    """Return literature keyed by stable source identifier."""

    return {item["id"]: item for item in literature_registry()}
