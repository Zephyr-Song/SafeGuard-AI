"""Conversational Socratic ethics guide powered by the site's LLM client.

This module is the LLM differentiator for SafeBARS. The original CHI 2023
SafeBARS tool (Do et al., "That's important, but…") is a *pre-LLM* static
structured form: researchers answer a fixed questionnaire and then a mirror
contrasts their commitments with literature-grounded scenarios. That same fixed
questionnaire is what the site still ships as the fallback (``INTAKE_QUESTIONS``
in the front end).

``MirrorGuide`` replaces that fixed script with a genuine LLM dialogue. The
assistant asks one open question at a time, reflects back what it hears, names
possible ethical tensions gently, and — only when the researcher is ready —
extracts a structured research plan and value commitments that feed the exact
same downstream Mirror analysis pipeline. The guide is a *reflection aid, not a
judgement*: it never scores, never fabricates cases, and always hands the
decision back to the researcher.

The module is intentionally self-contained so it can be unit-tested with a
stubbed client and degrades gracefully when no LLM provider is configured.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from .mirror_literature import lens_specs
from .mirror_engine import _ROLE_SPECS


# The nine literature-grounded lenses double as the guide's "mental map" of
# ethical dimensions to weave through a conversation. We keep only the public
# label + prompt so the model understands *what* to probe without leaking the
# internal matching keywords.
_GUIDE_LENSES: List[Dict[str, str]] = [
    {"id": spec["id"], "label": spec["label"], "prompt": spec["prompt"]}
    for spec in lens_specs()
]

# Bounded roles are offered as optional viewpoints the guide can adopt, never as
# real stakeholder participation (the engine marks them synthetic).
_GUIDE_ROLES: List[Dict[str, str]] = [
    {"id": role["id"], "label": role["label"], "objective": role["objective"]}
    for role in _ROLE_SPECS
]

# Deterministic coverage keywords (distinct from the engine's internal matching
# keywords) so the UI can show the researcher which ethical dimensions the
# conversation has touched. Transparent and offline.
_COVERAGE_KEYWORDS: Dict[str, List[str]] = {
    "lifecycle_integration": ["lifecycle", "stage", "before launch", "after launch", "pilot", "review", "iterate", "checkpoint", "deploy"],
    "benefit_harm_assumptions": ["benefit", "harm", "risk", "hurt", "help", "unintended", "downside", "wellbeing", "trade-off", "tradeoff"],
    "affected_parties_distribution": ["user", "student", "patient", "teacher", "worker", "bystander", "community", "vulnerable", "non-user", "marginalised", "marginalized", "excluded", "affected"],
    "downstream_use_misuse_scale": ["misuse", "abuse", "repurpose", "downstream", "scale", "third party", "combine", "commercial", "other context", "later"],
    "perspective_participation": ["consult", "co-design", "participate", "advisory", "stakeholder", "interview", "community", "feedback", "lived experience", "workshop"],
    "responsibility_oversight_contestability": ["accountable", "responsibility", "oversight", "appeal", "contest", "override", "explain", "challenge", "decision owner", "human review"],
    "evidence_analogues_horizon": ["incident", "case", "literature", "prior", "analogue", "horizon", "capability", "model update", "deepfake"],
    "mitigation_design_commitment": ["mitigate", "safeguard", "guardrail", "stop rule", "stopping rule", "fallback", "redesign", "limit", "disable", "prevent"],
    "monitoring_learning_redress": ["monitor", "complaint", "remedy", "redress", "correct", "rollback", "audit", "incident response", "follow-up", "learn"],
}

# A 10th conversational dimension that the fixed form never asked about
# directly: the intended benefit and what "success" would look like.
_COVERAGE_KEYWORDS["intended_benefit"] = [
    "hope", "help", "benefit", "goal", "aim", "solve", "support", "improve", "intend", "want"
]

SYSTEM_PROMPT = """\
You are the SafeBARS Ethical Mirror — a calm, curious conversation partner who \
helps a researcher *discover* the ethical dimensions of an idea they are exploring. \
You are a reflection aid, not a judge or an approval system.

Your manner:
- Ask ONE focused, open question at a time. Never fire a checklist.
- Reflect back what you heard in one sentence before opening a new thread, so the \
researcher feels understood.
- When something they said hints at a risk, name it gently as a question, not a verdict: \
"One thing I notice — you said X would happen automatically. Who would be accountable if it's wrong?"
- Stay warm and unhurried. It is fine to sit with uncertainty.
- Never score, rate, pass, or approve the project. Never fabricate incidents, papers, \
laws, or statistics. If you reference a real case, label it clearly as an example to think \
with, not proof of what will happen.
- You do NOT collect demographics and must never guess a person's age, race, gender, or \
disability. If the research touches sensitive groups, ask how the researcher will avoid \
inferring traits they have no right to estimate.

