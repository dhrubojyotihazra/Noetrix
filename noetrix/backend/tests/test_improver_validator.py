"""Unit tests for Deterministic Zero-Fabrication Validator (app/services/improver.py)."""

import pytest
from app.services.improver import (
    validate_bullet_rewrite,
    is_non_bullet_line,
    enhance_single_bullet
)


def test_validator_rejects_invented_numbers():
    """Rewrites introducing new numbers not in original must be rejected."""
    original = "Trained classification model on internal dataset."
    rewrite = "Trained classification model on internal dataset, reducing processing latency by 35%."

    is_valid, reason = validate_bullet_rewrite(original, rewrite)
    assert is_valid is False
    assert "Invented numbers or metrics detected" in reason


def test_validator_accepts_original_numbers():
    """Rewrites preserving numbers already in the original must be accepted."""
    original = "Trained model on 50,000 images achieving 94% accuracy."
    rewrite = "Engineered convolutional neural network on 50,000 images, attaining 94% accuracy."

    is_valid, reason = validate_bullet_rewrite(original, rewrite, candidate_skills=["neural network"])
    assert is_valid is True


def test_validator_rejects_unconfirmed_skills():
    """Rewrites injecting technologies not present in candidate experience must be rejected."""
    original = "Built REST endpoints for customer database."
    rewrite = "Built REST endpoints for customer database utilizing Docker, Kubernetes, and TensorFlow."

    # Candidate has none of these skills
    is_valid, reason = validate_bullet_rewrite(original, rewrite, candidate_skills=["python"])
    assert is_valid is False
    assert "Unconfirmed skill injected" in reason


def test_validator_rejects_meaning_reversal():
    """Rewrites inverting polarity (e.g. 'Prevented' -> 'Engineered') must be rejected."""
    original = "Prevented train-test data leakage during cross-validation pipeline."
    rewrite = "Engineered train-test data leakage during cross-validation pipeline."

    is_valid, reason = validate_bullet_rewrite(original, rewrite)
    assert is_valid is False
    assert "Meaning reversal detected" in reason


def test_validator_rejects_non_bullet_lines():
    """Non-bullet lines (job titles, tech stacks, degrees) must remain untouched."""
    assert is_non_bullet_line("B.Tech — Computer Science & Engineering") is True
    assert is_non_bullet_line("Flask · React · DistilBERT") is True
    assert is_non_bullet_line("Tech Stack: Python, SQL") is True

    original = "Flask · React · DistilBERT"
    rewrite = "Streamlined · React · DistilBERT"
    is_valid, reason = validate_bullet_rewrite(original, rewrite)
    assert is_valid is False
    assert "Non-bullet line must remain untouched" in reason


def test_validator_accepts_clean_active_verb_upgrade():
    """Rewrites that strengthen weak passive phrasing truthfully must be accepted."""
    original = "Worked on developing backend microservices for transaction processing."
    rewrite = "Developed backend microservices for transaction processing."

    is_valid, reason = validate_bullet_rewrite(original, rewrite)
    assert is_valid is True


def test_worked_on_building_becomes_built(monkeypatch):
    """A bullet with letters and spaces like 'Worked on building...' must NOT be treated as a non-bullet line."""
    monkeypatch.setenv("LLM_MODE", "off")
    bullet = "Worked on building a recommendation engine"
    assert is_non_bullet_line(bullet) is False, "A bullet consisting of letters and spaces must not match all-caps heading"
    res = enhance_single_bullet(bullet)
    assert res.enhanced == "Built a recommendation engine.", f"Expected 'Built a recommendation engine.', got '{res.enhanced}'"


def test_did_not_matched_as_action_verb():
    """The word 'Did' must not match 'directed' via loose prefix/suffix stripping."""
    from app.services.improver import is_action_verb_word
    assert is_action_verb_word("Did") is False
    assert is_action_verb_word("Directed") is True


def test_validator_rejects_dropped_numbers():
    """Rewrites dropping verified numbers present in the original bullet must be rejected."""
    original = "Trained model on 10,000 images achieving 92% accuracy."
    rewrite = "Trained model achieving 92% accuracy."
    is_valid, reason = validate_bullet_rewrite(original, rewrite)
    assert is_valid is False
    assert "Dropped numbers" in reason or "dropped" in reason.lower()


def test_validator_rejects_changed_number_words():
    """Rewrites changing number-words (e.g. four to five) must be rejected."""
    original = "Led a team of four software engineers."
    rewrite = "Led a team of five software engineers."
    is_valid, reason = validate_bullet_rewrite(original, rewrite)
    assert is_valid is False
    assert "number" in reason.lower()


def test_validator_normalizes_comma_numbers():
    """15,000 vs 15000 must be normalized and not flagged as a hallucinated number."""
    original = "Processed 15,000 transactions per second."
    rewrite = "Processed 15000 transactions per second."
    is_valid, reason = validate_bullet_rewrite(original, rewrite)
    assert is_valid is True, f"Expected valid rewrite, got rejection: {reason}"


def test_grounded_mappings_does_not_match_robert_as_bert():
    """Candidate named Robert must not trigger grounded skill suggestion for 'transformers' via 'bert'."""
    from app.services.improver import tailor_resume_to_jd
    from app.schemas.resume import ParsedResume
    from app.schemas.jd import JDFeatures

    resume = ParsedResume(
        raw_text="Robert is an experienced engineer who worked on enterprise databases.",
        skills=["sql"]
    )
    jd = JDFeatures(
        must_have_skills=["transformers"]
    )
    res = tailor_resume_to_jd(resume, jd)
    assert "transformers" not in (res.tailored_resume.skills or []), "Substring 'bert' in 'Robert' must not ground transformers"



