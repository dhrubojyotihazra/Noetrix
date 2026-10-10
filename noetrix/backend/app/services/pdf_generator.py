"""Generate clean, ATS-compliant single-column resume PDFs using ReportLab across 4 templates.

Templates:
1. 'classic' - ATS Standard (clean monochrome rules, standard margins, timeless typography)
2. 'modern' - Modern Minimal (subtle blue accents, clean section rules, structured headers)
3. 'compact' - Technical Compact (dense engineering layout, minimal spacers, high information density)
4. 'executive' - Executive Single-Column (elevated title banner, refined spacing)
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

from app.schemas.resume import ParsedResume


def generate_resume_pdf(resume: ParsedResume, template: str = "classic") -> bytes:
    """Render an ATS-optimized single-column PDF resume in the specified template style."""
    template_lower = (template or "classic").lower().strip()

    # Determine layout properties per template
    if template_lower == "compact":
        margin = 28
        h_color = colors.HexColor("#000000")
        accent_color = colors.HexColor("#000000")
        title_size = 18
        section_size = 10
        body_size = 8.5
        body_leading = 11
        spacer_h = 2
    elif template_lower == "modern":
        margin = 32
        h_color = colors.HexColor("#0F172A")
        accent_color = colors.HexColor("#2563EB")
        title_size = 20
        section_size = 11
        body_size = 9
        body_leading = 12
        spacer_h = 3
    elif template_lower == "executive":
        margin = 36
        h_color = colors.HexColor("#0F172A")
        accent_color = colors.HexColor("#0F172A")
        title_size = 22
        section_size = 11.5
        body_size = 9.5
        body_leading = 13
        spacer_h = 4
    else:  # classic
        margin = 36
        h_color = colors.HexColor("#0C0F17")
        accent_color = colors.HexColor("#666666")
        title_size = 20
        section_size = 11
        body_size = 9.5
        body_leading = 13
        spacer_h = 4

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ResumeTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=title_size,
        leading=title_size + 4,
        textColor=h_color,
        spaceAfter=2
    )

    contact_style = ParagraphStyle(
        "ResumeContact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=body_size - 0.5,
        leading=body_leading,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=8
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=section_size,
        leading=section_size + 3,
        textColor=accent_color,
        spaceBefore=6,
        spaceAfter=2,
        textTransform="uppercase"
    )

    job_title_style = ParagraphStyle(
        "JobTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=body_size + 0.5,
        leading=body_leading + 1,
        textColor=h_color
    )

    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=body_size,
        leading=body_leading,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        "ResumeBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=body_size,
        leading=body_leading,
        textColor=colors.HexColor("#1F2937"),
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2
    )

    story = []

    # 1. Header (Name & Contact)
    candidate_name = resume.contact.name or resume.filename.replace(".pdf", "").replace("_", " ").title()
    story.append(Paragraph(candidate_name, title_style))

    contact_bits = []
    if resume.contact.email:
        contact_bits.append(resume.contact.email)
    if resume.contact.phone:
        contact_bits.append(resume.contact.phone)
    if resume.contact.location:
        loc = resume.contact.location.replace("\n", " ").strip()
        contact_bits.append(loc)
    if resume.contact.linkedin:
        contact_bits.append("LinkedIn")
    if resume.contact.github:
        contact_bits.append("GitHub")

    contact_line = " &nbsp;|&nbsp; ".join(contact_bits) if contact_bits else "Contact information"
    story.append(Paragraph(contact_line, contact_style))
    story.append(HRFlowable(width="100%", thickness=1.0, color=accent_color, spaceAfter=6))

    # 2. Professional Summary
    if resume.summary and resume.summary.strip():
        story.append(Paragraph("Professional Summary", section_heading))
        story.append(Paragraph(resume.summary.strip(), body_style))
        story.append(Spacer(1, spacer_h))

    # 3. Technical Skills
    if resume.skills:
        story.append(Paragraph("Technical Skills", section_heading))
        skills_str = " &nbsp;&bull;&nbsp; ".join(resume.skills)
        story.append(Paragraph(skills_str, body_style))
        story.append(Spacer(1, spacer_h))

    # 4. Work Experience
    if resume.work_experience:
        story.append(Paragraph("Work Experience", section_heading))
        for exp in resume.work_experience:
            header_text = f"<b>{exp.title}</b>"
            if exp.company:
                header_text += f" &nbsp;—&nbsp; {exp.company}"
            if exp.dates:
                header_text += f" &nbsp;({exp.dates})"
            story.append(Paragraph(header_text, job_title_style))

            for bullet in exp.bullets:
                clean_b = bullet.strip().lstrip("-•*–—> ")
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{clean_b}", bullet_style))
            story.append(Spacer(1, spacer_h))

    # 5. Projects
    if resume.projects:
        story.append(Paragraph("Projects", section_heading))
        for proj in resume.projects:
            proj_header = f"<b>{proj.name}</b>"
            tech_str = ""
            if getattr(proj, "technologies", None):
                tech_str = ", ".join(proj.technologies) if isinstance(proj.technologies, list) else str(proj.technologies)
            elif getattr(proj, "tech_stack", None):
                tech_str = str(proj.tech_stack)
            if tech_str:
                proj_header += f" &nbsp;[{tech_str}]"
            story.append(Paragraph(proj_header, job_title_style))

            for bullet in proj.bullets:
                clean_b = bullet.strip().lstrip("-•*–—> ")
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{clean_b}", bullet_style))
            story.append(Spacer(1, spacer_h))

    # 6. Education
    if resume.education:
        story.append(Paragraph("Education", section_heading))
        for edu in resume.education:
            edu_str = f"<b>{edu.institution}</b>"
            if edu.degree:
                edu_str += f" &nbsp;—&nbsp; {edu.degree}"
            story.append(Paragraph(edu_str, job_title_style))
            for bullet in edu.bullets:
                clean_b = bullet.strip().lstrip("-•*–—> ")
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{clean_b}", bullet_style))
            story.append(Spacer(1, spacer_h))

    # 7. Certifications
    if resume.certifications:
        story.append(Paragraph("Certifications & Credentials", section_heading))
        for cert in resume.certifications:
            clean_c = cert.strip().lstrip("-•*–—> ")
            story.append(Paragraph(f"&bull;&nbsp;&nbsp;{clean_c}", bullet_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
