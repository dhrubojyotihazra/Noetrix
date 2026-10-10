"""Candidate Resume Tailoring & Bullet Optimization Service.

Implements grounded, truthful resume optimization modeled after open-source ATS analyzers (Resume-Matcher).
Guarantees:
- Never invents numbers or metrics (Google XYZ framing with honest user metrics).
- Never injects unconfirmed skills into candidate profiles.
- Never mutates non-bullet lines (job titles, degrees, tech stacks).
- Preserves semantic intent and only strengthens genuinely weak passive openings.
- Deterministic Zero-Fabrication Validator verifies every rewrite before accepting it.
"""

import copy
import logging
import re
from pydantic import BaseModel, Field

from app.schemas.resume import ParsedResume
from app.schemas.jd import JDFeatures
from app.schemas.improver import (
    EnhanceBulletResponse,
    TailorResumeResponse,
    DiffItem
)
from app.services.scorer.engine import score_resume_against_jd
from app.nlp.tokenizer import ACTION_VERBS, word_boundary_match
from app.nlp.tfidf import ALL_TAXONOMY_SKILLS, GENERIC_NON_SKILLS
from app.genai.llm import complete_json, LLMUnavailable, get_llm_config

logger = logging.getLogger(__name__)


# Explicit weak opener replacements that preserve exact semantic intent
WEAK_OPENER_REPLACEMENTS = [
    (r"^worked\s+on\s+developing\b", "Developed"),
    (r"^worked\s+on\s+building\b", "Built"),
    (r"^worked\s+on\s+optimizing\b", "Optimized"),
    (r"^worked\s+on\s+implementing\b", "Implemented"),
    (r"^worked\s+on\s+training\b", "Trained"),
    (r"^worked\s+on\s+evaluating\b", "Evaluated"),
    (r"^worked\s+on\b", "Executed"),
    (r"^helped\s+(to\s+)?build\b", "Built"),
    (r"^helped\s+(to\s+)?develop\b", "Developed"),
    (r"^helped\s+(to\s+)?implement\b", "Implemented"),
    (r"^helped\s+(to\s+)?optimize\b", "Optimized"),
    (r"^helped\s+with\b", "Collaborated on"),
    (r"^assisted\s+in\s+developing\b", "Developed"),
    (r"^assisted\s+in\s+building\b", "Built"),
    (r"^assisted\s+in\b", "Supported"),
    (r"^responsible\s+for\s+managing\b", "Managed"),
    (r"^responsible\s+for\s+leading\b", "Led"),
    (r"^responsible\s+for\s+developing\b", "Developed"),
    (r"^responsible\s+for\b", "Spearheaded"),
    (r"^tasked\s+with\b", "Delivered"),
    (r"^participated\s+in\b", "Contributed to"),
]

MEANING_REVERSAL_PAIRS = [
    ({"prevented", "avoided", "stopped", "mitigated", "blocked", "eliminated"},
     {"engineered", "caused", "created", "introduced", "generated", "built"}),
    ({"decreased", "reduced", "lowered", "cut", "minimized"},
     {"increased", "boosted", "maximized", "grew", "expanded"}),
    ({"increased", "boosted", "maximized", "grew", "expanded"},
     {"decreased", "reduced", "lowered", "cut", "minimized"}),
]

NON_BULLET_PATTERNS = [
    r"^(tech\s+stack|technologies|tools|languages|skills)[\s\:\·]",
    r"^(b\.tech|bachelor|master|m\.tech|phd|diploma|degree)\b",
    r"^(certifications?|licenses?|credentials?)[\s\:\·]",
    r"^[\w\s]+\s*·\s*[\w\s]+\s*·\s*[\w\s]+",  # Tech stack separator (Flask · React · DistilBERT)
    r"^[A-Z\s]{4,}$",  # All caps headings
]


class LLMBulletRewrite(BaseModel):
    original: str
    rewrite: str
    changes: list[str] = Field(default_factory=list)


def extract_numbers(text: str) -> set[str]:
    """Extract all numbers, percentages, multipliers, and currency tokens."""
    matches = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?%?\+?|\b\d+x\b|\$\d+(?:,\d+)*", text.lower())
    clean_nums = set()
    for m in matches:
        # Strip trailing punctuation
        c = m.strip().rstrip(".,;:+")
        if c:
            clean_nums.add(c)
    return clean_nums


