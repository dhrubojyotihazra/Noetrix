"""Batch ranking service for recruiters with multi-attribute tie breaking."""

import io
import csv
from app.schemas.resume import ParsedResume
from app.schemas.jd import JDFeatures
from app.schemas.scoring import ScoringConfig, RankedCandidate, ScoreResult
from app.services.scorer.engine import score_resume_against_jd


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
            years_experience=round(float(len(res.work_experience) * 2.0), 1),
            status="active",
            risk_flags=score_res.risk_flags,
            metrics=score_res.metrics,
            resume_summary=res.summary or (res.work_experience[0].title if res.work_experience else "")
        ))

    return ranked_results


def generate_candidates_csv(ranked: list[RankedCandidate]) -> str:
    """Generate RFC 4180 CSV export of ranked candidates."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Candidate Name", "File", "Overall Score", "Match Band",
        "Must-Have Coverage (%)", "Keyword Match Score", "Experience Score",
        "Impact Score", "Status", "Risk Flags"
    ])

    for c in ranked:
        writer.writerow([
            c.rank,
            c.candidate_name,
            c.filename,
            f"{c.overall_score:.1f}",
            c.match_band.capitalize(),
            f"{c.must_have_coverage:.1f}%",
            f"{c.metrics.get('keyword_match', {}).score:.1f}",
            f"{c.metrics.get('experience', {}).score:.1f}",
            f"{c.metrics.get('impact', {}).score:.1f}",
            c.status.capitalize(),
            "; ".join(c.risk_flags) if c.risk_flags else "None"
        ])

    return output.getvalue()
