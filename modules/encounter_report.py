"""Human-readable Word and PDF reports for SafeBARS encounter sessions."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List
from xml.sax.saxutils import escape

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    LongTable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


INK = "17202A"
MUTED = "66727F"
BLUE = "2E74B5"
DARK_BLUE = "1F4D78"
GREEN = "246B49"
TEAL = "176F73"
LIGHT_GRAY = "F2F4F7"
LINE = "D9DEE3"
AMBER_FILL = "FFF8E8"


def _text(value: Any, fallback: str = "Not provided") -> str:
    cleaned = str(value or "").strip()
    return cleaned or fallback


def _date(value: str) -> str:
    if not value:
        return "Not recorded"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return value


def _passage_lookup(session: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    return {item["id"]: item for item in session.get("passages", [])}


def _decision_summary(session: Dict[str, Any]) -> str:
    counts = Counter(item.get("decision", "pending") for item in session.get("issues", []))
    order = ["accept", "edit", "reject", "defer", "pending"]
    return ", ".join(f"{name}: {counts[name]}" for name in order if counts[name]) or "No issues"


def _set_run(run, *, size: float = 11, color: str = INK, bold: bool = False, italic: bool = False) -> None:
    run.font.name = "Calibri"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Calibri")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Calibri")
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    run.bold = bold
    run.italic = italic


def _set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def _set_cell_margins(cell, top: int = 80, start: int = 120, bottom: int = 80, end: int = 120) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for edge, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def _set_table_geometry(table, widths_dxa: List[int], indent_dxa: int = 120) -> None:
    total = sum(widths_dxa)
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl_pr = table._tbl.tblPr
    for tag, value in (("tblW", total), ("tblInd", indent_dxa)):
        node = tbl_pr.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            tbl_pr.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_dxa:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for index, cell in enumerate(row.cells):
            width = widths_dxa[min(index, len(widths_dxa) - 1)]
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(width))
            tc_w.set(qn("w:type"), "dxa")
            _set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def _set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def _add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("Page ")
    _set_run(run, size=9, color=MUTED)
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = " PAGE "
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char_begin)
    run._r.append(instr_text)
    run._r.append(fld_char_end)


def _add_label_paragraph(doc: Document, label: str, value: Any, *, after: float = 4) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(after)
    label_run = paragraph.add_run(f"{label}: ")
    _set_run(label_run, bold=True, color=DARK_BLUE)
    value_run = paragraph.add_run(_text(value))
    _set_run(value_run)


def _configure_docx(document: Document) -> None:
    section = document.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.right_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    normal = document.styles["Normal"]
    normal.font.name = "Calibri"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.10

    heading_tokens = {
        "Heading 1": (16, BLUE, 16, 8),
        "Heading 2": (13, BLUE, 12, 6),
        "Heading 3": (12, DARK_BLUE, 8, 4),
    }
    for style_name, (size, color, before, after) in heading_tokens.items():
        style = document.styles[style_name]
        style.font.name = "Calibri"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True

    header = section.header.paragraphs[0]
    header.text = "SAFEBARS  /  ENCOUNTER STRESS-TEST REPORT"
    _set_run(header.runs[0], size=9, color=MUTED, bold=True)
    footer = section.footer.paragraphs[0]
    _add_page_number(footer)


def _add_docx_boundary_callout(document: Document) -> None:
    table = document.add_table(rows=1, cols=1)
    _set_table_geometry(table, [9360])
    cell = table.cell(0, 0)
    _set_cell_shading(cell, AMBER_FILL)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    label = paragraph.add_run("Interpretation boundary. ")
    _set_run(label, bold=True, color="7A5A00")
    copy = paragraph.add_run(
        "This report contains planning hypotheses about the submitted protocol. It is not participant "
        "evidence, community representation, an ethics approval, or a prediction of real behavior."
    )
    _set_run(copy, color="5E4A17")


def build_docx_report(session: Dict[str, Any]) -> bytes:
    document = Document()
    _configure_docx(document)
    passages = _passage_lookup(session)

    title = document.add_paragraph()
    title.paragraph_format.space_before = Pt(12)
    title.paragraph_format.space_after = Pt(4)
    title_run = title.add_run("SAFEBARS REPORT")
    _set_run(title_run, size=23, color=INK, bold=True)

    subtitle = document.add_paragraph()
    subtitle.paragraph_format.space_after = Pt(14)
    subtitle_run = subtitle.add_run(_text(session.get("project", {}).get("title"), "Untitled fieldwork plan"))
    _set_run(subtitle_run, size=14, color=MUTED)

    metadata = document.add_table(rows=4, cols=2)
    _set_table_geometry(metadata, [1800, 7560])
    metadata_rows = [
        ("Session", session.get("id")),
        ("Generated", _date(session.get("updated_at", ""))),
        ("Status", session.get("status", "unknown")),
        (
            "Contents",
            f"{len(session.get('encounter_map', []))} stages | {len(session.get('traces', []))} traces | "
            f"{len(session.get('issues', []))} issues | {len(session.get('handoffs', []))} handoffs",
        ),
    ]
    for row, (label, value) in zip(metadata.rows, metadata_rows):
        label_p = row.cells[0].paragraphs[0]
        label_p.paragraph_format.space_after = Pt(0)
        _set_run(label_p.add_run(label), bold=True, color=DARK_BLUE)
        value_p = row.cells[1].paragraphs[0]
        value_p.paragraph_format.space_after = Pt(0)
        _set_run(value_p.add_run(_text(value)))
    document.add_paragraph().paragraph_format.space_after = Pt(2)
    _add_docx_boundary_callout(document)

    document.add_heading("1. Project context", level=1)
    _add_label_paragraph(document, "Context", session.get("project", {}).get("context"))
    _add_label_paragraph(document, "People and relationships", session.get("project", {}).get("target_people"))
    _add_label_paragraph(document, "Decision summary", _decision_summary(session))

    document.add_heading("2. Encounter map", level=1)
    map_table = document.add_table(rows=1, cols=4)
    map_table.style = "Table Grid"
    _set_table_geometry(map_table, [2600, 1300, 1200, 4260])
    headers = ["Stage", "Coverage", "Scope", "Sources / responsibility note"]
    for cell, header_text in zip(map_table.rows[0].cells, headers):
        _set_cell_shading(cell, LIGHT_GRAY)
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_after = Pt(0)
        _set_run(paragraph.add_run(header_text), size=9.5, bold=True, color=DARK_BLUE)
    _set_repeat_table_header(map_table.rows[0])
    for stage in session.get("encounter_map", []):
        row = map_table.add_row()
        values = [
            stage.get("name"),
            stage.get("coverage"),
            "Included" if stage.get("included", True) else "Excluded",
            ", ".join(stage.get("source_passage_ids", []))
            + (f" | {stage.get('notes')}" if stage.get("notes") else ""),
        ]
        for cell, value in zip(row.cells, values):
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            _set_run(paragraph.add_run(_text(value, "None")), size=9.5)
    _set_table_geometry(map_table, [2600, 1300, 1200, 4260])

    document.add_heading("3. Breakdown traces", level=1)
    if not session.get("traces"):
        document.add_paragraph("No scenario traces were run.")
    for index, trace in enumerate(session.get("traces", []), start=1):
        document.add_heading(f"3.{index} {trace.get('title', 'Untitled trace')}", level=2)
        _add_label_paragraph(document, "Status", trace.get("status"))
        for step in trace.get("steps", []):
            sources = ", ".join(step.get("source_passage_ids", [])) or "No cited passage"
            _add_label_paragraph(
                document,
                step.get("label", "Trace step"),
                f"{_text(step.get('text'))} [Sources: {sources}]",
            )
        _add_label_paragraph(document, "First gap or coverage result", trace.get("first_gap"))
        _add_label_paragraph(document, "Boundary", trace.get("uncertainty"), after=8)

    document.add_page_break()
    document.add_heading("4. Issue ledger", level=1)
    if not session.get("issues"):
        document.add_paragraph("No contestable issues were produced in this session.")
    for index, issue in enumerate(session.get("issues", []), start=1):
        document.add_heading(f"4.{index} {issue.get('title', 'Untitled issue')}", level=2)
        _add_label_paragraph(
            document,
            "Assessment",
            f"{_text(issue.get('severity')).upper()} | {_text(issue.get('decision')).upper()} | {_text(issue.get('agent'))}",
        )
        _add_label_paragraph(document, "Observation", issue.get("observation"))
        for passage_id in issue.get("source_passage_ids", []):
            passage = passages.get(passage_id)
            if passage:
                _add_label_paragraph(
                    document,
                    f"Source {passage_id} - {passage.get('artifact_label', '')}",
                    passage.get("text"),
                )
        _add_label_paragraph(document, "Proposed change", issue.get("suggestion"))
        _add_label_paragraph(document, "Researcher revision", issue.get("revised_text", ""))
        _add_label_paragraph(document, "Decision rationale", issue.get("decision_rationale", ""))
        _add_label_paragraph(document, "Boundary", issue.get("uncertainty"), after=8)

    document.add_heading("5. Real-world handoffs", level=1)
    if not session.get("handoffs"):
        document.add_paragraph("No real-world handoffs were recorded.")
    for index, handoff in enumerate(session.get("handoffs", []), start=1):
        document.add_heading(f"5.{index} {handoff.get('question', 'Unresolved question')}", level=2)
        _add_label_paragraph(document, "Why AI cannot resolve this", handoff.get("why_ai_cannot_resolve"))
        _add_label_paragraph(document, "Real-world owner", handoff.get("owner"), after=8)

    document.add_page_break()
    document.add_heading("Appendix A. Submitted materials", level=1)
    artifact_labels = {
        "recruitment": "Recruitment message",
        "consent": "Consent language",
        "interview": "Interview questions",
        "activity": "Workshop or activity plan",
        "safety": "Safety and escalation procedure",
        "follow_up": "Debrief, follow-up, and data use",
    }
    for key, label in artifact_labels.items():
        document.add_heading(label, level=2)
        document.add_paragraph(_text(session.get("artifacts", {}).get(key)))

    document.add_heading("Appendix B. Audit event history", level=1)
    for event in session.get("event_log", []):
        _add_label_paragraph(
            document,
            _date(event.get("created_at", "")),
            f"{event.get('event_type', 'event')} - {event.get('payload', {})}",
        )

    output = BytesIO()
    document.save(output)
    return output.getvalue()


def _pdf_styles() -> Dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "SafeBARSTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=23,
            leading=27, textColor=colors.HexColor(f"#{INK}"), alignment=TA_LEFT, spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "SafeBARSSubtitle", parent=base["Normal"], fontName="Helvetica", fontSize=14,
            leading=18, textColor=colors.HexColor(f"#{MUTED}"), spaceAfter=14,
        ),
        "body": ParagraphStyle(
            "SafeBARSBody", parent=base["BodyText"], fontName="Helvetica", fontSize=9.5,
            leading=12.5, textColor=colors.HexColor(f"#{INK}"), spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "SafeBARSSmall", parent=base["BodyText"], fontName="Helvetica", fontSize=8.2,
            leading=10.5, textColor=colors.HexColor(f"#{INK}"), spaceAfter=2,
        ),
        "h1": ParagraphStyle(
            "SafeBARSH1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=16,
            leading=19, textColor=colors.HexColor(f"#{BLUE}"), spaceBefore=16, spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "SafeBARSH2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12,
            leading=15, textColor=colors.HexColor(f"#{DARK_BLUE}"), spaceBefore=10, spaceAfter=5,
        ),
        "boundary": ParagraphStyle(
            "SafeBARSBoundary", parent=base["BodyText"], fontName="Helvetica", fontSize=9.5,
            leading=13, textColor=colors.HexColor("#5E4A17"), spaceAfter=0,
        ),
    }


def _p(value: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(_text(value)).replace("\n", "<br/>"), style)


def _label_pdf(label: str, value: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(f"<b>{escape(label)}:</b> {escape(_text(value)).replace(chr(10), '<br/>')}", style)


def _pdf_header_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor(f"#{LINE}"))
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, letter[1] - 0.58 * inch, letter[0] - doc.rightMargin, letter[1] - 0.58 * inch)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(colors.HexColor(f"#{MUTED}"))
    canvas.drawString(doc.leftMargin, letter[1] - 0.48 * inch, "SAFEBARS / ENCOUNTER STRESS-TEST REPORT")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def _pdf_meta_table(session: Dict[str, Any], styles: Dict[str, ParagraphStyle]) -> Table:
    data = [
        [_p("Session", styles["small"]), _p(session.get("id"), styles["small"])],
        [_p("Generated", styles["small"]), _p(_date(session.get("updated_at", "")), styles["small"])],
        [_p("Status", styles["small"]), _p(session.get("status"), styles["small"])],
        [
            _p("Contents", styles["small"]),
            _p(
                f"{len(session.get('encounter_map', []))} stages | {len(session.get('traces', []))} traces | "
                f"{len(session.get('issues', []))} issues | {len(session.get('handoffs', []))} handoffs",
                styles["small"],
            ),
        ],
    ]
    table = Table(data, colWidths=[1.25 * inch, 5.25 * inch], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor(f"#{LIGHT_GRAY}")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor(f"#{DARK_BLUE}")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(f"#{LINE}")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor(f"#{LINE}")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def build_pdf_report(session: Dict[str, Any]) -> bytes:
    output = BytesIO()
    styles = _pdf_styles()
    passages = _passage_lookup(session)
    document = SimpleDocTemplate(
        output,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=0.82 * inch,
        bottomMargin=0.72 * inch,
        title="SafeBARS Encounter Stress-Test Report",
        author="SafeBARS",
    )
    story: List[Any] = []
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("SAFEBARS REPORT", styles["title"]))
    story.append(_p(session.get("project", {}).get("title", "Untitled fieldwork plan"), styles["subtitle"]))
    story.append(_pdf_meta_table(session, styles))
    story.append(Spacer(1, 0.14 * inch))
    boundary = Table(
        [[Paragraph(
            "<b>Interpretation boundary.</b> This report contains planning hypotheses about the submitted "
            "protocol. It is not participant evidence, community representation, an ethics approval, or a "
            "prediction of real behavior.",
            styles["boundary"],
        )]],
        colWidths=[6.5 * inch],
    )
    boundary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(f"#{AMBER_FILL}")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D6B86A")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(boundary)

    story.append(Paragraph("1. Project context", styles["h1"]))
    story.append(_label_pdf("Context", session.get("project", {}).get("context"), styles["body"]))
    story.append(_label_pdf("People and relationships", session.get("project", {}).get("target_people"), styles["body"]))
    story.append(_label_pdf("Decision summary", _decision_summary(session), styles["body"]))

    story.append(Paragraph("2. Encounter map", styles["h1"]))
    map_rows = [[
        _p("Stage", styles["small"]), _p("Coverage", styles["small"]),
        _p("Scope", styles["small"]), _p("Sources / responsibility note", styles["small"]),
    ]]
    for stage in session.get("encounter_map", []):
        sources = ", ".join(stage.get("source_passage_ids", []))
        note = f"{sources} | {stage.get('notes')}" if stage.get("notes") else sources
        map_rows.append([
            _p(stage.get("name"), styles["small"]),
            _p(stage.get("coverage"), styles["small"]),
            _p("Included" if stage.get("included", True) else "Excluded", styles["small"]),
            _p(note or "None", styles["small"]),
        ])
    map_table = LongTable(map_rows, colWidths=[1.8 * inch, 0.9 * inch, 0.8 * inch, 3.0 * inch], repeatRows=1)
    map_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(f"#{LIGHT_GRAY}")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor(f"#{DARK_BLUE}")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(f"#{LINE}")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(map_table)

    story.append(Paragraph("3. Breakdown traces", styles["h1"]))
    if not session.get("traces"):
        story.append(_p("No scenario traces were run.", styles["body"]))
    for index, trace in enumerate(session.get("traces", []), start=1):
        block: List[Any] = [Paragraph(f"3.{index} {escape(_text(trace.get('title')))}", styles["h2"])]
        block.append(_label_pdf("Status", trace.get("status"), styles["body"]))
        for step in trace.get("steps", []):
            sources = ", ".join(step.get("source_passage_ids", [])) or "No cited passage"
            block.append(_label_pdf(step.get("label", "Trace step"), f"{_text(step.get('text'))} [Sources: {sources}]", styles["body"]))
        block.append(_label_pdf("First gap or coverage result", trace.get("first_gap"), styles["body"]))
        block.append(_label_pdf("Boundary", trace.get("uncertainty"), styles["body"]))
        story.extend(block)

    story.append(PageBreak())
    story.append(Paragraph("4. Issue ledger", styles["h1"]))
    if not session.get("issues"):
        story.append(_p("No contestable issues were produced in this session.", styles["body"]))
    for index, issue in enumerate(session.get("issues", []), start=1):
        story.append(Paragraph(f"4.{index} {escape(_text(issue.get('title')))}", styles["h2"]))
        story.append(_label_pdf(
            "Assessment",
            f"{_text(issue.get('severity')).upper()} | {_text(issue.get('decision')).upper()} | {_text(issue.get('agent'))}",
            styles["body"],
        ))
        story.append(_label_pdf("Observation", issue.get("observation"), styles["body"]))
        for passage_id in issue.get("source_passage_ids", []):
            passage = passages.get(passage_id)
            if passage:
                source_box = Table(
                    [[_label_pdf(f"Source {passage_id} - {passage.get('artifact_label', '')}", passage.get("text"), styles["small"])]],
                    colWidths=[6.5 * inch],
                )
                source_box.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(f"#{LIGHT_GRAY}")),
                    ("LINEBEFORE", (0, 0), (0, -1), 1.2, colors.HexColor(f"#{BLUE}")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]))
                story.append(source_box)
                story.append(Spacer(1, 3))
        story.append(_label_pdf("Proposed change", issue.get("suggestion"), styles["body"]))
        story.append(_label_pdf("Researcher revision", issue.get("revised_text", ""), styles["body"]))
        story.append(_label_pdf("Decision rationale", issue.get("decision_rationale", ""), styles["body"]))
        story.append(_label_pdf("Boundary", issue.get("uncertainty"), styles["body"]))

    story.append(Paragraph("5. Real-world handoffs", styles["h1"]))
    if not session.get("handoffs"):
        story.append(_p("No real-world handoffs were recorded.", styles["body"]))
    for index, handoff in enumerate(session.get("handoffs", []), start=1):
        story.append(Paragraph(f"5.{index} {escape(_text(handoff.get('question')))}", styles["h2"]))
        story.append(_label_pdf("Why AI cannot resolve this", handoff.get("why_ai_cannot_resolve"), styles["body"]))
        story.append(_label_pdf("Real-world owner", handoff.get("owner"), styles["body"]))

    story.append(PageBreak())
    story.append(Paragraph("Appendix A. Submitted materials", styles["h1"]))
    artifact_labels = {
        "recruitment": "Recruitment message",
        "consent": "Consent language",
        "interview": "Interview questions",
        "activity": "Workshop or activity plan",
        "safety": "Safety and escalation procedure",
        "follow_up": "Debrief, follow-up, and data use",
    }
    for key, label in artifact_labels.items():
        story.append(Paragraph(label, styles["h2"]))
        story.append(_p(session.get("artifacts", {}).get(key), styles["body"]))

    story.append(Paragraph("Appendix B. Audit event history", styles["h1"]))
    for event in session.get("event_log", []):
        story.append(_label_pdf(
            _date(event.get("created_at", "")),
            f"{event.get('event_type', 'event')} - {event.get('payload', {})}",
            styles["small"],
        ))

    document.build(story, onFirstPage=_pdf_header_footer, onLaterPages=_pdf_header_footer)
    return output.getvalue()
