"""Extract structured text and formatting metrics from PDF files using pdfplumber."""

import io
import re
import pdfplumber

from app.schemas.resume import ParsedResume, WorkEntry, EduEntry, ProjectEntry
from app.services.parser.contact_extractor import extract_contact_info
from app.services.parser.section_detector import split_into_sections
from app.nlp.tokenizer import word_boundary_match
from app.nlp.tfidf import ALL_TAXONOMY_SKILLS


def parse_pdf_bytes(file_bytes: bytes, filename: str = "resume.pdf") -> ParsedResume:
    """Parse resume PDF into structured ParsedResume object with robust bullet joining and section extraction."""
    full_text_pages: list[str] = []
    has_tables = False
    detected_columns = 1

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(layout=True) or ""
                full_text_pages.append(page_text)

                tables = page.extract_tables()
                if tables and len(tables) > 0:
                    has_tables = True

                # Accurate column detection:
                # In standard 1-column layouts, full-width sentences cross page center.
                # In true 2-column layouts, words are strictly bounded to left or right of a central gutter.
                words = page.extract_words()
                if len(words) > 40:
                    page_w = page.width
                    center_left = page_w * 0.44
                    center_right = page_w * 0.56
                    # Count words in the middle channel
                    words_in_gutter = sum(1 for w in words if w["x0"] < center_right and w["x1"] > center_left)
                    # If lines frequently cross the middle, it is definitely single column
                    crossing_ratio = words_in_gutter / len(words)
                    left_only = sum(1 for w in words if w["x1"] < center_left)
                    right_only = sum(1 for w in words if w["x0"] > center_right)
                    # Only flag 2 columns if gutter is virtually empty AND left & right columns both have dense bodies
                    if crossing_ratio < 0.05 and left_only > 0.35 * len(words) and right_only > 0.35 * len(words):
                        detected_columns = 2
                    else:
                        detected_columns = 1

    except Exception:
        full_text_pages.append(file_bytes.decode("utf-8", errors="ignore"))

    raw_text = "\n".join(full_text_pages).strip()
    contact = extract_contact_info(raw_text)
    sections = split_into_sections(raw_text)

    DATE_PATTERN = re.compile(r"\b(20\d\d|19\d\d|present|current|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", re.IGNORECASE)
    BULLET_PREFIX = re.compile(r"^[\-\•\*\–\—\>]\s*|^\d+[\.\)]\s*")

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
            is_tech_stack_line = bool(re.match(r"^(tech\s+stack|technologies|tools|flask|react|python|node)[\s\:\·]", trimmed, re.I))

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
                    current = ProjectEntry(
                        name=proj_name,
                        bullets=[],
                        tech_stack=parts[1] if len(parts) > 1 and parts[1] != dates_str else ""
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
                        current = ProjectEntry(name="Projects", bullets=[])
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
                        current = ProjectEntry(name=trimmed, bullets=[])
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
        edu_entries.append(EduEntry(
            id="edu_1",
            institution=inst,
            degree=deg or (edu_lines[1] if len(edu_lines) > 1 else ""),
            bullets=[el for el in edu_lines if el != inst and el != deg]
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
        parse_confidence=1.0 if len(sections_detected) >= 3 else 0.7,
        detected_columns=detected_columns,
        has_tables=has_tables
    )
