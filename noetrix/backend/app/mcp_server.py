"""Noetrix Explainable ATS Resume Screening & Tailoring MCP Server.

Provides Model Context Protocol (MCP) tools for Claude, Cursor, Antigravity,
and other MCP-compatible AI clients to directly evaluate, score, parse,
and rank resumes against job descriptions.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Any

# Ensure TensorFlow and PyTorch do not write unwanted diagnostic output to stdout.
# Stdout MUST be strictly reserved for JSON-RPC in stdio MCP servers.
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Direct all standard logging to stderr
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [noetrix-mcp] %(message)s",
)
logger = logging.getLogger("noetrix_mcp")

from mcp.server.fastmcp import FastMCP

from app.schemas.scoring import ScoringConfig, ScoreResult
from app.schemas.resume import ParsedResume
from app.schemas.jd import JDFeatures
from app.services.scorer.engine import score_resume_against_jd
from app.services.jd_parser import parse_job_description as internal_parse_jd
from app.services.parser.text_parser import parse_resume_text
from app.services.parser.file_parser import parse_resume_from_file

mcp = FastMCP(
    name="noetrix-ats",
    instructions=(
        "Noetrix Explainable ATS Resume Screening Engine. Provides deterministic 6-metric "
        "ATS evaluation, anti-keyword-stuffing soft knockout enforcement, resume/JD parsing, "
        "and candidate batch ranking."
    ),
)


def _build_scoring_config(
    weights: dict[str, float] | None = None,
    must_have_cap: float = 50.0,
) -> ScoringConfig:
    """Build a sanitized ScoringConfig instance."""
    cfg = ScoringConfig()
    cfg.must_have_cap = must_have_cap
    if weights:
        total = sum(weights.values()) or 1.0
        cfg.weights = {k: v / total for k, v in weights.items()}
    return cfg


def _format_score_result(result: ScoreResult) -> dict[str, Any]:
    """Serialize ScoreResult to a clean, structured dictionary."""
    return {
        "candidate_name": result.candidate_name,
        "filename": result.filename,
        "overall_score": round(result.overall_score, 1),
        "raw_fit_score": round(result.raw_fit_score, 1),
        "match_band": result.match_band,
        "is_capped": result.is_capped,
        "verdict": (
            f"Candidate scored {result.overall_score:.1f}/100 ({result.match_band.upper()} MATCH)"
            + (" — [CAPPED at 50% due to missing mandatory must-have skills]" if result.is_capped else "")
        ),
        "metrics": {
            k: {
                "score": round(m.score, 1),
                "weight": round(m.weight, 2),
                "weighted_score": round(m.weighted_score, 1),
                "evidence": m.evidence[:10],
                "missing": m.missing[:10],
                "rationale": m.rationale,
            }
            for k, m in result.metrics.items()
        },
        "matched_keywords": result.matched_keywords,
        "missing_keywords": result.missing_keywords,
        "priority_fixes": result.priority_fixes,
        "risk_flags": result.risk_flags,
        "ats_sees": result.ats_sees,
    }


@mcp.tool()
def score_resume(
    resume_text: str,
    job_description: str,
    weights: dict[str, float] | None = None,
    must_have_cap: float = 50.0,
) -> dict[str, Any]:
    """Score a candidate resume against a job description using Noetrix's explainable 6-metric ATS engine.

    Evaluates:
      1. Keyword Match (30%): Technical skills taxonomy overlap and synonym expansion.
      2. Semantic Fit (20%): Dense contextual vector similarity (Sentence-Transformers / cosine).
      3. Experience Tenure (20%): Relevant career tenure vs role requirements.
      4. Education Fit (10%): Degree, field of study, and institution relevance.
      5. Impact Quantification (10%): Measurable metric density (XYZ accomplishment format).
      6. Formatting Health (10%): Layout parsability, column count, and structure health.

    Enforces the 50% Soft Knockout anti-keyword-stuffing rule: if a candidate satisfies
    fewer than half (<50%) of mandatory must-have skills in context, the total score
    is capped at 50.0.

    Args:
        resume_text: Raw plain text or markdown of the candidate resume.
        job_description: Full text of the target job description or requirements.
        weights: Optional custom weights dict (e.g. {"keyword_match": 0.35, "semantic_fit": 0.25, ...}).
        must_have_cap: Maximum score allowed when <50% must-have skills are present (default 50.0).

    Returns:
        Structured ATS scorecard containing overall score, match band (strong/moderate/weak),
        is_capped flag, 6 metric breakdowns, matched keywords, missing keywords, priority fixes,
        and what the ATS parser sees.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("resume_text cannot be empty.")
    if not job_description or not job_description.strip():
        raise ValueError("job_description cannot be empty.")

    parsed_resume = parse_resume_text(resume_text, filename="candidate_resume.txt")
    parsed_jd = internal_parse_jd(job_description)
    cfg = _build_scoring_config(weights, must_have_cap)

    result = score_resume_against_jd(parsed_resume, parsed_jd, cfg)
    return _format_score_result(result)


