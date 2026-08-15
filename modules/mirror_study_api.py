"""Flask Blueprint for the StressLens CHI 2027 study.

This is intentionally separate from the main SafeBARS Ethical Mirror API so
that the experimental intervention can be versioned and analysed independently.
"""

from __future__ import annotations

import json
import os
import random
from typing import Any, Dict, Tuple

from flask import Blueprint, current_app, jsonify, request, url_for

from .mirror_study_data import (
    CONDITIONS,
    FIXES,
    ISSUE_GALLERY,
    SHARED_VIGNETTE,
    classify_issue,
    public_config,
)
from .mirror_study_store import MirrorStudyStore
from .ratelimit import rate_limit
from .llm_client import LLMClient


mirror_study_api = Blueprint(
    "safebars_mirror_study",
    __name__,
    url_prefix="/api/safebars/mirror-study",
)

mirror_study_store = MirrorStudyStore()

# AI analysis client (mirrors the transition-companion architecture: a server-side
# endpoint proxies an LLM and returns structured JSON the front end renders).
_LLM: Any = None


def _get_llm() -> Any:
    global _LLM
    if _LLM is None:
        _LLM = LLMClient()
    return _LLM


# Image ids the AI is allowed to pick from (keeps the visual grounded in the
# curated, paper-ready illustration set rather than generating images on the fly).
_IMAGE_IDS = [item["id"] for item in ISSUE_GALLERY if item["id"] != "default"]
_IMAGE_BY_ID = {item["id"]: item for item in ISSUE_GALLERY}

_ANALYZE_SYSTEM = (
    "You are Mirror, an ethical-research companion for the SafeBARS StressLens study. "
    "A graduate researcher will describe a real ethical concern from their own AI/ML research. "
    "Your job is to help them reflect, not to judge their design. Respond with ONLY a JSON "
    "object (no markdown, no code fences) using exactly these keys:\n"
    "- summary: one warm, non-judgemental sentence that acknowledges the concern\n"
    "- reflection: 2-3 sentences that surface the key ethical tension(s) and why they "
    "matter for someone designing an ethics protocol\n"
    "- theme_label: a short 3-8 word label for the concern\n"
    "- suggested_image_id: the id from this list that BEST matches the concern: "
    f"{', '.join(_IMAGE_IDS)}\n"
    "- related_concerns: an array of exactly 3 short concern phrases (4-8 words each), "
    "each a DIFFERENT facet the researcher might also want to consider\n"
    "- ethical_dimensions: an array of 2-4 short ethical-dimension labels (2-4 words each) "
    "that apply to this concern\n"
    "Be concise, specific and genuinely useful. Never invent an image id outside the list."
)


