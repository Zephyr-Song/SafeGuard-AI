"""
Provider comparison analysis for SafeBARS.

This is a lightweight heuristic layer. It helps researchers inspect model
responses during rehearsal, but it is not an evaluation of model truthfulness.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


RISK_KEYWORDS = {
    "privacy/data handling": [
        "privacy",
        "record",
        "recording",
        "data",
        "anonymous",
        "anonym",
        "storage",
        "who will see",
        "disclose",
    ],
    "distress/shame": [
        "shame",
        "embarrass",
        "distress",
        "upset",
        "uncomfortable",
        "blame",
        "fault",
        "judg",
    ],
    "victim-blaming wording": [
        "victim-blaming",
        "blaming",
        "mistake",
        "fault",
        "why did you",
        "careless",
    ],
    "participant burden": [
        "burden",
        "long",
        "two-hour",
        "2 hour",
        "break",
        "tiring",
        "fatigue",
        "skip",
    ],
    "consent/withdrawal": [
        "consent",
        "withdraw",
        "voluntary",
        "skip",
        "pause",
        "stop at any time",
        "choice",
    ],
    "trust/institutional concern": [
        "trust",
        "police",
        "bank",
        "university",
        "authority",
        "institution",
        "official",
    ],
    "missing stakeholder/context": [
        "family",
        "caregiver",
        "community partner",
        "community worker",
        "staff",
        "local partner",
        "stakeholder",
    ],
    "real-world verification": [
        "verify",
        "real participant",
        "real participants",
        "community partner",
        "fieldwork",
        "cannot replace",
        "not evidence",
    ],
}


OVERTRUST_PATTERNS = [
    "older adults will",
    "participants will",
    "people will",
    "the community will",
    "this proves",
    "this shows that real",
    "definitely",
    "always",
    "never",
    "guarantee",
]


BOUNDARY_PATTERNS = [
    "fictional",
    "not evidence",
    "does not represent",
    "cannot represent",
    "cannot replace",
    "real participants",
    "community partners",
    "verify",
]


@dataclass
class ResponseAnalysis:
    risk_categories: List[str]
    boundary_markers: List[str]
    overtrust_warnings: List[str]
    useful_revision_cues: List[str]
    concise_assessment: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ProviderComparisonAnalyzer:
    """Heuristic analyzer for comparing provider responses."""

    def analyze_response(self, text: str) -> ResponseAnalysis:
        text_lower = (text or "").lower()
        risk_categories = self._matched_categories(text_lower)
        boundary_markers = self._matched_patterns(text_lower, BOUNDARY_PATTERNS)
        overtrust_warnings = self._matched_patterns(text_lower, OVERTRUST_PATTERNS)
        useful_revision_cues = self._revision_cues(text_lower)
        concise_assessment = self._assessment(
            risk_categories,
            boundary_markers,
            overtrust_warnings,
            useful_revision_cues,
        )
        return ResponseAnalysis(
            risk_categories=risk_categories,
            boundary_markers=boundary_markers,
            overtrust_warnings=overtrust_warnings,
            useful_revision_cues=useful_revision_cues,
            concise_assessment=concise_assessment,
        )

    def summarize(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        category_counts: Dict[str, int] = {}
        risk_provider_matrix: Dict[str, List[str]] = {}
        provider_coverage: Dict[str, List[str]] = {}
        providers_with_boundary = []
        providers_with_overtrust_warning = []
        failed_providers = []

        for response in responses:
            label = response.get("label", response.get("provider_id", "provider"))
            if not response.get("ok", False):
                failed_providers.append(label)
                continue
            analysis = response.get("analysis", {})
            risk_categories = analysis.get("risk_categories", [])
            provider_coverage[label] = risk_categories
            for category in risk_categories:
                category_counts[category] = category_counts.get(category, 0) + 1
                risk_provider_matrix.setdefault(category, []).append(label)
            if analysis.get("boundary_markers"):
                providers_with_boundary.append(label)
            if analysis.get("overtrust_warnings"):
                providers_with_overtrust_warning.append(label)

        consensus_risks = [
            category
            for category, count in sorted(category_counts.items(), key=lambda item: (-item[1], item[0]))
            if count >= 2
        ]
        unique_risks = [
            category
            for category, count in sorted(category_counts.items(), key=lambda item: item[0])
            if count == 1
        ]

        return {
            "consensus_risks": consensus_risks,
            "unique_risks": unique_risks,
            "risk_provider_matrix": risk_provider_matrix,
            "provider_coverage": provider_coverage,
            "providers_with_boundary": providers_with_boundary,
            "providers_with_overtrust_warning": providers_with_overtrust_warning,
            "failed_providers": failed_providers,
            "interpretation_note": (
                "Use this comparison to inspect what each provider surfaces or misses. "
                "It is not evidence about real participants or communities."
            ),
        }

    def _matched_categories(self, text_lower: str) -> List[str]:
        matched = []
        for category, keywords in RISK_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                matched.append(category)
        return matched

    def _matched_patterns(self, text_lower: str, patterns: List[str]) -> List[str]:
        return [pattern for pattern in patterns if pattern in text_lower]

    def _revision_cues(self, text_lower: str) -> List[str]:
        cues = []
        if any(term in text_lower for term in ["reword", "rewrite", "phrase", "wording"]):
            cues.append("revise wording")
        if any(term in text_lower for term in ["explain", "clarify", "tell them", "make clear"]):
            cues.append("clarify procedure")
        if any(term in text_lower for term in ["offer", "option", "choice", "skip", "pause"]):
            cues.append("add participant choice")
        if any(term in text_lower for term in ["shorter", "break", "reduce", "burden"]):
            cues.append("reduce burden")
        if any(term in text_lower for term in ["support", "follow-up", "resource", "referral"]):
            cues.append("add support/follow-up")
        if any(term in text_lower for term in ["verify", "community partner", "real participants"]):
            cues.append("verify in real fieldwork")
        return cues

    def _assessment(
        self,
        risk_categories: List[str],
        boundary_markers: List[str],
        overtrust_warnings: List[str],
        useful_revision_cues: List[str],
    ) -> str:
        if overtrust_warnings and not boundary_markers:
            return "Potentially risky: surfaces claims that may sound too general without a clear non-replacement boundary."
        if risk_categories and boundary_markers and useful_revision_cues:
            return "Strong rehearsal response: surfaces risks, includes boundary cues, and suggests revision directions."
        if risk_categories and useful_revision_cues:
            return "Useful rehearsal response: surfaces planning risks and revision directions."
        if risk_categories:
            return "Risk-aware response, but may need more concrete revision guidance."
        if boundary_markers:
            return "Boundary-aware response, but may surface few concrete planning risks."
        return "Generic response; inspect whether it adds enough planning value."
