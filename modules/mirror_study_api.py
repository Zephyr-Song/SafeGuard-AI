"""Flask Blueprint for the StressLens CHI 2027 study.

This is intentionally separate from the main SafeBARS Ethical Mirror API so
that the experimental intervention can be versioned and analysed independently.
"""

from __future__ import annotations

import random
from typing import Any, Dict, Tuple

from flask import Blueprint, current_app, jsonify, request, url_for

from .mirror_study_data import CONDITIONS, FIXES, SHARED_VIGNETTE, public_config
from .mirror_study_store import MirrorStudyStore
from .ratelimit import rate_limit


mirror_study_api = Blueprint(
    "safebars_mirror_study",
    __name__,
    url_prefix="/api/safebars/mirror-study",
)

mirror_study_store = MirrorStudyStore()


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


@mirror_study_api.get("/config")
def get_config():
    """Return the public vignette, conditions, and fixes with URLs."""
    cfg = public_config()
    cfg["conditions"] = {
        k: _condition_with_urls(v) for k, v in cfg["conditions"].items()
    }
    cfg["fixes"] = _fixes_with_urls()
    return jsonify({"success": True, **cfg})


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
    session_payload = {
        "condition_id": condition_id,
        "condition_label": condition["label"],
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
