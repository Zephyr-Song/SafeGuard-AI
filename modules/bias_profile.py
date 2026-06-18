"""
Bias and risk-response profiles for SafeBARS.

The values are functional rehearsal controls, not psychological measures.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any


CORE_DIMENSIONS = [
    "authority_trust",
    "confirmation_bias",
    "urgency_sensitivity",
    "shame_stigma_sensitivity",
    "institutional_distrust",
    "social_proof_susceptibility",
    "help_seeking_reluctance",
    "privacy_sensitivity",
    "distress_sensitivity",
]


@dataclass
class BiasProfile:
    """A 0-4 functional risk-response profile for a synthetic stakeholder."""

    authority_trust: int = 2
    confirmation_bias: int = 2
    urgency_sensitivity: int = 2
    shame_stigma_sensitivity: int = 2
    institutional_distrust: int = 2
    social_proof_susceptibility: int = 2
    help_seeking_reluctance: int = 2
    privacy_sensitivity: int = 2
    distress_sensitivity: int = 2
    victim_blaming_risk: int = 0
    resource_constraint_sensitivity: int = 0
    participant_burden_sensitivity: int = 0
    institutional_defensiveness: int = 0
    research_fatigue: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BiasProfile":
        values = {}
        for field in cls.__dataclass_fields__:
            raw = data.get(field, getattr(cls(), field))
            values[field] = cls._clamp(raw)
        return cls(**values)

    @staticmethod
    def _clamp(value: Any) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = 2
        return max(0, min(4, parsed))

    def to_dict(self) -> Dict[str, int]:
        return asdict(self)

    def high_dimensions(self, threshold: int = 3) -> Dict[str, int]:
        return {k: v for k, v in self.to_dict().items() if v >= threshold}

    def behavior_notes(self) -> Dict[str, str]:
        """Return short behavior notes for prompt/debug display."""
        notes = {}
        if self.authority_trust >= 3:
            notes["authority_trust"] = "likely to defer to official or expert sources"
        if self.shame_stigma_sensitivity >= 3:
            notes["shame_stigma_sensitivity"] = "hesitant around blame, embarrassment, and personal loss"
        if self.institutional_distrust >= 3:
            notes["institutional_distrust"] = "skeptical of universities, platforms, police, or banks"
        if self.help_seeking_reluctance >= 3:
            notes["help_seeking_reluctance"] = "reluctant to report harm or seek support"
        if self.privacy_sensitivity >= 3:
            notes["privacy_sensitivity"] = "asks about recording, storage, anonymity, and data access"
        if self.distress_sensitivity >= 3:
            notes["distress_sensitivity"] = "may need pauses, skip options, or support resources"
        if self.resource_constraint_sensitivity >= 3:
            notes["resource_constraint_sensitivity"] = "emphasizes staffing, time, and feasibility"
        if self.participant_burden_sensitivity >= 3:
            notes["participant_burden_sensitivity"] = "raises burden, accessibility, and follow-up concerns"
        if self.victim_blaming_risk >= 3:
            notes["victim_blaming_risk"] = "may unintentionally frame responsibility as individual failure"
        return notes


class BiasProfileLibrary:
    """Preset profiles used by the v0.1 prototype."""

    PRESETS = {
        "affected_high_privacy": {
            "label": "Affected participant: high privacy and stigma",
            "role": "affected_participant",
            "profile": {
                "authority_trust": 1,
                "confirmation_bias": 2,
                "urgency_sensitivity": 2,
                "shame_stigma_sensitivity": 4,
                "institutional_distrust": 3,
                "social_proof_susceptibility": 2,
                "help_seeking_reluctance": 3,
                "privacy_sensitivity": 4,
                "distress_sensitivity": 3,
            },
        },
        "family_helper_protective": {
            "label": "Family helper: protective and urgent",
            "role": "family_helper",
            "profile": {
                "authority_trust": 3,
                "confirmation_bias": 2,
                "urgency_sensitivity": 3,
                "shame_stigma_sensitivity": 2,
                "institutional_distrust": 1,
                "social_proof_susceptibility": 3,
                "help_seeking_reluctance": 1,
                "privacy_sensitivity": 2,
                "distress_sensitivity": 2,
                "victim_blaming_risk": 3,
            },
        },
        "community_worker_feasibility": {
            "label": "Community worker: feasibility and burden",
            "role": "community_worker",
            "profile": {
                "authority_trust": 2,
                "confirmation_bias": 1,
                "urgency_sensitivity": 2,
                "shame_stigma_sensitivity": 2,
                "institutional_distrust": 2,
                "social_proof_susceptibility": 2,
                "help_seeking_reluctance": 1,
                "privacy_sensitivity": 3,
                "distress_sensitivity": 3,
                "resource_constraint_sensitivity": 4,
                "participant_burden_sensitivity": 4,
            },
        },
    }

    @classmethod
    def get_presets(cls) -> Dict[str, Dict[str, Any]]:
        return cls.PRESETS

    @classmethod
    def get_profile(cls, preset_id: str) -> BiasProfile:
        preset = cls.PRESETS.get(preset_id, cls.PRESETS["affected_high_privacy"])
        return BiasProfile.from_dict(preset["profile"])

