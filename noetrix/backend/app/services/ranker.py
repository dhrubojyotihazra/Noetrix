"""Batch ranking service for recruiters with multi-attribute tie breaking."""

import io
import csv
from app.schemas.resume import ParsedResume
from app.schemas.jd import JDFeatures
from app.schemas.scoring import ScoringConfig, RankedCandidate, ScoreResult
from app.services.scorer.engine import score_resume_against_jd
from app.services.scorer.experience_scorer import estimate_years_of_experience


def rank_resumes_batch(
    resumes: list[ParsedResume],
    jd: JDFeatures,
    config: ScoringConfig | None = None
) -> list[RankedCandidate]:
    """Score and rank a batch of resumes using 6-tier deterministic tie breaking."""
    cfg = config or ScoringConfig()
    scored_items: list[tuple[ScoreResult, ParsedResume]] = []

    for res in resumes:
        score_res = score_resume_against_jd(res, jd, cfg)
        scored_items.append((score_res, res))

    # Compute tie-break metrics
    must_haves_set = set(s.lower() for s in jd.must_have_skills)

    decorated: list[tuple[tuple, ScoreResult, ParsedResume]] = []
    for idx, (score_res, res) in enumerate(scored_items):
        if must_haves_set:
            matched_must = sum(1 for m in score_res.matched_keywords if m.lower() in must_haves_set)
            coverage = matched_must / len(must_haves_set)
        else:
            coverage = 1.0

        # Sort key tuple (descending order for scores and counts, ascending for original index)
        sort_key = (
            -score_res.overall_score,
            -coverage,
            -score_res.metrics["keyword_match"].score,
            -score_res.metrics["experience"].score,
            -score_res.metrics["impact"].score,
            idx  # FIFO fallback
        )
        decorated.append((sort_key, score_res, res))

    # Deterministic sort
    decorated.sort(key=lambda item: item[0])

    ranked_results: list[RankedCandidate] = []
    for rank_idx, (_, score_res, res) in enumerate(decorated, start=1):
        if must_haves_set:
            matched_must = sum(1 for m in score_res.matched_keywords if m.lower() in must_haves_set)
            cov = round((matched_must / len(must_haves_set)) * 100, 1)
        else:
            cov = 100.0

        candidate_name = res.contact.name or res.filename
        ranked_results.append(RankedCandidate(
            rank=rank_idx,
            candidate_name=candidate_name,
            filename=res.filename,
            overall_score=score_res.overall_score,
            match_band=score_res.match_band,
            must_have_coverage=cov,
            years_experience=estimate_years_of_experience(res),
            status="active",
            risk_flags=score_res.risk_flags,
            metrics=score_res.metrics,
            resume_summary=res.summary or (res.work_experience[0].title if res.work_experience else "")
        ))

    return ranked_results


def sanitize_csv_cell(val) -> str:
    """Neutralise CSV injection by prefixing formula triggers (=, +, -, @) with a single quote."""
    s = str(val) if val is not None else ""
    if s and s[0] in ("=", "+", "-", "@"):
        return "'" + s
    return s


def _metric_score_val(metric_obj) -> float:
    if hasattr(metric_obj, "score"):
        return float(metric_obj.score)
    if isinstance(metric_obj, dict):
        return float(metric_obj.get("score", 0.0))
    return 0.0


def generate_candidates_csv(ranked: list[RankedCandidate]) -> str:
    """Generate RFC 4180 CSV export of ranked candidates with formula injection neutralization."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Candidate Name", "File", "Overall Score", "Match Band",
        "Must-Have Coverage (%)", "Keyword Match Score", "Experience Score",
        "Impact Score", "Status", "Risk Flags"
    ])

    for c in ranked:
        row = [
            c.rank,
            c.candidate_name,
            c.filename,
            f"{c.overall_score:.1f}",
            c.match_band.capitalize(),
            f"{c.must_have_coverage:.1f}%",
            f"{_metric_score_val(c.metrics.get('keyword_match')):.1f}",
            f"{_metric_score_val(c.metrics.get('experience')):.1f}",
            f"{_metric_score_val(c.metrics.get('impact')):.1f}",
            c.status.capitalize(),
            "; ".join(c.risk_flags) if c.risk_flags else "None"
        ]
        writer.writerow([sanitize_csv_cell(cell) for cell in row])

    return output.getvalue()
