"""Education and certifications scoring with prestige-free fairness rules."""

import re
from app.schemas.scoring import MetricScore
from app.schemas.resume import ParsedResume
from app.schemas.jd import JDFeatures

DEGREE_HIERARCHY = {
    "phd": (100.0, "Doctorate / Ph.D."),
    "doctor": (100.0, "Doctorate"),
    "master": (90.0, "Master's Degree"),
    "mba": (90.0, "MBA"),
    "ms": (90.0, "Master of Science"),
    "bachelor": (80.0, "Bachelor's Degree"),
    "bs": (80.0, "Bachelor of Science"),
    "ba": (80.0, "Bachelor of Arts"),
    "b.tech": (80.0, "Bachelor of Technology"),
    "b.e": (80.0, "Bachelor of Engineering"),
    "associate": (60.0, "Associate Degree"),
    "diploma": (50.0, "Diploma")
}


def score_education(resume: ParsedResume, jd: JDFeatures, weight: float = 0.10) -> MetricScore:
    """Score education level and certifications without institutional prestige bias."""
    edu_text = " ".join(
        f"{e.degree} {e.institution} {e.field_of_study} {' '.join(e.bullets)}"
        for e in resume.education
    ).lower()

    if not edu_text:
        # Fallback search in raw text
        edu_text = resume.raw_text.lower()

    best_score = 40.0  # Base level for general credentials
    highest_degree = "No formal degree clearly identified"

    for marker, (score, label) in DEGREE_HIERARCHY.items():
        if re.search(rf"\b{re.escape(marker)}\b", edu_text):
            if score > best_score:
                best_score = score
                highest_degree = label

    # Bonus for relevant certifications (+5 pts per cert, max +15)
    cert_count = len(resume.certifications)
    if cert_count > 0:
        best_score = min(100.0, best_score + min(15.0, cert_count * 5.0))

    evidence = [
        f"Highest educational qualification recognized: {highest_degree}.",
    ]
    if cert_count > 0:
        evidence.append(f"Detected {cert_count} professional credentials/certifications.")

    # Small bonus (+5 pts) if candidate meets or exceeds the required education level in the JD
    if jd and getattr(jd, "education_required", ""):
        req_deg = jd.education_required.lower()
        req_threshold = 40.0
        for marker, (score, label) in DEGREE_HIERARCHY.items():
            if marker in req_deg:
                req_threshold = score
                break
        if best_score >= req_threshold:
            best_score = min(100.0, best_score + 5.0)
            evidence.append(f"Meets or exceeds JD education requirement ({jd.education_required}).")

    score_val = round(best_score, 1)

    missing = []
    if best_score < 75.0:
        missing.append("Bachelor's or equivalent degree not explicitly detected in education section.")

    rationale = f"Evaluated degree tier ({highest_degree}) and {cert_count} certifications (scored without institutional prestige bias)."

    return MetricScore(
        score=score_val,
        weight=weight,
        weighted_score=round(score_val * weight, 2),
        evidence=evidence,
        missing=missing,
        rationale=rationale
    )
