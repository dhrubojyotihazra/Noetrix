"""Extract contact information (name, email, phone, location, links) from resume text."""

import re
from app.schemas.resume import ContactInfo

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[a-zA-Z0-9_-]+", re.IGNORECASE)
GITHUB_RE = re.compile(r"github\.com/[a-zA-Z0-9_-]+", re.IGNORECASE)
LOCATION_RE = re.compile(r"\b([A-Z][a-zA-Z\s]+,\s*[A-Z]{2}|[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+)\b")


def extract_contact_info(text: str) -> ContactInfo:
    """Extract contact information from first 1000 characters of resume."""
    head_text = text[:1500]
    lines = [line.strip() for line in head_text.split("\n") if line.strip()]

    contact = ContactInfo()

    # Email
    email_match = EMAIL_RE.search(head_text)
    if email_match:
        contact.email = email_match.group(0)

    # Phone
    phone_match = PHONE_RE.search(head_text)
    if phone_match:
        contact.phone = phone_match.group(0)

    # LinkedIn & GitHub
    li_match = LINKEDIN_RE.search(head_text)
    if li_match:
        contact.linkedin = "https://" + li_match.group(0)

    gh_match = GITHUB_RE.search(head_text)
    if gh_match:
        contact.github = "https://" + gh_match.group(0)

    # Location
    loc_match = LOCATION_RE.search(head_text)
    if loc_match:
        contact.location = loc_match.group(0)

    # Candidate Name: Heuristic from top 3 non-empty lines
    for line in lines[:3]:
        # Discard lines with emails, links, or digits
        if "@" in line or "http" in line or any(char.isdigit() for char in line):
            continue
        words = line.split()
        if 1 <= len(words) <= 4:
            contact.name = line
            break

    return contact
