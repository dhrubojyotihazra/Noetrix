"""Tests for PDF parser improvements (Item 12):
- ProjectEntry technologies field populated (not ignored tech_stack)
- Column and sidebar layout detection clustering word x-positions and per-page tracking
- Parse confidence computed from sections, bullets, and contact completeness
- Degree string stripped of dates, and dates extracted to EduEntry.dates
"""

import pytest
from app.services.parser.pdf_parser import parse_pdf_bytes, detect_page_columns, compute_parse_confidence
from app.schemas.resume import ContactInfo, WorkEntry, ProjectEntry, EduEntry


def test_project_technologies_populated():
    """Verify ProjectEntry.technologies is populated from header and tech stack lines."""
    resume_text = """
John Doe
john@example.com | 555-123-4567

PROJECTS
Smart Search Engine | Python, Elasticsearch, FastAPI | 2023
- Built semantic retrieval engine indexing 1M documents
- Tech Stack: Redis, Docker, PyTorch

EXPERIENCE
Software Engineer | Acme Corp | 2022 - 2023
- Developed backend services
"""
    parsed = parse_pdf_bytes(resume_text.encode("utf-8"), filename="test_proj.pdf")
    assert len(parsed.projects) >= 1
    proj = parsed.projects[0]
    assert "Smart Search Engine" in proj.name
    # Check that technologies list is populated and contains items from both header and tech stack line
    techs_lower = [t.lower() for t in proj.technologies]
    assert any("python" in t for t in techs_lower)
    assert any("elasticsearch" in t or "fastapi" in t for t in techs_lower)
    assert any("redis" in t or "pytorch" in t for t in techs_lower)


def test_education_dates_stripped_from_degree():
    """Verify that graduation dates are stripped from the degree string and saved to dates."""
    resume_text = """
Jane Doe
jane@example.com | 555-987-6543

EDUCATION
University of California, Berkeley
Bachelor of Science in Computer Science (2018 - 2022)

EXPERIENCE
Developer | Tech Inc | 2022 - Present
- Built scalable web APIs
"""
    parsed = parse_pdf_bytes(resume_text.encode("utf-8"), filename="test_edu.pdf")
    assert len(parsed.education) >= 1
    edu = parsed.education[0]
    assert "2018" not in edu.degree
    assert "2022" not in edu.degree
    assert "Bachelor of Science in Computer Science" in edu.degree
    assert "2018 - 2022" in edu.dates or "2018" in edu.dates


def test_detect_page_columns_clustering():
    """Verify two-column and sidebar detection on word x-positions."""
    # 1. Single column: words span full width
    single_col_words = [
        {"text": f"word_{i}", "x0": 50.0, "x1": 550.0, "top": i * 15.0, "bottom": i * 15.0 + 10.0}
        for i in range(50)
    ]
    assert detect_page_columns(single_col_words, page_width=600.0) == 1

    # 2. Balanced two-column: words in left (x=50..250) and right (x=350..550), middle gutter empty
    two_col_words = []
    for i in range(30):
        two_col_words.append({"text": f"left_{i}", "x0": 50.0, "x1": 240.0, "top": i * 15.0, "bottom": i * 15.0 + 10.0})
        two_col_words.append({"text": f"right_{i}", "x0": 360.0, "x1": 550.0, "top": i * 15.0, "bottom": i * 15.0 + 10.0})
    assert detect_page_columns(two_col_words, page_width=600.0) == 2

    # 3. Sidebar layout: words in left 25% (x=30..150) and right 75% (x=210..550), gutter at ~30%
    sidebar_words = []
    for i in range(20):
        sidebar_words.append({"text": f"side_{i}", "x0": 30.0, "x1": 150.0, "top": i * 20.0, "bottom": i * 20.0 + 10.0})
    for i in range(40):
        sidebar_words.append({"text": f"main_{i}", "x0": 210.0, "x1": 550.0, "top": i * 12.0, "bottom": i * 12.0 + 10.0})
    assert detect_page_columns(sidebar_words, page_width=600.0) == 2


def test_compute_parse_confidence_nuanced():
    """Verify parse_confidence is computed from sections, bullets, and contact completeness."""
    # Complete resume: 5 sections, 6 bullets, all 3 contact items
    high_conf = compute_parse_confidence(
        sections_detected=["summary", "experience", "education", "skills", "projects"],
        work_entries=[WorkEntry(bullets=["B1", "B2", "B3", "B4"])],
        project_entries=[ProjectEntry(bullets=["P1", "P2"])],
        contact=ContactInfo(name="Alice", email="alice@test.com", phone="1234567890")
    )
    assert high_conf >= 0.95

    # Sparse resume: 1 section, 0 bullets, 0 contact items
    low_conf = compute_parse_confidence(
        sections_detected=["skills"],
        work_entries=[],
        project_entries=[],
        contact=ContactInfo()
    )
    assert low_conf <= 0.35
