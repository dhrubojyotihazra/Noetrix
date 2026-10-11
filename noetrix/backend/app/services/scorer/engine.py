"""Master ATS Scoring Engine orchestrating the 6-metric pipeline and explainability contracts."""

from app.schemas.resume import ParsedResume
from app.schemas.jd import JDFeatures
from app.schemas.scoring import ScoringConfig, ScoreResult, MetricScore
from app.services.scorer.keyword_scorer import score_keywords
from app.services.scorer.semantic_scorer import score_semantic_fit
from app.services.scorer.experience_scorer import score_experience
from app.services.scorer.education_scorer import score_education
from app.services.scorer.impact_scorer import score_impact
from app.services.scorer.format_scorer import score_format_health


def score_resume_against_jd(
    resume: ParsedResume,
    jd: JDFeatures,
    config: ScoringConfig | None = None
) -> ScoreResult:
    """Run full deterministic 6-metric ATS evaluation."""
    cfg = config or ScoringConfig()
    weights = cfg.weights

    # Normalize weights so they sum to 1.0
    weight_sum = sum(weights.values()) or 1.0
    norm_w = {k: v / weight_sum for k, v in weights.items()}

    # 1. Run all 6 metric scorers
    kw_score, matched_kws, missing_kws = score_keywords(resume, jd, norm_w.get("keyword_match", 0.30))
    sem_score = score_semantic_fit(resume, jd, norm_w.get("semantic_fit", 0.20))
    exp_score, est_years = score_experience(resume, jd, norm_w.get("experience", 0.20))
    edu_score = score_education(resume, jd, norm_w.get("education", 0.10))
    imp_score = score_impact(resume, norm_w.get("impact", 0.10))
    fmt_score = score_format_health(resume, norm_w.get("format", 0.10))

    metrics: dict[str, MetricScore] = {
        "keyword_match": kw_score,
        "semantic_fit": sem_score,
        "experience": exp_score,
        "education": edu_score,
        "impact": imp_score,
        "format": fmt_score
    }

    # Raw composite score (0 - 100)
    raw_composite = sum(m.score * norm_w.get(k, 0.0) for k, m in metrics.items())
    raw_composite = round(raw_composite, 1)

    # 2. Check Must-Have Knockout Rule
    is_capped = False
    risk_flags: list[str] = []

    if jd.must_have_skills:
        matched_must_haves = [s for s in jd.must_have_skills if any(m.lower() == s.lower() for m in matched_kws)]
        missing_must_haves = [s for s in jd.must_have_skills if not any(m.lower() == s.lower() for m in matched_kws)]
        coverage_ratio = len(matched_must_haves) / len(jd.must_have_skills) if jd.must_have_skills else 1.0

        # PRD rule: Soft knockout cap applies ONLY if candidate covers FEWER THAN HALF (< 50%) of must-have skills
        if coverage_ratio < 0.50:
            risk_flags.append(f"Missing >50% of mandatory must-have skills ({len(missing_must_haves)}/{len(jd.must_have_skills)} missing): {', '.join(missing_must_haves[:5])}")
            if cfg.enable_must_have_cap and raw_composite > cfg.must_have_cap:
                final_score = cfg.must_have_cap
                is_capped = True
            else:
                final_score = raw_composite
        else:
            final_score = raw_composite
            if missing_must_haves:
                risk_flags.append(f"Missing secondary must-have skills ({len(missing_must_haves)}/{len(jd.must_have_skills)}): {', '.join(missing_must_haves[:4])}")
    else:
        final_score = raw_composite

    # Additional Risk Flags
    if resume.detected_columns > 1:
        risk_flags.append("Multi-column layout may cause text interleaving in strict parsers.")
    if imp_score.score < 40.0:
        risk_flags.append("Few or no quantified metrics in experience descriptions.")
    if jd.min_experience_years > 0 and est_years < jd.min_experience_years:
        risk_flags.append(f"Tenure deficit: {est_years} yrs vs {jd.min_experience_years} yrs required.")

    # 3. Classify Match Band
    if is_capped:
        match_band = "weak"
    elif final_score >= cfg.strong_band_threshold:
        match_band = "strong"
    elif final_score >= cfg.moderate_band_threshold:
        match_band = "moderate"
    else:
        match_band = "weak"

    # 4. Generate Top-5 Prioritized Fixes
    priority_fixes: list[str] = []
    if missing_kws:
        priority_fixes.append(f"Add key missing technologies to your experience bullets: {', '.join(missing_kws[:3])}.")
    if imp_score.score < 70.0:
        priority_fixes.append("Quantify your accomplishments using the XYZ formula: Accomplished [X] as measured by [Y] by doing [Z].")
    if fmt_score.missing:
        priority_fixes.append(fmt_score.missing[0])
    if exp_score.missing:
        priority_fixes.append(exp_score.missing[0])
    if edu_score.missing:
        priority_fixes.append(edu_score.missing[0])
    if len(priority_fixes) < 5 and len(missing_kws) > 3:
        priority_fixes.append(f"Include secondary preferred skills: {', '.join(missing_kws[3:6])}.")

    # 5. Build "What the ATS Sees" View (OpenResume pattern)
    ats_sees = {
        "candidate_name": resume.contact.name or "Not detected",
        "email": resume.contact.email or "Not detected",
        "phone": resume.contact.phone or "Not detected",
        "location": resume.contact.location or "Not detected",
        "sections_detected": resume.sections_detected,
        "skills_extracted_count": len(resume.skills),
        "skills_list": resume.skills[:20],
        "work_roles_extracted": [f"{w.title} ({w.company})" for w in resume.work_experience if w.title],
        "bullets_extracted_count": sum(len(w.bullets) for w in resume.work_experience),
        "columns_detected": resume.detected_columns,
        "tables_detected": resume.has_tables,
        "extraction_source": f"extracted by: {'AI' if getattr(resume, 'overall_parse_method', 'rules') == 'llm' else 'rules'}",
        "provenance": getattr(resume, "provenance", {}),
        "parse_method": getattr(resume, "overall_parse_method", "rules")
    }

    return ScoreResult(
        candidate_name=resume.contact.name or resume.filename,
        filename=resume.filename,
        overall_score=final_score,
        raw_fit_score=raw_composite,
        is_capped=is_capped,
        match_band=match_band,
        metrics=metrics,
        matched_keywords=matched_kws,
        missing_keywords=missing_kws,
        priority_fixes=priority_fixes[:5],
        risk_flags=risk_flags,
        ats_sees=ats_sees
    )
