"""Unit tests for Resume PDF Templates and ATS Compatibility (app/services/pdf_generator.py)."""

import pytest
from app.schemas.resume import ParsedResume, WorkEntry, EduEntry, ContactInfo
from app.services.pdf_generator import generate_resume_pdf
from app.services.parser.pdf_parser import parse_pdf_bytes


@pytest.fixture
def candidate_profile():
    return ParsedResume(
        filename="test_template_candidate.pdf",
        contact=ContactInfo(
            name="Sarah Connor",
            email="sarah.connor@example.com",
            phone="+1-555-019-0144",
            location="Los Angeles, CA"
        ),
        summary="Experienced Machine Learning Engineer with deep expertise in PyTorch and neural networks.",
        skills=["python", "pytorch", "docker", "fastapi", "scikit-learn"],
        work_experience=[
            WorkEntry(
                id="1",
                title="ML Engineer",
                company="Cyberdyne Systems",
                dates="2021 - Present",
                bullets=[
                    "Spearheaded R&D on neural network architectures for real-time sensor processing.",
                    "Optimized model inference latency by 45% using TensorRT."
                ]
            )
        ],
        education=[
            EduEntry(
                id="1",
                institution="MIT",
                degree="Bachelor of Science in Computer Science",
                dates="2017 - 2021"
            )
        ],
        certifications=["AWS Machine Learning Specialty"],
        sections_detected=["summary", "skills", "experience", "education", "certifications"]
    )


@pytest.mark.parametrize("template_name", ["classic", "modern", "compact", "executive"])
def test_template_ats_safety(candidate_profile, template_name):
    """Every template must generate a valid PDF that parses with 1 column, all sections, and confidence >= 0.85."""
    pdf_bytes = generate_resume_pdf(candidate_profile, template=template_name)
    assert pdf_bytes.startswith(b"%PDF"), f"Template {template_name} failed to generate valid PDF header"

    parsed = parse_pdf_bytes(pdf_bytes, filename=f"test_{template_name}.pdf")

    # 1. Single-column layout
    assert parsed.detected_columns == 1, f"Template {template_name} generated multi-column layout"

    # 2. Required sections detected
    sections = parsed.sections_detected
    assert "experience" in sections, f"Template {template_name} failed to isolate experience section"
    assert "education" in sections, f"Template {template_name} failed to isolate education section"
    assert "skills" in sections, f"Template {template_name} failed to isolate skills section"

    # 3. High parse confidence
    assert parsed.parse_confidence >= 0.85, f"Template {template_name} parse confidence below 0.85"

    # 4. Contact recovery: email & phone must survive
    assert parsed.contact.email == "sarah.connor@example.com", f"Template {template_name} lost email"
    assert parsed.contact.phone is not None and "0144" in parsed.contact.phone, f"Template {template_name} lost phone"

    # 5. Work experience bullets and dates recovery
    all_bullets = [b for w in parsed.work_experience for b in w.bullets]
    assert len(all_bullets) >= 2, f"Template {template_name} lost bullets, recovered: {all_bullets}"
    assert any("R&D" in b for b in all_bullets), f"Template {template_name} corrupted 'R&D' in bullets: {all_bullets}"

    # Dates recovered in work or education
    dates_found = [w.dates for w in parsed.work_experience if w.dates] + [e.dates for e in parsed.education if e.dates]
    assert any("2021" in d for d in dates_found), f"Template {template_name} lost dates: {dates_found}"
