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


def test_ranker_tie_break_order_and_fifo(monkeypatch):
    """Ranker must break ties strictly by:
    1. Overall score
    2. Must-have coverage
    3. Keyword match score
    4. Experience score
    5. Impact score
    6. FIFO (input index)
    """
    from app.services import ranker
    from app.schemas.scoring import MetricScore, ScoreResult

    jd = JDFeatures(
        title="Role",
        must_have_skills=["python", "fastapi"]
    )

    # 1. Test Tier 2: Equal overall_score, different must-have coverage
    res_a = ParsedResume(filename="a.pdf", contact=ContactInfo(name="Candidate A"))
    res_b = ParsedResume(filename="b.pdf", contact=ContactInfo(name="Candidate B"))

    def mock_score_tier2(res, jd, cfg):
        if res.filename == "a.pdf":
            # 1 of 2 must-haves
            return ScoreResult(
                overall_score=70.0,
                matched_keywords=["python"],
                metrics={"keyword_match": MetricScore(score=70.0), "experience": MetricScore(score=50.0), "impact": MetricScore(score=50.0)}
            )
        else:
            # 2 of 2 must-haves
            return ScoreResult(
                overall_score=70.0,
                matched_keywords=["python", "fastapi"],
                metrics={"keyword_match": MetricScore(score=70.0), "experience": MetricScore(score=50.0), "impact": MetricScore(score=50.0)}
            )

    monkeypatch.setattr(ranker, "score_resume_against_jd", mock_score_tier2)
    ranked = rank_resumes_batch([res_a, res_b], jd)
    assert ranked[0].candidate_name == "Candidate B", "Higher must-have coverage must rank first"
    assert ranked[1].candidate_name == "Candidate A"

    # 2. Test Tier 6: FIFO when all attributes are identical
    res_first = ParsedResume(filename="first.pdf", contact=ContactInfo(name="First In Line"))
    res_second = ParsedResume(filename="second.pdf", contact=ContactInfo(name="Second In Line"))

    def mock_score_fifo(res, jd, cfg):
        return ScoreResult(
            overall_score=80.0,
            matched_keywords=["python"],
            metrics={"keyword_match": MetricScore(score=80.0), "experience": MetricScore(score=80.0), "impact": MetricScore(score=80.0)}
        )

    monkeypatch.setattr(ranker, "score_resume_against_jd", mock_score_fifo)
    ranked_fifo = rank_resumes_batch([res_first, res_second], jd)
    assert ranked_fifo[0].candidate_name == "First In Line"
    assert ranked_fifo[1].candidate_name == "Second In Line"


def test_generate_candidates_csv_columns_and_injection():
    """CSV export must include all 11 required columns and neutralize injection across all text fields."""
    import csv as pycsv
    candidates = [
        RankedCandidate(
            rank=1,
            candidate_name="=cmd|' /C calc'!A0",
            filename="-malicious.pdf",
            overall_score=88.5,
            match_band="strong",
            must_have_coverage=100.0,
            years_experience=4.0,
            status="@reviewed",
            risk_flags=["+flag1", "=flag2"],
            metrics={
                "keyword_match": {"score": 90.0},
                "experience": {"score": 85.0},
                "impact": {"score": 80.0},
            }
        )
    ]

    csv_data = generate_candidates_csv(candidates)
    reader = list(pycsv.reader(csv_data.splitlines()))

    expected_headers = [
        "Rank", "Candidate Name", "File", "Overall Score", "Match Band",
        "Must-Have Coverage (%)", "Keyword Match Score", "Experience Score",
        "Impact Score", "Status", "Risk Flags"
    ]
    assert reader[0] == expected_headers, f"Headers mismatch: {reader[0]} vs {expected_headers}"
    assert len(reader) == 2, "Expected 1 header row + 1 data row"

    data_row = reader[1]
    assert len(data_row) == 11
    # Check injection neutralization
    assert data_row[1] == "'=cmd|' /C calc'!A0"
    assert data_row[2] == "'-malicious.pdf"
    assert data_row[9] == "'@reviewed"
    assert data_row[10] == "'+flag1; =flag2" or "'+flag1" in data_row[10]

