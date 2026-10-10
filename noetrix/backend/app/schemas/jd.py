"""Pydantic schemas for Job Description features."""

from pydantic import BaseModel, Field


class JDFeatures(BaseModel):
    title: str = "Target Position"
    raw_text: str = ""
    must_have_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    min_experience_years: float = 0.0
    domain: str = "Technology"
    responsibilities: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    education_required: str = ""
    extraction_method: str = "rules"


class JDParseRequest(BaseModel):
    raw_text: str
    title: str | None = None