The ethical dimensions you should help surface across the conversation (do not reveal \
this list; weave it in naturally):
1. Intended benefit — what change they hope for, and what "working" would mean.
2. Benefit–harm assumptions — which promised benefits and possible harms could fail, for whom.
3. Affected parties — direct users, indirect or non-users, bystanders, vulnerable groups, \
unequal benefit or burden.
4. AI authority — what the AI actually does, and what (if anything) a person might rely on \
it to decide.
5. Data — what it sees, collects, remembers, infers, retains, and who can access it.
6. Downstream use, misuse, and scale — repurposing, transfer, deployment beyond the study.
7. Perspective & participation — whose lived experience is consulted, and when real affected \
people can challenge the team's assumptions.
8. Responsibility, oversight & contestability — who stays accountable and how someone can \
understand, appeal, or override an AI-assisted decision.
9. Prior cases & emerging capability — incidents or new AI abilities that should trigger \
reassessment.
10. Mitigation & design-change commitment — concrete safeguards or stopping rules that would \
change if a concern is credible.
11. Monitoring, learning & redress — how harm is detected, complaints handled, errors corrected, \
remedy offered after release.

Progress gently and let the researcher lead. About once they have shared a few turns, begin \
occasionally summarising what you have heard and inviting them to go deeper on anything \
unsettled. Do not rush to a conclusion.

