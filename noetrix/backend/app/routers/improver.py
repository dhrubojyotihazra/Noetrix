"""Candidate AI resume improvement and tailoring endpoints."""

from fastapi import APIRouter
from app.schemas.improver import (
    EnhanceBulletRequest,
    EnhanceBulletResponse,
    TailorResumeRequest,
    TailorResumeResponse
)
from app.services.improver import enhance_single_bullet, tailor_resume_to_jd

router = APIRouter(prefix="/api/improve", tags=["Improvement"])


@router.post("/bullet", response_model=EnhanceBulletResponse)
def enhance_bullet_endpoint(req: EnhanceBulletRequest):
    """Enhance a single experience bullet using XYZ impact framing and target technologies."""
    return enhance_single_bullet(
        bullet=req.bullet,
        job_title=req.job_title,
        target_keywords=req.target_keywords
    )


@router.post("/tailor", response_model=TailorResumeResponse)
def tailor_resume_endpoint(req: TailorResumeRequest):
    """Generate tailored resume variant with optimized bullets, injected keywords, and before/after diffs."""
    return tailor_resume_to_jd(
        resume=req.resume,
        jd=req.jd,
        strategy=req.prompt_strategy
    )
