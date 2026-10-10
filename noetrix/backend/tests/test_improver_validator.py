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
