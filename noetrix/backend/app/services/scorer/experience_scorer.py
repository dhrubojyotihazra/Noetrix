import os
import re
from datetime import date
from app.schemas.scoring import MetricScore
from app.schemas.resume import ParsedResume
from app.schemas.jd import JDFeatures
from app.nlp.tokenizer import count_action_verbs


MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12
}


def get_reference_date(ref_date: date | None = None) -> tuple[int, int]:
    """Return (year, month) using explicit parameter, env override, or date.today()."""
    if ref_date:
        return ref_date.year, ref_date.month
    env_date = os.environ.get("NOETRIX_CURRENT_DATE")
    if env_date:
        try:
            d = date.fromisoformat(env_date)
            return d.year, d.month
        except Exception:
            pass
    env_year = os.environ.get("NOETRIX_CURRENT_YEAR")
    env_month = os.environ.get("NOETRIX_CURRENT_MONTH")
    if env_year:
        try:
            return int(env_year), int(env_month) if env_month else 1
        except Exception:
            pass
    today = date.today()
    return today.year, today.month


def estimate_years_of_experience(resume: ParsedResume, reference_date: date | None = None) -> float:
    """Estimate total years of experience by scanning dates strictly in work entries."""
    curr_year, curr_month = get_reference_date(reference_date)
    total_months = 0

    # Search for date spans within each work entry
    date_range_regex = re.compile(
        r"([a-z]{3,9}\.?\s+)?(20\d\d|19\d\d)\s*(?:-|–|—|to)\s*([a-z]{3,9}\.?\s+)?(20\d\d|19\d\d|present|current)",
        re.IGNORECASE
    )

    work_texts = []
    for w in resume.work_experience:
        work_texts.append(f"{w.title} {w.company} {w.dates} {' '.join(w.bullets)}")

    for text in work_texts:
        matches = date_range_regex.findall(text)
        for m in matches:
            start_m_str, start_y_str, end_m_str, end_y_str = m
            try:
                start_y = int(start_y_str)
                start_m = MONTH_MAP.get(start_m_str.strip().lower().replace(".", ""), 1) if start_m_str else 1

                if end_y_str.lower() in ["present", "current"]:
                    end_y = curr_year
                    end_m = curr_month
                else:
                    end_y = int(end_y_str)
                    end_m = MONTH_MAP.get(end_m_str.strip().lower().replace(".", ""), 12) if end_m_str else 12

                diff_months = (end_y - start_y) * 12 + (end_m - start_m) + 1
                if 1 <= diff_months <= 480:
                    total_months += diff_months
            except Exception:
                continue

    if total_months > 0:
        return round(total_months / 12.0, 1)

    # Fallback: If roles exist but without explicit parseable dates, count 0.5 yrs per role/internship
    if len(resume.work_experience) > 0:
        return round(min(3.0, len(resume.work_experience) * 0.5), 1)

    return 0.5


def score_experience(
    resume: ParsedResume,
    jd: JDFeatures,
    weight: float = 0.20,
    reference_date: date | None = None
) -> tuple[MetricScore, float]:
    """Score candidate experience against JD required tenure and quality signals."""
    est_years = estimate_years_of_experience(resume, reference_date=reference_date)
    req_years = jd.min_experience_years

    # Tenure score
    if req_years <= 0:
        tenure_score = 100.0
    else:
        ratio = est_years / req_years
        if ratio >= 1.0:
            tenure_score = 100.0
        else:
            tenure_score = min(100.0, ratio * 100.0)

    # Action verbs score
    all_bullets = [b for w in resume.work_experience for b in w.bullets]
    total_bullets = len(all_bullets)
    if total_bullets > 0:
        action_verb_count = count_action_verbs(all_bullets)
        verb_ratio = action_verb_count / total_bullets
        verb_score = min(100.0, 30.0 + (verb_ratio * 70.0))
    else:
        action_verb_count = 0
        verb_score = 40.0

    # Composite experience score (60% tenure, 40% quality/action verbs)
    composite = (tenure_score * 0.60) + (verb_score * 0.40)
    score_val = max(0.0, min(100.0, round(composite, 1)))

    evidence = [
        f"Estimated tenure: {est_years} years (JD required: {req_years if req_years > 0 else 'None specified'}).",
        f"Detected {len(resume.work_experience)} distinct roles in career history.",
        f"Identified {action_verb_count} action-oriented accomplishments ({round((action_verb_count/total_bullets*100) if total_bullets else 0)}% of bullets)."
    ]

    missing = []
    if req_years > 0 and est_years < req_years:
        missing.append(f"Short on target experience: {est_years} yrs vs {req_years} yrs required.")
    if total_bullets > 0 and action_verb_count < 3:
        missing.append("Low frequency of strong action verbs in work descriptions.")

    rationale = f"Evaluated candidate tenure ({est_years} yrs) and action verb intensity across {len(resume.work_experience)} recorded positions."

    return MetricScore(
        score=score_val,
        weight=weight,
        weighted_score=round(score_val * weight, 2),
        evidence=evidence,
        missing=missing,
        rationale=rationale
    ), est_years
