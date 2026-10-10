"""Recruiter batch ranking endpoint."""

from fastapi import APIRouter
from app.schemas.scoring import RankRequest, RankedCandidate
from app.services.ranker import rank_resumes_batch

router = APIRouter(prefix="/api", tags=["Ranking"])


@router.post("/rank", response_model=list[RankedCandidate])
def rank_candidates_endpoint(req: RankRequest):
    """Rank a batch of candidate resumes against job criteria with deterministic tie breaks."""
    return rank_resumes_batch(req.resumes, req.jd, req.config)
