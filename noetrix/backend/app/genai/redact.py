"""PII and Sensitive Data Redaction for CV and JD text before LLM calls.

Non-negotiable rule:
Only redacted CV and JD text may be sent to Groq. Remove names, email addresses,
and phone numbers before sending CV text.
"""

import re

EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{3,5}\b"
)
URL_REGEX = re.compile(
    r"https?://[^\s]+|www\.[^\s]+|(?:linkedin\.com|github\.com)/[^\s]+",
    re.IGNORECASE
)

SENSITIVE_LINE_KEYWORDS = [
    "date of birth", "dob:", "d.o.b", "gender:", "sex:", "marital status",
    "nationality:", "religion:", "citizenship:", "passport"
]


def redact_pii(text: str, candidate_name: str = "") -> str:
    """Redact personal identifiable information from text.
    
    Replaces:
    - Candidate name -> [NAME]
    - Email -> [EMAIL]
    - Phone -> [PHONE]
    - Links/URLs -> [LINK]
    - Drops lines with protected demographics (DOB, gender, marital status, nationality).
    """
    if not text:
        return ""

    lines = text.split("\n")
    cleaned_lines = []

    # Prepare name tokens to redact
    name_tokens = []
    if candidate_name and candidate_name.strip():
        # Strip generic labels
        clean_name = re.sub(r"[,\-_|]", " ", candidate_name).strip()
        tokens = [t.strip() for t in clean_name.split() if len(t.strip()) > 2]
        name_tokens.extend(tokens)

    for line in lines:
        lower_line = line.lower().strip()
        # Drop lines with protected personal demographics
        if any(kw in lower_line for kw in SENSITIVE_LINE_KEYWORDS):
            continue

        redacted = line
        # Redact emails first
        redacted = EMAIL_REGEX.sub("[EMAIL]", redacted)

        # Redact URLs second
        redacted = URL_REGEX.sub("[LINK]", redacted)

        # Redact phones
        if any(c.isdigit() for c in redacted):
            redacted = PHONE_REGEX.sub("[PHONE]", redacted)

        # Redact candidate name tokens
        for token in name_tokens:
            pattern = re.compile(rf"\b{re.escape(token)}\b", re.IGNORECASE)
            redacted = pattern.sub("[NAME]", redacted)

        cleaned_lines.append(redacted)

    result = "\n".join(cleaned_lines)
    # Collapse multiple consecutive [NAME], [EMAIL], [PHONE] tags
    result = re.sub(r"(\[NAME\]\s*)+", "[NAME] ", result)
    result = re.sub(r"(\[EMAIL\]\s*)+", "[EMAIL] ", result)
    result = re.sub(r"(\[PHONE\]\s*)+", "[PHONE] ", result)
    return result.strip()