def _extract_json(text: str) -> Any:
    """Best-effort JSON extraction from an LLM response."""
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```", 2)
        if len(parts) >= 2:
            text = parts[1]
            if text.lower().startswith("json"):
                text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except Exception:
        return None


def _normalize_analysis(data: Dict[str, Any], issue: str) -> Dict[str, Any]:
    suggested = data.get("suggested_image_id")
    if suggested not in _IMAGE_BY_ID:
        suggested = classify_issue(issue)["id"]
    theme = _IMAGE_BY_ID.get(suggested, ISSUE_GALLERY[-1])
    related = [str(x).strip() for x in data.get("related_concerns", []) if str(x).strip()][:3]
    dims = [str(x).strip() for x in data.get("ethical_dimensions", []) if str(x).strip()][:4]
    return {
        "issue": issue,
        "summary": str(data.get("summary", "")).strip()[:400],
        "reflection": str(data.get("reflection", "")).strip()[:1200],
        "theme_label": str(data.get("theme_label", theme["label"])).strip()[:120],
        "theme_id": theme["id"],
        "image_url": _image_url(theme["image"]),
        "related_concerns": related,
        "ethical_dimensions": dims,
    }


def _fallback_analysis(issue: str) -> Dict[str, Any]:
    theme = classify_issue(issue)
    others = [t["label"] for t in ISSUE_GALLERY if t["id"] not in (theme["id"], "default")]
    return {
        "issue": issue,
        "summary": "Thanks for sharing that — it is worth thinking through carefully.",
        "reflection": theme["reflection"],
        "theme_label": theme["label"],
        "theme_id": theme["id"],
        "image_url": _image_url(theme["image"]),
        "related_concerns": others[:3],
        "ethical_dimensions": [],
    }


def _call_deepseek(api_key: str, issue: str) -> Dict[str, Any]:
    """Direct OpenAI-compatible DeepSeek call (mirrors the Transition Companion)."""
    import requests

    base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    resp = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": _ANALYZE_SYSTEM},
                {"role": "user", "content": f"Researcher's concern: {issue}"},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.4,
            "max_tokens": 600,
        },
        timeout=40,
    )
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"]
    data = _extract_json(text)
    if not data or not data.get("reflection") or not isinstance(data.get("related_concerns"), list):
        raise ValueError("DeepSeek returned an incomplete response")
    return _normalize_analysis(data, issue)


def _analyze_with_llm(issue: str) -> Dict[str, Any]:
    """Call an LLM and return a normalized analysis, or None on any failure.

    Prefers a dedicated DeepSeek key (matching the Transition Companion prototype),
    then falls back to the shared multi-provider SafeBARS client.
    """
    ds_key = os.getenv("DEEPSEEK_API_KEY")
    if ds_key:
        try:
            return _call_deepseek(ds_key, issue)
        except Exception:
            current_app.logger.exception("Mirror /analyze DeepSeek call failed")
    llm = _get_llm()
    if llm and llm.is_configured():
        try:
            resp = llm.chat(
                [
                    {"role": "system", "content": _ANALYZE_SYSTEM},
                    {"role": "user", "content": f"Researcher's concern: {issue}"},
                ],
                temperature=0.4,
            )
            data = _extract_json(resp) if resp else None
            if data and data.get("reflection") and isinstance(data.get("related_concerns"), list):
                return _normalize_analysis(data, issue)
        except Exception:
            current_app.logger.exception("Mirror /analyze LLM call failed")
    return None


def _json_object() -> Tuple[Dict[str, Any], Any]:
    payload = request.get_json(silent=True)
    if payload is None:
        return {}, None
    if not isinstance(payload, dict):
        return {}, (
            jsonify({"success": False, "error": "Request body must be a JSON object."}),
            400,
        )
    return payload, None


def _image_url(path: str) -> str:
    """Resolve a static image path to an absolute URL."""
    return url_for("static", filename=path, _external=False)


def _condition_with_urls(condition: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of a condition with image URLs resolved."""
    out = {**condition}
    out["frames"] = [
        {**frame, "image_url": _image_url(frame["image"])}
        for frame in condition.get("frames", [])
    ]
    return out


def _fixes_with_urls() -> List[Dict[str, Any]]:
    return [{**fix, "image_url": _image_url(fix["image"])} for fix in FIXES]


def _issue_gallery_with_urls() -> List[Dict[str, Any]]:
    return [{**item, "image_url": _image_url(item["image"])} for item in ISSUE_GALLERY]


@mirror_study_api.get("/config")
def get_config():
    """Return the public vignette, conditions, fixes and issue gallery with URLs."""
    cfg = public_config()
    cfg["conditions"] = {
        k: _condition_with_urls(v) for k, v in cfg["conditions"].items()
    }
    cfg["fixes"] = _fixes_with_urls()
    cfg["issue_gallery"] = _issue_gallery_with_urls()
    return jsonify({"success": True, **cfg})


@mirror_study_api.post("/issue-image")
@rate_limit(max_requests=10, window_seconds=60, scope="mirror_study_issue_image")
def issue_image():
    """Map a user-supplied issue to a generated AI illustration.

    Body:
      {"issue": "free-text description of the ethical concern"}

    Response:
      {
        "success": true,
        "theme_id": "...",
        "theme_label": "...",
        "image_url": "...",
        "reflection": "...",
        "matched_issue": "user text"
      }

    The mapping is deterministic and reproducible, matching issue keywords to
    curated AI-generated themes.  This satisfies the CHI 2027 expectation that
    each participant's own issue is reflected back as a concrete visual.
    """
    payload, error = _json_object()
    if error:
        return error

    issue = payload.get("issue", "").strip()
    if not issue:
        return jsonify({"success": False, "error": "'issue' text is required."}), 400

    if len(issue) > 2000:
        return jsonify({"success": False, "error": "Issue text is too long (max 2000 chars)."}), 400

    theme = classify_issue(issue)
    return jsonify({
        "success": True,
        "theme_id": theme["id"],
        "theme_label": theme["label"],
        "image_url": _image_url(theme["image"]),
        "reflection": theme["reflection"],
        "matched_issue": issue,
    })


@mirror_study_api.post("/analyze")
@rate_limit(max_requests=15, window_seconds=60, scope="mirror_study_analyze")
def analyze():
    """AI-analyse a researcher's free-text concern and return structured content.

    This mirrors the transition-companion architecture: the server proxies an LLM
    and returns structured JSON (reflection, theme, related concerns, ethical
    dimensions) that the front end renders. When no LLM key is configured it
    degrades gracefully to the deterministic classifier so the study still works.

    Body: {"issue": "free-text description of the ethical concern"}
    Response: {"success": true, "source": "ai"|"fallback", "theme_label", ...}
    """
    payload, error = _json_object()
    if error:
        return error

    issue = (payload.get("issue") or "").strip()
    if not issue:
        return jsonify({"success": False, "error": "'issue' text is required."}), 400
    if len(issue) > 2000:
        return jsonify({"success": False, "error": "Issue text is too long (max 2000 chars)."}), 400

    analysis = _analyze_with_llm(issue)
    source = "ai" if analysis is not None else "fallback"
    if analysis is None:
        analysis = _fallback_analysis(issue)

    llm = _get_llm()
    return jsonify({
        "success": True,
        "source": source,
        "deepseek_configured": bool(os.getenv("DEEPSEEK_API_KEY")),
        "llm_configured": bool(llm and llm.is_configured()),
        "provider_count": len(llm.providers) if llm else 0,
        **analysis,
    })


@mirror_study_api.post("/sessions")
@rate_limit(max_requests=20, window_seconds=60, scope="mirror_study_create")
def create_session():
    """Create a new study session and randomly assign a condition.

    Body (optional):
      {"condition_id": "c1_nothing_changes" | "c2_you_could_be_anyone"}
    If omitted, condition is assigned uniformly at random.
    """
    payload, error = _json_object()
    if error:
        return error

    condition_id = payload.get("condition_id")
    if condition_id and condition_id not in CONDITIONS:
        return jsonify(
            {"success": False, "error": f"Unknown condition_id: {condition_id}"}
        ), 400
    if condition_id is None:
        condition_id = random.choice(list(CONDITIONS.keys()))

    condition = _condition_with_urls(CONDITIONS[condition_id])
    issue_text = (payload.get("issue") or "").strip()
    req_theme = payload.get("theme_id")
    if issue_text:
        issue_theme = (
            next((t for t in ISSUE_GALLERY if t["id"] == req_theme), None)
            or classify_issue(issue_text)
        )
    else:
        issue_theme = None
    session_payload = {
        "condition_id": condition_id,
        "condition_label": condition["label"],
        "issue_text": issue_text,
        "issue_theme": issue_theme,
        "vignette": SHARED_VIGNETTE,
        "condition": condition,
        "fixes": _fixes_with_urls(),
        "responses": {},
        "timestamps": {"created": mirror_study_store._now()},
    }

    try:
        session_id = mirror_study_store.create(condition_id, session_payload)
    except Exception as exc:
        current_app.logger.exception("Could not create mirror-study session")
        return jsonify(
            {"success": False, "error": "Could not create session. Please retry."}
        ), 500

    return jsonify(
        {
            "success": True,
            "session_id": session_id,
            "condition_id": condition_id,
            "condition": condition,
            "vignette": SHARED_VIGNETTE,
            "fixes": session_payload["fixes"],
            "max_fixes": 3,
        }
    )


@mirror_study_api.get("/sessions/<session_id>")
def get_session(session_id: str):
    """Return the current state of a study session."""
    record = mirror_study_store.get(session_id)
    if record is None:
        return jsonify({"success": False, "error": "Session not found."}), 404
    return jsonify(
        {
            "success": True,
            "session_id": session_id,
            "status": record["status"],
            "condition_id": record["condition_id"],
            "data": record["payload"],
        }
    )


@mirror_study_api.post("/sessions/<session_id>/response")
@rate_limit(max_requests=40, window_seconds=120, scope="mirror_study_response")
def save_response(session_id: str):
    """Save participant responses for a session.

    Body:
      {
        "step": "frames" | "veil" | "fixes" | "demographics" | "final",
        "data": { ... }
      }
    The step field lets the front end save incrementally.
    """
    payload, error = _json_object()
    if error:
        return error

    step = payload.get("step")
    data = payload.get("data")
    if not step or not isinstance(data, dict):
        return jsonify(
            {"success": False, "error": "Both 'step' and 'data' are required."}
        ), 400

    record = mirror_study_store.get(session_id)
    if record is None:
        return jsonify({"success": False, "error": "Session not found."}), 404

    session_payload = record["payload"]
    session_payload["responses"][step] = data
    if "timestamps" not in session_payload:
        session_payload["timestamps"] = {}
    session_payload["timestamps"][step] = mirror_study_store._now()

    if step == "final":
        session_payload["timestamps"]["submitted"] = mirror_study_store._now()
        mirror_study_store.set_status(session_id, "completed")

    try:
        mirror_study_store.update_payload(session_id, session_payload)
    except Exception as exc:
        current_app.logger.exception("Could not save mirror-study response")
        return jsonify(
            {"success": False, "error": "Could not save response. Please retry."}
        ), 500

    return jsonify({"success": True, "session_id": session_id, "step": step})
