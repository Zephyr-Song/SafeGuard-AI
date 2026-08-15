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


@mirror_api.post("/sessions/<session_id>/decisions")
def record_decision(session_id: str):
    """Record a per-issue redesign decision (Condition B: visualization mode)."""

    payload, error = _json_object()
    if error:
        return error
    choice = payload.get("choice")
    if choice not in ("fix", "accept_risk", "defer"):
        return jsonify(
            {"success": False, "error": "choice must be fix, accept_risk, or defer."}
        ), 400
    try:
        session = mirror_engine.record_issue_decision(
            session_id,
            issue_id=payload.get("issue_id", ""),
            choice=choice,
            rationale=payload.get("rationale", ""),
            tradeoff=payload.get("tradeoff"),
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return _unexpected("record the issue decision", exc)
    if not session:
        return jsonify({"success": False, "error": "Session not found."}), 404
    return jsonify({"success": True, "session": session})


@mirror_api.get("/sessions/<session_id>/redesign")
def redesign_summary(session_id: str):
    """Return the derived Day-1 -> Day-7 design-evolution visualization."""

    try:
        summary = mirror_engine.redesign_summary(session_id)
    except Exception as exc:
        return _unexpected("build the redesign summary", exc)
    if summary is None:
        return jsonify({"success": False, "error": "Session not found."}), 404
    return jsonify({"success": True, **summary})


@mirror_api.post("/sessions/<session_id>/export-application")
def export_application(session_id: str):
    """Return a DOCX ethics-application draft built from the Mirror session."""

    from flask import Response

    try:
        session = mirror_engine.get_session(session_id)
    except Exception as exc:
        return _unexpected("load the Ethical Mirror session", exc)
    if not session:
        return jsonify({"success": False, "error": "Session not found."}), 404
    try:
        from .mirror_application import build_committee_application_docx

        data = build_committee_application_docx(session)
    except Exception as exc:
        return _unexpected("build the ethics-application draft", exc)
    safe_id = "".join(ch for ch in session_id if ch.isalnum() or ch in "-_") or "session"
    return Response(
        data,
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="ethics-application-{safe_id}.docx"'
            )
        },
    )
