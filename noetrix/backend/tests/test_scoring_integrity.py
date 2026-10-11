"""Unit tests for Scoring Engine Integrity and Determinism (app/services/scorer/engine.py)."""

import pytest
from app.schemas.resume import ParsedResume, WorkEntry, EduEntry, ContactInfo
from app.schemas.jd import JDFeatures
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

