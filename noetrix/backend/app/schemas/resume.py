"""Pydantic schemas for Resume representations."""

from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""


class WorkEntry(BaseModel):
    id: str = ""
    company: str = ""
    title: str = ""
    dates: str = ""
    location: str = ""
    bullets: list[str] = Field(default_factory=list)


class EduEntry(BaseModel):
    id: str = ""
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    dates: str = ""
    gpa: str = ""
    bullets: list[str] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    id: str = ""
    name: str = ""
    role: str = ""
    dates: str = ""
    technologies: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)


class ParsedResume(BaseModel):
    filename: str = "resume.pdf"
    raw_text: str = ""
    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: str = ""
    sections_detected: list[str] = Field(default_factory=list)
    work_experience: list[WorkEntry] = Field(default_factory=list)
    education: list[EduEntry] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    parse_confidence: float = 1.0
    detected_columns: int = 1
    has_tables: bool = False
    has_graphics: bool = False
    provenance: dict[str, str] = Field(default_factory=dict)
    overall_parse_method: str = "rules"
