"""Build a university-ethics-committee application draft from a Mirror session.

The Ethical Mirror helps a researcher anticipate unintended consequences of an
AI / data-driven research plan *before* implementation.  This module turns the
reflection that the Mirror captures (research plan, literature-grounded lenses,
role probes, tension map, researcher revisions) into a structured draft that
the researcher can hand to an institutional ethics committee.

It deliberately follows the Ethics and Society Review (ESR; Bernstein et al.,
PNAS 2021) framing: standard review (for example an IRB under the Common Rule)
focuses on risks to individual participants, but research can also create risks
to society, to subgroups, and globally.  The draft therefore surfaces those
societal / subgroup / global risks and asks the researcher to commit to
mitigations.  The document is a DRAFT and never an approval or compliance
verdict.
"""

from __future__ import annotations

import io
from typing import Any, Dict, List

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x5A, 0x5A, 0x5A)
AMBER = RGBColor(0x7A, 0x5A, 0x00)

INTAKE_LABELS: Dict[str, str] = {
    "research_context": "Research context and purpose",
    "intended_change": "Intended benefit / change",
    "direct_users": "Direct users",
    "ai_role": "Role of AI in the research",
    "data_materials": "Data and materials",
    "sensitive_data_justification": "Sensitive data justification",
    "affected_others": "Indirectly affected others",
    "value_commitment": "Value commitment",
    "stop_condition": "Redesign / stop threshold",
    "optional_perspective_context": "Additional perspective context",
}

# Lens statuses ordered from weakest to strongest evidence of reflection.
WEAK_LENS_STATUSES = {"missing", "claimed"}


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, (list, tuple)):
        return "; ".join(str(v) for v in value if v)
    if isinstance(value, dict):
        return "; ".join(str(v) for v in value.values() if v)
    return str(value)


def _set_run(run, size=None, color=None, bold=False, italic=False):
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = color
    run.bold = bold
    run.italic = italic


def _label_paragraph(document: Document, label: str, value: Any) -> None:
    paragraph = document.add_paragraph()
    _set_run(paragraph.add_run(f"{label}: "), bold=True)
    paragraph.add_run(_text(value))
    return None


def _add_esr_section(document: Document, session: Dict[str, Any]) -> None:
    """ESR-style societal / subgroup / global risk statement (Bernstein 2021)."""

    document.add_heading(
        "4. Societal & community risk statement (Ethics and Society Review)",
        level=1,
    )
    paragraph = document.add_paragraph()
    _set_run(paragraph.add_run(
        "Standard ethics review (for example an IRB under the US Common Rule) "
        "focuses on risks to individual participants. The Ethics and Society "
        "Review (ESR; Bernstein, Levi, Magnus, Rajala, Satz & Waeiss, PNAS 2021, "
        "DOI 10.1073/pnas.2117261118) argues that research can also create risks "
        "to society, to subgroups within society, and globally, and that "
        "researchers should state those risks and commit to mitigation "
        "strategies before the work proceeds."
    ))
    document.add_paragraph(
        "Use the prompts below to state, in your own words, who might be "
        "affected beyond the direct participants, what could go wrong, and how "
        "you will mitigate it. Leave no blank line unaddressed before submission."
    )

    # Surface the people/roles the researcher already named as prompts.
    prompts: List[str] = []
    intake = session.get("intake_answers") or {}
    if _text(intake.get("direct_users")):
        prompts.append(
            f"Direct users you named: {_text(intake.get('direct_users'))}. "
            "Who else could be affected, and how?"
        )
    if _text(intake.get("affected_others")):
        prompts.append(
            f"Indirectly affected others you named: "
            f"{_text(intake.get('affected_others'))}. "
            "What subgroup or community-level harms could arise?"
        )
    if not prompts:
        prompts.append(
            "Who beyond the direct participants could be affected by this "
            "research, at the subgroup or societal level?"
        )
    prompts.append(
        "What global, long-term, or systemic consequence could this work "
        "produce, even if individual participants are protected?"
    )
    prompts.append(
        "Which literature lens below is 'Missing' or only 'Claimed' (not yet "
        "reasoned or action-linked)? State the risk it points to and your "
        "mitigation commitment."
    )

    for index, prompt in enumerate(prompts, start=1):
        item = document.add_paragraph(style="List Number")
        _set_run(item.add_run(prompt))
        blank = document.add_paragraph()
        _set_run(blank.add_run("Mitigation statement (researcher to complete): "), bold=True)
        blank.add_run("_" * 60)

    # Echo the weak lenses so the researcher sees exactly which dimensions are open.
    lenses = session.get("lenses") or []
    weak = [l for l in lenses if l.get("status") in WEAK_LENS_STATUSES]
    if weak:
        note = document.add_paragraph()
        _set_run(note.add_run("Open ethical dimensions flagged by the Mirror:"), bold=True)
        for lens in weak:
            line = document.add_paragraph(style="List Bullet")
            _set_run(line.add_run(
                f"{_text(lens.get('label') or lens.get('id'), 'Lens')} "
                f"[{_text(lens.get('status'))}] — {_text(lens.get('evidence') or lens.get('interpretation'))}"
            ))


