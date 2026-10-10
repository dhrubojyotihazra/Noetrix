"""Pydantic schemas for Candidate AI Editing and Resume Tailoring."""

from typing import Any
from pydantic import BaseModel, Field

from app.schemas.jd import JDFeatures
from app.schemas.resume import ParsedResume


class EnhanceBulletRequest(BaseModel):
    bullet: str
    job_title: str = ""
    target_keywords: list[str] = Field(default_factory=list)
    action_verb: str | None = None


class EnhanceBulletResponse(BaseModel):
    original: str
    enhanced: str
    keywords_included: list[str] = Field(default_factory=list)
    metrics_added: list[str] = Field(default_factory=list)
    rationale: str = ""


class DiffItem(BaseModel):
    section: str  # summary, experience, skills
    item_id: str = ""
    change_type: str  # added, modified, removed
    original: str = ""
    modified: str = ""


class TailorResumeRequest(BaseModel):
    resume: ParsedResume
    jd: JDFeatures
    prompt_strategy: str = "balanced"  # keywords, impact, balanced


class TailorResumeResponse(BaseModel):
    tailored_resume: ParsedResume
    diffs: list[DiffItem] = Field(default_factory=list)
    added_keywords: list[str] = Field(default_factory=list)
    bullets_enhanced_count: int = 0
    estimated_score_before: float = 0.0
    estimated_score_after: float = 0.0
    estimated_gain: float = 0.0
