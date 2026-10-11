"""Extract structured text and formatting metrics from PDF files using pdfplumber."""

import io
import re
import pdfplumber

from app.schemas.resume import ParsedResume, WorkEntry, EduEntry, ProjectEntry
from app.services.parser.contact_extractor import extract_contact_info
from app.services.parser.section_detector import split_into_sections
from app.nlp.tokenizer import word_boundary_match
from app.nlp.tfidf import ALL_TAXONOMY_SKILLS


def detect_page_columns(words: list[dict], page_width: float) -> int:
    """Detect whether a page has a multi-column or sidebar layout by analyzing word x-positions."""
    if len(words) < 20 or page_width <= 0:
        return 1

    total = len(words)
    # Check candidate vertical gutters across page width (from ~28% to 72%)
    # Covers standard 50/50 two-column layouts as well as 30/70 and 70/30 sidebar layouts.
    for split_ratio in [0.28, 0.33, 0.40, 0.50, 0.60, 0.67, 0.72]:
        g_left = page_width * (split_ratio - 0.03)
        g_right = page_width * (split_ratio + 0.03)

        words_in_gutter = sum(1 for w in words if w["x0"] < g_right and w["x1"] > g_left)
        crossing_ratio = words_in_gutter / total

        left_count = sum(1 for w in words if w["x1"] <= g_left)
        right_count = sum(1 for w in words if w["x0"] >= g_right)

        # In true 2-column or sidebar layouts:
        # 1. Very few words cross the vertical gutter (< 5% of all words)
        # 2. Both sides contain a substantial share of content (>= 15% on each side)
        if crossing_ratio < 0.05 and (left_count / total) >= 0.15 and (right_count / total) >= 0.15:
            return 2

    return 1


def compute_parse_confidence(
    sections_detected: list[str],
    work_entries: list[WorkEntry],
    project_entries: list[ProjectEntry],
    contact
) -> float:
    """Compute parse confidence based on sections detected, bullet recovery, and contact completeness."""
    # 1. Section score (weight 0.40)
    sec_count = len(sections_detected)
    if sec_count >= 4:
        sec_score = 1.0
    elif sec_count == 3:
        sec_score = 0.90
    elif sec_count == 2:
        sec_score = 0.65
    elif sec_count == 1:
        sec_score = 0.40
    else:
        sec_score = 0.15

    # 2. Bullets score (weight 0.35)
    total_bullets = sum(len(w.bullets) for w in work_entries) + sum(len(p.bullets) for p in project_entries)
    if total_bullets >= 4:
        bullet_score = 1.0
    elif total_bullets >= 2:
        bullet_score = 0.80
    elif total_bullets >= 1:
        bullet_score = 0.60
    else:
        bullet_score = 0.20

    # 3. Contact completeness score (weight 0.25)
    contact_fields = sum(1 for f in [contact.name, contact.email, contact.phone] if f and str(f).strip())
    contact_score = contact_fields / 3.0

    confidence = round(0.40 * sec_score + 0.35 * bullet_score + 0.25 * contact_score, 2)
    return max(0.1, min(1.0, confidence))


