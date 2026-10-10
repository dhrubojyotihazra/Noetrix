"""Candidate scoring endpoint."""

from fastapi import APIRouter
from app.schemas.scoring import ScoreRequest, ScoreResult
from app.services.scorer.engine import score_resume_against_jd

router = APIRouter(prefix="/api", tags=["Scoring"])


@router.post("/score", response_model=ScoreResult)
def score_candidate_resume(req: ScoreRequest):
    """Run full deterministic 6-metric ATS evaluation for a single resume."""
    return score_resume_against_jd(req.resume, req.jd, req.config)


@router.post("/explain")
def explain_score_endpoint(req: ScoreRequest):
    """Generate grounded evidence-backed explanation (strengths, gaps, fixes) for a score."""
    from app.genai.explain import explain
    score_res = score_resume_against_jd(req.resume, req.jd, req.config)
    return explain(req.resume, req.jd, score_res)

