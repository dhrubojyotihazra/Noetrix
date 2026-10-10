"""Detect standard ATS sections and segment resume text."""

import re

SECTION_PATTERNS = {
    "summary": [
        r"(professional\s+)?summary",
        r"profile",
        r"about(\s+me)?",
        r"executive\s+summary",
        r"objective"
    ],
    "experience": [
        r"(work|professional|employment)\s+experience",
        r"work\s+history",
        r"career\s+history",
        r"experience"
    ],
    "projects": [
        r"(ml\s+(&|and)\s+ai\s+)?projects?",
        r"(technical|personal|key|academic)\s+projects?",
        r"projects?\s+(&|and)\s+experience",
        r"portfolio"
    ],
    "education": [
        r"leadership\s+(&|and)\s+education",
        r"education\s+(&|and)\s+leadership",
        r"academic\s+background",
        r"education",
        r"degrees?",
        r"academics?"
    ],
    "skills": [
        r"(technical\s+)?skills(\s+(&|and)\s+(tools|technologies))?",
        r"core\s+competencies",
        r"technologies",
        r"tools\s+(&|and)\s+technologies"
    ],
    "certifications": [
        r"certifications?",
        r"licenses?\s+(&|and)\s+certifications?",
        r"certifications?\s+(&|and)\s+licenses?",
        r"certificates?",
        r"courses?\s+(&|and)\s+certifications?",
        r"credentials"
    ]
}


def classify_heading(line: str) -> str | None:
    """Classify a line as a section heading if it matches header heuristics."""
    clean = line.strip().lower()
    # Strip leading/trailing numbering or symbols like "1. EXPERIENCE:" or "--- EDUCATION ---"
    clean = re.sub(r"^[0-9\.\-\—\*\:\s]+", "", clean)
    clean = re.sub(r"[\:\-\—\*\s]+$", "", clean)

    if len(clean) > 50 or len(clean) < 3:
        return None

    # Check against known section patterns
    for section_name, patterns in SECTION_PATTERNS.items():
        for pat in patterns:
            # Check either start of line match or whole-token word boundary match
            if re.search(r"\b" + pat + r"\b", clean):
                return section_name
    return None


def split_into_sections(text: str) -> dict[str, list[str]]:
    """Segment resume text lines into detected canonical sections."""
    sections: dict[str, list[str]] = {
        "header": [],
        "summary": [],
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "certifications": [],
        "other": []
    }

    current_section = "header"
    lines = text.split("\n")

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        detected = classify_heading(line)
        if detected:
            current_section = detected
        else:
            sections[current_section].append(line)

    return sections
