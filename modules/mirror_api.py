"""Flask Blueprint for the isolated SafeBARS Ethical Mirror API."""

from __future__ import annotations

from typing import Any, Dict, Tuple

from flask import Blueprint, current_app, jsonify, request

from .mirror_engine import MirrorEngine
from .mirror_guide import MirrorGuide, guide_dimensions
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
mirror_guide = MirrorGuide(mirror_engine.llm_client)


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


@mirror_api.get("/guide/dimensions")
def get_guide_dimensions():
    """Return the ethical dimensions the conversational guide weaves through."""

    return jsonify({"success": True, "dimensions": guide_dimensions()})


@mirror_api.post("/guide")
@rate_limit(max_requests=40, window_seconds=120, scope="mirror_guide")
def guide_turn():
    """Run one conversational-guide turn.

    Body:
      {"action": "start" | "reply" | "finalize",
       "message": str,            # user text for "reply"
       "history": [{"role","content"}, ...]}  # front end owns history
    Returns the updated history, the next assistant reply, a coverage map, and
    (for "finalize") a structured research plan + value commitments.
    """

    payload, error = _json_object()
    if error:
        return error
    action = (payload.get("action") or "reply").lower()
    history = payload.get("history") or []
    if not isinstance(history, list):
        history = []

    llm_error = None
    try:
        if action == "start":
            reply = mirror_guide.start()
            history = [{"role": "assistant", "content": reply}]
            structured = None
        elif action == "finalize":
            structured = mirror_guide.finalize(history)
            reply = (
                "Here's the plan I'll hand to the mirror. Review it on the next step — "
                "you can revise anything before building the consequence map."
            )
            history = list(history) + [{"role": "assistant", "content": reply}]
        else:  # reply
            message = (payload.get("message") or "").strip()
            if message:
                history = list(history) + [{"role": "user", "content": message}]
            reply, llm_error = mirror_guide.reply_detailed(history)
            if reply is None:
                if mirror_guide.llm_available():
                    reply = (
                        "I'm having trouble reaching the language model right now. You can "
                        "keep writing your thoughts here, or switch to the 'Guided questions' "
                        "tab to continue. Nothing you've shared is lost."
                    )
                else:
                    reply = (
                        "The AI guide isn't connected to a language model on this deployment. "
                        "Switch to the 'Guided questions' tab for the full structured walkthrough."
                    )
            history = list(history) + [{"role": "assistant", "content": reply}]
            structured = None
    except Exception as exc:
        return _unexpected("run the conversational guide", exc)

    coverage = mirror_guide.track_coverage(history)
    return jsonify(
        {
            "success": True,
            "action": action,
            "reply": reply,
            "history": history,
            "coverage": coverage,
            "structured": structured,
            "llm_available": mirror_guide.llm_available(),
            "llm_error": llm_error,
        }
    )


@mirror_api.get("/guide/debug-llm")
def debug_llm():
    """Non-sensitive LLM wiring diagnostics (no API key is exposed)."""
    llm = mirror_engine.llm_client
    return jsonify({
        "is_configured": bool(llm and llm.is_configured()),
        "provider_ids": list(llm.providers.keys()) if llm else [],
        "active_provider_id": getattr(llm, "active_provider_id", None),
        "feature_enabled": mirror_engine._llm_feature_enabled,
        "guide_llm_available": mirror_guide.llm_available(),
    })


@mirror_api.get("/guide/probe-providers")
def probe_providers():
    """Ping every configured provider once to expose reachability (no key leaked).

    Each provider gets a trivial prompt with a short timeout so the deployment
    can report which Chinese LLM endpoints are reachable from its region.
    """
    llm = mirror_engine.llm_client
    if not llm or not llm.is_configured():
        return jsonify({"success": True, "probed": False, "results": []})
    probe_msg = [{"role": "user", "content": "Reply with the single word: ok"}]
    results = []
    for pid in llm.providers:
        det = llm.chat_with_provider_detailed(pid, probe_msg, temperature=0.0, timeout=12)
        results.append({
            "provider": pid,
            "ok": bool(det.get("ok")),
            "error_type": det.get("error_type"),
            "status_code": det.get("status_code"),
            "model": det.get("model"),
        })
    reachable = [r["provider"] for r in results if r["ok"]]
    return jsonify({
        "success": True,
        "probed": True,
        "results": results,
        "reachable": reachable,
    })


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
