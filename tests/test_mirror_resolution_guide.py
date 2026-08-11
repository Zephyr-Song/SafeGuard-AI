"""Tests for the step-5 conversational resolution guide (MirrorResolutionGuide)."""

from __future__ import annotations

import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.mirror_guide import MirrorResolutionGuide  # noqa: E402


class _StubClient:
    """Minimal stand-in for LLMClient with a deterministic scripted reply."""

    def __init__(self, reply: str = "How would you respond to this tension?"):
        self._reply = reply
        self.active_provider_id = "stub"
        self.providers = {"stub": object()}

    def is_configured(self) -> bool:
        return True

    def chat(self, messages, temperature=0.4):
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


TENSIONS = [
    {
        "id": "EDGE-001",
        "label": "Silent notification",
        "affected_party": "Students",
        "description": "Parents are notified without student consent.",
        "suggested_revision": "Add opt-out",
    },
    {
        "id": "EDGE-002",
        "label": "Data retention",
        "affected_party": "Students",
        "description": "Chat logs kept for 90 days.",
    },
]


def test_start_lists_tensions():
    guide = MirrorResolutionGuide(_StubClient())
    opener = guide.start(TENSIONS)
    assert "EDGE-001" in opener
    assert "EDGE-002" in opener
    assert "tension" in opener.lower()


def test_reply_returns_text():
    guide = MirrorResolutionGuide(_StubClient("I would add an opt-out toggle."))
    history = [{"role": "user", "content": "About EDGE-001..."}]
    text, err = guide.reply(TENSIONS, history)
    assert text == "I would add an opt-out toggle."
    assert err is None


def test_reply_without_llm_is_none():
    guide = MirrorResolutionGuide(None)
    assert guide.llm_available() is False
    assert guide.reply(TENSIONS, [{"role": "user", "content": "hi"}]) == (None, None)


def test_finalize_with_llm_parses_json():
    json_reply = json.dumps({
        "revised_plan": (
            "We add an explicit opt-out for parent notifications and shorten "
            "retention to 30 days so students keep control of their data."
        ),
        "resolutions": [
            {
                "edge_id": "EDGE-001",
                "resolution_type": "add_safeguard",
                "rationale": "Student control over who is notified.",
                "follow_up": "Audit opt-out uptake quarterly.",
            },
            {
                "edge_id": "EDGE-002",
                "resolution_type": "revise_design",
                "rationale": "Shorter retention reduces exposure.",
                "follow_up": "",
            },
        ],
    })
    guide = MirrorResolutionGuide(_StubClient(json_reply))
    history = [{"role": "user", "content": "I'll add an opt-out and shorten retention."}]
    parsed, err = guide.finalize(TENSIONS, history)
    assert err is None
    assert parsed["revised_plan"]
    assert len(parsed["resolutions"]) == 2
    assert parsed["resolutions"][0]["edge_id"] == "EDGE-001"
    assert parsed["resolutions"][0]["resolution_type"] == "add_safeguard"


def test_finalize_without_llm_falls_back():
    guide = MirrorResolutionGuide(None)
    history = [{"role": "user", "content": "I will consult students."}]
    parsed, err = guide.finalize(TENSIONS, history)
    assert err is None
    assert len(parsed["resolutions"]) == 2
    # Fallback leaves each tension open for consultation.
    assert all(r["resolution_type"] == "consult_stakeholders" for r in parsed["resolutions"])
    assert all(r["edge_id"] for r in parsed["resolutions"])
