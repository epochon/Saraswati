from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
import re
import os


def generate_complaint_pdf(content: str, filename="complaint.pdf") -> str:
    """
    Generates a well-formatted PDF from Markdown-like text.
    Returns the path to the generated PDF.
    """

    output_path = os.path.join(os.getcwd(), filename)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # --- Custom styles (unique names only) ---
    styles.add(
        ParagraphStyle(
            name="TitleStyle",
            fontSize=16,
            leading=20,
            spaceAfter=14,
            spaceBefore=10,
            alignment=TA_LEFT,
            fontName="Helvetica-Bold",
        )
    )

    styles.add(
        ParagraphStyle(
            name="HeaderStyle",
            fontSize=13,
            leading=16,
            spaceAfter=10,
            spaceBefore=12,
            fontName="Helvetica-Bold",
        )
    )

    styles.add(
        ParagraphStyle(
            name="BodyStyle",
            fontSize=10.5,
            leading=14,
            spaceAfter=8,
            fontName="Helvetica",
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallItalic",
            fontSize=9.5,
            leading=12,
            spaceAfter=8,
            fontName="Helvetica-Oblique",
        )
    )

    flowables = []

    lines = content.splitlines()
    bullet_buffer = []

    def flush_bullets():
        nonlocal bullet_buffer
        if bullet_buffer:
            flowables.append(
                ListFlowable(
                    [
                        ListItem(
                            Paragraph(item, styles["BodyStyle"])
                        )
                        for item in bullet_buffer
                    ],
                    bulletType="bullet",
                    start="circle",
                    leftIndent=18,
                )
            )
            bullet_buffer = []

    for raw_line in lines:
        line = raw_line.strip()

        # Empty line
        if not line:
            flush_bullets()
            flowables.append(Spacer(1, 0.12 * inch))
            continue

        # Markdown headings
        if re.match(r"^\*\*.+\*\*$", line):
            flush_bullets()
            text = line.strip("*")
            flowables.append(Paragraph(text, styles["HeaderStyle"]))
            continue

        # Numbered headings (e.g., "1. Legal Strength Rating")
        if re.match(r"^\d+\.\s+", line):
            flush_bullets()
            flowables.append(Paragraph(line, styles["HeaderStyle"]))
            continue

        # Bullet points
        if line.startswith("- ") or line.startswith("•"):
            bullet_buffer.append(line.lstrip("-• ").strip())
            continue

        # Quoted / note blocks
        if line.lower().startswith("note:"):
            flush_bullets()
            flowables.append(Paragraph(line, styles["SmallItalic"]))
            continue

        # Default paragraph
        flush_bullets()
        flowables.append(Paragraph(line, styles["BodyStyle"]))

    flush_bullets()

    doc.build(flowables)

    return output_path
