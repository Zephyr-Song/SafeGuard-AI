"""
Researcher-facing reflection dashboard for SafeBARS.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any


@dataclass
class ReflectionReport:
    session_specific_takeaways: List[str]
    concrete_rewrite_suggestions: List[str]
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
    """Heuristic reflection analysis for turning rehearsal logs into revision prompts."""

    def generate_report(self, session_data: Dict[str, Any]) -> ReflectionReport:
        plan = session_data.get("research_plan", {})
        turns = session_data.get("turns", [])
        revised_plan = session_data.get("revised_plan", "")
        stakeholder = session_data.get("stakeholder", {})
        text_blob = " ".join(
            [
                plan.get("title", ""),
                plan.get("goal", ""),
                plan.get("target_community", ""),
                plan.get("planned_method", ""),
                plan.get("draft_materials", ""),
                plan.get("known_risks", ""),
                plan.get("rehearsal_focus", ""),
                revised_plan,
            ]
            + [turn.get("text", "") for turn in turns]
        ).lower()
        flags = self._all_flags(turns)
        signals = [
            turn.get("metadata", {}).get("rehearsal_signal")
            for turn in turns
            if turn.get("metadata", {}).get("rehearsal_signal")
        ]

        missing = self._missing_stakeholders(text_blob, stakeholder.get("role", ""))
        assumptions = self._hidden_assumptions(text_blob)
        ethical = self._ethical_risks(text_blob, signals, flags)
        safety = self._safety_gaps(text_blob, signals, flags)
        burden = self._participant_burden(text_blob, signals, flags)
        takeaways = self._session_specific_takeaways(turns, flags, signals)
        concrete_revisions = self._concrete_rewrite_suggestions(text_blob, flags)
        trust = [
            "Synthetic stakeholder responses are rehearsal prompts, not evidence about real participants.",
            "Use this session to identify questions that should be verified with real participants or community partners.",
        ]
        if len(set(signals)) > 1:
            trust.append("Different rehearsal turns surfaced different signals, so avoid treating one response as the full risk picture.")
        if revised_plan:
            trust.append("Compare the initial and revised plans as evidence of researcher reflection, not as evidence about the community.")
        revisions = self._recommended_revisions(ethical, safety, burden, missing)
        fieldwork_questions = self._open_questions(missing, safety)
        evidence_notes = self._evidence_notes(turns)

        return ReflectionReport(
            session_specific_takeaways=takeaways,
            concrete_rewrite_suggestions=concrete_revisions,
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

    def _session_specific_takeaways(
        self,
        turns: List[Dict[str, Any]],
        flags: List[str],
        signals: List[str],
    ) -> List[str]:
        takeaways = []
        researcher_text = " ".join(
            turn.get("text", "")
            for turn in turns
            if turn.get("speaker") == "researcher"
        ).lower()
        stakeholder_text = " ".join(
            turn.get("text", "")
            for turn in turns
            if turn.get("speaker") == "stakeholder"
        ).lower()

        if "why you believed" in researcher_text or "why did you believe" in researcher_text:
            takeaways.append(
                "This rehearsal specifically challenged the 'why did you believe it' wording because it can sound like blame."
            )
        if "how much money" in researcher_text or "money you lost" in researcher_text or "amount" in researcher_text:
            takeaways.append(
                "This rehearsal specifically challenged exact financial-loss disclosure; the plan should make this optional or justify why it is needed."
            )
        if "record" in researcher_text or "recording" in researcher_text:
            takeaways.append(
                "This rehearsal surfaced recording/data-use as a trust issue; participants need choices and clear access boundaries before sensitive questions."
            )
        if "speak over" in researcher_text or "convince" in researcher_text or "autonomy concern" in flags:
            takeaways.append(
                "This rehearsal focused on autonomy: family helpers should not become the voice of the affected older adult."
            )
        if "support resource gap" in flags or "follow-up" in researcher_text or "referral" in researcher_text:
            takeaways.append(
                "This rehearsal focused on after-session responsibility: the plan needs realistic support, referral, and follow-up procedures."
            )
        if "not sure what you're asking" in stakeholder_text or "need more context" in stakeholder_text:
            takeaways.append(
                "The stakeholder response suggests the prompt itself was underspecified; the researcher should ask one focused question at a time."
            )
        if "participant burden" in signals or "two-hour" in researcher_text or "2 hour" in researcher_text:
            takeaways.append(
                "This rehearsal surfaced burden concerns; session length, story-sharing, and activity load may need to be reduced."
            )
        if not takeaways and turns:
            takeaways.append(
                "This session did not surface a strong specific risk yet; ask a more concrete question about wording, consent, recording, distress, or follow-up."
            )
        if not turns:
            takeaways.append(
                "No rehearsal turn has been recorded yet; send at least one concrete question before generating the report."
            )
        return takeaways[:5]

    def _concrete_rewrite_suggestions(self, text: str, flags: List[str]) -> List[str]:
        suggestions = []
        if "why did you believe" in text or "why you believed" in text or "potential victim-blaming" in flags:
            suggestions.append(
                "Replace 'Why did you believe the message?' with 'What made the message seem trustworthy at the time, and what warning signs became clearer later?'"
            )
        if "how much money" in text or "money you lost" in text or "amount" in text:
            suggestions.append(
                "Replace 'How much money did you lose?' with 'You may skip financial details. If useful, you can share a rough range or describe the impact in your own words.'"
            )
        if "record" in text or "recording" in text or "privacy concern" in flags:
            suggestions.append(
                "Before recording, add: 'Recording is optional. You can participate without being recorded, stop recording at any time, and ask us not to include any part of your response.'"
            )
        if "autonomy concern" in flags:
            suggestions.append(
                "For family-helper interviews, add a separate consent boundary: 'Please describe your own support role, but do not answer on behalf of the older adult unless they explicitly agree.'"
            )
        if "support resource gap" in flags:
            suggestions.append(
                "Add a safety step: 'If a participant becomes distressed or reveals an active scam, pause the activity and offer a prepared referral/resource list.'"
            )
        if "participant burden" in flags or "two-hour" in text or "2 hour" in text:
            suggestions.append(
                "Offer a shorter version of the session, breaks, and a no-story-sharing option for participants who do not want to disclose personal experiences."
            )
        if not suggestions:
            suggestions.append(
                "Ask a more targeted rehearsal question to generate a concrete rewrite, such as: 'Does this consent script make recording and withdrawal clear?'"
            )
        return suggestions[:6]

    def _all_flags(self, turns: List[Dict[str, Any]]) -> List[str]:
        flags = []
        for turn in turns:
            flags.extend(turn.get("metadata", {}).get("safety_flags", []))
        return sorted(set(flags))

    def _evidence_notes(self, turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        notes = []
        latest_researcher_prompt = ""
        for turn in turns:
            if turn.get("speaker") == "researcher":
                latest_researcher_prompt = turn.get("text", "").replace("\n", " ").strip()
                continue
            if turn.get("speaker") != "stakeholder":
                continue
            metadata = turn.get("metadata", {})
            signal = metadata.get("rehearsal_signal")
            flags = metadata.get("safety_flags", [])
            if not signal or signal in ["none", "useful question"] and not flags:
                continue
            text = turn.get("text", "").replace("\n", " ").strip()
            notes.append({
                "signal": signal,
                "flags": flags,
                "quote": self._short_quote(text),
                "interpretation": self._interpret_signal(signal, flags, latest_researcher_prompt),
            })
        return notes[:8]

    def _short_quote(self, text: str) -> str:
        marker = "[Rehearsal signal:"
        if marker in text:
            text = text.split(marker)[0].strip()
        if len(text) <= 220:
            return text
        return text[:217].rstrip() + "..."

    def _interpret_signal(self, signal: str, flags: List[str], researcher_prompt: str = "") -> str:
        prompt = researcher_prompt.lower()
        if "potential victim-blaming" in flags:
            return "The researcher prompt may make responsibility or judgment too salient; revise toward context, trust cues, and optional disclosure."
        if "privacy concern" in flags:
            return "The prompt asks for sensitive information or mentions data/recording; clarify purpose, access, anonymization, and skip options."
        if "support resource gap" in flags:
            return "The plan needs a concrete after-session support or referral path before promising help."
        if "autonomy concern" in flags:
            return "The plan should protect the affected person's voice and consent boundaries, especially when family helpers are involved."
        if "participant burden" in flags:
            return "The planned activity may be too long or intensive; consider shorter formats, breaks, or lower-disclosure alternatives."
        if "consent issue" in flags:
            return "The plan should make consent, withdrawal, anonymity, and recording choices more explicit."
        if "authority or institution issue" in flags:
            return "The plan may assume institutional endorsement creates trust; explain consequences, reporting paths, and data boundaries."
        if "how much" in prompt or "money" in prompt:
            return "Exact financial loss may not be necessary; make it optional or ask for ranges/examples only if justified."
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

    def _missing_stakeholders(self, text: str, role: str) -> List[str]:
        missing = []
        fraud_context = any(term in text for term in ["fraud", "scam", "older adult", "online safety"])
        if fraud_context and role != "family_helper" and "family" not in text and "caregiver" not in text:
            missing.append("Consider whether family helpers or caregivers shape disclosure and help-seeking.")
        if fraud_context and role != "community_worker" and "community worker" not in text and "staff" not in text and "local partner" not in text:
            missing.append("Consider involving a community worker or local partner before fieldwork.")
        if fraud_context and "platform" not in text and "bank" not in text and "police" not in text and "report" not in text:
            missing.append("Consider whether platform, bank, or authority stakeholders affect reporting pathways.")
        return missing

    def _hidden_assumptions(self, text: str) -> List[str]:
        assumptions = []
        if "why did you believe" in text or "why you believed" in text:
            assumptions.append("The plan may assume participants can explain scam belief without feeling blamed or embarrassed.")
        if "how much money" in text or "exact" in text or "amount" in text:
            assumptions.append("The plan may assume exact financial disclosure is necessary, even when a range or optional disclosure may be safer.")
        if "teach" in text or "educate" in text:
            assumptions.append("The plan may assume the main problem is lack of knowledge rather than trust, shame, or support barriers.")
        if "should" in text or "must" in text:
            assumptions.append("Directive language may assume participants can act on advice without social or practical constraints.")
        if "workshop" in text and "follow-up" not in text:
            assumptions.append("The plan may assume a one-time workshop is enough without follow-up support.")
        if "record" in text and "optional" not in text and "anonymous" not in text and "anonymized" not in text:
            assumptions.append("The plan may assume recording is acceptable without first giving participants meaningful choices.")
        return assumptions

    def _ethical_risks(self, text: str, signals: List[str], flags: List[str]) -> List[str]:
        risks = []
        if "potential victim-blaming" in flags or "mistake" in text or "fault" in text or "why did you believe" in text:
            risks.append("Some wording may sound victim-blaming; use neutral language about context and decision points.")
        if "privacy concern" in signals or "privacy concern" in flags or "record" in text or "data" in text or "money" in text:
            risks.append("Privacy and data-use explanation needs to be explicit before sensitive disclosure.")
        if "distress risk" in signals or "distress risk" in flags or "victim" in text or "loss" in text or "embarrass" in text:
            risks.append("Discussion of harm or financial loss may create distress and should include skip/pause options.")
        if "autonomy concern" in flags:
            risks.append("Family-helper involvement may create autonomy risks if helpers speak for or pressure the affected person.")
        if "authority or institution issue" in flags:
            risks.append("Institutional reporting or endorsement may affect trust and should not be presented as automatically safe.")
        return risks

    def _safety_gaps(self, text: str, signals: List[str], flags: List[str]) -> List[str]:
        gaps = []
        sensitive_topic = any(term in text for term in ["loss", "money", "victim", "distress", "record", "story", "fraud", "scam"])
        if sensitive_topic and "skip" not in text and "withdraw" not in text and "pause" not in text:
            gaps.append("Add explicit skip, pause, and withdrawal options.")
        if ("support resource gap" in flags or "distress risk" in flags or "workshop" in text) and "resource" not in text and "support" not in text and "follow-up" not in text:
            gaps.append("Add support resources or follow-up procedures for participants who become distressed.")
        if ("record" in text or "data" in text or "privacy concern" in flags) and "consent" not in text:
            gaps.append("Clarify consent language, recording choices, and data boundaries.")
        if "authority or institution issue" in flags and "reporting path" not in text:
            gaps.append("Clarify what happens if a participant reports an active scam or asks for institutional help.")
        return gaps

    def _participant_burden(self, text: str, signals: List[str], flags: List[str]) -> List[str]:
        items = []
        if "participant burden" in signals or "participant burden" in flags or "two-hour" in text or "2 hour" in text:
            items.append("Session length or activity load may be too high for sensitive topics.")
        if "detailed stories" in text or "exact" in text or "how much money" in text:
            items.append("Detailed disclosure may not be necessary and may increase burden.")
        if "same day" in text:
            items.append("Combining interview and workshop on the same day may be too intense for sensitive disclosure.")
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
