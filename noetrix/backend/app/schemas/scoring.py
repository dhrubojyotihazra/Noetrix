"""Pydantic schemas for ATS Scoring & Ranking."""

from typing import Any
from pydantic import BaseModel, Field

from app.schemas.jd import JDFeatures
from app.schemas.resume import ParsedResume


class MetricScore(BaseModel):
    score: float = 0.0  # 0 to 100
    weight: float = 0.0
    weighted_score: float = 0.0
    evidence: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    rationale: str = ""


class ScoringConfig(BaseModel):
    # Default 6-metric weights: 30 / 20 / 20 / 10 / 10 / 10
    weights: dict[str, float] = Field(
        default_factory=lambda: {
            "keyword_match": 0.30,
            "semantic_fit": 0.20,
            "experience": 0.20,
            "education": 0.10,
            "impact": 0.10,
            "format": 0.10,
        }
    )
    must_have_cap: float = 50.0
    enable_must_have_cap: bool = True
    strong_band_threshold: float = 75.0
    moderate_band_threshold: float = 50.0


class ScoreResult(BaseModel):
    candidate_name: str = ""
    filename: str = ""
    overall_score: float = 0.0
    raw_fit_score: float = 0.0
    is_capped: bool = False
    match_band: str = "moderate"  # strong, moderate, weak
    metrics: dict[str, MetricScore] = Field(default_factory=dict)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    priority_fixes: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    ats_sees: dict[str, Any] = Field(default_factory=dict)


class RankedCandidate(BaseModel):
    rank: int = 1
    candidate_name: str = ""
    filename: str = ""
    overall_score: float = 0.0
    match_band: str = "moderate"
    must_have_coverage: float = 0.0
    years_experience: float = 0.0
    status: str = "active"  # active, shortlisted, hold, rejected
    risk_flags: list[str] = Field(default_factory=list)
    metrics: dict[str, MetricScore] = Field(default_factory=dict)
    resume_summary: str = ""


class ScoreRequest(BaseModel):
    resume: ParsedResume
    jd: JDFeatures
    config: ScoringConfig = Field(default_factory=ScoringConfig)


class RankRequest(BaseModel):
    resumes: list[ParsedResume]
    jd: JDFeatures
    config: ScoringConfig = Field(default_factory=ScoringConfig)
