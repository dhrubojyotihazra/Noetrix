"""Placement-weighted keyword matching with synonym tolerance and frequency boost."""

from app.schemas.scoring import MetricScore
from app.schemas.resume import ParsedResume
from app.schemas.jd import JDFeatures
from app.nlp.tokenizer import word_boundary_match
from app.nlp.synonyms import get_synonyms, normalize_term


def score_keywords(resume: ParsedResume, jd: JDFeatures, weight: float = 0.30) -> tuple[MetricScore, list[str], list[str]]:
    """Compute placement-weighted keyword score against JD requirements."""
    jd_skills = jd.must_have_skills + jd.nice_to_have_skills + jd.keywords
    # Deduplicate while preserving order
    unique_jd_skills = []
    seen = set()
    for s in jd_skills:
        clean = s.strip().lower()
        if clean and clean not in seen:
            seen.add(clean)
            unique_jd_skills.append(clean)

    if not unique_jd_skills:
        return MetricScore(
            score=100.0,
            weight=weight,
            weighted_score=100.0 * weight,
            evidence=["No specific target skills extracted from JD."],
            missing=[],
            rationale="No explicit skills required in job description."
        ), [], []

    # Segregate resume texts for placement weighting:
    # 1. Experience bullets (1.0x weight)
    bullets_text = " ".join(
        b for w in resume.work_experience for b in w.bullets
    ).lower()

    # 2. Skills section (0.8x weight)
    skills_text = " ".join(resume.skills).lower()

    # 3. General raw text (0.5x weight)
    general_text = resume.raw_text.lower()

    total_weight_possible = len(unique_jd_skills) * 1.0
    accumulated_score = 0.0
    matched_list: list[str] = []
    missing_list: list[str] = []
    evidence: list[str] = []

    for skill in unique_jd_skills:
        synonyms = get_synonyms(skill)
        found = False
        placement_credit = 0.0
        match_location = ""

        # Check in experience bullets (highest value proof of applied skill)
        for syn in synonyms:
            if word_boundary_match(syn, bullets_text):
                found = True
                placement_credit = 1.0
                match_location = "experience bullets"
                break

        # Check in skills section (0.5x weight to mitigate ungrounded keyword stuffing)
        if not found:
            for syn in synonyms:
                if word_boundary_match(syn, skills_text):
                    found = True
                    placement_credit = 0.5
                    match_location = "skills section"
                    break

        # Check in general text (0.3x weight)
        if not found:
            for syn in synonyms:
                if word_boundary_match(syn, general_text):
                    found = True
                    placement_credit = 0.3
                    match_location = "general text"
                    break

        if found:
            accumulated_score += placement_credit
            matched_list.append(skill)
            evidence.append(f"Matched '{skill}' (found in {match_location}).")
        else:
            missing_list.append(skill)

    # Calculate normalized score 0 - 100
    raw_percentage = (accumulated_score / total_weight_possible) * 100.0
    score_val = max(0.0, min(100.0, round(raw_percentage, 1)))

    rationale = (
        f"Matched {len(matched_list)}/{len(unique_jd_skills)} required technical terms "
        f"({round(len(matched_list)/len(unique_jd_skills)*100)}% coverage). "
        f"Key terms verified across experience bullets and skills list."
    )

    return MetricScore(
        score=score_val,
        weight=weight,
        weighted_score=round(score_val * weight, 2),
        evidence=evidence[:10],
        missing=missing_list[:10],
        rationale=rationale
    ), matched_list, missing_list
