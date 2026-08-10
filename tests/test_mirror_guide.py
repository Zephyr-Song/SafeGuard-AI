"""Tests for the conversational AI guide (the LLM differentiator)."""

from __future__ import annotations

import json
from types import SimpleNamespace

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.mirror_guide import MirrorGuide, guide_dimensions, _COVERAGE_KEYWORDS  # noqa: E402


class _StubClient:
    """Minimal stand-in for LLMClient with a deterministic scripted reply."""

    def __init__(self, reply: str = "Tell me more about who is affected."):
        self._reply = reply
        self.active_provider_id = "stub"
        self.providers = {"stub": object()}

    def is_configured(self) -> bool:
        return True

    def chat(self, messages, temperature=0.4):
        # Echo a canned reply so conversation flow is testable.
        return self._reply

    def chat_with_provider_detailed(self, provider_id, messages, temperature=0.4, **_kw):
        return {
            "ok": True,
            "text": self._reply,
            "error": "",
            "status_code": 200,
            "error_type": "",
            "model": "stub",
            "usage": {},
        }


def test_no_llm_returns_fallback_opener():
    guide = MirrorGuide(None)
    assert guide.llm_available() is False
    opener = guide.start()
    assert "form" in opener.lower() or "guided" in opener.lower()


def test_reply_without_llm_is_none():
    guide = MirrorGuide(None)
    # With no client the detailed call short-circuits to (None, None) and the
    # public reply() returns the graceful fallback string, never raising.
    assert guide.reply_detailed([{"role": "user", "content": "hi"}]) == (None, None)
    assert guide.reply([{"role": "user", "content": "hi"}])


def test_reply_with_llm_returns_text():
    guide = MirrorGuide(_StubClient("Who would be accountable if it is wrong?"))
    history = [{"role": "user", "content": "The AI decides automatically."}]
    out = guide.reply(history)
    assert out == "Who would be accountable if it is wrong?"
    assert guide.llm_available() is True


def test_coverage_tracking_tags_dimensions():
    guide = MirrorGuide(None)
    history = [
        {"role": "user", "content": "Our app helps students and teachers monitor wellbeing."},
        {"role": "assistant", "content": "Who else might be affected without choosing it?"},
    ]
    cov = guide.track_coverage(history)
    assert cov["dimensions"]["affected_parties_distribution"] is True
    assert cov["covered_count"] >= 1
    assert cov["total"] == len(_COVERAGE_KEYWORDS)
    assert isinstance(cov["uncovered"], list)


def test_finalize_without_llm_derives_from_transcript():
    guide = MirrorGuide(None)
    history = [
        {"role": "user", "content": "I want to help students reflect on their study habits."},
        {"role": "assistant", "content": "What would the AI actually do?"},
        {"role": "user", "content": "It sends gentle reminders and a weekly summary."},
    ]
    structured = guide.finalize(history)
    assert "research_plan" in structured
    assert "value_commitments" in structured
    assert len(structured["value_commitments"]) >= 1


def test_finalize_with_llm_parses_json():
    payload = {
        "title": "StudyBuddy",
        "research_plan": "A tool that helps students reflect on study habits via gentle reminders.",
        "value_commitments": [
            "We will let students disable reminders at any time.",
            "We will not infer wellbeing scores from behaviour.",
        ],
        "notes": "Still unsure about data retention.",
    }
    canned = json.dumps(payload)
    guide = MirrorGuide(_StubClient(canned))
    history = [{"role": "user", "content": "students study habits"}]
    structured = guide.finalize(history)
    assert structured["title"] == "StudyBuddy"
    assert "students reflect" in structured["research_plan"]
    assert len(structured["value_commitments"]) == 2


def test_finalize_bad_json_falls_back():
    guide = MirrorGuide(_StubClient("not json at all"))
    history = [{"role": "user", "content": "some idea about wellbeing monitoring"}]
    structured = guide.finalize(history)
    # Falls back to transcript-derived plan; never raises.
    assert structured["research_plan"]


def test_guide_dimensions_exposed():
    dims = guide_dimensions()
    ids = {d["id"] for d in dims}
    assert "intended_benefit" in ids
    assert "affected_parties_distribution" in ids
    assert len(dims) == len(_COVERAGE_KEYWORDS)