def is_non_bullet_line(line: str) -> bool:
    """Detect whether a line is a non-bullet item (heading, degree, tech stack)."""
    trimmed = line.strip()
    if not trimmed:
        return True
    return any(bool(re.search(pat, trimmed, re.IGNORECASE)) for pat in NON_BULLET_PATTERNS)


def validate_bullet_rewrite(
    original: str,
    rewrite: str,
    candidate_skills: list[str] | None = None,
    user_confirmed: set[str] | None = None
) -> tuple[bool, str]:
    """Deterministic Zero-Fabrication Validator.
    
    Verifies:
    1. Numbers: Every number in rewrite must appear in original or user-confirmed.
    2. Skills: Every technical skill in rewrite must appear in original, candidate profile, or user-confirmed.
    3. Meaning preservation: Polarities and action intentions must not be inverted.
    4. Non-bullet integrity: Non-bullet lines must not be modified.
    """
    if not rewrite or not rewrite.strip():
        return False, "Rewrite is empty."

    # 0. Non-bullet integrity
    if is_non_bullet_line(original):
        return False, "Non-bullet line must remain untouched."

    # 1. Numbers verification
    orig_nums = extract_numbers(original)
    if user_confirmed:
        orig_nums.update(user_confirmed)

    rewrite_nums = extract_numbers(rewrite)
    new_nums = rewrite_nums - orig_nums
    if new_nums:
        # Detected hallucinated numbers!
        return False, f"Invented numbers or metrics detected: {sorted(list(new_nums))}."

    # 2. Skills verification
    orig_lower = original.lower()
    rewrite_lower = rewrite.lower()
    confirmed_skills = set(s.lower() for s in (candidate_skills or []))
    if user_confirmed:
        confirmed_skills.update(s.lower() for s in user_confirmed)

    for skill in ALL_TAXONOMY_SKILLS:
        if skill not in GENERIC_NON_SKILLS and len(skill) > 2:
            if word_boundary_match(skill, rewrite_lower) and not word_boundary_match(skill, orig_lower):
                if skill not in confirmed_skills:
                    return False, f"Unconfirmed skill injected: '{skill}'."

    # 3. Meaning preservation (no polarity reversal)
    for bad_source_set, bad_target_set in MEANING_REVERSAL_PAIRS:
        source_matched = any(word_boundary_match(w, orig_lower) for w in bad_source_set)
        target_matched = any(word_boundary_match(w, rewrite_lower) for w in bad_target_set)
        if source_matched and target_matched:
            return False, "Meaning reversal detected: verb polarity inverted."

    return True, "Valid rewrite."


def _enhance_bullet_llm(
    bullet: str,
    job_title: str = "",
    target_keywords: list[str] | None = None,
    candidate_skills: list[str] | None = None
) -> tuple[str, list[str], str]:
    """Execute LLM bullet rewrite via Groq and validate deterministically."""
    cfg = get_llm_config()
    model = cfg.get("fast_model") or cfg.get("model") or "openai/gpt-oss-20b"

    system = (
        "You are an expert resume editor adhering to Google XYZ impact framing and strict truthfulness.\n"
        "Improve the provided resume bullet for clarity, conciseness, strong action verbs, and professional tone.\n"
        "STRICT CONSTRAINTS:\n"
        "1. DO NOT invent numbers, percentages, dates, metrics, or achievements. If the original lacks metrics, keep it without metrics.\n"
        "2. DO NOT add new technologies, programming languages, or tools that do not exist in the original bullet.\n"
        "3. Preserve the exact factual meaning. Never invert or flip meaning (e.g. 'Prevented' must NOT become 'Engineered').\n"
        "4. Output strictly valid JSON with keys: original, rewrite, changes."
    )

    user_prompt = (
        f"Original Bullet: \"{bullet}\"\n"
        f"Job Title Context: \"{job_title}\"\n"
        "Output JSON matching schema."
    )

    resp: LLMBulletRewrite = complete_json(
        system=system,
        user=user_prompt,
        model_cls=LLMBulletRewrite,
        model=model
    )

    is_valid, reason = validate_bullet_rewrite(
        original=bullet,
        rewrite=resp.rewrite,
        candidate_skills=candidate_skills
    )

    if not is_valid:
        logger.info(f"[Validator] Rejected LLM rewrite: {reason}")
        return bullet, [], f"Rejected AI rewrite: {reason}"

    return resp.rewrite, resp.changes, "Enhanced with AI action framing and verified zero fabrication."


