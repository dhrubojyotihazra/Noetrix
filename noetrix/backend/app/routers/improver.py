import logging
from fastapi import APIRouter
from app.schemas.improver import (
    EnhanceBulletRequest,
    EnhanceBulletResponse,
    TailorResumeRequest,
    TailorResumeResponse
)
from app.services.improver import enhance_single_bullet, tailor_resume_to_jd

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/improve", tags=["Improvement"])


@router.post("/bullet", response_model=EnhanceBulletResponse)
def enhance_bullet_endpoint(req: EnhanceBulletRequest):
    """Enhance a single experience bullet using XYZ impact framing and target technologies."""
    try:
        return enhance_single_bullet(
            bullet=req.bullet,
            job_title=req.job_title,
            target_keywords=req.target_keywords
        )
    except Exception as e:
        logger.warning(f"Error in enhance_bullet_endpoint: {e}")
        return EnhanceBulletResponse(
            original=req.bullet,
            enhanced=req.bullet,
            rationale="Bullet preserved untouched."
        )


@router.post("/tailor", response_model=TailorResumeResponse)
def tailor_resume_endpoint(req: TailorResumeRequest):
    """Generate tailored resume variant with optimized bullets, injected keywords, and before/after diffs."""
    try:
        return tailor_resume_to_jd(
            resume=req.resume,
            jd=req.jd,
            strategy=req.prompt_strategy
        )
    except Exception as e:
        logger.exception(f"Error in tailor_resume_endpoint: {e}")
        from app.services.scorer.engine import score_resume_against_jd
        try:
            base_score = score_resume_against_jd(req.resume, req.jd).overall_score
        except Exception:
            base_score = 50.0
        return TailorResumeResponse(
            tailored_resume=req.resume,
            diffs=[],
            added_keywords=[],
            bullets_enhanced_count=0,
            estimated_score_before=base_score,
            estimated_score_after=base_score,
            estimated_gain=0.0
        )

