"""Unit tests for Candidate Ranker and CSV Export (app/services/ranker.py & app/routers/export.py)."""

import pytest
from app.schemas.resume import ParsedResume, WorkEntry, ContactInfo
from app.schemas.jd import JDFeatures
from app.schemas.scoring import RankedCandidate
from app.services.ranker import rank_resumes_batch, generate_candidates_csv


def test_ranker_uses_estimate_years_of_experience():
    """Ranker must use estimate_years_of_experience rather than 2.0 * len(work_experience)."""
    # 1 role spanning Jan 2020 to Jan 2025 (~5 years)
    resume = ParsedResume(
        filename="experienced_dev.pdf",
        contact=ContactInfo(name="Alex Dev"),
        skills=["python"],
        work_experience=[
            WorkEntry(
                id="w1",
                title="Software Engineer",
                company="TechCorp",
                dates="Jan 2020 - Jan 2025",
                bullets=["Built Python services"]
            )
        ]
    )
    jd = JDFeatures(title="Python Dev", must_have_skills=["python"])

    ranked = rank_resumes_batch([resume], jd)
    assert len(ranked) == 1
    # 2.0 * 1 role would be 2.0, whereas estimate_years_of_experience returns ~5.1 years
    assert ranked[0].years_experience > 4.0, (
        f"Expected estimated years > 4.0, got {ranked[0].years_experience} (likely using 2.0 * num_roles)"
    )


def test_generate_candidates_csv_neutralizes_injection():
    """CSV cells beginning with =, +, -, @ must be prefixed with a single quote."""
    candidates = [
        RankedCandidate(
            rank=1,
            candidate_name="=CMD|' /C calc'!A0",
            filename="-payload.pdf",
            overall_score=85.0,
            match_band="strong",
            must_have_coverage=100.0,
            years_experience=5.0,
            status="@admin",
            risk_flags=["+dangerous_flag"],
            metrics={}
        )
    ]
    csv_text = generate_candidates_csv(candidates)
    lines = [line.strip() for line in csv_text.splitlines() if line.strip()]
    data_line = lines[1]

    # Verify formula injection characters are neutralised
    assert "'=CMD" in data_line, "Formula starting with = must be prefixed with '"
    assert "'-payload.pdf" in data_line, "Filename starting with - must be prefixed with '"
    assert "'@admin" in data_line, "Cell starting with @ must be prefixed with '"
    assert "'+dangerous_flag" in data_line, "Cell starting with + must be prefixed with '"


def test_export_pdf_sanitizes_content_disposition():
    """The export-pdf route must sanitize filenames in Content-Disposition against CRLF/quotes."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    resume_payload = {
        "filename": "test.pdf",
        "contact": {"name": "Evil\r\nInjected-Header: bad; \"quote\" name"},
        "summary": "Summary",
        "skills": ["python"],
        "work_experience": [],
        "education": []
    }
    resp = client.post("/api/export-pdf?template=classic", json=resume_payload)
    assert resp.status_code == 200
    cd_header = resp.headers.get("Content-Disposition", "")
    assert "\r" not in cd_header, "Content-Disposition must not contain carriage returns"
    assert "\n" not in cd_header, "Content-Disposition must not contain newlines"
    assert '"quote"' not in cd_header, "Quotes must be stripped from the filename"
    # Ensure there is no second semicolon injected
    assert cd_header.count(";") == 1, "Only one semicolon allowed for 'attachment; filename=...'"
