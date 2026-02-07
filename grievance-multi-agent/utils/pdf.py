from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import os
import re


def generate_complaint_pdf(markdown_text: str, filename="complaint.pdf") -> str:
    output_dir = "exports"
    os.makedirs(output_dir, exist_ok=True)

    path = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Heading",
        fontSize=14,
        spaceAfter=12,
        spaceBefore=12,
        leading=16,
        fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="Bold",
        fontSize=10,
        fontName="Helvetica-Bold"
    ))

    story = []

    lines = markdown_text.split("\n")
    bullet_buffer = []

    def flush_bullets():
        nonlocal bullet_buffer
        if bullet_buffer:
            story.append(
                ListFlowable(
                    [ListItem(Paragraph(b, styles["Normal"])) for b in bullet_buffer],
                    bulletType="bullet",
                    start="•"
                )
            )
            bullet_buffer = []

    for line in lines:
        line = line.strip()

        # Headings (## or **1. Title**)
        if re.match(r"^\*\*\d+\.", line) or line.startswith("**") and line.endswith("**"):
            flush_bullets()
            story.append(Paragraph(line.strip("*"), styles["Heading"]))
            continue

        # Bullet points
        if line.startswith("- ") or line.startswith("•"):
            bullet_buffer.append(line.lstrip("-• ").strip())
            continue

        # Blockquote
        if line.startswith(">"):
            flush_bullets()
            story.append(Paragraph(
                f"<i>{line[1:].strip()}</i>",
                styles["Normal"]
            ))
            story.append(Spacer(1, 0.1 * inch))
            continue

        # Empty line
        if not line:
            flush_bullets()
            story.append(Spacer(1, 0.15 * inch))
            continue

        # Bold text
        line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)

        flush_bullets()
        story.append(Paragraph(line, styles["Normal"]))

    flush_bullets()
    doc.build(story)
    return path
