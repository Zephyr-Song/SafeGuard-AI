"""
Researcher-facing reflection dashboard for SafeBARS.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any


@dataclass
class ReflectionReport:
    missing_stakeholders: List[str]
    hidden_assumptions: List[str]
    ethical_risks: List[str]
    safety_gaps: List[str]
    participant_burden: List[str]
    trust_calibration_notes: List[str]
    recommended_revisions: List[str]
    open_questions_for_real_fieldwork: List[str]
    evidence_notes: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ReflectionDashboard:
    """Heuristic v0.1 reflection analysis."""

    def generate_report(self, session_data: Dict[str, Any]) -> ReflectionReport:
        plan = session_data.get("research_plan", {})
        turns = session_data.get("turns", [])
        revised_plan = session_data.get("revised_plan", "")
        text_blob = " ".join(
            [plan.get("draft_materials", ""), plan.get("known_risks", ""), revised_plan]
            + [turn.get("text", "") for turn in turns]
        ).lower()
        signals = [
            turn.get("metadata", {}).get("rehearsal_signal")
            for turn in turns
            if turn.get("metadata", {}).get("rehearsal_signal")
        ]

        missing = self._missing_stakeholders(text_blob)
        assumptions = self._hidden_assumptions(text_blob)
        ethical = self._ethical_risks(text_blob, signals)
        safety = self._safety_gaps(text_blob, signals)
        burden = self._participant_burden(text_blob, signals)
        trust = [
            "Synthetic stakeholder responses are rehearsal prompts, not evidence about real participants.",
            "Use this session to identify questions that should be verified with real participants or community partners.",
        ]
        if revised_plan:
            trust.append("Compare the initial and revised plans as evidence of researcher reflection, not as evidence about the community.")
        revisions = self._recommended_revisions(ethical, safety, burden, missing)
        fieldwork_questions = self._open_questions(missing, safety)
        evidence_notes = self._evidence_notes(turns)

        return ReflectionReport(
            missing_stakeholders=missing,
            hidden_assumptions=assumptions,
            ethical_risks=ethical,
            safety_gaps=safety,
            participant_burden=burden,
            trust_calibration_notes=trust,
            recommended_revisions=revisions,
            open_questions_for_real_fieldwork=fieldwork_questions,
            evidence_notes=evidence_notes,
        )

    def _evidence_notes(self, turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        notes = []
        for turn in turns:
            if turn.get("speaker") != "stakeholder":
                continue
            metadata = turn.get("metadata", {})
            signal = metadata.get("rehearsal_signal")
            flags = metadata.get("safety_flags", [])
            if not signal or signal == "none":
                continue
            text = turn.get("text", "").replace("\n", " ").strip()
            notes.append({
                "signal": signal,
                "flags": flags,
                "quote": self._short_quote(text),
                "interpretation": self._interpret_signal(signal, flags),
            })
        return notes[:8]

    def _short_quote(self, text: str) -> str:
        marker = "[Rehearsal signal:"
        if marker in text:
            text = text.split(marker)[0].strip()
        if len(text) <= 220:
            return text
        return text[:217].rstrip() + "..."

    def _interpret_signal(self, signal: str, flags: List[str]) -> str:
        if signal == "privacy concern":
            return "The plan may need clearer recording, data access, anonymization, or disclosure boundaries."
        if signal == "distress risk":
            return "The wording or topic may need a less blaming framing and clearer pause/skip options."
        if signal == "participant burden":
            return "The planned session may be too long, intense, or demanding for sensitive fieldwork."
        if signal == "missing context":
            return "The plan may be missing a stakeholder relationship, practical constraint, or social context."
        if signal == "trust issue":
            return "Institutional support alone may not create trust; data use and consequences need explanation."
        if signal == "unclear consent":
            return "Consent, withdrawal, or recording choices may need to be explained more clearly."
        if signal == "limitation reminder":
            return "This is a reminder to verify assumptions with real participants or community partners."
        if flags:
            return f"Review flagged issues: {', '.join(flags)}."
        return "Review this moment as a possible planning signal."

    def _missing_stakeholders(self, text: str) -> List[str]:
        missing = []
        if "family" not in text and "caregiver" not in text:
            missing.append("Consider whether family helpers or caregivers shape disclosure and help-seeking.")
        if "community" not in text and "staff" not in text and "worker" not in text:
            missing.append("Consider involving a community worker or local partner before fieldwork.")
        if "platform" not in text and "bank" not in text and "police" not in text:
            missing.append("Consider whether platform, bank, or authority stakeholders affect reporting pathways.")
        return missing

    def _hidden_assumptions(self, text: str) -> List[str]:
        assumptions = []
        if "teach" in text or "educate" in text:
            assumptions.append("The plan may assume the main problem is lack of knowledge rather than trust, shame, or support barriers.")
        if "should" in text or "must" in text:
            assumptions.append("Directive language may assume participants can act on advice without social or practical constraints.")
        if "workshop" in text and "follow-up" not in text:
            assumptions.append("The plan may assume a one-time workshop is enough without follow-up support.")
        return assumptions

    def _ethical_risks(self, text: str, signals: List[str]) -> List[str]:
        risks = []
        if "mistake" in text or "fault" in text:
            risks.append("Some wording may sound victim-blaming; use neutral language about context and decision points.")
        if "privacy concern" in signals or "record" in text or "data" in text:
            risks.append("Privacy and data-use explanation needs to be explicit before sensitive disclosure.")
        if "distress risk" in signals or "victim" in text or "loss" in text:
            risks.append("Discussion of harm or financial loss may create distress and should include skip/pause options.")
        return risks

    def _safety_gaps(self, text: str, signals: List[str]) -> List[str]:
        gaps = []
        if "skip" not in text and "withdraw" not in text:
            gaps.append("Add explicit skip, pause, and withdrawal options.")
        if "resource" not in text and "support" not in text and "follow-up" not in text:
            gaps.append("Add support resources or follow-up procedures for participants who become distressed.")
        if "consent" not in text:
            gaps.append("Clarify consent language, recording choices, and data boundaries.")
        return gaps

    def _participant_burden(self, text: str, signals: List[str]) -> List[str]:
        items = []
        if "participant burden" in signals or "two-hour" in text or "2 hour" in text:
            items.append("Session length or activity load may be too high for sensitive topics.")
        if "detailed stories" in text or "exact" in text:
            items.append("Detailed disclosure may not be necessary and may increase burden.")
        return items

    def _recommended_revisions(
        self,
        ethical: List[str],
        safety: List[str],
        burden: List[str],
        missing: List[str],
    ) -> List[str]:
        revisions = []
        if ethical:
            revisions.append("Rewrite sensitive questions to avoid blame and explain why each detail is needed.")
        if safety:
            revisions.append("Add a safety script covering consent, skip options, pause options, withdrawal, and support resources.")
        if burden:
            revisions.append("Shorten the session or offer lower-burden alternatives for sensitive disclosure.")
        if missing:
            revisions.append("Create a stakeholder map and decide which real stakeholders should review the plan.")
        if not revisions:
            revisions.append("Use the rehearsal transcript to identify what still needs verification with real participants.")
        return revisions

    def _open_questions(self, missing: List[str], safety: List[str]) -> List[str]:
        questions = [
            "Which assumptions from this rehearsal need to be checked with real participants?",
            "What community partner should review the plan before recruitment?",
        ]
        if missing:
            questions.append("Which missing stakeholders could change the design of recruitment, consent, or follow-up?")
        if safety:
            questions.append("What concrete resources are available if a participant becomes distressed?")
        return questions
