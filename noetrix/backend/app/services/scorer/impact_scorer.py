"""Impact and quantification scoring: metrics, percentages, and scale indicators."""

from app.schemas.scoring import MetricScore
from app.schemas.resume import ParsedResume
from app.nlp.tokenizer import count_quantified_bullets


def score_impact(resume: ParsedResume, weight: float = 0.10) -> MetricScore:
    """Score the ratio of work experience bullets backed by quantifiable achievements."""
    all_bullets = [b for w in resume.work_experience for b in w.bullets]
    total_bullets = len(all_bullets)

    if total_bullets == 0:
        return MetricScore(
            score=30.0,
            weight=weight,
            weighted_score=round(30.0 * weight, 2),
            evidence=["No itemized bullet points detected in experience section."],
            missing=["Add bullet points containing percentages, dollar values, or measurable metrics."],
            rationale="No experience bullets detected to evaluate for measurable impact."
        )

    quant_count, quant_bullets = count_quantified_bullets(all_bullets)
    ratio = quant_count / total_bullets

    # Base score 30 pts + up to 70 pts based on proportion of quantified bullets
    # If 40%+ of bullets are quantified, candidate receives 100% impact credit
    scale_factor = min(1.0, ratio / 0.40)
    score_val = round(30.0 + (scale_factor * 70.0), 1)

    evidence = [
        f"Detected {quant_count}/{total_bullets} bullets ({round(ratio * 100)}%) with quantified metrics.",
    ]
    if quant_bullets:
        evidence.append(f"Sample metric bullet: '{quant_bullets[0][:80]}...'")

    missing = []
    if quant_count == 0:
        missing.append("Zero quantified achievements found (missing %, $, scale metrics, or time savings).")
    elif ratio < 0.25:
        missing.append("Less than 25% of bullet points contain quantifiable scale or performance metrics.")

    rationale = f"Evaluated evidence of quantifiable impact ({quant_count} metric-backed bullets detected across career history)."

    return MetricScore(
        score=score_val,
        weight=weight,
        weighted_score=round(score_val * weight, 2),
        evidence=evidence,
        missing=missing,
        rationale=rationale
    )
