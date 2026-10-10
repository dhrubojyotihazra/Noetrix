"""Parsing endpoints for resumes and job descriptions."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.resume import ParsedResume
from app.schemas.jd import JDFeatures, JDParseRequest
from app.services.parser.pdf_parser import parse_pdf_bytes
from app.services.parser.docx_parser import parse_docx_bytes
from app.services.jd_parser import parse_job_description

router = APIRouter(prefix="/api", tags=["Parsing"])


@router.post("/parse", response_model=ParsedResume)
async def parse_resume_upload(file: UploadFile = File(...)):
    """Upload and parse a single PDF or DOCX resume into structured data."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    content = await file.read()
    filename_lower = file.filename.lower()

    if filename_lower.endswith(".pdf"):
        parsed = parse_pdf_bytes(content, filename=file.filename)
    elif filename_lower.endswith((".docx", ".doc")):
        parsed = parse_docx_bytes(content, filename=file.filename)
    elif filename_lower.endswith(".txt"):
        text = content.decode("utf-8", errors="ignore")
        from app.services.parser.contact_extractor import extract_contact_info
        from app.services.parser.section_detector import split_into_sections
        contact = extract_contact_info(text)
        sections = split_into_sections(text)
        parsed = ParsedResume(
            filename=file.filename,
            raw_text=text,
            contact=contact,
            summary="\n".join(sections.get("summary", [])),
            sections_detected=[k for k, v in sections.items() if v and k not in ("header", "other")],
            skills=[]
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, or TXT.")

    from app.genai.cv_extract import extract_cv_structure_hybrid
    return extract_cv_structure_hybrid(parsed)


@router.post("/parse-jd", response_model=JDFeatures)
def parse_jd_endpoint(req: JDParseRequest):
    """Parse raw job description text into structured criteria and keywords."""
    if not req.raw_text.strip():
        raise HTTPException(status_code=400, detail="Job description text cannot be empty")
    from app.genai.jd_extract import extract_jd_criteria
    return extract_jd_criteria(req.raw_text, title=req.title)

