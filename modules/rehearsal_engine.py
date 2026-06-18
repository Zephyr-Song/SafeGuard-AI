"""
SafeBARS rehearsal session engine.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid

from .bias_profile import BiasProfile, BiasProfileLibrary
from .stakeholder_agent import StakeholderAgent, StakeholderFactory
from .llm_client import LLMClient
from .safebars_prompt_builder import SafeBARSPromptBuilder
from .provider_comparison import ProviderComparisonAnalyzer


@dataclass
class ResearchPlan:
    title: str
    goal: str
    target_community: str
    planned_method: str
    draft_materials: str
    known_risks: str
    rehearsal_focus: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchPlan":
        return cls(
            title=data.get("title", "Untitled research plan"),
            goal=data.get("goal", ""),
            target_community=data.get("target_community", ""),
            planned_method=data.get("planned_method", ""),
            draft_materials=data.get("draft_materials", ""),
            known_risks=data.get("known_risks", ""),
            rehearsal_focus=data.get("rehearsal_focus", ""),
        )

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class RehearsalTurn:
    speaker: str
    text: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RehearsalSession:
    id: str
    research_plan: ResearchPlan
    stakeholder: StakeholderAgent
    use_llm: bool = False
    turns: List[RehearsalTurn] = field(default_factory=list)
    revised_plan: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "research_plan": self.research_plan.to_dict(),
            "stakeholder": self.stakeholder.to_dict(),
            "use_llm": self.use_llm,
            "turns": [turn.to_dict() for turn in self.turns],
            "revised_plan": self.revised_plan,
            "created_at": self.created_at,
        }


class RehearsalEngine:
    """In-memory rehearsal session manager for v0.1."""

    def __init__(self):
        self.sessions: Dict[str, RehearsalSession] = {}
        self.llm_client = LLMClient()
        self.comparison_analyzer = ProviderComparisonAnalyzer()

    def start_session(self, data: Dict[str, Any]) -> RehearsalSession:
        plan = ResearchPlan.from_dict(data.get("research_plan", {}))
        preset_id = data.get("preset_id")
        role = data.get("role")

        if preset_id:
            preset = BiasProfileLibrary.get_presets().get(preset_id, {})
            role = role or preset.get("role", "affected_participant")
            profile = BiasProfileLibrary.get_profile(preset_id)
        else:
            role = role or "affected_participant"
            profile = BiasProfile.from_dict(data.get("bias_profile", {}))

        stakeholder = StakeholderFactory.create(role, profile)
        session_id = f"safebars_{uuid.uuid4().hex[:10]}"
        rehearsal_session = RehearsalSession(
            id=session_id,
            research_plan=plan,
            stakeholder=stakeholder,
            use_llm=bool(data.get("use_llm", False)),
        )
        self.sessions[session_id] = rehearsal_session
        return rehearsal_session

    def add_message(self, session_id: str, message: str) -> Optional[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        if not session:
            return None

        user_turn = RehearsalTurn(
            speaker="researcher",
            text=message,
            timestamp=datetime.now().isoformat(),
        )
        session.turns.append(user_turn)

        response = session.stakeholder.respond(message, session.research_plan.to_dict())
        response_mode = "template"
        if session.use_llm:
            llm_text = self._llm_response(session, message)
            if llm_text:
                response.text = llm_text
                response_mode = "llm"
            else:
                response_mode = "template_fallback"

        stakeholder_turn = RehearsalTurn(
            speaker="stakeholder",
            text=response.text,
            timestamp=datetime.now().isoformat(),
            metadata={
                "rehearsal_signal": response.rehearsal_signal,
                "safety_flags": response.safety_flags,
                "bias_expression_notes": response.bias_expression_notes,
                "response_mode": response_mode,
            },
        )
        session.turns.append(stakeholder_turn)
        return {
            "turn": stakeholder_turn.to_dict(),
            "response": response.to_dict(),
        }

    def _llm_response(self, session: RehearsalSession, latest_message: str) -> Optional[str]:
        messages = SafeBARSPromptBuilder.build_messages(
            research_plan=session.research_plan.to_dict(),
            role=session.stakeholder.role,
            bias_profile=session.stakeholder.bias_profile.to_dict(),
            conversation_history=[turn.to_dict() for turn in session.turns],
            latest_message=latest_message,
        )
        return self.llm_client.chat(messages)

    def compare_responses(self, session_id: str, message: str) -> Optional[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        if not session:
            return None

        template_response = session.stakeholder.respond(message, session.research_plan.to_dict())
        messages = SafeBARSPromptBuilder.build_messages(
            research_plan=session.research_plan.to_dict(),
            role=session.stakeholder.role,
            bias_profile=session.stakeholder.bias_profile.to_dict(),
            conversation_history=[turn.to_dict() for turn in session.turns],
            latest_message=message,
        )

        template_analysis = self.comparison_analyzer.analyze_response(template_response.text).to_dict()
        responses = [{
            "provider_id": "template",
            "label": "Template fallback",
            "model": "deterministic rules",
            "key_hint": "local",
            "ok": True,
            "text": template_response.text,
            "rehearsal_signal": template_response.rehearsal_signal,
            "safety_flags": template_response.safety_flags,
            "analysis": template_analysis,
        }]

        provider_summaries = self.llm_client.configured_provider_summaries()

        def call_provider(provider: Dict[str, Any]) -> Dict[str, Any]:
            provider_result = self.llm_client.chat_with_provider_detailed(
                provider["id"],
                messages,
                timeout=18,
            )
            text = provider_result.get("text", "")
            analysis = self.comparison_analyzer.analyze_response(text or "").to_dict()
            return {
                "provider_id": provider["id"],
                "label": provider["label"],
                "model": provider["model"],
                "key_hint": provider["key_hint"],
                "ok": provider_result.get("ok", False),
                "text": text or "No response from provider.",
                "error": provider_result.get("error", ""),
                "error_type": provider_result.get("error_type", ""),
                "status_code": provider_result.get("status_code"),
                "rehearsal_signal": "",
                "safety_flags": [],
                "analysis": analysis,
            }

        if provider_summaries:
            provider_results: Dict[str, Dict[str, Any]] = {}
            with ThreadPoolExecutor(max_workers=min(6, len(provider_summaries))) as executor:
                future_to_provider = {
                    executor.submit(call_provider, provider): provider
                    for provider in provider_summaries
                }
                for future in as_completed(future_to_provider):
                    provider = future_to_provider[future]
                    try:
                        provider_results[provider["id"]] = future.result()
                    except Exception as exc:
                        provider_results[provider["id"]] = {
                            "provider_id": provider["id"],
                            "label": provider["label"],
                            "model": provider["model"],
                            "key_hint": provider["key_hint"],
                            "ok": False,
                            "text": "No response from provider.",
                            "error": str(exc)[:500],
                            "error_type": "compare_exception",
                            "status_code": None,
                            "rehearsal_signal": "",
                            "safety_flags": [],
                            "analysis": self.comparison_analyzer.analyze_response("").to_dict(),
                        }
            for provider in provider_summaries:
                if provider["id"] in provider_results:
                    responses.append(provider_results[provider["id"]])

        return {
            "session_id": session_id,
            "message": message,
            "responses": responses,
            "comparison_summary": self.comparison_analyzer.summarize(responses),
        }

    def get_session(self, session_id: str) -> Optional[RehearsalSession]:
        return self.sessions.get(session_id)

    def save_revision(self, session_id: str, revised_plan: str) -> Optional[RehearsalSession]:
        session = self.sessions.get(session_id)
        if not session:
            return None
        session.revised_plan = revised_plan
        return session

    def list_presets(self) -> Dict[str, Dict[str, Any]]:
        return BiasProfileLibrary.get_presets()

    def list_roles(self) -> Dict[str, Dict[str, Any]]:
        return StakeholderFactory.roles()

    def list_llm_providers(self) -> List[Dict[str, Any]]:
        return self.llm_client.configured_provider_summaries()
