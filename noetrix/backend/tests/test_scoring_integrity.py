"""Unit tests for Scoring Engine Integrity and Determinism (app/services/scorer/engine.py)."""

import pytest
from app.schemas.resume import ParsedResume, WorkEntry, EduEntry, ContactInfo
from app.schemas.jd import JDFeatures
from app.schemas.scoring import ScoringConfig, MetricScore
from app.services.scorer.engine import score_resume_against_jd
from app.services.improver import tailor_resume_to_jd



@pytest.fixture
def sample_data():
    resume = ParsedResume(
        filename="test_candidate.pdf",
        contact=ContactInfo(name="Alex Smith", email="alex@example.com"),
        summary="Backend developer with Python and FastAPI expertise.",
        skills=["python", "fastapi", "docker", "postgresql"],
        work_experience=[
            WorkEntry(
                id="1",
                title="Backend Engineer",
                company="DataFlow",
                dates="2022 - 2024",
                bullets=[
                    "Built FastAPI microservices handling 2,000 RPS.",
                    "Optimized PostgreSQL queries reducing latency by 30%."
                ]
            )
        ],
        education=[
            EduEntry(
                id="1",
                institution="State University",
                degree="Bachelor of Science in Computer Science",
                dates="2018 - 2022"
            )
        ],
        sections_detected=["summary", "skills", "experience", "education"]
    )

    jd = JDFeatures(
        title="Python Backend Engineer",
        raw_text="Requirements: Python, FastAPI, Docker, PostgreSQL. 2+ years experience.",
        must_have_skills=["python", "fastapi", "docker", "postgresql"],
        nice_to_have_skills=["aws", "redis"],
        min_experience_years=2.0
    )
    return resume, jd


def test_scorer_is_deterministic(sample_data):
    """Same resume + same JD must ALWAYS return identical scoreResult."""
    resume, jd = sample_data

    score1 = score_resume_against_jd(resume, jd)
    score2 = score_resume_against_jd(resume, jd)

    assert score1.overall_score == score2.overall_score
    assert score1.matched_keywords == score2.matched_keywords
    assert score1.match_band == score2.match_band
    for k in score1.metrics:
        assert score1.metrics[k].score == score2.metrics[k].score


def test_tailoring_gain_matches_actual_score_delta(sample_data):
    """Estimated score gain in tailoring must equal actual post-tailoring score minus baseline."""
    resume, jd = sample_data

    tailored_res = tailor_resume_to_jd(resume, jd)

    baseline_score = score_resume_against_jd(resume, jd).overall_score
    after_score = score_resume_against_jd(tailored_res.tailored_resume, jd).overall_score

    expected_gain = round(max(0.0, after_score - baseline_score), 1)
    assert tailored_res.estimated_gain == expected_gain
    assert tailored_res.estimated_score_before == baseline_score
    assert tailored_res.estimated_score_after == after_score


def test_capped_cv_gets_weak_band():
    """A CV that triggers the soft knockout cap must get band 'weak' instead of 'moderate'."""
    resume = ParsedResume(
        filename="capped_candidate.pdf",
        contact=ContactInfo(name="Bob Smith", email="bob@example.com"),
        summary="Senior Software Engineer with 8 years of experience.",
        skills=["python"],  # only 1 skill out of 4 must-haves (25% coverage < 50%)
        work_experience=[
            WorkEntry(
                id="1",
                title="Software Engineer",
                company="TechCorp",
                dates="2016 - 2024",
                bullets=[
                    "Engineered Python backends serving 50,000 users with 99.9% uptime.",
                    "Reduced database query times by 40% across PostgreSQL clusters."
                ]
            )
        ],
        education=[EduEntry(id="1", institution="MIT", degree="Master of Science in Computer Science", dates="2014 - 2016")],
        sections_detected=["summary", "skills", "experience", "education"]
    )
    jd = JDFeatures(
        title="ML Platform Engineer",
        raw_text="Requirements: pytorch, docker, kubernetes, terraform. 5+ years experience.",
        must_have_skills=["pytorch", "docker", "kubernetes", "terraform"],
        nice_to_have_skills=["python"],
        min_experience_years=5.0
    )

    res = score_resume_against_jd(resume, jd)
    assert res.is_capped is True, "Candidate with 0/4 must-haves and high composite score must be capped"
    assert res.overall_score == 50.0, "Capped score must equal 50.0"
    assert res.match_band == "weak", f"Capped score must be classified as 'weak', got '{res.match_band}'"


def test_keyword_stuffing_does_not_jump_sales_cv_to_moderate():
    """A sales CV stuffed with all JD must-have skills in its skills list must not jump to moderate."""
    from scripts.run_regression import build_canonical_sample_cvs
    from app.services.jd_parser import parse_job_description
    import copy

    jd = parse_job_description(
        "Role: ML Engineer\nMust Have: python, pytorch, scikit-learn, sql, docker, fastapi, pandas, numpy\n"
    )
    cvs = build_canonical_sample_cvs()
    sales_cv = cvs[5]  # cv_06_non_technical
    stuffed_cv = copy.deepcopy(sales_cv)
    stuffed_cv.skills = ["python", "pytorch", "scikit-learn", "sql", "docker", "fastapi", "pandas", "numpy", "sales", "crm"]

    res = score_resume_against_jd(stuffed_cv, jd)
    assert res.match_band == "weak", f"Expected 'weak', got '{res.match_band}' with score {res.overall_score}"
    assert res.overall_score <= 50.0, f"Expected score <= 50.0, got {res.overall_score}"


