"""File-based resume parser supporting PDF, DOCX, and text formats."""

import os
from pathlib import Path
from app.schemas.resume import ParsedResume
from app.services.parser.pdf_parser import parse_pdf_bytes
from app.services.parser.docx_parser import parse_docx_bytes
from app.services.parser.text_parser import parse_resume_text


def parse_resume_from_file(file_path: str | Path) -> ParsedResume:
    """Parse a resume file (PDF, DOCX, TXT, MD) from local filesystem."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Resume file not found at: {file_path}")

    ext = path.suffix.lower()
    filename = path.name

    with open(path, "rb") as f:
        file_bytes = f.read()

    if ext == ".pdf":
        return parse_pdf_bytes(file_bytes, filename=filename)
    elif ext == ".docx":
        return parse_docx_bytes(file_bytes, filename=filename)
    elif ext in (".txt", ".md", ".json", ".rtf"):
        text = file_bytes.decode("utf-8", errors="ignore")
        return parse_resume_text(text, filename=filename)
    else:
        # Attempt text decode fallback
        try:
            text = file_bytes.decode("utf-8")
            return parse_resume_text(text, filename=filename)
        except Exception:
            raise ValueError(
                f"Unsupported file format '{ext}'. Supported formats are: .pdf, .docx, .txt, .md"
            )
