"""PDF text extraction and research-paper aware cleanup and section splitting."""

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
    r"^\s*(?:(?:\d+(?:\.\d+)*|[ivxlcdm]+)\.?\s+)?"
    r"(abstract|introduction|background|related work|literature review|method|methods|"
    r"methodology|approach|proposed method|experiment|experiments|experimental setup|"
    r"results|discussion|conclusion|conclusions|references)\s*$",
    re.IGNORECASE,
)

INLINE_HEADING_PATTERN = re.compile(
    r"(?im)(?:^|\n)\s*(?:(?:\d+(?:\.\d+)*|[ivxlcdm]+)\.?\s+)?"
    r"(abstract|introduction|background|related work|literature review|method|methods|"
    r"methodology|approach|proposed method|experiment|experiments|experimental setup|"
    r"results|discussion|conclusion|conclusions|references)\s*\n"
)


def _normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _margin_line_key(line: str) -> str:
    lowered = line.lower().strip()
    lowered = re.sub(r"\d+", "#", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def _looks_like_heading(line: str) -> bool:
    return bool(HEADING_PATTERN.match(line.strip()))


def _detect_repeated_margin_lines(page_lines: list[list[str]]) -> set[str]:
    repeated: dict[str, int] = {}
    for lines in page_lines:
        if not lines:
            continue
        candidates = lines[:2] + lines[-2:]
        seen = {_margin_line_key(line) for line in candidates if line.strip()}
        for candidate in seen:
            repeated[candidate] = repeated.get(candidate, 0) + 1

    threshold = 2 if len(page_lines) < 4 else max(2, len(page_lines) // 2)
    return {
        candidate
        for candidate, count in repeated.items()
        if count >= threshold and len(candidate) > 2 and "abstract" not in candidate
    }


def _clean_page_lines(lines: list[str], repeated_margin_lines: set[str]) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if _margin_line_key(stripped) in repeated_margin_lines and not _looks_like_heading(stripped):
            continue
        if re.fullmatch(r"\d{1,4}", stripped):
            continue
        cleaned.append(stripped)
    return cleaned


def _repair_broken_lines(lines: list[str]) -> list[str]:
    repaired: list[str] = []
    for line in lines:
        if not repaired:
            repaired.append(line)
            continue

        previous = repaired[-1]
        if _looks_like_heading(line):
            repaired.append(line)
            continue

        if previous.endswith("-") and not previous.endswith("--"):
            repaired[-1] = previous[:-1] + line.lstrip()
            continue

        should_join = (
            not previous.endswith((".", "?", "!", ":", ";"))
            and not _looks_like_heading(previous)
            and bool(re.match(r"^[a-z(\[]", line))
        )
        if should_join:
            repaired[-1] = f"{previous} {line}"
            continue

        repaired.append(line)

    return repaired


def _split_inline_headings(text: str) -> str:
    return INLINE_HEADING_PATTERN.sub(lambda match: f"\n{match.group(1).title()}\n", text)


def _assess_text_quality(full_text: str, page_count: int) -> dict:
    """Estimate whether the PDF contains enough real text for downstream NLP."""
    normalized = _normalize_text(full_text)
    char_count = len(normalized)
    alpha_count = sum(1 for char in normalized if char.isalpha())
    chars_per_page = char_count / max(page_count, 1)
    alpha_ratio = alpha_count / max(char_count, 1)
    likely_scanned = char_count < 600 or chars_per_page < 250 or alpha_ratio < 0.45

    return {
        "char_count": char_count,
        "chars_per_page": chars_per_page,
        "alpha_ratio": alpha_ratio,
        "likely_scanned": likely_scanned,
    }


def _extract_with_pymupdf(path: Path) -> tuple[str, int]:
    page_lines: list[list[str]] = []
    with fitz.open(path) as document:
        page_count = document.page_count
        for page in document:
            page_text = page.get_text("text")
            page_lines.append(page_text.splitlines())

    repeated_margin_lines = _detect_repeated_margin_lines(page_lines)
    cleaned_pages = [
        _repair_broken_lines(_clean_page_lines(lines, repeated_margin_lines))
        for lines in page_lines
    ]
    text = "\n\n".join("\n".join(lines) for lines in cleaned_pages if lines)
    return _normalize_text(_split_inline_headings(text)), page_count


def _extract_with_pdfplumber(path: Path) -> tuple[str, int]:
    try:
        import pdfplumber
    except Exception as exc:
        raise RuntimeError("pdfplumber fallback is not installed") from exc

    page_lines: list[list[str]] = []
    with pdfplumber.open(path) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            page_lines.append((page.extract_text() or "").splitlines())

    repeated_margin_lines = _detect_repeated_margin_lines(page_lines)
    cleaned_pages = [
        _repair_broken_lines(_clean_page_lines(lines, repeated_margin_lines))
        for lines in page_lines
    ]
    text = "\n\n".join("\n".join(lines) for lines in cleaned_pages if lines)
    return _normalize_text(_split_inline_headings(text)), page_count


def _split_references(text: str) -> tuple[str, str]:
    reference_match = None
    for match in INLINE_HEADING_PATTERN.finditer(f"\n{text}\n"):
        if match.group(1).lower() == "references":
            reference_match = match
            break

    if reference_match is None:
        return text.strip(), ""

    reference_start = max(0, reference_match.start() - 1)
    body_text = text[:reference_start].strip()
    references_text = text[reference_start:].strip()
    return body_text, references_text


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
        "quality": _assess_text_quality(full_text, page_count),
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
    body_text, references_text = _split_references(full_text)
    sections = split_sections(full_text)
    if references_text:
        sections["references"] = _normalize_text(references_text)
    return {
        "full_text": full_text,
        "body_text": body_text,
        "sections": sections,
        "page_count": extracted["page_count"],
        "extraction_method": extracted["extraction_method"],
        "quality": extracted["quality"],
    }
