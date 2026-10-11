"""Job description section chunker and feature extractor."""

import re
from app.schemas.jd import JDFeatures
from app.nlp.tokenizer import word_boundary_match
from app.nlp.tfidf import ALL_TAXONOMY_SKILLS, extract_jd_keywords


def parse_job_description(raw_text: str, title: str | None = None) -> JDFeatures:
    """Parse raw JD text into structured JDFeatures."""
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    inferred_title = title or (lines[0] if lines else "Target Role")

    # Extract keywords
    extracted_keywords = extract_jd_keywords(raw_text, top_n=25)

    # Detect minimum experience years (allow up to 3 words between 'years' and 'experience')
    min_years = 0.0
    exp_matches = re.findall(r"(\d+)\+?(?:\s*(?:to|-)\s*\d+)?\s*years?(?:\s+\w+){0,3}?\s+experience", raw_text, re.IGNORECASE)
    if exp_matches:
        try:
            min_years = float(exp_matches[0])
        except Exception:
            pass

    # Helper to group "X or Y" skills
    def group_or_skills(text: str, skills: list[str]) -> list[str]:
        if len(skills) < 2:
            return skills
        grouped = []
        skip = set()
        lower_t = text.lower()
        for i, s1 in enumerate(skills):
            if s1 in skip:
                continue
            paired = False
            for j in range(i + 1, len(skills)):
                s2 = skills[j]
                if s2 in skip:
                    continue
                pat1 = rf"\b{re.escape(s1)}\b\s+(?:or|/)\s+\b{re.escape(s2)}\b"
                pat2 = rf"\b{re.escape(s2)}\b\s+(?:or|/)\s+\b{re.escape(s1)}\b"
                if re.search(pat1, lower_t):
                    grouped.append(f"{s1} or {s2}")
                    skip.add(s1)
                    skip.add(s2)
                    paired = True
                    break
                elif re.search(pat2, lower_t):
                    grouped.append(f"{s2} or {s1}")
                    skip.add(s1)
                    skip.add(s2)
                    paired = True
                    break
            if not paired and s1 not in skip:
                grouped.append(s1)
        return grouped

    # Segregate must-have vs nice-to-have skills
    must_haves: set[str] = set()
    nice_to_haves: set[str] = set()
    responsibilities: list[str] = []

    current_mode = "general"
    for line in lines:
        lower_line = line.lower()
        if any(h in lower_line for h in ["must have", "required", "requirements", "basic qualifications", "what you need"]):
            current_mode = "must_have"
            continue
        elif any(h in lower_line for h in ["nice to have", "preferred", "bonus", "preferred qualifications"]):
            current_mode = "nice_to_have"
            continue
        elif any(h in lower_line for h in ["responsibilities", "what you'll do", "what you will do"]):
            current_mode = "responsibilities"
            continue

        if current_mode == "responsibilities":
            if line.startswith(("-", "•", "*")):
                responsibilities.append(line.lstrip("-•* ").strip())

        # Check for clauses or sub-sections on this line
        line_is_familiarity = any(f in lower_line for f in ["familiarity with", "familiar with", "exposure to"])
        clauses = re.split(r"\s+and\s+(?=(?:building|developing|scaling|designing|architecting|implementing|maintaining)\b)", line, flags=re.IGNORECASE)

        for clause in clauses:
            lower_clause = clause.lower()
            clause_is_fam = any(f in lower_clause for f in ["familiarity with", "familiar with", "exposure to"])
            mode = "nice_to_have" if (clause_is_fam or (line_is_familiarity and len(clauses) == 1)) else current_mode

            clause_skills = [
                skill for skill in ALL_TAXONOMY_SKILLS
                if word_boundary_match(skill, lower_clause)
            ]
            clause_grouped = group_or_skills(lower_clause, clause_skills)

            for s in clause_grouped:
                if mode == "must_have":
                    must_haves.add(s)
                elif mode == "nice_to_have":
                    nice_to_haves.add(s)

    from app.nlp.tfidf import GENERIC_NON_SKILLS

    # Detect education requirement
    education_required = ""
    for deg in ["phd", "doctorate", "master", "ms", "m.tech", "bachelor", "bs", "b.tech", "degree", "diploma"]:
        if re.search(rf"\b{re.escape(deg)}\b", raw_text, re.IGNORECASE):
            education_required = deg.capitalize()
            break

    # Filter out any generic non-skills
    clean_must_haves = [s for s in must_haves if s not in GENERIC_NON_SKILLS]
    clean_nice_to_haves = [s for s in nice_to_haves if s not in GENERIC_NON_SKILLS]

    # If no explicit must-haves detected via section headers, take top 5 prominent skills
    if not clean_must_haves and extracted_keywords:
        clean_must_haves = [k for k in extracted_keywords if k not in GENERIC_NON_SKILLS][:5]

    return JDFeatures(
        title=inferred_title,
        raw_text=raw_text,
        must_have_skills=sorted(list(set(clean_must_haves))),
        nice_to_have_skills=sorted(list(set(clean_nice_to_haves))),
        min_experience_years=min_years,
        domain="Technology",
        responsibilities=responsibilities[:10],
        keywords=extracted_keywords,
        education_required=education_required,
        extraction_method="rules"
    )
