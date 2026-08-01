"""Flask Blueprint for the isolated SafeBARS Ethical Mirror API."""

from __future__ import annotations

from typing import Any, Dict, Tuple

from flask import Blueprint, current_app, jsonify, request

from .mirror_engine import MirrorEngine
from .mirror_literature import (
    EVIDENCE_STATE_NOTICE,
    LENS_SYNTHESIS_NOTICE,
)
from .ratelimit import rate_limit


mirror_api = Blueprint(
    "safebars_mirror",
    __name__,
    url_prefix="/api/safebars/mirror",
)
mirror_engine = MirrorEngine()


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


def _unexpected(action: str, exc: Exception):
    current_app.logger.exception("SafeBARS Mirror could not %s", action)
    return jsonify(
        {
            "success": False,
            # Exception details remain in the server log; research plans,
            # database paths, provider messages, and stack details must not be
            # reflected into a public production response.
            "error": f"Could not {action}. Please retry or contact the service operator.",
        }
    ), 500


@mirror_api.get("/config")
def get_config():
    """Return public literature-lens, role, limit, and boundary metadata."""

    return jsonify({"success": True, **mirror_engine.public_config()})


@mirror_api.get("/literature")
def get_literature():
    """Return the inspectable source registry used by the design synthesis."""

    return jsonify(
        {
            "success": True,
            "literature": mirror_engine.literature(),
            "lens_synthesis_notice": LENS_SYNTHESIS_NOTICE,
            "interpretation_boundary": EVIDENCE_STATE_NOTICE,
        }
    )


@mirror_api.post("/sessions")
def create_session():
    payload, error = _json_object()
    if error:
        return error
    try:
        session = mirror_engine.create_session(payload)
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return _unexpected("create the Ethical Mirror session", exc)
    return jsonify({"success": True, "session": session}), 201


@mirror_api.get("/sessions/<session_id>")
def get_session(session_id: str):
    try:
        session = mirror_engine.get_session(session_id)
    except Exception as exc:
        return _unexpected("load the Ethical Mirror session", exc)
    if not session:
        return jsonify({"success": False, "error": "Session not found."}), 404
    return jsonify({"success": True, "session": session})


@mirror_api.post("/sessions/<session_id>/analyze")
@rate_limit(max_requests=8, window_seconds=120, scope="mirror_analyze")
def analyze_session(session_id: str):
    payload, error = _json_object()
    if error:
        return error
    try:
        session = mirror_engine.analyze_session(
            session_id,
            use_llm=bool(payload.get("use_llm", False)),
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return _unexpected("analyze the research plan", exc)
    if not session:
        return jsonify({"success": False, "error": "Session not found."}), 404
    return jsonify({"success": True, "session": session})


@mirror_api.post("/sessions/<session_id>/revisions")
def add_revision(session_id: str):
    payload, error = _json_object()
    if error:
        return error
    try:
        session = mirror_engine.add_revision(
            session_id,
            revised_plan=payload.get("revised_plan", ""),
            resolutions=payload.get("resolutions", []),
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return _unexpected("save the research-plan revision", exc)
    if not session:
        return jsonify({"success": False, "error": "Session not found."}), 404
    return jsonify({"success": True, "session": session})


@mirror_api.post("/sessions/<session_id>/replay")
@rate_limit(max_requests=6, window_seconds=120, scope="mirror_replay")
def replay_session(session_id: str):
    payload, error = _json_object()
    if error:
        return error
    try:
        session = mirror_engine.replay_session(
            session_id,
            revision_id=payload.get("revision_id"),
            use_llm=bool(payload.get("use_llm", False)),
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return _unexpected("replay the revised research plan", exc)
    if not session:
        return jsonify({"success": False, "error": "Session not found."}), 404
    return jsonify({"success": True, "session": session})
