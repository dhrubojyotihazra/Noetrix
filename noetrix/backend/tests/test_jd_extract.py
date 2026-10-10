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
