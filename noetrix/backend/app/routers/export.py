"""Export ranked candidate list as CSV file."""

from fastapi import APIRouter
from fastapi.responses import Response
from app.schemas.scoring import RankedCandidate
from app.services.ranker import generate_candidates_csv

from app.schemas.resume import ParsedResume
from app.services.pdf_generator import generate_resume_pdf

router = APIRouter(prefix="/api", tags=["Export"])


@router.post("/export-csv")
def export_candidates_csv(ranked: list[RankedCandidate]):
    """Download ranked leaderboard as a clean CSV file."""
    csv_data = generate_candidates_csv(ranked)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=noetrix_ranked_candidates.csv"}
    )


@router.post("/export-pdf")
def export_tailored_pdf(resume: ParsedResume, template: str = "classic"):
    """Download tailored resume as a clean, single-page, ATS-compliant PDF in chosen template."""
    import re
    pdf_bytes = generate_resume_pdf(resume, template=template)
    raw_name = (resume.contact.name or "tailored_resume").replace(" ", "_")
    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "", raw_name).strip("._") or "tailored_resume"
    safe_template = re.sub(r"[^a-zA-Z0-9_\-]", "", template).strip("._") or "classic"
    filename = f"{safe_name}_{safe_template}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
