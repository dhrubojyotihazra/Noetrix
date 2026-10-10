"""Job Description Criteria Extraction Service (LLM with deterministic rules fallback).

Non-negotiable requirements:
- Skills are concrete technologies, programming languages, frameworks, and tools.
- Generic words ('learning', 'experience', 'years', 'familiarity', etc.) are never emitted as skills.
- Only extract skills appearing in the JD text or known synonyms.
- Normalizes skill names to canonical taxonomy names; preserves unknown skills.
- Post-validation drops unsupported skills deterministically.
- Falls back cleanly to parse_job_description() with extraction_method='rules'.
"""

import logging
import re
from pydantic import BaseModel, Field

from app.schemas.jd import JDFeatures
from app.services.jd_parser import parse_job_description
from app.nlp.synonyms import normalize_term, get_synonyms
from app.nlp.tfidf import GENERIC_NON_SKILLS, extract_jd_keywords
from app.nlp.tokenizer import word_boundary_match
from app.genai.llm import complete_json, LLMUnavailable

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert technical recruiter and ATS parser. Extract structured job criteria from the provided job description.

Rules:
1. Skills MUST be concrete technologies, programming languages, frameworks, libraries, databases, cloud platforms, or engineering tools (e.g. Python, PyTorch, Docker, PostgreSQL, React).
2. NEVER emit generic words as skills: "learning", "experience", "years", "familiarity", "strong", "ability", "understanding", "working", "knowledge", "communication", "role", "qualifications".
3. ONLY extract skills and qualifications that explicitly appear in the job description text. Do NOT infer or hallucinate technologies not mentioned.
4. Distinguish strictly between:
   - must_have_skills: mandatory/required technical requirements.
   - nice_to_have_skills: preferred/bonus/optional technologies.
5. Extract min_experience_years as a float (0 if not specified).
6. Extract education_required if specified (e.g. "Bachelor's", "Master's", "PhD").
7. Extract up to 8 core technical responsibilities.
8. Output strictly valid JSON matching the schema."""


class LLMJobCriteria(BaseModel):
    title: str = "Target Position"
    must_have_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    min_experience_years: float = 0.0
    education_required: str = ""
    domain: str = "Technology"
    responsibilities: list[str] = Field(default_factory=list)


def _validate_and_filter_skills(skills: list[str], jd_text: str) -> list[str]:
    """Deterministically filter skills: ensure in JD text or synonyms, exclude generic words, normalize canonical."""
    lower_jd = jd_text.lower()
    valid_skills: list[str] = []
    seen: set[str] = set()

    for raw_skill in skills:
        cleaned = raw_skill.strip().lower()
        if not cleaned or len(cleaned) < 2:
            continue

        # Drop generic non-skills
        if cleaned in GENERIC_NON_SKILLS or any(g == cleaned for g in ["learning", "years", "experience", "skills"]):
            continue

        # Check if skill appears in JD text directly or via synonyms
        all_variants = get_synonyms(cleaned)
        appears_in_jd = any(word_boundary_match(var, lower_jd) for var in all_variants)
        if not appears_in_jd:
            # Check simple substring if multi-word
            appears_in_jd = any(var in lower_jd for var in all_variants)

        if appears_in_jd:
            canonical = normalize_term(cleaned)
            if canonical not in seen and canonical not in GENERIC_NON_SKILLS:
                seen.add(canonical)
                valid_skills.append(canonical)

    return valid_skills


def extract_jd_criteria(jd_text: str, title: str | None = None) -> JDFeatures:
    """Extract structured criteria from JD text via LLM with deterministic post-validation and rules fallback."""
    if not jd_text or not jd_text.strip():
        return parse_job_description(jd_text, title=title)

    try:
        # Prompt LLM
        prompt_user = f"Job Description Text:\n\"\"\"\n{jd_text[:3500]}\n\"\"\""
        extracted: LLMJobCriteria = complete_json(
            system=SYSTEM_PROMPT,
            user=prompt_user,
            model_cls=LLMJobCriteria
        )

        # Post-validate skills deterministically
        validated_must = _validate_and_filter_skills(extracted.must_have_skills, jd_text)
        validated_nice = _validate_and_filter_skills(extracted.nice_to_have_skills, jd_text)

        # Validate min_experience_years: ensure not wildly hallucinated
        min_years = max(0.0, min(20.0, float(extracted.min_experience_years or 0.0)))
        exp_matches = re.findall(r"(\d+)\+?\s*(?:to\s*\d+\s*)?years?", jd_text, re.IGNORECASE)
        if exp_matches and min_years == 0.0:
            try:
                min_years = float(exp_matches[0])
            except Exception:
                pass

        # Keywords for TF-IDF scoring
        keywords = extract_jd_keywords(jd_text, top_n=25)

        # If LLM returned empty must_haves, take top verified keywords
        if not validated_must and keywords:
            validated_must = [k for k in keywords if k not in GENERIC_NON_SKILLS][:5]

        inferred_title = title or extracted.title
        if not inferred_title or inferred_title == "Target Position":
            first_line = jd_text.strip().split("\n")[0]
            if len(first_line) < 80:
                inferred_title = first_line

        return JDFeatures(
            title=inferred_title,
            raw_text=jd_text,
            must_have_skills=sorted(list(set(validated_must))),
            nice_to_have_skills=sorted(list(set(validated_nice))),
            min_experience_years=min_years,
            domain=extracted.domain or "Technology",
            responsibilities=extracted.responsibilities[:10],
            keywords=keywords,
            education_required=extracted.education_required or "",
            extraction_method="llm"
        )

    except LLMUnavailable as e:
        logger.info(f"LLM criteria extraction unavailable ({e}), using rules parser.")
        return parse_job_description(jd_text, title=title)
    except Exception as e:
        logger.warning(f"Error during LLM criteria extraction ({e}), falling back to rules parser.")
        return parse_job_description(jd_text, title=title)
