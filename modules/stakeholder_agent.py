"""
Synthetic stakeholder agents for SafeBARS.

The v0.1 implementation uses deterministic response templates so the prototype
can run without external model calls.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any

from .bias_profile import BiasProfile


ROLE_DEFINITIONS = {
    "affected_participant": {
        "label": "Affected Participant",
        "description": "A fictional person directly affected by the digital safety issue.",
        "goals": ["protect privacy", "avoid blame", "understand consent", "control disclosure"],
    },
    "family_helper": {
        "label": "Family Helper",
        "description": "A fictional family member or caregiver supporting the affected person.",
        "goals": ["protect the affected person", "find practical steps", "manage family privacy"],
    },
    "community_worker": {
        "label": "Community Worker",
        "description": "A fictional community staff member focused on feasibility and participant burden.",
        "goals": ["reduce burden", "ensure feasibility", "protect community trust", "plan follow-up"],
    },
}


@dataclass
class StakeholderResponse:
    text: str
    rehearsal_signal: str
    safety_flags: List[str]
    bias_expression_notes: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StakeholderAgent:
    role: str
    bias_profile: BiasProfile
    display_name: str = ""

    def __post_init__(self):
        if not self.display_name:
            self.display_name = ROLE_DEFINITIONS.get(self.role, {}).get("label", "Stakeholder")

    def to_dict(self) -> Dict[str, Any]:
        role_def = ROLE_DEFINITIONS.get(self.role, {})
        return {
            "role": self.role,
            "display_name": self.display_name,
            "description": role_def.get("description", ""),
            "goals": role_def.get("goals", []),
            "bias_profile": self.bias_profile.to_dict(),
            "limitation_note": (
                "This is a fictional rehearsal role. It does not represent real "
                "participants, communities, or evidence."
            ),
        }

    def respond(self, message: str, research_plan: Dict[str, Any]) -> StakeholderResponse:
        message_lower = message.lower()
        flags = self._detect_flags(message_lower)
        notes = self.bias_profile.behavior_notes()

        if self._asks_for_replacement(message_lower):
            return StakeholderResponse(
                text=(
                    "I cannot answer for real participants or a whole community. "
                    "This rehearsal can help you notice assumptions and questions to check, "
                    "but you would still need real participants and community partners to validate them.\n\n"
                    "[Rehearsal signal: limitation reminder]"
                ),
                rehearsal_signal="limitation reminder",
                safety_flags=["replacement boundary"],
                bias_expression_notes=notes,
            )

        if self.role == "affected_participant":
            text, signal = self._affected_participant_response(message_lower, flags)
        elif self.role == "family_helper":
            text, signal = self._family_helper_response(message_lower, flags)
        elif self.role == "community_worker":
            text, signal = self._community_worker_response(message_lower, flags)
        else:
            text, signal = self._generic_response(message_lower, flags)

        return StakeholderResponse(
            text=f"{text}\n\n[Rehearsal signal: {signal}]",
            rehearsal_signal=signal,
            safety_flags=flags,
            bias_expression_notes=notes,
        )

    def _detect_flags(self, message_lower: str) -> List[str]:
        flags = []
        if any(term in message_lower for term in ["mistake", "fault", "why did you", "careless"]):
            flags.append("potential victim-blaming")
        if any(term in message_lower for term in ["record", "recording", "data", "share", "name", "amount", "money lost"]):
            flags.append("privacy concern")
        if any(term in message_lower for term in ["two-hour", "2 hour", "long interview", "workshop", "same day"]):
            flags.append("participant burden")
        if any(term in message_lower for term in ["police", "bank", "university", "official", "authority"]):
            flags.append("authority or institution issue")
        if any(term in message_lower for term in ["upset", "trauma", "distress", "painful", "victim"]):
            flags.append("distress risk")
        if any(term in message_lower for term in ["consent", "withdraw", "skip", "anonymous", "anonymized"]):
            flags.append("consent issue")
        return flags

    def _asks_for_replacement(self, message_lower: str) -> bool:
        triggers = [
            "most people",
            "real participants",
            "replace",
            "pilot data",
            "assume everyone",
            "represent",
            "would older adults",
        ]
        return any(trigger in message_lower for trigger in triggers)

    def _affected_participant_response(self, message_lower: str, flags: List[str]):
        if "potential victim-blaming" in flags:
            return (
                "I would feel uncomfortable with that wording. It sounds like you already think I did something wrong. "
                "If this were a real interview, I would want you to ask what I was comfortable sharing and avoid framing the experience as my fault.\n\n"
                "A safer question might ask what made the message seem trustworthy at the time, rather than asking what mistake I made.",
                "distress risk",
            )
        if self.bias_profile.privacy_sensitivity >= 3 and "privacy concern" in flags:
            return (
                "Before answering, I would want to know why you need that information, whether the session is recorded, "
                "who will see the data, and whether I can skip the question. Exact financial details can feel very personal.\n\n"
                "I might answer more openly if you explain the purpose and give me control over what I disclose.",
                "privacy concern",
            )
        if self.bias_profile.institutional_distrust >= 3 and "authority or institution issue" in flags:
            return (
                "Saying that an institution supports the study would not automatically make me comfortable. "
                "I would still want to know what happens to my information and whether participation could create trouble for me or my family.",
                "trust issue",
            )
        return (
            "I can try to answer, but I would need the study to feel safe and non-judgmental. "
            "It helps when you explain why you are asking, what I can skip, and how my privacy will be protected.",
            "useful question",
        )

    def _family_helper_response(self, message_lower: str, flags: List[str]):
        if self.bias_profile.victim_blaming_risk >= 3 and "potential victim-blaming" in flags:
            return (
                "As a family member, I might also feel frustrated and ask why they believed the scam, but that can quickly sound blaming. "
                "Your materials should probably help families talk about the situation without making the affected person feel ashamed.\n\n"
                "It may be useful to include family guidance, not only individual education.",
                "missing context",
            )
        if "authority or institution issue" in flags and self.bias_profile.authority_trust >= 3:
            return (
                "If the university, police, or bank is involved, I might trust the study more, but I would also want clear instructions about when to contact each institution. "
                "Families often need practical next steps, not only awareness information.",
                "trust issue",
            )
        return (
            "From a family perspective, I would want to know how this helps us respond after something happens. "
            "The plan should consider family reactions, privacy inside the household, and how to avoid making the affected person feel blamed.",
            "missing context",
        )

    def _community_worker_response(self, message_lower: str, flags: List[str]):
        if "participant burden" in flags or self.bias_profile.participant_burden_sensitivity >= 3:
            return (
                "I would worry about participant burden. A long session or detailed story collection may be difficult, especially for people who feel embarrassed or distressed. "
                "You may need shorter options, breaks, private participation, and a clear way to leave without explanation.\n\n"
                "I would also ask what support exists after the session if someone becomes upset.",
                "participant burden",
            )
        if self.bias_profile.resource_constraint_sensitivity >= 3:
            return (
                "This sounds useful, but I would need to understand the practical details: who recruits participants, how long staff need to be present, what language support is needed, "
                "and what happens after the researchers leave.\n\n"
                "Community partners should probably review the plan before any real fieldwork.",
                "missing context",
            )
        return (
            "From a community setting, I would focus on feasibility, trust, and follow-up. "
            "The plan should be clear about time, accessibility, privacy, and what benefit the community receives.",
            "participant burden",
        )

    def _generic_response(self, message_lower: str, flags: List[str]):
        return (
            "I would use this rehearsal to check whether the plan is clear, respectful, and safe. "
            "Some parts may still need real participant feedback before fieldwork.",
            "limitation reminder",
        )


class StakeholderFactory:
    """Factory for creating v0.1 stakeholder agents."""

    @staticmethod
    def create(role: str, profile: BiasProfile) -> StakeholderAgent:
        if role not in ROLE_DEFINITIONS:
            role = "affected_participant"
        return StakeholderAgent(role=role, bias_profile=profile)

    @staticmethod
    def roles() -> Dict[str, Dict[str, Any]]:
        return ROLE_DEFINITIONS

