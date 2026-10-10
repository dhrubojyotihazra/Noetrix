"""Format and ATS parse health scorer."""

from app.schemas.scoring import MetricScore
from app.schemas.resume import ParsedResume


def score_format_health(resume: ParsedResume, weight: float = 0.10) -> MetricScore:
    """Evaluate resume ATS parse readability, section completeness, and layout hygiene."""
    score_val = 100.0
    deductions: list[str] = []
    evidence: list[str] = []

    # 1. Section presence (essential: experience, education, skills)
    essential = {"experience", "education", "skills"}
    detected = set(resume.sections_detected)
    missing_sections = essential - detected
    if missing_sections:
        penalty = len(missing_sections) * 15.0
        score_val -= penalty
        deductions.append(f"Missing essential standard section headers: {', '.join(missing_sections)} (-{penalty} pts).")
    else:
        evidence.append("All primary ATS sections detected (Experience, Education, Skills).")

    # 2. Contact details
    if not resume.contact.email:
        score_val -= 10.0
        deductions.append("Missing or unparseable email address (-10 pts).")
    else:
        evidence.append("Valid candidate email address extracted.")

    if not resume.contact.phone:
        score_val -= 5.0
        deductions.append("Missing phone number (-5 pts).")

    # 3. Multi-column hazard
    if resume.detected_columns > 1:
        score_val -= 15.0
        deductions.append("Multi-column layout detected (may scramble text extraction order in strict ATS) (-15 pts).")
    else:
        evidence.append("Single-column linear text layout detected.")

    # 4. Embedded tables hazard
    if resume.has_tables:
        score_val -= 10.0
        deductions.append("Tables detected (some legacy ATS parsers fail to parse text in table cells) (-10 pts).")

    # 5. Word count bounds
    word_count = len(resume.raw_text.split())
    if word_count < 150:
        score_val -= 20.0
        deductions.append(f"Resume text is unusually short ({word_count} words; minimum recommended is 200 words) (-20 pts).")
    elif word_count > 1500:
        score_val -= 10.0
        deductions.append(f"Resume is excessively long ({word_count} words; standard limit is under 1,000 words) (-10 pts).")
    else:
        evidence.append(f"Optimal word count length ({word_count} words).")

    final_score = max(10.0, min(100.0, round(score_val, 1)))

    rationale = f"Evaluated ATS readability: {len(resume.sections_detected)} sections detected, {word_count} words, column hygiene."

    return MetricScore(
        score=final_score,
        weight=weight,
        weighted_score=round(final_score * weight, 2),
        evidence=evidence,
        missing=deductions,
        rationale=rationale
    )