def test_estimate_years_of_experience_respects_reference_date_and_env(monkeypatch):
    """estimate_years_of_experience must use reference_date or env override instead of hardcoded 2026."""
    from datetime import date
    from app.services.scorer.experience_scorer import estimate_years_of_experience

    resume = ParsedResume(
        work_experience=[
            WorkEntry(
                id="w1",
                title="Software Engineer",
                company="Acme Corp",
                dates="Jan 2020 - Present",
                bullets=["Built distributed services"]
            )
        ]
    )

    # With reference_date in 2030 (10.1 years experience: Jan 2020 to Jan 2030 = 121 mos)
    tenure_2030 = estimate_years_of_experience(resume, reference_date=date(2030, 1, 1))
    assert tenure_2030 == 10.1, f"Expected 10.1 years in 2030, got {tenure_2030}"

    # With env override
    monkeypatch.setenv("NOETRIX_CURRENT_DATE", "2028-01-01")
    tenure_2028 = estimate_years_of_experience(resume)
    assert tenure_2028 == 8.1, f"Expected 8.1 years in 2028, got {tenure_2028}"


def test_explain_endpoint_returns_grounded_explanation(sample_data):
    """Test that /api/explain returns a grounded explanation with generated_by metadata."""
    from fastapi.testclient import TestClient
    from app.main import app

    resume, jd = sample_data
    client = TestClient(app)
    resp = client.post(
        "/api/explain",
        json={
            "resume": resume.model_dump(),
            "jd": jd.model_dump(),
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data and len(data["summary"]) > 0
    assert "strengths" in data
    assert "gaps" in data
    assert "fixes" in data
    assert "generated_by" in data
    assert data["generated_by"] in ["rules", "llm"]


def test_cap_fires_only_below_half_coverage():
    """Must-have cap (50.0 points and 'weak' band) fires ONLY when fewer than half of must-haves match."""
    jd = JDFeatures(
        title="Senior Python Backend",
        raw_text="Requires Python, FastAPI, Docker, and PostgreSQL with 5+ years experience.",
        must_have_skills=["python", "fastapi", "docker", "postgresql"],  # 4 must-haves
        min_experience_years=5.0,
    )

    def make_candidate(skills_in_bullets: list[str]) -> ParsedResume:
        bullets = [
            f"Engineered backends with {s} handling 50,000 requests per minute with 99.9% uptime."
            for s in skills_in_bullets
        ]
        # Add quantified impact bullet
        bullets.append("Optimized distributed caching layer reducing latency by 45%.")
        return ParsedResume(
            filename="candidate.pdf",
            contact=ContactInfo(name="Candidate"),
            summary="Senior Software Engineer with 8 years of backend engineering experience.",
            skills=skills_in_bullets,
            work_experience=[
                WorkEntry(
                    id="w1",
                    title="Senior Software Engineer",
                    company="TechCorp",
                    dates="2016 - 2024",
                    bullets=bullets,
                )
            ],
            education=[
                EduEntry(
                    id="e1",
                    institution="MIT",
                    degree="Master of Science in Computer Science",
                    dates="2012 - 2016",
                )
            ],
            sections_detected=["summary", "skills", "experience", "education"],
        )

    # 1 of 4 (25% < 50%): CAP FIRES
    cv_1 = make_candidate(["python"])
    score_1 = score_resume_against_jd(cv_1, jd)
    assert score_1.is_capped is True
    assert score_1.match_band == "weak"
    assert score_1.overall_score <= 50.0

    # 2 of 4 (50% >= 50%): CAP DOES NOT FIRE
    cv_2 = make_candidate(["python", "fastapi"])
    score_2 = score_resume_against_jd(cv_2, jd)
    assert score_2.is_capped is False
    assert score_2.overall_score > 50.0

    # 3 of 4 (75% >= 50%): CAP DOES NOT FIRE
    cv_3 = make_candidate(["python", "fastapi", "docker"])
    score_3 = score_resume_against_jd(cv_3, jd)
    assert score_3.is_capped is False
    assert score_3.overall_score > 50.0


def test_band_edges_49_9_50_74_9_75(monkeypatch):
    """Band thresholds must strictly evaluate:
    >= 75.0 -> 'strong'
    74.9 -> 'moderate'
    50.0 -> 'moderate'
    < 50.0 (e.g. 49.9) -> 'weak'
    """
    resume = ParsedResume(
        filename="test.pdf",
        contact=ContactInfo(name="Candidate"),
        skills=["python"],
        work_experience=[],
    )
    jd = JDFeatures(title="Role", must_have_skills=[])

    from app.services.scorer import engine

    test_cases = [
        (75.0, "strong"),
        (74.9, "moderate"),
        (50.0, "moderate"),
        (49.9, "weak"),
    ]

    for target_score, expected_band in test_cases:
        monkeypatch.setattr(
            engine,
            "score_keywords",
            lambda r, j, weight=1.0, ts=target_score: (
                MetricScore(score=ts, weight=weight, weighted_score=ts * weight),
                [],
                []
            ),
        )
        cfg = ScoringConfig(
            weights={
                "keyword_match": 1.0,
                "semantic_fit": 0.0,
                "experience": 0.0,
                "education": 0.0,
                "impact": 0.0,
                "format": 0.0,
            }
        )
        res = score_resume_against_jd(resume, jd, cfg)
        assert res.overall_score == target_score
        assert res.match_band == expected_band, (
            f"Score {target_score} should be band '{expected_band}', got '{res.match_band}'"
        )