@mcp.tool()
def score_resume_file(
    file_path: str,
    job_description: str,
    weights: dict[str, float] | None = None,
    must_have_cap: float = 50.0,
) -> dict[str, Any]:
    """Score a local resume document (.pdf, .docx, .txt, or .md) against a job description.

    Extracts text, table data, and layout characteristics (such as multi-column detection
    risks) directly from the filesystem file and evaluates it against the job description.

    Args:
        file_path: Absolute or relative filesystem path to the resume document.
        job_description: Full text of the target job description.
        weights: Optional custom weights dict.
        must_have_cap: Score ceiling for must-have deficit (default 50.0).

    Returns:
        Structured ATS evaluation dictionary including column detection and document layout health.
    """
    if not file_path or not file_path.strip():
        raise ValueError("file_path cannot be empty.")
    if not job_description or not job_description.strip():
        raise ValueError("job_description cannot be empty.")

    parsed_resume = parse_resume_from_file(file_path)
    parsed_jd = internal_parse_jd(job_description)
    cfg = _build_scoring_config(weights, must_have_cap)

    result = score_resume_against_jd(parsed_resume, parsed_jd, cfg)
    return _format_score_result(result)


@mcp.tool()
def parse_resume(resume_text: str) -> dict[str, Any]:
    """Parse raw resume text into structured ATS entities without scoring.

    Extracts contact info, detected sections, work history with individual bullet points,
    education credentials, technical skills matched against Noetrix's taxonomy,
    projects, and certifications.

    Args:
        resume_text: Raw plain text or markdown of the candidate resume.

    Returns:
        Structured resume dictionary with contact info, sections, experience entries,
        education entries, skills, and overall parse confidence score (0.0 to 1.0).
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("resume_text cannot be empty.")

    parsed = parse_resume_text(resume_text)
    return {
        "candidate_name": parsed.contact.name or "Not detected",
        "contact": parsed.contact.model_dump(),
        "summary": parsed.summary,
        "sections_detected": parsed.sections_detected,
        "skills_count": len(parsed.skills),
        "skills": parsed.skills,
        "work_experience": [w.model_dump() for w in parsed.work_experience],
        "education": [e.model_dump() for e in parsed.education],
        "projects": [p.model_dump() for p in parsed.projects],
        "certifications": parsed.certifications,
        "parse_confidence": parsed.parse_confidence,
        "detected_columns": parsed.detected_columns,
        "has_tables": parsed.has_tables,
    }


@mcp.tool()
def parse_resume_file(file_path: str) -> dict[str, Any]:
    """Parse a local resume document (.pdf, .docx, .txt, .md) into structured ATS entities.

    Analyzes file layout, multi-column gutters, tables, contact headers, and extracts
    structured experience and education blocks.

    Args:
        file_path: Filesystem path to the resume file.

    Returns:
        Structured dictionary of parsed entities and layout analysis.
    """
    parsed = parse_resume_from_file(file_path)
    return {
        "filename": parsed.filename,
        "candidate_name": parsed.contact.name or "Not detected",
        "contact": parsed.contact.model_dump(),
        "summary": parsed.summary,
        "sections_detected": parsed.sections_detected,
        "skills_count": len(parsed.skills),
        "skills": parsed.skills,
        "work_experience": [w.model_dump() for w in parsed.work_experience],
        "education": [e.model_dump() for e in parsed.education],
        "projects": [p.model_dump() for p in parsed.projects],
        "certifications": parsed.certifications,
        "parse_confidence": parsed.parse_confidence,
        "detected_columns": parsed.detected_columns,
        "has_tables": parsed.has_tables,
    }


@mcp.tool()
def parse_job_description(job_description: str, title: str = "") -> dict[str, Any]:
    """Parse a job description into structured ATS recruiting criteria.

    Identifies mandatory must-have skills, preferred nice-to-have skills,
    minimum years of required experience, education criteria, and core responsibilities.

    Args:
        job_description: Raw text of the job description.
        title: Optional title of the position. If omitted, inferred from the first line.

    Returns:
        Structured JD dictionary containing title, must_have_skills, nice_to_have_skills,
        min_experience_years, education_required, responsibilities, and extracted keywords.
    """
    if not job_description or not job_description.strip():
        raise ValueError("job_description cannot be empty.")

    jd = internal_parse_jd(job_description, title=title or None)
    return {
        "title": jd.title,
        "must_have_skills": jd.must_have_skills,
        "nice_to_have_skills": jd.nice_to_have_skills,
        "min_experience_years": jd.min_experience_years,
        "education_required": jd.education_required,
        "responsibilities": jd.responsibilities,
        "keywords": jd.keywords,
        "extraction_method": jd.extraction_method,
    }


@mcp.tool()
def rank_resumes(
    resumes: list[dict[str, Any]],
    job_description: str,
    weights: dict[str, float] | None = None,
    must_have_cap: float = 50.0,
) -> list[dict[str, Any]]:
    """Rank a batch of candidate resumes against a single job description.

    Accepts multiple candidates and returns a ranked leaderboard sorted by ATS score descending.

    Args:
        resumes: List of candidate dicts. Each item must contain either:
                 - 'resume_text': string of resume text, OR
                 - 'file_path': string path to a local resume file.
                 Optional 'name': custom label/name for the candidate.
        job_description: Full text of the target job description.
        weights: Optional custom metric weights.
        must_have_cap: Anti-stuffing ceiling for missing mandatory must-haves.

    Returns:
        List of ranked candidate summaries sorted by overall ATS score descending, with rank,
        candidate name, overall score, match band, is_capped, matched skills count, and key risk flags.
    """
    if not resumes:
        return []
    if not job_description or not job_description.strip():
        raise ValueError("job_description cannot be empty.")

    parsed_jd = internal_parse_jd(job_description)
    cfg = _build_scoring_config(weights, must_have_cap)

    candidates = []
    for idx, item in enumerate(resumes):
        custom_name = item.get("name")
        resume_text = item.get("resume_text")
        file_path = item.get("file_path")

        if file_path:
            parsed_resume = parse_resume_from_file(file_path)
        elif resume_text:
            parsed_resume = parse_resume_text(
                resume_text, filename=f"candidate_{idx+1}.txt"
            )
        else:
            continue

        if custom_name:
            parsed_resume.contact.name = custom_name

        score_res = score_resume_against_jd(parsed_resume, parsed_jd, cfg)
        candidates.append((score_res, parsed_resume))

    # Sort descending by overall score, tie-breaking by raw fit score
    candidates.sort(key=lambda x: (x[0].overall_score, x[0].raw_fit_score), reverse=True)

    leaderboard = []
    for rank, (score_res, parsed_resume) in enumerate(candidates, start=1):
        leaderboard.append({
            "rank": rank,
            "candidate_name": score_res.candidate_name,
            "overall_score": round(score_res.overall_score, 1),
            "match_band": score_res.match_band,
            "is_capped": score_res.is_capped,
            "matched_skills_count": len(score_res.matched_keywords),
            "matched_keywords": score_res.matched_keywords[:8],
            "missing_keywords": score_res.missing_keywords[:5],
            "risk_flags": score_res.risk_flags,
            "years_experience": round(
                sum(
                    # approximate years from experience score
                    1.0 for _ in parsed_resume.work_experience
                ) * 1.5,
                1,
            ),
        })

    return leaderboard


@mcp.tool()
def explain_score(
    resume_text: str,
    job_description: str,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Generate an in-depth explainability dossier for why a candidate received their score.

    Details the candidate's alignment with evidence quotes, gap analysis, anti-gaming checks,
    and prioritized bullet-level improvement advice following the XYZ formula.

    Args:
        resume_text: Candidate resume text.
        job_description: Target job description.
        weights: Optional custom scoring weights.

    Returns:
        Comprehensive breakdown including summary verdict, strengths with source evidence,
        gaps with missing requirements, anti-gaming analysis, and actionable advice.
    """
    score_data = score_resume(resume_text, job_description, weights=weights)

    strengths = []
    gaps = []

    for metric_name, m_info in score_data["metrics"].items():
        if m_info["score"] >= 70.0 and m_info["evidence"]:
            strengths.append({
                "metric": metric_name,
                "score": m_info["score"],
                "evidence_quotes": m_info["evidence"][:3],
                "rationale": m_info["rationale"],
            })
        elif m_info["score"] < 60.0:
            gaps.append({
                "metric": metric_name,
                "score": m_info["score"],
                "missing_items": m_info["missing"][:3],
                "rationale": m_info["rationale"],
            })

    anti_gaming = {
        "is_capped": score_data["is_capped"],
        "soft_knockout_triggered": score_data["is_capped"],
        "explanation": (
            "Candidate triggered the 50% Soft Knockout ceiling because fewer than half of "
            "mandatory must-have skills were evidenced with contextual proof in experience or projects."
            if score_data["is_capped"]
            else "Candidate cleared the 50% mandatory must-have skills coverage requirement. No anti-gaming cap was applied."
        ),
    }

    return {
        "candidate_name": score_data["candidate_name"],
        "overall_score": score_data["overall_score"],
        "match_band": score_data["match_band"],
        "verdict": score_data["verdict"],
        "strengths": strengths,
        "gaps": gaps,
        "anti_gaming_analysis": anti_gaming,
        "priority_fixes": score_data["priority_fixes"],
        "matched_keywords": score_data["matched_keywords"],
        "missing_keywords": score_data["missing_keywords"],
    }


def main():
    """Run the Noetrix FastMCP server over standard I/O (stdio)."""
    logger.info("Starting Noetrix ATS MCP Server on stdio transport...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