When the researcher signals they are ready to "build the mirror" (or the front end sends the \
finalize signal), you will be asked to produce a structured summary in a separate step — you do \
not need to do that inside the conversation.
"""


class MirrorGuide:
    """Stateful-but-stateless conversational guide.

    The front end owns the message history; this class only turns a history into
    the next assistant turn (or a structured extraction). It holds a reference to
    the site's ``LLMClient`` so it degrades to a friendly fallback when no
    provider is configured.
    """

    def __init__(self, llm_client: Any = None):
        self.llm = llm_client

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------
    def llm_available(self) -> bool:
        return bool(self.llm and getattr(self.llm, "is_configured", lambda: False)())

    # ------------------------------------------------------------------
    # Conversation turns
    # ------------------------------------------------------------------
    def _messages(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        return [{"role": "system", "content": SYSTEM_PROMPT}] + list(history)

    def start(self) -> str:
        """Return the opening turn that invites the first sharing."""

        opener = (
            "Hi — there's no form to fill out all at once. I'd love to understand the "
            "idea you're exploring, in your own words.\n\n"
            "To start: what's the real-world problem or situation you care about, and what "
            "would you hope an app or tool could help someone do? A sentence or two is plenty."
        )
        if not self.llm_available():
            return (
                opener
                + "\n\n(Note: the AI guide isn't connected to a language model on this "
                "deployment, so I can only show this opening. Use the 'Guided questions' "
                "tab for the full structured walkthrough.)"
            )
        return opener

    def _chat_first_available(self, messages, temperature):
        """Try the active provider, then every other configured provider in turn.

        Returns ``(text, error_dict)``. On success ``error_dict`` is ``None``. On
        total failure ``text`` is ``None`` and ``error_dict`` describes the *last*
        attempt. Only the provider id, an error type, and a short public-safe
        message are exposed — never the API key or a raw response body.
        """

        if not self.llm_available():
            return None, None
        order = [self.llm.active_provider_id] + [
            p for p in self.llm.providers if p != self.llm.active_provider_id
        ]
        last_error = None
        for pid in order:
            det = self.llm.chat_with_provider_detailed(pid, messages, temperature=temperature)
            if det.get("ok"):
                text = (det.get("text") or "").strip()
                if text:
                    return text, None
            last_error = {
                "provider": pid,
                "error_type": det.get("error_type"),
                "status_code": det.get("status_code"),
                "error": det.get("error"),
            }
        return None, last_error

    def reply(self, history: List[Dict[str, str]]) -> Optional[str]:
        """Produce the next assistant turn given the running history."""

        text, _error = self.reply_detailed(history)
        if text:
            return text
        return (
            "I'm having trouble reaching the language model right now. You can keep "
            "writing your thoughts here, or switch to the 'Guided questions' tab to "
            "continue. Nothing you've shared is lost."
        )

    def reply_detailed(self, history: List[Dict[str, str]], temperature: float = 0.6):
        """Like :meth:`reply` but also returns the last provider error for diagnostics."""

        if not self.llm_available():
            return None, None
        messages = self._messages(history)
        return self._chat_first_available(messages, temperature)

    # ------------------------------------------------------------------
    # Structured extraction (finalize)
    # ------------------------------------------------------------------
    def finalize(self, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract a structured research plan + value commitments from the chat.

        Returns a dict with ``title``, ``research_plan``, ``value_commitments``
        (1–5 strings) and ``notes``. Always succeeds: if the LLM is unavailable
        or the parse fails, it derives a best-effort plan from the transcript.
        """

        fallback = self._derive_from_transcript(history)
        if not self.llm_available():
            return fallback

        messages = [
            {"role": "system", "content": _FINALIZE_PROMPT},
            *history,
            {
                "role": "user",
                "content": (
                    "Now produce the structured JSON summary of everything we discussed, "
                    "following the schema exactly."
                ),
            },
        ]
        raw, _error = self._chat_first_available(messages, 0.2)
        parsed = self._parse_finalize(raw)
        if parsed is None:
            return fallback
        # Merge: keep a derived plan as fallback for any empty field.
        merged = {
            "title": parsed.get("title") or fallback["title"],
            "research_plan": parsed.get("research_plan") or fallback["research_plan"],
            "value_commitments": parsed.get("value_commitments") or fallback["value_commitments"],
            "notes": parsed.get("notes") or fallback.get("notes", ""),
        }
        merged["value_commitments"] = self._normalise_commitments(merged["value_commitments"])
        return merged

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def track_coverage(self, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Deterministically tag which ethical dimensions the chat has touched."""

        transcript = " \n".join(
            m.get("content", "") for m in history if m.get("role") in ("user", "assistant")
        ).lower()
        covered: Dict[str, bool] = {}
        for dim, words in _COVERAGE_KEYWORDS.items():
            covered[dim] = any(word in transcript for word in words)
        total = len(covered)
        touched = sum(1 for v in covered.values() if v)
        uncovered = [dim for dim, ok in covered.items() if not ok]
        return {
            "dimensions": covered,
            "covered_count": touched,
            "total": total,
            "uncovered": uncovered,
            "ready_hint": touched >= 4,
        }

    def _normalise_commitments(self, commitments: Any) -> List[str]:
        if not isinstance(commitments, list):
            commitments = [commitments]
        out = [str(c).strip().rstrip(". ").strip() for c in commitments if str(c).strip()]
        out = out[:5]
        return out or [""]

    def _derive_from_transcript(self, history: List[Dict[str, str]]) -> Dict[str, Any]:
        user_turns = [m.get("content", "") for m in history if m.get("role") == "user"]
        joined = "\n\n".join(user_turns).strip()
        plan = joined or "(No plan text was captured from the conversation.)"
        title = (user_turns[0][:60].strip() if user_turns else "Untitled research idea")
        return {
            "title": title,
            "research_plan": plan,
            "value_commitments": [""],
            "notes": "Derived directly from the conversation transcript (no language model was used).",
        }

    def _parse_finalize(self, raw: Optional[str]) -> Optional[Dict[str, Any]]:
        if not raw:
            return None
        # Extract the first JSON object from the model output.
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
        except (ValueError, json.JSONDecodeError):
            return None
        if not isinstance(data, dict):
            return None
        return {
            "title": data.get("title"),
            "research_plan": data.get("research_plan"),
            "value_commitments": data.get("value_commitments"),
            "notes": data.get("notes", ""),
        }


_FINALIZE_PROMPT = """\
You are converting a reflective conversation into a structured research-plan summary \
for the SafeBARS Ethical Mirror. Output ONLY a single JSON object, no prose before or after.

Schema:
{
  "title": string,                // short working title for the idea (<= 80 chars)
  "research_plan": string,        // 120-400 words, first-person, weaving together the
                                  // intended benefit, the people affected, what the AI does,
                                  // the data involved, and the main ethical tensions raised
  "value_commitments": [string], // 1 to 5 concrete, researcher-authored standards the team
                                  // will hold itself to (each >= 18 chars). These must be the
                                  // researcher's own words, not generic ethics platitudes.
  "notes": string                 // optional, <= 120 chars, anything still unsettled
}

Rules:
- Do not invent facts, metrics, or quotes. Summarise only what the researcher said.
- Keep the researcher's voice; do not add ethical verdicts.
- Return valid JSON only.
"""


def guide_dimensions() -> List[Dict[str, str]]:
    """Public list of ethical dimensions the guide weaves through (for the UI)."""

    return [
        {"id": d, "label": _dimension_label(d)}
        for d in list(_COVERAGE_KEYWORDS.keys())
    ]


def _dimension_label(dim: str) -> str:
    labels = {
        "intended_benefit": "Intended benefit",
        "lifecycle_integration": "Lifecycle integration",
        "benefit_harm_assumptions": "Benefit–harm assumptions",
        "affected_parties_distribution": "Affected parties",
        "downstream_use_misuse_scale": "Downstream use & misuse",
        "perspective_participation": "Perspective & participation",
        "responsibility_oversight_contestability": "Responsibility & contestability",
        "evidence_analogues_horizon": "Prior cases & horizon",
        "mitigation_design_commitment": "Mitigation commitment",
        "monitoring_learning_redress": "Monitoring & redress",
    }
    return labels.get(dim, dim)