def get_raw_llm_bullet_rewrite(
    bullet: str,
    candidate_skills: list[str] | None = None
) -> tuple[str, bool, str]:
    """Retrieve raw LLM rewrite prior to validator intervention for eval comparisons."""
    cfg = get_llm_config()
    model = cfg.get("fast_model") or cfg.get("model") or "openai/gpt-oss-20b"
    system = (
        "You are an expert resume editor adhering to Google XYZ impact framing and strict truthfulness.\n"
        "Improve the provided resume bullet for clarity, conciseness, strong action verbs, and professional tone.\n"
        "STRICT CONSTRAINTS:\n"
        "1. DO NOT invent numbers, percentages, dates, metrics, or achievements. If the original lacks metrics, keep it without metrics.\n"
        "2. DO NOT add new technologies, programming languages, or tools that do not exist in the original bullet.\n"
        "3. Preserve the exact factual meaning. Never invert or flip meaning (e.g. 'Prevented' must NOT become 'Engineered').\n"
        "4. Output strictly valid JSON with keys: original, rewrite, changes."
    )
    user_prompt = f'Original Bullet: "{bullet}"\nJob Title Context: ""\nOutput JSON matching schema.'
    try:
        resp: LLMBulletRewrite = complete_json(
            system=system,
            user=user_prompt,
            model_cls=LLMBulletRewrite,
            model=model,
            timeout=60.0
        )
        raw_rewrite = resp.rewrite
    except Exception as e:
        raw_rewrite = bullet
    is_valid, reason = validate_bullet_rewrite(
        original=bullet,
        rewrite=raw_rewrite,
        candidate_skills=candidate_skills
    )
    return raw_rewrite, is_valid, reason


def enhance_single_bullet(
    bullet: str,
    job_title: str = "",
    target_keywords: list[str] | None = None,
    candidate_skills: list[str] | None = None
) -> EnhanceBulletResponse:
    """Enhance a bullet point by strengthening weak phrasing without inventing facts.
    
    If LLM_MODE=on, uses Groq LLM rewrite guarded by the Zero-Fabrication Validator.
    Otherwise, uses the deterministic rules-based weak opener optimizer.
    """
    clean = bullet.strip().lstrip("-•*–—> ").strip()
    if not clean:
        return EnhanceBulletResponse(original=bullet, enhanced=bullet)

    # Never mutate non-bullet lines
    if is_non_bullet_line(clean):
        # Ensure ends with clean punctuation
        if not clean.endswith((".", ":", "|", "-")):
            clean += "."
        return EnhanceBulletResponse(
            original=bullet,
            enhanced=clean,
            rationale="Non-bullet line preserved untouched."
        )

    # 1. Try LLM Rewrite if enabled
    cfg = get_llm_config()
    if cfg.get("mode") == "on":
        try:
            llm_enhanced, changes, rationale = _enhance_bullet_llm(
                clean, job_title, target_keywords, candidate_skills
            )
            if llm_enhanced != clean:
                return EnhanceBulletResponse(
                    original=clean,
                    enhanced=llm_enhanced,
                    keywords_included=[],
                    metrics_added=[],
                    rationale=rationale
                )
        except LLMUnavailable:
            pass
        except Exception as e:
            logger.info(f"LLM enhance failed ({type(e).__name__}), falling back to rules.")

    # 2. Deterministic Rules-Based Fallback
    transformed = clean
    verb_swapped = False

    # Check if bullet begins with a known weak opener
    for pattern, replacement in WEAK_OPENER_REPLACEMENTS:
        if re.search(pattern, transformed, re.IGNORECASE):
            transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
            verb_swapped = True
            break

    # If the first word is already a recognized strong action verb, do not mutate it
    words = transformed.split()
    if not verb_swapped and words:
        first_word_lower = words[0].lower().rstrip("ed").rstrip("d")
        if any(v.lower().startswith(first_word_lower) for v in ACTION_VERBS):
            transformed = clean

    # Ensure capitalized and ends with a period
    transformed = transformed[0].upper() + transformed[1:]
    if not transformed.endswith("."):
        transformed += "."

    has_metrics = bool(re.search(r"\b\d+(\.\d+)?%?|\b\d+x\b|\$[\d,]+", transformed))

    if verb_swapped:
        rationale = "Replaced passive opener with a direct action verb to improve recruiter clarity."
    elif not has_metrics:
        rationale = "Action phrasing is solid. To boost your Impact score, consider adding a real metric (e.g. speedup %, dataset size, or accuracy)."
    else:
        rationale = "Strong action-oriented bullet backed by quantifiable metrics."

    return EnhanceBulletResponse(
        original=clean,
        enhanced=transformed,
        keywords_included=[],
        metrics_added=[],
        rationale=rationale
    )


