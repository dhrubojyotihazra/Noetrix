"""Unit tests for Contact Information Extraction (app/services/parser/contact_extractor.py)."""

import pytest
from app.services.parser.contact_extractor import extract_contact_info, PHONE_RE, LOCATION_RE


def test_location_re_does_not_span_linebreaks():
    """LOCATION_RE must not capture text across newlines (e.g. 'Software Engineer\\nNew York, NY')."""
    text = "Software Engineer\nNew York, NY\nemail@example.com"
    contact = extract_contact_info(text)
    assert contact.location == "New York, NY"
    assert "\n" not in (contact.location or "")
    assert "Engineer" not in (contact.location or "")


def test_phone_re_accepts_international_and_spaced_formats():
    """PHONE_RE must accept +91 98765 43210, +91-9876543210, and 10-digit numbers with spaces."""
    test_cases = [
        ("Candidate with international phone: +91 98765 43210", "+91 98765 43210"),
        ("Candidate with hyphenated international phone: +91-9876543210", "+91-9876543210"),
        ("Candidate with spaced 10-digit phone: 98765 43210", "98765 43210"),
        ("Candidate with US phone: +1 (555) 012-3456", "+1 (555) 012-3456"),
    ]
    for text, expected_phone in test_cases:
        contact = extract_contact_info(text)
        assert contact.phone == expected_phone, f"Failed for text: '{text}', got: '{contact.phone}'"
