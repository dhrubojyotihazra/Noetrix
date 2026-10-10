"""Health check endpoint for liveness and deployment verification."""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
def health_check():
    """Liveness probe for Render and local development."""
    return {"status": "ok", "app": "Noetrix", "version": "1.0.0"}


@router.get("/llm/health")
def llm_health_check():
    """Report LLM mode, provider, model, and reachability without exposing secrets."""
    from app.genai.llm import check_llm_health
    return check_llm_health()