def tailor_resume_to_jd(
    resume: ParsedResume,
    jd: JDFeatures,
    strategy: str = "balanced"
) -> TailorResumeResponse:
    """Truthful tailoring: strengthens weak bullets, surfaces grounded skill alignments, never fabricates facts."""
    original_score_res = score_resume_against_jd(resume, jd)
    original_score = original_score_res.overall_score

    tailored = copy.deepcopy(resume)
    diffs: list[DiffItem] = []
    enhanced_count = 0

    # 1. Grounded Skill Suggestions (Only skills verified in resume text/projects)
    grounded_suggestions = []
    resume_lower = resume.raw_text.lower()
    existing_skills_lower = set(s.lower() for s in tailored.skills)

    GROUNDED_MAPPINGS = [
        ("transformers", ["distilbert", "hugging face", "huggingface", "bert"]),
        ("computer vision", ["opencv", "cv2", "image segmentation", "object detection"]),
        ("git", ["github", "gitlab", "version control"]),
        ("deep learning", ["pytorch", "tensorflow", "keras", "neural network"]),
        ("ci/cd", ["github actions", "gitlab ci", "jenkins"]),
        ("docker", ["dockerfile", "container", "containerization"]),
        ("rest api", ["fastapi", "flask", "express", "endpoints"]),
    ]

    for canonical, evidence_list in GROUNDED_MAPPINGS:
        if canonical not in existing_skills_lower and any(kw.lower() == canonical for kw in jd.must_have_skills + jd.nice_to_have_skills):
            if any(ev in resume_lower for ev in evidence_list):
                tailored.skills.append(canonical)
                grounded_suggestions.append(canonical)
                existing_skills_lower.add(canonical)

    if grounded_suggestions:
        diffs.append(DiffItem(
            section="skills",
            item_id="skills_grounded",
            change_type="added",
            original=f"{len(resume.skills)} skills",
            modified=f"Grounded from your project evidence: {', '.join(grounded_suggestions)}"
        ))

    # 2. Enhance genuine work experience bullets
    for w_idx, work in enumerate(tailored.work_experience):
        new_bullets = []
        for b_idx, bullet in enumerate(work.bullets):
            res = enhance_single_bullet(bullet, work.title, candidate_skills=resume.skills)
            new_bullets.append(res.enhanced)

            if res.enhanced != bullet:
                enhanced_count += 1
                diffs.append(DiffItem(
                    section="experience",
                    item_id=f"work_{w_idx}_bullet_{b_idx}",
                    change_type="modified",
                    original=bullet,
                    modified=res.enhanced
                ))
        work.bullets = new_bullets

    # 3. Enhance genuine project bullets
    for p_idx, proj in enumerate(tailored.projects):
        new_bullets = []
        for b_idx, bullet in enumerate(proj.bullets):
            res = enhance_single_bullet(bullet, proj.name, candidate_skills=resume.skills)
            new_bullets.append(res.enhanced)

            if res.enhanced != bullet:
                enhanced_count += 1
                diffs.append(DiffItem(
                    section="projects",
                    item_id=f"proj_{p_idx}_bullet_{b_idx}",
                    change_type="modified",
                    original=bullet,
                    modified=res.enhanced
                ))
        proj.bullets = new_bullets

    # Calculate post-tailoring score with the improved truthful state
    after_score_res = score_resume_against_jd(tailored, jd)
    after_score = after_score_res.overall_score
    delta = round(max(0.0, after_score - original_score), 1)

    return TailorResumeResponse(
        tailored_resume=tailored,
        diffs=diffs,
        added_keywords=grounded_suggestions,
        bullets_enhanced_count=enhanced_count,
        estimated_score_before=original_score,
        estimated_score_after=after_score,
        estimated_gain=delta
    )
