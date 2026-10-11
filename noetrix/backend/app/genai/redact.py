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


def _is_plausible_phone(match: re.Match) -> str:
    """Validate that matched candidate string has a plausible phone shape.
    
    Requires:
    - At least 9 digits in total, OR
    - A leading '+', OR
    - A bracketed area code like (555).
    Rejects year ranges like '2021-2023'.
    """
    s = match.group(0)
    digits_count = sum(1 for c in s if c.isdigit())
    has_plus = s.strip().startswith("+")
    has_brackets = bool(re.search(r"\(\d{2,5}\)", s))

    if digits_count >= 9 or has_plus or has_brackets:
        return "[PHONE]"
    return s


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

        # Redact phones (only plausible phone shapes, avoiding year ranges)
        if any(c.isdigit() for c in redacted):
            redacted = PHONE_REGEX.sub(_is_plausible_phone, redacted)

        # Redact candidate name tokens
        for token in name_tokens:
            pattern = re.compile(rf"\b{re.escape(token)}\b", re.IGNORECASE)
            redacted = pattern.sub("[NAME]", redacted)

        cleaned_lines.append(redacted)

    result = "\n".join(cleaned_lines)
    # Collapse multiple consecutive tags on the same line without swallowing newlines
    result = re.sub(r"(\[NAME\][ \t]*)+", "[NAME] ", result)
    result = re.sub(r"(\[EMAIL\][ \t]*)+", "[EMAIL] ", result)
    result = re.sub(r"(\[PHONE\][ \t]*)+", "[PHONE] ", result)
    result = re.sub(r"(\[LINK\][ \t]*)+", "[LINK] ", result)
    return result.strip()
