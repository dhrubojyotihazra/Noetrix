"""Parsing endpoints for resumes and job descriptions."""

import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from starlette.concurrency import run_in_threadpool
from app.schemas.resume import ParsedResume
from app.schemas.jd import JDFeatures, JDParseRequest
from app.services.parser.pdf_parser import parse_pdf_bytes
from app.services.parser.docx_parser import parse_docx_bytes
from app.services.jd_parser import parse_job_description

router = APIRouter(prefix="/api", tags=["Parsing"])


def _parse_txt_content(content: bytes, filename: str) -> ParsedResume:
    text = content.decode("utf-8", errors="ignore")
    from app.services.parser.contact_extractor import extract_contact_info
    from app.services.parser.section_detector import split_into_sections
    from app.nlp.tfidf import ALL_TAXONOMY_SKILLS
    from app.nlp.tokenizer import word_boundary_match

    contact = extract_contact_info(text)
    sections = split_into_sections(text)
    skills = [s for s in ALL_TAXONOMY_SKILLS if word_boundary_match(s, text.lower())]

    return ParsedResume(
        filename=filename,
        raw_text=text,
        contact=contact,
        summary="\n".join(sections.get("summary", [])),
        sections_detected=[k for k, v in sections.items() if v and k not in ("header", "other")],
        skills=sorted(skills)
    )


@router.post("/parse", response_model=ParsedResume)
async def parse_resume_upload(file: UploadFile = File(...)):
    """Upload and parse a single PDF, DOCX, or TXT resume into structured data.
    
    Enforces maximum upload size (5 MB by default, configurable via MAX_UPLOAD_SIZE_MB)
    and strictly validates file extensions. Offloads blocking CPU parser workloads to threadpool.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    filename_lower = file.filename.lower()

    # Reject legacy .doc with a clear actionable message
    if filename_lower.endswith(".doc"):
        raise HTTPException(
            status_code=400,
            detail="Legacy .doc format is not supported. Please convert your file to modern .docx, .pdf, or .txt format."
        )

    # Validate supported extensions
    allowed_extensions = (".pdf", ".docx", ".txt")
    if not filename_lower.endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file.filename}'. Please upload PDF, DOCX, or TXT."
        )

    # Read content and enforce max upload size limit
    content = await file.read()
    max_size_mb = float(os.getenv("MAX_UPLOAD_SIZE_MB", "5.0"))
    max_bytes = int(max_size_mb * 1024 * 1024)

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum upload size of {max_size_mb:.1f} MB (received {len(content) / (1024*1024):.2f} MB)."
        )

    # Offload blocking parsing to threadpool
    if filename_lower.endswith(".pdf"):
        parsed = await run_in_threadpool(parse_pdf_bytes, content, file.filename)
    elif filename_lower.endswith(".docx"):
        parsed = await run_in_threadpool(parse_docx_bytes, content, file.filename)
    else:
        parsed = await run_in_threadpool(_parse_txt_content, content, file.filename)

    from app.genai.cv_extract import extract_cv_structure_hybrid
    return await run_in_threadpool(extract_cv_structure_hybrid, parsed)


@router.post("/parse-jd", response_model=JDFeatures)
def parse_jd_endpoint(req: JDParseRequest):
    """Parse raw job description text into structured criteria and keywords."""
    if not req.raw_text.strip():
        raise HTTPException(status_code=400, detail="Job description text cannot be empty")
    from app.genai.jd_extract import extract_jd_criteria
    return extract_jd_criteria(req.raw_text, title=req.title)
