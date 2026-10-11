"""Unit tests for Central Groq Generative AI Adapter (app/genai/llm.py)."""

import os
import pytest
from pydantic import BaseModel

from app.genai.llm import (
    complete_json,
    check_llm_health,
    LLMUnavailable,
    _SEMAPHORE,
    _compute_cache_key
)
from app.genai.redact import redact_pii


class SampleModel(BaseModel):
    message: str
    code: int


def test_llm_unavailable_when_mode_off(monkeypatch):
    """complete_json must raise LLMUnavailable when LLM_MODE is off."""
    monkeypatch.setenv("LLM_MODE", "off")
    monkeypatch.setenv("GROQ_API_KEY", "dummy_key")

    with pytest.raises(LLMUnavailable) as exc:
        complete_json("system", "user", SampleModel)
    assert "LLM mode is off" in str(exc.value)


def test_llm_unavailable_when_key_missing(monkeypatch):
    """complete_json must raise LLMUnavailable when GROQ_API_KEY is empty."""
    monkeypatch.setenv("LLM_MODE", "on")
    monkeypatch.setenv("GROQ_API_KEY", "")

    with pytest.raises(LLMUnavailable) as exc:
        complete_json("system", "user", SampleModel)
    assert "GROQ_API_KEY is not configured" in str(exc.value)


def test_health_check_reports_accurate_state_without_exposing_keys(monkeypatch):
    """check_llm_health must return accurate state and never expose credentials."""
    monkeypatch.setenv("LLM_MODE", "off")
    health = check_llm_health()
    assert health["mode"] == "off"
    assert health["reachable"] is False
    assert "api_key" not in health
    assert "authorization" not in health


def test_redact_pii_removes_personal_details():
    """redact_pii must strip names, emails, and phone numbers from CV text."""
    raw = "John Doe\njohn.doe@example.com\n+1-555-0199\nhttps://github.com/johndoe\nSoftware Engineer"
    redacted = redact_pii(raw, candidate_name="John Doe")

    assert "john.doe@example.com" not in redacted
    assert "+1-555-0199" not in redacted
    assert "[EMAIL]" in redacted
    assert "[PHONE]" in redacted
    assert "[NAME]" in redacted


def test_cache_key_generation_is_deterministic():
    """Cache key generation must be deterministic and match across identical calls."""
    k1 = _compute_cache_key("test-model", "system prompt", "user query")
    k2 = _compute_cache_key("test-model", "system prompt", "user query")
    k3 = _compute_cache_key("test-model", "system prompt", "different query")

    assert k1 == k2
    assert k1 != k3


def test_redact_preserves_year_ranges():
    """Redaction must not convert year ranges like '2021-2023' into [PHONE]."""
    text = "Machine Learning Engineer\n2021-2023\nBuilt deep learning models."
    redacted = redact_pii(text)
    assert "2021-2023" in redacted, f"Year range '2021-2023' must survive redaction, got: {redacted}"
    assert "[PHONE]" not in redacted


def test_redact_preserves_newlines_across_tags():
    """Collapsing consecutive tags must not swallow newlines and merge lines."""
    text = "John\nDoe\nSoftware Engineer"
    redacted = redact_pii(text, candidate_name="John Doe")
    assert "\n" in redacted
    lines = [line.strip() for line in redacted.split("\n") if line.strip()]
    assert len(lines) >= 2, f"Lines were collapsed across newlines: {redacted}"
