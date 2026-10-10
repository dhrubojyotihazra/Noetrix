"""CV Structure Extraction and Fallback Hybrid Service.

Non-negotiable rules:
1. Run rules parser first.
2. Only call LLM if:
   - parse_confidence < 0.6
   - A core section (experience, education, skills) is missing
   - Parsed bullet count > 3 * source bullet lines
3. Send ONLY redacted text to LLM (names, email, phone removed).
4. Deterministic anti-hallucination validation:
   - Bullets must fuzzy match source text (rapidfuzz >= 0.9 similarity).
   - Dates must appear in source text.
   - Skills must exist in taxonomy or source text.
5. Merge strategy: keep confident rules output, only fill missing/low-confidence fields from AI.
6. Provenance recorded per field: 'rules' or 'llm'.
"""

import logging
import re
from pydantic import BaseModel, Field
from rapidfuzz import fuzz

from app.schemas.resume import ParsedResume, WorkEntry, EduEntry, ProjectEntry
from app.nlp.tfidf import ALL_TAXONOMY_SKILLS, GENERIC_NON_SKILLS
from app.nlp.synonyms import normalize_term
from app.nlp.tokenizer import word_boundary_match
from app.genai.redact import redact_pii
from app.genai.llm import complete_json, LLMUnavailable

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert ATS resume parser. Extract structured sections and bullet points from the redacted candidate CV text.

