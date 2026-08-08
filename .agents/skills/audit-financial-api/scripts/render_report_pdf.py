#!/usr/bin/env python3
"""Render the Markdown audit report as a polished, Cyrillic-safe PDF."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#1677A6")
PALE_BLUE = colors.HexColor("#EAF4F8")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")
BORDER = colors.HexColor("#BCCCDC")
PAPER = colors.HexColor("#F8FAFC")


def find_font(names: Iterable[str]) -> Path | None:
    for value in names:
        path = Path(value)
        if path.exists():
            return path
    return None


def register_fonts() -> tuple[str, str]:
    regular = find_font([
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ])
    bold = find_font([
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    ])
    if not regular or not bold:
        raise SystemExit("Cyrillic-capable Arial, Segoe UI, or DejaVu Sans fonts are required")
    pdfmetrics.registerFont(TTFont("AuditSans", str(regular)))
    pdfmetrics.registerFont(TTFont("AuditSansBold", str(bold)))
    pdfmetrics.registerFontFamily(
        "AuditSans",
        normal="AuditSans",
        bold="AuditSansBold",
        italic="AuditSans",
        boldItalic="AuditSansBold",
    )
    return "AuditSans", "AuditSansBold"


def inline_markup(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<link href="\2" color="#1677A6"><u>\1</u></link>',
        escaped,
    )
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(
        r"\x60([^\x60]+)\x60",
        r'<font color="#334E68" backColor="#EAF4F8">\1</font>',
        escaped,
    )
    return escaped


def styles(normal_font: str, bold_font: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "AuditTitle",
            parent=base["Title"],
            fontName=bold_font,
            fontSize=19,
            leading=23,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=7 * mm,
        ),
        "h2": ParagraphStyle(
            "AuditH2",
            parent=base["Heading2"],
            fontName=bold_font,
            fontSize=13.5,
            leading=16,
            textColor=NAVY,
            spaceBefore=5 * mm,
            spaceAfter=1.5 * mm,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "AuditH3",
            parent=base["Heading3"],
            fontName=bold_font,
            fontSize=10.5,
            leading=13,
            textColor=BLUE,
            spaceBefore=3 * mm,
            spaceAfter=1.5 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "AuditBody",
            parent=base["BodyText"],
            fontName=normal_font,
            fontSize=8.8,
            leading=12,
            textColor=INK,
            spaceAfter=1.5 * mm,
        ),
        "bullet": ParagraphStyle(
            "AuditBullet",
            parent=base["BodyText"],
            fontName=normal_font,
            fontSize=8.6,
            leading=11.5,
            textColor=INK,
            leftIndent=5 * mm,
            firstLineIndent=-3.5 * mm,
            spaceAfter=1 * mm,
        ),
        "table": ParagraphStyle(
            "AuditTable",
            parent=base["BodyText"],
            fontName=normal_font,
            fontSize=6.9,
            leading=9.3,
            textColor=INK,
            wordWrap="CJK",
        ),
        "table_header": ParagraphStyle(
            "AuditTableHeader",
            parent=base["BodyText"],
            fontName=bold_font,
            fontSize=7,
            leading=9.3,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "code": ParagraphStyle(
            "AuditCode",
            parent=base["Code"],
            fontName=normal_font,
            fontSize=7.7,
            leading=10.2,
            textColor=INK,
            backColor=PALE_BLUE,
            leftIndent=3 * mm,
            rightIndent=3 * mm,
            borderPadding=3 * mm,
            spaceAfter=1.5 * mm,
        ),
    }


def table_flowable(rows: list[list[str]], style_map: dict[str, ParagraphStyle], width: float) -> Table:
    column_count = max(len(row) for row in rows)
    normalized = [row + [""] * (column_count - len(row)) for row in rows]
    data = []
    for row_index, row in enumerate(normalized):
        style = style_map["table_header"] if row_index == 0 else style_map["table"]
        data.append([Paragraph(inline_markup(cell), style) for cell in row])
    if column_count == 5:
        weights = [0.10, 0.13, 0.12, 0.34, 0.31]
    else:
        weights = [1 / column_count] * column_count
    table = Table(
        data,
        colWidths=[width * weight for weight in weights],
        repeatRows=1,
        hAlign="LEFT",
    )
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.1 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.1 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 1.7 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.7 * mm),
    ]
    for row_index in range(1, len(data)):
        if row_index % 2 == 0:
            commands.append(("BACKGROUND", (0, row_index), (-1, row_index), PAPER))
    table.setStyle(TableStyle(commands))
    return table


def parse_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows: list[list[str]] = []
    index = start
    while index < len(lines) and lines[index].strip().startswith("|"):
        cells = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
        if index != start + 1 or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            rows.append(cells)
        index += 1
    return rows, index


def markdown_story(text: str, style_map: dict[str, ParagraphStyle], width: float) -> list:
    lines = text.splitlines()
    story: list = []
    paragraph: list[str] = []
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph)), style_map["body"]))
            paragraph.clear()

    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if stripped.startswith(chr(96) * 3):
            flush_paragraph()
            if in_code:
                story.append(Preformatted("\n".join(code_lines), style_map["code"]))
                code_lines.clear()
                in_code = False
            else:
                in_code = True
            index += 1
            continue
        if in_code:
            code_lines.append(raw)
            index += 1
            continue
        if stripped.startswith("|"):
            flush_paragraph()
            rows, index = parse_table(lines, index)
            story.append(table_flowable(rows, style_map, width))
            story.append(Spacer(1, 3 * mm))
            continue
        if not stripped:
            flush_paragraph()
            index += 1
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), style_map["title"]))
        elif stripped.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[3:]), style_map["h2"]))
        elif stripped.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[4:]), style_map["h3"]))
        elif re.match(r"^[-*]\s+", stripped):
            flush_paragraph()
            item = re.sub(r"^[-*]\s+", "", stripped)
            story.append(
                Paragraph(inline_markup(item), style_map["bullet"], bulletText="•")
            )
        elif re.match(r"^\d+\.\s+", stripped):
            flush_paragraph()
            match = re.match(r"^(\d+)\.\s+(.*)", stripped)
            assert match
            story.append(
                Paragraph(
                    inline_markup(match.group(2)),
                    style_map["bullet"],
                    bulletText=match.group(1) + ".",
                )
            )
        else:
            paragraph.append(stripped)
        index += 1
    flush_paragraph()
    if code_lines:
        story.append(Preformatted("\n".join(code_lines), style_map["code"]))
    return story


def render(input_path: Path, output_path: Path, document_title: str) -> None:
    normal, bold = register_fonts()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    left = right = 16 * mm
    usable_width = A4[0] - left - right
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=left,
        rightMargin=right,
        topMargin=19 * mm,
        bottomMargin=14 * mm,
        title=document_title,
        author="audit-financial-api",
        subject="Financial API data-quality audit",
    )
    style_map = styles(normal, bold)
    story = markdown_story(input_path.read_text(encoding="utf-8"), style_map, usable_width)

    def page(canvas, document) -> None:
        canvas.saveState()
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.4)
        canvas.line(left, A4[1] - 12 * mm, A4[0] - right, A4[1] - 12 * mm)
        canvas.setFont(normal, 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(left, A4[1] - 9.4 * mm, document_title[:95])
        canvas.drawRightString(
            A4[0] - right, 9 * mm, f"Страница {document.page}"
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=page, onLaterPages=page)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_markdown")
    parser.add_argument("output_pdf")
    parser.add_argument("--title", default="Аудит финансового API")
    args = parser.parse_args()
    render(Path(args.input_markdown), Path(args.output_pdf), args.title)
    print(Path(args.output_pdf).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
