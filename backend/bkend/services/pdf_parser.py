"""PDF text extraction and simple research-paper section splitting."""

from __future__ import annotations

import re
from pathlib import Path

import fitz


SECTION_ALIASES = {
    "abstract": "abstract",
    "introduction": "introduction",
    "background": "background",
    "related work": "related_work",
    "literature review": "related_work",
    "method": "methodology",
    "methods": "methodology",
    "methodology": "methodology",
    "approach": "methodology",
    "proposed method": "methodology",
    "experiment": "experiments",
    "experiments": "experiments",
    "experimental setup": "experiments",
    "results": "results",
    "discussion": "discussion",
    "conclusion": "conclusion",
    "conclusions": "conclusion",
    "references": "references",
}


HEADING_PATTERN = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*\.?\s+)?"
    r"(abstract|introduction|background|related work|literature review|method|methods|"
    r"methodology|approach|proposed method|experiment|experiments|experimental setup|"
    r"results|discussion|conclusion|conclusions|references)\s*$",
    re.IGNORECASE,
)


def _normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_with_pymupdf(path: Path) -> tuple[str, int]:
    page_texts: list[str] = []
    with fitz.open(path) as document:
        page_count = document.page_count
        for page in document:
            page_texts.append(page.get_text("text"))

    return _normalize_text("\n\n".join(page_texts)), page_count


def _extract_with_pdfplumber(path: Path) -> tuple[str, int]:
    try:
        import pdfplumber
    except Exception as exc:
        raise RuntimeError("pdfplumber fallback is not installed") from exc

    page_texts: list[str] = []
    with pdfplumber.open(path) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            page_texts.append(page.extract_text() or "")

    return _normalize_text("\n\n".join(page_texts)), page_count


def extract_text_from_pdf(file_path: str | Path) -> str:
    """Extract plain text from every page of a PDF."""
    result = extract_pdf_text_and_metadata(file_path)
    return result["full_text"]


def extract_pdf_text_and_metadata(file_path: str | Path) -> dict:
    """Extract PDF text, page count, and extraction method."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("file_path must point to a PDF file")

    try:
        full_text, page_count = _extract_with_pymupdf(path)
        method = "pymupdf"
    except Exception:
        full_text, page_count = _extract_with_pdfplumber(path)
        method = "pdfplumber"

    if not full_text:
        raise ValueError("No extractable text found in PDF")

    return {
        "full_text": full_text,
        "page_count": page_count,
        "extraction_method": method,
    }


def split_sections(text: str) -> dict[str, str]:
    """
    Split extracted paper text into common academic sections.

    This intentionally uses headings, not a complicated parser, so it is fast
    and predictable for local development.
    """
    sections: dict[str, list[str]] = {}
    current_section = "unknown"
    sections[current_section] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        match = HEADING_PATTERN.match(line)
        if match:
            current_section = SECTION_ALIASES[match.group(1).lower()]
            sections.setdefault(current_section, [])
            continue

        sections.setdefault(current_section, []).append(line)

    cleaned = {
        name: _normalize_text(" ".join(lines))
        for name, lines in sections.items()
        if _normalize_text(" ".join(lines))
    }

    return cleaned


def parse_pdf(file_path: str | Path) -> dict:
    """Return full PDF text plus a dictionary of detected paper sections."""
    extracted = extract_pdf_text_and_metadata(file_path)
    full_text = extracted["full_text"]
    return {
        "full_text": full_text,
        "sections": split_sections(full_text),
        "page_count": extracted["page_count"],
        "extraction_method": extracted["extraction_method"],
    }