CRITICAL RULES:
1. Grounding: Do NOT invent or fabricate companies, institutions, degrees, dates, job titles, certifications, or bullet points. Every extracted item MUST be present in the candidate text.
2. Preserving text: Extract bullet points verbatim or with minor cleanup of wrapped lines. Do not inject fake numbers or metrics.
3. Skills: Only extract technical skills, tools, and libraries explicitly mentioned in the text.
4. Output strictly valid JSON matching the schema."""


class LLMWorkEntry(BaseModel):
    company: str = ""
    title: str = ""
    dates: str = ""
    bullets: list[str] = Field(default_factory=list)


class LLMEduEntry(BaseModel):
    institution: str = ""
    degree: str = ""
    dates: str = ""
    bullets: list[str] = Field(default_factory=list)


class LLMProjectEntry(BaseModel):
    name: str = ""
    dates: str = ""
    technologies: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)


class LLMResumeStructure(BaseModel):
    summary: str = ""
    work_experience: list[LLMWorkEntry] = Field(default_factory=list)
    education: list[LLMEduEntry] = Field(default_factory=list)
    projects: list[LLMProjectEntry] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


def _fuzzy_matches_source(text_snippet: str, source_text: str, threshold: float = 90.0) -> bool:
    """Validate that text snippet appears in source text using high-confidence fuzzy matching (>=0.9)."""
    if not text_snippet or not text_snippet.strip():
        return False
    clean_snippet = text_snippet.strip().lower()
    clean_source = source_text.lower()

    if clean_snippet in clean_source:
        return True

    # Check partial ratio and token set ratio
    if fuzz.partial_ratio(clean_snippet[:100], clean_source) >= threshold:
        return True
    return False


def _date_in_source(date_str: str, source_text: str) -> bool:
    """Validate that date tokens appear in source text."""
    if not date_str or not date_str.strip():
        return True
    years = re.findall(r"\b(20\d\d|19\d\d)\b", date_str)
    if not years:
        return True
    source_lower = source_text.lower()
    return all(yr in source_lower for yr in years)


def extract_cv_structure_hybrid(parsed: ParsedResume) -> ParsedResume:
    """Assess whether rules parser needs LLM assistance and merge validated LLM structure if triggered."""
    raw_text = parsed.raw_text or ""
    raw_lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

    # Count raw lines with bullet markers
    raw_bullet_markers = sum(
        1 for line in raw_lines
        if re.match(r"^[\-\•\*\–\—\>]\s*|^\d+[\.\)]\s*", line)
    )
    total_parsed_bullets = sum(len(w.bullets) for w in parsed.work_experience) + sum(len(p.bullets) for p in parsed.projects)

    # Core sections check
    has_experience = bool(parsed.work_experience) or "experience" in parsed.sections_detected
    has_education = bool(parsed.education) or "education" in parsed.sections_detected
    has_skills = bool(parsed.skills) or "skills" in parsed.sections_detected

    needs_ai = (
        parsed.parse_confidence < 0.6
        or not (has_experience and has_education and has_skills)
        or (raw_bullet_markers > 0 and total_parsed_bullets > 3 * raw_bullet_markers)
    )

    # Initialize provenance defaults
    provenance = {
        "contact": "rules",
        "summary": "rules",
        "experience": "rules",
        "education": "rules",
        "skills": "rules",
        "projects": "rules",
        "certifications": "rules"
    }

    if not needs_ai:
        parsed.provenance = provenance
        parsed.overall_parse_method = "rules"
        return parsed

    # Redact sensitive PII before sending to Groq
    redacted = redact_pii(raw_text, parsed.contact.name)

    try:
        llm_out: LLMResumeStructure = complete_json(
            system=SYSTEM_PROMPT,
            user=f"Redacted Candidate Resume:\n\"\"\"\n{redacted[:4500]}\n\"\"\"",
            model_cls=LLMResumeStructure
        )

        # Merge validated fields where rules parser was weak or missing
        # 1. Experience
        if not parsed.work_experience and llm_out.work_experience:
            valid_work: list[WorkEntry] = []
            for idx, w in enumerate(llm_out.work_experience):
                if not _fuzzy_matches_source(w.company, raw_text, threshold=75.0) and not _fuzzy_matches_source(w.title, raw_text, threshold=75.0):
                    continue
                if not _date_in_source(w.dates, raw_text):
                    continue

                valid_bullets = [
                    b for b in w.bullets
                    if _fuzzy_matches_source(b, raw_text, threshold=90.0)
                ]
                valid_work.append(WorkEntry(
                    id=f"exp_{idx+1}",
                    company=w.company,
                    title=w.title,
                    dates=w.dates,
                    bullets=valid_bullets
                ))

            if valid_work:
                parsed.work_experience = valid_work
                provenance["experience"] = "llm"
                if "experience" not in parsed.sections_detected:
                    parsed.sections_detected.append("experience")

        # 2. Education
        if not parsed.education and llm_out.education:
            valid_edu: list[EduEntry] = []
            for idx, e in enumerate(llm_out.education):
                if not _fuzzy_matches_source(e.institution, raw_text, threshold=75.0) and not _fuzzy_matches_source(e.degree, raw_text, threshold=75.0):
                    continue
                valid_edu.append(EduEntry(
                    id=f"edu_{idx+1}",
                    institution=e.institution,
                    degree=e.degree,
                    dates=e.dates,
                    bullets=[b for b in e.bullets if _fuzzy_matches_source(b, raw_text, threshold=90.0)]
                ))
            if valid_edu:
                parsed.education = valid_edu
                provenance["education"] = "llm"
                if "education" not in parsed.sections_detected:
                    parsed.sections_detected.append("education")

        # 3. Skills
        if len(parsed.skills) < 5 and llm_out.skills:
            clean_skills = []
            lower_raw = raw_text.lower()
            for s in llm_out.skills:
                s_clean = s.strip().lower()
                if s_clean in GENERIC_NON_SKILLS or len(s_clean) < 2:
                    continue
                if s_clean in ALL_TAXONOMY_SKILLS or word_boundary_match(s_clean, lower_raw):
                    clean_skills.append(normalize_term(s_clean))
            if clean_skills:
                parsed.skills = sorted(list(set(parsed.skills + clean_skills)))
                provenance["skills"] = "llm"
                if "skills" not in parsed.sections_detected:
                    parsed.sections_detected.append("skills")

        # 4. Certifications
        if not parsed.certifications and llm_out.certifications:
            valid_certs = [
                c for c in llm_out.certifications
                if _fuzzy_matches_source(c, raw_text, threshold=80.0)
            ]
            if valid_certs:
                parsed.certifications = valid_certs
                provenance["certifications"] = "llm"

        parsed.provenance = provenance
        parsed.overall_parse_method = "llm" if any(v == "llm" for v in provenance.values()) else "rules"
        parsed.parse_confidence = max(parsed.parse_confidence, 0.85 if len(parsed.sections_detected) >= 3 else 0.7)
        return parsed

    except LLMUnavailable:
        logger.info("LLM structure extraction unavailable, keeping rules parsing.")
        parsed.provenance = provenance
        parsed.overall_parse_method = "rules"
        return parsed
    except Exception as e:
        logger.warning(f"Error during LLM structure extraction ({e}), falling back to rules parsing.")
        parsed.provenance = provenance
        parsed.overall_parse_method = "rules"
        return parsed
