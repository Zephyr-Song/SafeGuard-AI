"""Flask API routes for the SafeBARS v2 encounter workspace."""

from __future__ import annotations

import json

from flask import Blueprint, Response, jsonify, request

from .encounter_engine import EncounterEngine
from .encounter_report import build_docx_report, build_pdf_report


encounter_api = Blueprint("encounter_v2", __name__, url_prefix="/api/safebars/v2")
encounter_engine = EncounterEngine()


@encounter_api.get("/options")
def options():
    return jsonify({"success": True, **encounter_engine.public_options()})


@encounter_api.post("/sessions")
def create_session():
    try:
        encounter_session = encounter_engine.create_session(request.get_json(silent=True) or {})
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": f"Could not create encounter session: {str(exc)[:400]}"}), 500
    return jsonify({"success": True, "session": encounter_session}), 201


@encounter_api.get("/sessions/<session_id>")
def get_session(session_id: str):
    encounter_session = encounter_engine.get_session(session_id)
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.patch("/sessions/<session_id>/map")
def update_map(session_id: str):
    payload = request.get_json(silent=True) or {}
    encounter_session = encounter_engine.update_map(session_id, payload.get("stages", []))
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.post("/sessions/<session_id>/audit")
def run_audit(session_id: str):
    payload = request.get_json(silent=True) or {}
    try:
        encounter_session = encounter_engine.run_audit(session_id, payload.get("scenario_ids"))
    except Exception as exc:
        return jsonify({"success": False, "error": f"Audit failed: {str(exc)[:400]}"}), 500
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    return jsonify({"success": True, "session": encounter_session})


@encounter_api.post("/sessions/<session_id>/issues/<issue_id>/decision")
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


@encounter_api.get("/sessions/<session_id>/export")
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
def export_session_docx(session_id: str):
    encounter_session = encounter_engine.get_session(session_id)
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    try:
        report = build_docx_report(encounter_session)
    except Exception as exc:
        return jsonify({"success": False, "error": f"Could not create Word report: {str(exc)[:400]}"}), 500
    filename = f"safebars_{session_id}.docx"
    return Response(
        report,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@encounter_api.get("/sessions/<session_id>/export.pdf")
def export_session_pdf(session_id: str):
    encounter_session = encounter_engine.get_session(session_id)
    if not encounter_session:
        return jsonify({"success": False, "error": "Session not found"}), 404
    try:
        report = build_pdf_report(encounter_session)
    except Exception as exc:
        return jsonify({"success": False, "error": f"Could not create PDF report: {str(exc)[:400]}"}), 500
    filename = f"safebars_{session_id}.pdf"
    return Response(
        report,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
