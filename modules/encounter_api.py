"""Flask API routes for the SafeBARS v2 encounter workspace."""

from __future__ import annotations

import json
from functools import wraps

from flask import Blueprint, Response, current_app, g, jsonify, request

from .encounter_engine import EncounterEngine
from .technical_evidence import build_public_evidence
from .ratelimit import rate_limit
from .adaptive_intake import build_intake_plan
from .encounter_report import (
    build_docx_report,
    build_ethics_application_docx,
    build_expert_portfolio_docx,
    build_expert_summary_docx,
    build_pdf_report,
    build_research_design_docx,
)


encounter_api = Blueprint("encounter_v2", __name__, url_prefix="/api/safebars/v2")
encounter_engine = EncounterEngine()


def require_session_role(*allowed_roles: str):
    """Protect one session with a role-specific capability token."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_app.config.get("SAFEBARS_REQUIRE_ROLE_AUTH", True):
                return view(*args, **kwargs)
            session_id = kwargs.get("session_id")
            token = request.headers.get("X-SafeBARS-Access", "").strip()
            if not token:
                return jsonify({
                    "success": False,
                    "error": "A SafeBARS session access token is required.",
                }), 401
            role = encounter_engine.access_role(session_id, token)
            if role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "error": "This access token does not permit that action.",
                }), 403
            g.safebars_role = role
            return view(*args, **kwargs)
        return wrapped
    return decorator


@encounter_api.get("/options")
def options():
    return jsonify({
        "success": True,
        **encounter_engine.public_options(),
        "role_auth_required": current_app.config.get("SAFEBARS_REQUIRE_ROLE_AUTH", True),
    })


@encounter_api.get("/evidence/technical")
def technical_evidence():
    """Return public, read-only technical spec-conformance evidence."""
    try:
        evidence = build_public_evidence()
    except Exception as exc:
        current_app.logger.exception("Could not compute technical evidence")
        return jsonify({
            "success": False,
            "error": f"Could not compute technical evidence: {str(exc)[:300]}",
        }), 500
    return jsonify({"success": True, "evidence": evidence})


@encounter_api.post("/adaptive-intake/plan")
@rate_limit(max_requests=20, window_seconds=60, scope="adaptive_intake_plan")
def adaptive_intake_plan():
    """Return the adaptive guided-intake question plan for a project.

    Accepts either ``{"project": {...}}`` (matching the workspace payload) or a
    flat project description. No session token is required: this is a
    pre-session helper that lets the frontend render the conversational intake
    from the server's canonical question schema.
    """
    payload = request.get_json(silent=True) or {}
    project = payload.get("project", payload) if isinstance(payload, dict) else {}
    plan = build_intake_plan(project or {})
    return jsonify({"success": True, **plan})


@encounter_api.post("/sessions")
def create_session():
    try:
        encounter_session = encounter_engine.create_session(request.get_json(silent=True) or {})
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": f"Could not create encounter session: {str(exc)[:400]}"}), 500
    access = encounter_engine.issue_access(encounter_session["id"])
    return jsonify({"success": True, "session": encounter_session, "access": access}), 201


@encounter_api.get("/sessions/<session_id>")
@require_session_role("researcher")
def get_session(session_id: str):
    encounter_session = encounter_engine.get_session(session_id)
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.post("/sessions/<session_id>/versions")
@require_session_role("researcher")
def create_protocol_version(session_id: str):
    encounter_session = encounter_engine.create_protocol_version(session_id)
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    access = encounter_engine.issue_access(encounter_session["id"])
    return jsonify({"success": True, "session": encounter_session, "access": access}), 201


@encounter_api.patch("/sessions/<session_id>/map")
@require_session_role("researcher")
def update_map(session_id: str):
    payload = request.get_json(silent=True) or {}
    try:
        encounter_session = encounter_engine.update_map(session_id, payload.get("stages", []))
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.patch("/sessions/<session_id>/plan")
@require_session_role("researcher")
def update_audit_plan(session_id: str):
    payload = request.get_json(silent=True) or {}
    try:
        encounter_session = encounter_engine.update_audit_plan(
            session_id, payload.get("scenario_ids")
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.patch("/sessions/<session_id>/application-profile")
@require_session_role("researcher")
def update_application_profile(session_id: str):
    payload = request.get_json(silent=True) or {}
    try:
        encounter_session = encounter_engine.update_application_profile(
            session_id, payload.get("profile_id", "")
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.patch("/sessions/<session_id>/tradeoffs")
@require_session_role("researcher")
def update_tradeoffs(session_id: str):
    payload = request.get_json(silent=True) or {}
    try:
        encounter_session = encounter_engine.update_tradeoff_deliberations(
            session_id,
            payload.get("deliberations", []),
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.post("/sessions/<session_id>/audit")
@rate_limit(max_requests=10, window_seconds=120, scope="v2_audit")
@require_session_role("researcher")
def run_audit(session_id: str):
    payload = request.get_json(silent=True) or {}
    try:
        encounter_session = encounter_engine.run_audit(session_id, payload.get("scenario_ids"))
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": f"Audit failed: {str(exc)[:400]}"}), 500
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.post("/sessions/<session_id>/tasks/<task_id>/rerun")
@rate_limit(max_requests=20, window_seconds=120, scope="v2_rerun")
@require_session_role("researcher")
def rerun_task(session_id: str, task_id: str):
    try:
        encounter_session = encounter_engine.rerun_task(session_id, task_id)
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except KeyError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"success": False, "error": f"Task rerun failed: {str(exc)[:400]}"}), 500
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.post("/sessions/<session_id>/issues/<issue_id>/decision")
@require_session_role("researcher")
def record_decision(session_id: str, issue_id: str):
    payload = request.get_json(silent=True) or {}
    try:
        encounter_session = encounter_engine.record_decision(
            session_id,
            issue_id,
            payload.get("decision", "pending"),
            payload.get("rationale", ""),
            payload.get("revised_text", ""),
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except KeyError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.get("/sessions/<session_id>/expert-summary")
@require_session_role("expert")
def expert_summary(session_id: str):
    summary = encounter_engine.expert_summary(session_id)
    if not summary:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "summary": summary})


@encounter_api.post("/sessions/<session_id>/handoffs/<handoff_id>/researcher-response")
@require_session_role("researcher")
def respond_to_handoff(session_id: str, handoff_id: str):
    payload = request.get_json(silent=True) or {}
    try:
        encounter_session = encounter_engine.respond_to_handoff(
            session_id=session_id,
            handoff_id=handoff_id,
            response=payload.get("response", ""),
            revised_text=payload.get("revised_text", ""),
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except KeyError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.post("/sessions/<session_id>/handoffs/<handoff_id>/review")
@require_session_role("expert")
def review_handoff(session_id: str, handoff_id: str):
    payload = request.get_json(silent=True) or {}
    try:
        encounter_session = encounter_engine.review_handoff(
            session_id=session_id,
            handoff_id=handoff_id,
            action=payload.get("action", "advise"),
            reviewer_role=payload.get("reviewer_role", "ethics_board"),
            reviewer_name=payload.get("reviewer_name", ""),
            advice=payload.get("advice", ""),
            rationale=payload.get("rationale", ""),
            redirect_role=payload.get("redirect_role", ""),
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except KeyError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.post("/sessions/<session_id>/access/rotate-expert")
@require_session_role("researcher")
def rotate_expert_access(session_id: str):
    try:
        token = encounter_engine.rotate_expert_access(session_id)
    except KeyError:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "expert_token": token})


@encounter_api.get("/sessions/<session_id>/export")
@require_session_role("researcher")
def export_session(session_id: str):
    encounter_session = encounter_engine.get_session(session_id)
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    filename = f"{session_id}.json"
    return Response(
        json.dumps(encounter_session, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@encounter_api.get("/sessions/<session_id>/export.docx")
@require_session_role("researcher")
def export_session_docx(session_id: str):
    encounter_session = encounter_engine.get_session(session_id)
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    try:
        report = build_docx_report(encounter_session)
    except Exception as exc:
        return jsonify({"success": False, "error": f"Could not create Word report: {str(exc)[:400]}"}), 500
    filename = f"safebars_{session_id}_full_audit_report.docx"
    return Response(
        report,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@encounter_api.get("/sessions/<session_id>/export.pdf")
@require_session_role("researcher")
def export_session_pdf(session_id: str):
    encounter_session = encounter_engine.get_session(session_id)
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    try:
        report = build_pdf_report(encounter_session)
    except Exception as exc:
        return jsonify({"success": False, "error": f"Could not create PDF report: {str(exc)[:400]}"}), 500
    filename = f"safebars_{session_id}_full_audit_report.pdf"
    return Response(
        report,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@encounter_api.get("/sessions/<session_id>/export.application.docx")
@require_session_role("researcher")
def export_ethics_application_docx(session_id: str):
    encounter_session = encounter_engine.get_session(session_id)
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    try:
        report = build_ethics_application_docx(encounter_session)
    except Exception as exc:
        return jsonify({"success": False, "error": f"Could not create application draft: {str(exc)[:400]}"}), 500
    filename = f"safebars_{session_id}_ethics_application_draft.docx"
    return Response(
        report,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@encounter_api.get("/sessions/<session_id>/export.research-design.docx")
@require_session_role("researcher")
def export_research_design_docx(session_id: str):
    encounter_session = encounter_engine.get_session(session_id)
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    try:
        report = build_research_design_docx(encounter_session)
    except Exception as exc:
        return jsonify({"success": False, "error": f"Could not create research design: {str(exc)[:400]}"}), 500
    filename = f"safebars_{session_id}_research_design.docx"
    return Response(
        report,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@encounter_api.get("/sessions/<session_id>/export.expert.docx")
@require_session_role("expert")
def export_expert_summary_docx(session_id: str):
    encounter_session = encounter_engine.get_session(session_id)
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    try:
        report = build_expert_summary_docx(encounter_session)
    except Exception as exc:
        return jsonify({"success": False, "error": f"Could not create expert summary: {str(exc)[:400]}"}), 500
    filename = f"safebars_{session_id}_expert_review_summary.docx"
    return Response(
        report,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@encounter_api.post("/expert/export.portfolio.docx")
def export_expert_portfolio_docx():
    payload = request.get_json(silent=True) or {}
    cases = payload.get("cases", [])
    if not isinstance(cases, list) or not cases:
        return jsonify({"success": False, "error": "At least one expert-accessible case is required."}), 400
    if len(cases) > 25:
        return jsonify({"success": False, "error": "A portfolio export is limited to 25 cases."}), 400

    sessions = []
    seen = set()
    role_auth_required = current_app.config.get("SAFEBARS_REQUIRE_ROLE_AUTH", True)
    for case in cases:
        if not isinstance(case, dict):
            return jsonify({"success": False, "error": "Each case must include a session ID and expert token."}), 400
        session_id = str(case.get("session_id", "")).strip()
        token = str(case.get("expert_token", "")).strip()
        if not session_id or session_id in seen:
            continue
        if role_auth_required and encounter_engine.access_role(session_id, token) != "expert":
            return jsonify({"success": False, "error": f"Expert access was not valid for case {session_id}."}), 403
        encounter_session = encounter_engine.get_session(session_id)
        if not encounter_session:
            return jsonify({"success": False, "error": f"Case {session_id} was not found."}), 404
        sessions.append(encounter_session)
        seen.add(session_id)

    if not sessions:
        return jsonify({"success": False, "error": "No valid expert-accessible cases were supplied."}), 400
    try:
        report = build_expert_portfolio_docx(sessions)
    except Exception as exc:
        return jsonify({"success": False, "error": f"Could not create expert caseload summary: {str(exc)[:400]}"}), 500
    return Response(
        report,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="safebars_expert_caseload_summary.docx"'},
    )
