"""Unit tests for Job Description Criteria Extraction (app/genai/jd_extract.py)."""

import pytest
from app.genai.jd_extract import extract_jd_criteria, _validate_and_filter_skills
from app.services.jd_parser import parse_job_description
from app.nlp.tfidf import GENERIC_NON_SKILLS


def test_generic_non_skills_are_never_emitted():
    """Words like 'learning', 'years', 'experience' must never be emitted as skills."""
    jd_text = """
    Software Engineer
    Required: 5+ years of experience in machine learning and deep learning.
    Familiarity with solid qualifications and working knowledge.
    Skills: Python, Docker.
    """
    res = parse_job_description(jd_text)

    for skill in res.must_have_skills + res.nice_to_have_skills:
        assert skill not in GENERIC_NON_SKILLS
        assert skill not in ["learning", "years", "experience", "qualifications", "machine"]


def test_unsupported_skills_are_dropped_by_validator():
    """Skills not present in JD text or synonyms must be dropped."""
    jd_text = "We are seeking a Python backend engineer with FastAPI and PostgreSQL."
    candidate_skills = ["python", "fastapi", "postgresql", "kubernetes", "golang"]

    filtered = _validate_and_filter_skills(candidate_skills, jd_text)
    assert "python" in filtered
    assert "fastapi" in filtered
    assert "postgresql" in filtered
    # kubernetes and golang were not in the JD text
    assert "kubernetes" not in filtered
    assert "golang" not in filtered


def test_synonyms_are_normalized_to_canonical_form():
    """Synonyms like 'k8s' -> 'kubernetes', 'postgres' -> 'postgresql' must normalize."""
    jd_text = "Experience with k8s, postgres, and py is required."
    candidate_skills = ["k8s", "postgres", "py"]

    filtered = _validate_and_filter_skills(candidate_skills, jd_text)
    assert "kubernetes" in filtered
    assert "postgresql" in filtered
    assert "python" in filtered


def test_rules_fallback_when_llm_mode_off(monkeypatch):
    """When LLM_MODE is off, extract_jd_criteria must fall back to rules parser."""
    monkeypatch.setenv("LLM_MODE", "off")
    jd_text = "Requirements: Python, Docker, SQL. Must have 3+ years experience."

    res = extract_jd_criteria(jd_text)
    assert res.extraction_method == "rules"
    assert "python" in [s.lower() for s in res.must_have_skills]
    assert res.min_experience_years == 3.0


def test_extract_jd_keywords_drops_junk_ngrams():
    """extract_jd_keywords must drop junk n-grams like 'using', 'time inference', 'science related', 'transformers ci'."""
    from app.nlp.tfidf import extract_jd_keywords
    jd_text = """
    We are seeking a Machine Learning Engineer using PyTorch and Docker.
    The role requires real-time inference, Computer Science or related degree,
    and hands-on experience with transformers, CI/CD pipelines.
    """
    kws = extract_jd_keywords(jd_text)
    assert "using" not in kws
    assert "time inference" not in kws
    assert "science related" not in kws
    assert "transformers ci" not in kws
    assert "requires" not in kws
    assert "seeking" not in kws
    assert "related" not in kws
    assert "pytorch" in kws
    assert "docker" in kws
    assert "transformers" in kws


def test_jd_parser_years_experience_with_intermediate_words():
    """Verify years regex captures '1+ years practical experience' and '5+ years of software engineering experience'."""
    jd1 = "We require 1+ years practical experience with Python."
    res1 = parse_job_description(jd1)
    assert res1.min_experience_years == 1.0

    jd2 = "Requirements:\n- 5+ years of software engineering experience in backend systems."
    res2 = parse_job_description(jd2)
    assert res2.min_experience_years == 5.0


def test_jd_parser_requirement_groups_and_familiarity():
    """Verify 'X or Y' is treated as one requirement group and 'familiarity with' as nice-to-have."""
    jd_text = """
    Requirements:
    - Strong proficiency in Python, FastAPI or Flask, and PostgreSQL
    - Familiarity with AWS, Kubernetes, and Redis
    """
    res = parse_job_description(jd_text)
    must_lower = [s.lower() for s in res.must_have_skills]
    nice_lower = [s.lower() for s in res.nice_to_have_skills]

    # 'fastapi or flask' should be one requirement group
    assert any("fastapi or flask" in s or "flask or fastapi" in s for s in must_lower)
    assert "python" in must_lower
    assert "postgresql" in must_lower

    # Familiarity skills must be in nice_to_have, not must_have
    assert "aws" in nice_lower
    assert "kubernetes" in nice_lower
    assert "redis" in nice_lower
    assert "aws" not in must_lower
    assert "kubernetes" not in must_lower
    assert "redis" not in must_lower


def test_education_scorer_rewards_matching_education_required():
    """Verify candidate receives small bonus when meeting JD education_required."""
    from app.schemas.resume import ParsedResume, EduEntry
    from app.schemas.jd import JDFeatures
    from app.services.scorer.education_scorer import score_education

    resume = ParsedResume(
        education=[EduEntry(degree="Bachelor of Science in Computer Science")]
    )
    jd_with_req = JDFeatures(education_required="Bachelor")
    jd_without_req = JDFeatures(education_required="")

    score_with = score_education(resume, jd_with_req)
    score_without = score_education(resume, jd_without_req)

    assert score_with.score == score_without.score + 5.0