def build_committee_application_docx(session: Dict[str, Any]) -> bytes:
    """Return a DOCX ethics-application draft for ``session`` as raw bytes."""

    document = Document()
    normal = document.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)

    title = document.add_paragraph()
    _set_run(
        title.add_run("ETHICS APPLICATION DRAFT — Generated by SafeBARS Ethical Mirror"),
        size=18, bold=True, color=INK,
    )
    subtitle = document.add_paragraph()
    _set_run(
        subtitle.add_run(_text(session.get("title"), "Untitled research project")),
        size=13, color=MUTED,
    )

    notice = document.add_paragraph()
    _set_run(notice.add_run(
        "DRAFT ONLY — this is not an approval or compliance verdict. Transfer "
        "the content below into your institution's required form. Generated or "
        "scaffolded text requires researcher verification and formal "
        "institutional ethics review."
    ), bold=True, color=AMBER)

    # 1. Research summary ---------------------------------------------------
    document.add_heading("1. Research summary", level=1)
    research_plan = _text(session.get("research_plan"))
    if research_plan:
        _label_paragraph(document, "Research plan (as submitted)", research_plan)
    intake = session.get("intake_answers") or {}
    for key in INTAKE_LABELS:
        if _text(intake.get(key)):
            _label_paragraph(document, INTAKE_LABELS[key], intake[key])
    commitments = session.get("value_commitments") or []
    if commitments:
        _label_paragraph(document, "Value commitments", "; ".join(commitments))

    # 2. Ethical considerations across literature lenses -------------------
    document.add_heading("2. Ethical considerations across literature lenses", level=1)
    lenses = session.get("lenses") or []
    if not lenses:
        document.add_paragraph(
            "Run the Mirror analysis to populate literature-grounded ethical "
            "dimensions. Each dimension below will show its coverage, the "
            "plan passage it was grounded in, and the relevant source."
        )
    for lens in lenses:
        heading = document.add_heading(level=2)
        _set_run(
            heading.add_run(_text(lens.get("label") or lens.get("id"), "Lens")),
            size=13, bold=True,
        )
        _label_paragraph(document, "Coverage", lens.get("status"))
        _label_paragraph(
            document,
            "Evidence / interpretation",
            _text(lens.get("evidence") or lens.get("interpretation")),
        )
        source_ids = lens.get("source_ids") or []
        if source_ids:
            _label_paragraph(
                document, "Literature source(s)",
                ", ".join(_text(s) for s in source_ids),
            )
        if lens.get("status") in WEAK_LENS_STATUSES:
            blank = document.add_paragraph()
            _set_run(blank.add_run("Researcher note (to complete): "), bold=True)
            blank.add_run("_" * 60)

    # 3. Identified risks and mitigations ----------------------------------
    document.add_heading("3. Identified risks and mitigations", level=1)
    scenarios = session.get("scenarios") or []
    if scenarios:
        document.add_paragraph(
            "The Mirror probed bounded roles and breakdown scenarios. Each is a "
            "hypothesis about how the plan could go wrong, not stakeholder "
            "testimony."
        )
        for scenario in scenarios:
            item = document.add_paragraph(style="List Bullet")
            label = _text(scenario.get("label") or scenario.get("title") or scenario.get("role"))
            desc = _text(scenario.get("description") or scenario.get("harm") or scenario.get("rationale"))
            _set_run(item.add_run(f"{label}: "), bold=True)
            item.add_run(desc)
    else:
        document.add_paragraph("No role probes were generated for this plan.")

    edges = session.get("dissonance_edges") or []
    if edges:
        document.add_paragraph("Tension paths the researcher must reconcile:")
        for edge in edges:
            item = document.add_paragraph(style="List Bullet")
            label = _text(edge.get("label") or edge.get("id"))
            status = _text(edge.get("status"))
            rationale = _text(edge.get("rationale") or edge.get("description"))
            _set_run(item.add_run(f"{label} [{status}]: "), bold=True)
            item.add_run(rationale)

    # 4. ESR societal & community risk statement ---------------------------
    _add_esr_section(document, session)

    # 5. Researcher revisions and decisions --------------------------------
    document.add_heading("5. Researcher revisions and decisions", level=1)
    revisions = session.get("revisions") or []
    if revisions:
        for revision in revisions:
            item = document.add_paragraph(style="List Bullet")
            summary = _text(
                revision.get("summary") or revision.get("revised_plan") or revision.get("note")
            )
            _set_run(item.add_run("Revision: "), bold=True)
            item.add_run(summary)
    else:
        document.add_paragraph(
            "No revisions recorded yet. Responding to tensions in Step 5 "
            "(Revise / Add safeguard / Contest / Consult) will populate this "
            "section and the change ledger."
        )

    # 6. References ---------------------------------------------------------
    document.add_heading("6. References", level=1)
    references = [
        "Bernstein, M. S., Levi, M., Magnus, D., Rajala, B. A., Satz, D., & "
        "Waeiss, C. (2021). Ethics and society review: Ethics reflection as a "
        "precondition to research funding. PNAS, 118(52), e2117261118. "
        "DOI 10.1073/pnas.2117261118.",
        "National Commission for the Protection of Human Subjects of "
        "Biomedical and Behavioral Research (1979). The Belmont Report: "
        "Ethical Principles and Guidelines for the Protection of Human "
        "Subjects of Research.",
        "Dittrich, D., Kenneally, E., et al. (2012). The Menlo Report: "
        "Ethical Principles Guiding Information and Communication Technology "
        "Research.",
        "NIST (2023). AI Risk Management Framework (AI RMF 1.0). NIST AI 100-1.",
        "Friedman, B., Kahn, P. H., Borning, A., & Huldtgren, A. (2013). "
        "Value Sensitive Design and information systems. In Early Engagement "
        "and New Technologies: Opening up the Laboratory.",
    ]
    for ref in references:
        item = document.add_paragraph(style="List Bullet")
        item.add_run(ref)

    bio = io.BytesIO()
    document.save(bio)
    return bio.getvalue()