def parse_pdf_bytes(file_bytes: bytes, filename: str = "resume.pdf") -> ParsedResume:
    """Parse resume PDF into structured ParsedResume object with robust bullet joining and section extraction."""
    full_text_pages: list[str] = []
    has_tables = False
    per_page_columns: list[int] = []

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(layout=True) or ""
                full_text_pages.append(page_text)

                tables = page.extract_tables()
                if tables and len(tables) > 0:
                    has_tables = True

                words = page.extract_words()
                cols = detect_page_columns(words, page.width)
                per_page_columns.append(cols)

    except Exception:
        full_text_pages.append(file_bytes.decode("utf-8", errors="ignore"))

    detected_columns = 2 if any(c == 2 for c in per_page_columns) else 1

    raw_text = "\n".join(full_text_pages).strip()
    contact = extract_contact_info(raw_text)
    sections = split_into_sections(raw_text)

    DATE_PATTERN = re.compile(r"\b(20\d\d|19\d\d|present|current|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", re.IGNORECASE)
    BULLET_PREFIX = re.compile(r"^[\-\•\*\–\—\>]\s*|^\d+[\.\)]\s*|^\(cid:\d+\)\s*")

    # Helper: parse items with bullet wrapping support
    def parse_experience_or_projects(lines: list[str], is_project: bool = False):
        entries = []
        current = None

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            # Check if this line is an action bullet
            is_bullet = bool(BULLET_PREFIX.match(trimmed))
            clean_content = BULLET_PREFIX.sub("", trimmed).strip()

            # Check if line looks like a role or project header (has dates, company separator, or title keywords)
            has_date = bool(DATE_PATTERN.search(trimmed))
            has_separator = any(sep in trimmed for sep in [" | ", " — ", " – ", " - "]) and len(trimmed) < 100
            is_tech_stack_line = bool(re.match(r"^(tech\s+stack|technologies|tools|flask|react|python|node)[\s\:\·]", clean_content, re.I))

            if is_tech_stack_line and is_project and current:
                tech_content = re.sub(r"^(?:tech\s+stack|technologies|tools)[\s\:\·]+", "", clean_content, flags=re.I).strip()
                for t in re.split(r"[,\|/•·]", tech_content):
                    t_clean = t.strip()
                    if t_clean and t_clean not in current.technologies:
                        current.technologies.append(t_clean)
                continue

            if (has_date or has_separator) and not is_bullet:
                # Save previous entry if exists
                if current and (current.bullets or getattr(current, "title", None) or getattr(current, "name", None)):
                    entries.append(current)

                parts = [p.strip() for p in re.split(r"\s*[\|\—\–]\s*", trimmed) if p.strip()]
                dates_str = ""
                for p in parts:
                    if DATE_PATTERN.search(p):
                        dates_str = p
                        break

                if is_project:
                    proj_name = parts[0] if parts else trimmed
                    tech_raw = parts[1] if len(parts) > 1 and parts[1] != dates_str else ""
                    techs = [t.strip() for t in re.split(r"[,\|/•·]", tech_raw) if t.strip()] if tech_raw else []
                    current = ProjectEntry(
                        id=f"proj_{len(entries)+1}",
                        name=proj_name,
                        dates=dates_str,
                        technologies=techs,
                        bullets=[]
                    )
                else:
                    title = parts[0] if parts else "Role"
                    company = parts[1] if len(parts) > 1 and parts[1] != dates_str else ""
                    current = WorkEntry(
                        id=f"exp_{len(entries)+1}",
                        title=title,
                        company=company,
                        dates=dates_str,
                        bullets=[]
                    )
            elif is_bullet:
                if current is None:
                    if is_project:
                        current = ProjectEntry(id=f"proj_{len(entries)+1}", name="Projects", bullets=[], technologies=[])
                    else:
                        current = WorkEntry(id=f"exp_{len(entries)+1}", title="Experience", bullets=[])
                # Only add if it's an actual description and not a pure tech-stack line
                if not is_tech_stack_line:
                    current.bullets.append(clean_content)
            else:
                # Not starting with a bullet marker.
                # Could be a wrapped line from the previous bullet!
                if current and current.bullets and not is_tech_stack_line:
                    # Wrapped continuation of previous bullet
                    current.bullets[-1] = f"{current.bullets[-1]} {trimmed}"
                elif current is None:
                    # First line before bullets
                    if is_project:
                        current = ProjectEntry(id=f"proj_{len(entries)+1}", name=trimmed, bullets=[], technologies=[])
                    else:
                        current = WorkEntry(id=f"exp_{len(entries)+1}", title=trimmed, bullets=[])

        if current and (current.bullets or getattr(current, "title", None) or getattr(current, "name", None)):
            entries.append(current)

        return entries

    work_entries: list[WorkEntry] = parse_experience_or_projects(sections.get("experience", []), is_project=False)
    project_entries: list[ProjectEntry] = parse_experience_or_projects(sections.get("projects", []), is_project=True)

    # Build education entries
    edu_entries: list[EduEntry] = []
    edu_lines = sections.get("education", [])
    if edu_lines:
        inst = edu_lines[0]
        deg = ""
        for el in edu_lines:
            if any(deg_kw in el.lower() for deg_kw in ["bachelor", "b.tech", "btech", "b.s", "master", "m.tech", "m.s", "phd", "degree", "diploma"]):
                deg = el
                break

        extracted_dates = ""
        if deg:
            date_match = re.search(r"\(?\b(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*)?\d{4}\s*(?:[-–—to]+\s*(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*)?(?:\d{4}|present|current))?\)?", deg, re.I)
            if date_match and any(char.isdigit() for char in date_match.group(0)):
                extracted_dates = date_match.group(0).strip("()")
                deg_cleaned = deg[:date_match.start()] + deg[date_match.end():]
                deg = re.sub(r"[\s\|\—\–\,\-]+$", "", deg_cleaned).strip()
                deg = re.sub(r"^[\s\|\—\–\,\-]+", "", deg).strip()

        if not extracted_dates:
            for el in edu_lines:
                dm = re.search(r"\(?\b(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*)?\d{4}\s*(?:[-–—to]+\s*(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*)?(?:\d{4}|present|current))?\)?", el, re.I)
                if dm and any(char.isdigit() for char in dm.group(0)):
                    extracted_dates = dm.group(0).strip("()")
                    break

        edu_entries.append(EduEntry(
            id="edu_1",
            institution=inst,
            degree=deg or (edu_lines[1] if len(edu_lines) > 1 else ""),
            dates=extracted_dates,
            bullets=[el for el in edu_lines if el != inst and el != deg and el != extracted_dates]
        ))

    # Extract certifications
    raw_cert_lines = list(sections.get("certifications", []))
    if not raw_cert_lines:
        for el in sections.get("education", []):
            if any(kw in el.lower() for kw in ["certif", "skillsbuild", "camp", "coursera", "udemy", "credential", "license", "forage", "job simulation"]):
                raw_cert_lines.append(el)

    certifications = []
    for c_line in raw_cert_lines:
        clean_c = BULLET_PREFIX.sub("", c_line).strip()
        if not clean_c or len(clean_c) <= 3:
            continue
        pipe_parts = clean_c.split("|")
        for part in pipe_parts:
            part = part.strip()
            if not part:
                continue
            if ":" in part and any(ckw in part.lower() for ckw in ["skillsbuild", "forage", "certif", "camp", "ibm", "simulation"]):
                prefix, rest = part.split(":", 1)
                sub_certs = [c.strip() for c in rest.split(",") if len(c.strip()) > 2]
                if sub_certs:
                    for sc in sub_certs:
                        certifications.append(f"{prefix.strip()}: {sc}")
                else:
                    certifications.append(part)
            else:
                certifications.append(part)

    # Extract skills
    skills_lines = sections.get("skills", [])
    extracted_skills: set[str] = set()
    skills_text = " ".join(skills_lines).lower()
    for skill in ALL_TAXONOMY_SKILLS:
        if word_boundary_match(skill, skills_text):
            extracted_skills.add(skill)

    # Also scan general raw text if skills section was sparse
    if len(extracted_skills) < 8:
        lower_raw = raw_text.lower()
        for skill in ALL_TAXONOMY_SKILLS:
            if word_boundary_match(skill, lower_raw):
                extracted_skills.add(skill)

    sections_detected = [k for k, v in sections.items() if len(v) > 0 and k != "header" and k != "other"]
    confidence = compute_parse_confidence(sections_detected, work_entries, project_entries, contact)

    return ParsedResume(
        filename=filename,
        raw_text=raw_text,
        contact=contact,
        summary="\n".join(sections.get("summary", [])),
        sections_detected=sections_detected,
        work_experience=work_entries,
        education=edu_entries,
        skills=sorted(list(extracted_skills)),
        projects=project_entries,
        certifications=certifications,
        parse_confidence=confidence,
        detected_columns=detected_columns,
        has_tables=has_tables
    )
