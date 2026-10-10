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
    pdf_bytes = generate_resume_pdf(resume, template=template)
    clean_name = (resume.contact.name or "tailored_resume").replace(" ", "_").lower()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={clean_name}_{template}.pdf"}
    )
