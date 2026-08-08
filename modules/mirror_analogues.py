"""Real, citable failure cases for the SafeBARS Ethical Mirror.

These cases power improvement #2: instead of only flagging a lens as
``Missing`` (e.g. ``evidence_analogues_horizon``), the Mirror now returns a
short, *citable* reading list of systems that actually went wrong in a similar
domain. The goal is not to score the researcher but to convert an abstract
"you lack analogies" gap into "go read these three real cases".

All entries are real, peer-reviewed, or documented by regulators / reputable
press. Source URLs point to canonical landing pages (DOI, official regulator,
or Wikipedia for widely-reported events). The Mirror still labels these as
*hypothesis-generating pointers, not testimony*.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence


# Domains used both here and in mirror_audit.classify_domain_flags so that
# recommend_analogues can match a session's detected domains to cases.
_CASES: List[Dict[str, Any]] = [
    {
        "id": "obermeyer_health_bias_2019",
        "title": "Racial bias in a health-care risk-prediction algorithm",
        "year": 2019,
        "domain_tags": ["automated_decision", "sensitive_personal_data", "bias_fairness", "vulnerable_population"],
        "summary": (
            "A widely used US health-care algorithm assigned lower risk scores to "
            "Black patients than to white patients with equal illness severity, "
            "because it used health-cost history as a proxy for need."
        ),
        "lesson": (
            "A proxy variable that looks neutral can silently encode the very bias "
            "you are trying to avoid. Audit subgroup disparity, not just overall accuracy."
        ),
        "source_name": "Obermeyer et al., Science (2019)",
        "source_url": "https://www.science.org/doi/10.1126/science.aax2342",
    },
    {
        "id": "propublica_compas_2016",
        "title": "COMPAS recidivism risk scores favoured white defendants",
        "year": 2016,
        "domain_tags": ["automated_decision", "bias_fairness", "downstream_misuse", "vulnerable_population"],
        "summary": (
            "ProPublica found the COMPAS pretrial risk tool falsely flagged Black "
            "defendants as future offenders at nearly twice the rate of white defendants."
        ),
        "lesson": (
            "A risk flag is treated by downstream decision-makers as ground truth. "
            "Document false-positive and false-negative stakes before deploying any score."
        ),
        "source_name": "ProPublica, 'Machine Bias' (2016)",
        "source_url": "https://www.propublica.org/article/machine-bias-risk-assessments-in-criminal-sentencing",
    },
    {
        "id": "uk_a_levels_algorithm_2020",
        "title": "UK A-level grading algorithm unfairly downgraded students",
        "year": 2020,
        "domain_tags": ["automated_decision", "minors_students", "bias_fairness", "downstream_misuse"],
        "summary": (
            "Ofqual's statistical model replaced cancelled exams and systematically "
            "downgraded students from disadvantaged schools; it was scrapped within days."
        ),
        "lesson": (
            "When an algorithm overrides human assessment at scale, small model "
            "assumptions produce large, visible injustices and loss of public trust."
        ),
        "source_name": "2020 British educational assessment controversy (Wikipedia)",
        "source_url": "https://en.wikipedia.org/wiki/2020_British_educational_assessment_controversy",
    },
    {
        "id": "gender_shades_2018",
        "title": "Commercial facial-analysis AI was worst on women with dark skin",
        "year": 2018,
        "domain_tags": ["automated_decision", "bias_fairness", "sensitive_personal_data", "vulnerable_population"],
        "summary": (
            "Buolamwini & Gebru showed leading gender classifiers (IBM, Microsoft, "
            "Face++) had error rates up to 34% on darker-skinned women versus <1% on "
            "lighter-skinned men."
        ),
        "lesson": (
            "Benchmark on the subgroups you will actually affect. Aggregate accuracy "
            "hides discriminatory failure on the most vulnerable users."
        ),
        "source_name": "Buolamwini & Gebru, 'Gender Shades' (2018)",
        "source_url": "https://proceedings.mlr.press/v81/buolamwini18a.html",
    },
    {
        "id": "netflix_prize_reidentification_2008",
        "title": "Anonymised Netflix ratings were re-identified",
        "year": 2008,
        "domain_tags": ["sensitive_personal_data", "downstream_misuse", "vulnerable_population"],
        "summary": (
            "Narayanan & Shmatikov re-identified Netflix subscribers in the 'anonymous' "
            "prize dataset by cross-referencing the public IMDb ratings."
        ),
        "lesson": (
            "Pseudonymisation and aggregation are not anonymity. If a dataset can be "
            "joined to outside data, assume it can be re-identified."
        ),
        "source_name": "Narayanan & Shmatikov, USENIX Security (2008)",
        "source_url": "https://www.cs.utexas.edu/~shmat/shmat_netflix.pdf",
    },
    {
        "id": "google_flu_trends_2014",
        "title": "Google Flu Trends consistently over-predicted flu rates",
        "year": 2014,
        "domain_tags": ["automated_decision", "downstream_misuse", "bias_fairness"],
        "summary": (
            "The query-based flu model drifted badly because search behaviour changed "
            "for non-epidemic reasons; Lazer et al. called it a 'big data hubris' case."
        ),
        "lesson": (
            "Models drift when the world changes. Without monitoring and a human "
            "override, an over-confident model quietly becomes wrong."
        ),
        "source_name": "Lazer et al., Science (2014)",
        "source_url": "https://www.science.org/doi/10.1126/science.1248506",
    },
    {
        "id": "sweden_school_facial_recognition_2019",
        "title": "Swedish school fined for facial-recognition attendance tracking",
        "year": 2019,
        "domain_tags": ["surveillance_monitoring", "minors_students", "sensitive_personal_data", "consent_transparency"],
        "summary": (
            "Datainspektionen fined a school for using facial recognition to monitor "
            "student attendance without a valid legal basis or proper consent."
        ),
        "lesson": (
            "Monitoring students with biometrics needs a lawful basis, a DPIA, and "
            "genuine, informed consent — not just a stated efficiency goal."
        ),
        "source_name": "IAPP / Swedish DPA (2019)",
        "source_url": "https://iapp.org/news/a/sweden-dpa-fines-school-for-facial-recognition/",
    },
    {
        "id": "apple_card_gender_bias_2019",
        "title": "Apple Card offered lower limits to women",
        "year": 2019,
        "domain_tags": ["automated_decision", "bias_fairness", "downstream_misuse", "vulnerable_population"],
        "summary": (
            "Goldman Sachs' algorithm was found to give married women lower credit "
            "limits than their husbands; NYDFS investigated and required fixes."
        ),
        "lesson": (
            "Opaque scoring decisions invite discrimination claims even when no "
            "protected attribute is used directly. Keep the decision auditable."
        ),
        "source_name": "NYDFS investigation (2021)",
        "source_url": "https://www.dfs.ny.gov/reports_and_publications/press_releases/pr2021110901",
    },
    {
        "id": "microsoft_tay_2016",
        "title": "Microsoft's Tay chatbot was corrupted within a day",
        "year": 2016,
        "domain_tags": ["downstream_misuse", "automated_decision", "vulnerable_population"],
        "summary": (
            "Tay learned from public replies and was quickly turned into an offensive "
            "spewer; Microsoft pulled it within 24 hours."
        ),
        "lesson": (
            "Any system that learns from or is reachable by the public will be "
            "redirected. Build abuse resistance and a fast kill-switch before launch."
        ),
        "source_name": "Tay (bot), Wikipedia",
        "source_url": "https://en.wikipedia.org/wiki/Tay_(bot)",
    },
    {
        "id": "predpol_predictive_policing",
        "title": "Predictive-policing deployment amplified prior policing bias",
        "year": 2020,
        "domain_tags": ["surveillance_monitoring", "automated_decision", "bias_fairness", "downstream_misuse"],
        "summary": (
            "PredPol-style hotspot prediction sent patrols to areas already heavily "
            "policed, creating a feedback loop that inflated 'crime' there."
        ),
        "lesson": (
            "Predictive systems inherit and magnify the bias in their input data and "
            "deployment context. Map the feedback loop before claiming neutrality."
        ),
        "source_name": "PredPol, Wikipedia",
        "source_url": "https://en.wikipedia.org/wiki/PredPol",
    },
    {
        "id": "exam_proctoring_surveillance_2020",
        "title": "Remote exam-proctoring AI produced discriminatory false flags",
        "year": 2020,
        "domain_tags": ["surveillance_monitoring", "minors_students", "automated_decision", "vulnerable_population", "consent_transparency"],
        "summary": (
            "Students and advocates reported that automated proctoring flagged "
            "students of colour, disabled students, and those in shared homes "
            "disproportionately, while surveilling them intensely."
        ),
        "lesson": (
            "Surveillance tooling aimed at 'integrity' can punish the already "
            "marginalised. Offer a human-reviewed alternative and disclose the monitoring."
        ),
        "source_name": "EFF (2020)",
        "source_url": "https://www.eff.org/deeplinks/2020/08/proctoring-apps-subject-students-intense-surveillance-and-discriminatory-treatment",
    },
]

# Map each literature lens to the case domains it is most relevant to, so that
# a Missing lens can pull the right reading list even when domain detection is quiet.
_LENS_DOMAIN_MAP: Dict[str, List[str]] = {
    "lifecycle_integration": ["downstream_misuse", "automated_decision"],
    "benefit_harm_assumptions": ["bias_fairness", "benefit_harm", "vulnerable_population"],
    "affected_parties_distribution": ["vulnerable_population", "minors_students", "consent_transparency"],
    "downstream_use_misuse_scale": ["downstream_misuse", "surveillance_monitoring"],
    "perspective_participation": ["consent_transparency", "vulnerable_population"],
    "responsibility_oversight_contestability": ["automated_decision", "downstream_misuse"],
    "evidence_analogues_horizon": [],  # matched purely by detected domains
    "mitigation_design_commitment": ["bias_fairness", "automated_decision"],
    "monitoring_learning_redress": ["automated_decision", "surveillance_monitoring", "vulnerable_population"],
}


def get_cases() -> List[Dict[str, Any]]:
    return [dict(case) for case in _CASES]


def recommend_analogues(
    missing_lens_ids: Sequence[str],
    domain_ids: Sequence[str],
    plan: str = "",
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Return the most relevant real failure cases for a session's gaps.

    Relevance = overlap between (a) domains of the session's Missing lenses and
    detected high-risk domains and (b) each case's ``domain_tags``.
    """
    relevant_domains: set = set(domain_ids or [])
    for lens_id in missing_lens_ids or []:
        relevant_domains.update(_LENS_DOMAIN_MAP.get(lens_id, []))
    if not relevant_domains:
        # Fall back to keyword scan so the feature still helps with no domain hit.
        lowered = (plan or "").lower()
        for case in _CASES:
            if any(tag.replace("_", " ") in lowered for tag in case["domain_tags"]):
                relevant_domains.update(case["domain_tags"])

    scored: List[Dict[str, Any]] = []
    for case in _CASES:
        overlap = relevant_domains & set(case["domain_tags"])
        if overlap:
            scored.append(
                {
                    "id": case["id"],
                    "title": case["title"],
                    "year": case["year"],
                    "summary": case["summary"],
                    "lesson": case["lesson"],
                    "source_name": case["source_name"],
                    "source_url": case["source_url"],
                    "matched_tags": sorted(overlap),
                    "relevance": len(overlap),
                }
            )
    scored.sort(key=lambda item: item["relevance"], reverse=True)
    return scored[:limit]
