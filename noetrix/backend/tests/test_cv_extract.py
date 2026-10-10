"""Unit tests for CV Structure Extraction and Provenance (app/genai/cv_extract.py)."""

import pytest
from app.schemas.resume import ParsedResume, WorkEntry, ContactInfo
from app.genai.cv_extract import (
    extract_cv_structure_hybrid,
    _fuzzy_matches_source,
    _date_in_source
)


def test_fuzzy_match_detects_real_source_lines():
    """_fuzzy_matches_source must return True for real lines and False for hallucinated text."""
    source = "Architected PyTorch model pipeline handling 4,500 requests per second."
    assert _fuzzy_matches_source("Architected PyTorch model pipeline", source) is True
    assert _fuzzy_matches_source("Built Kubernetes cluster on Azure with Terraform", source) is False


def test_date_in_source_validates_dates():
    """_date_in_source must detect hallucinated years not in source text."""
    source = "Employed at Tech Corp from 2021 to 2023."
    assert _date_in_source("2021 - 2023", source) is True
    assert _date_in_source("2015 - 2018", source) is False


def test_provenance_defaults_to_rules_when_confident():
    """Confident parsed resume must retain rules provenance without triggering AI."""
    resume = ParsedResume(
        filename="test.pdf",
        raw_text="Jane Doe\nExperience\nSoftware Engineer at Alpha\n• Built APIs\nEducation\nBS Computer Science",
        contact=ContactInfo(name="Jane Doe"),
        work_experience=[WorkEntry(id="1", title="Software Engineer", bullets=["Built APIs"])],
        sections_detected=["experience", "education", "skills"],
        skills=["python", "docker"],
        parse_confidence=1.0
    )

    result = extract_cv_structure_hybrid(resume)
    assert result.overall_parse_method == "rules"
    assert result.provenance["experience"] == "rules"
    assert result.provenance["education"] == "rules"
