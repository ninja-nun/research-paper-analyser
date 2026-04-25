"""Basic metadata extraction for research papers."""

from __future__ import annotations

import re


YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w.-]+\.\w+\b")
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
JOURNAL_PATTERN = re.compile(
    r"\b(?:journal|proceedings|transactions|conference)\s+(?:of|on|in)?\s*([A-Z][A-Za-z0-9 &-]{3,120})",
    re.IGNORECASE,
)
AFFILIATION_WORDS = ("university", "institute", "department", "college", "school", "laboratory", "lab")
FUNDING_PATTERN = re.compile(
    r"\b(?:funded by|supported by|grant from|acknowledg(?:e|ement).*?(?:by|from))\s+([^.;\n]+)",
    re.IGNORECASE,
)


def _clean_line(line: str) -> str:
    line = EMAIL_PATTERN.sub("", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip(" -,\t")


def extract_title(text: str) -> str:
    """Use the first substantial non-heading line as a title candidate."""
    for raw_line in text.splitlines()[:40]:
        line = _clean_line(raw_line)
        if len(line) < 8:
            continue
        if line.lower() in {"abstract", "introduction", "keywords"}:
            continue
        if YEAR_PATTERN.fullmatch(line):
            continue
        return line
    return "Unknown Title"


def extract_authors(text: str) -> list[str]:
    """
    Extract likely authors from lines immediately after the title.

    PDF text varies a lot, so this keeps the logic conservative and returns an
    empty list when no useful author line is detected.
    """
    lines = [_clean_line(line) for line in text.splitlines()[:50]]
    lines = [line for line in lines if line]

    title = extract_title(text)
    try:
        start = lines.index(title) + 1
    except ValueError:
        start = 1

    for line in lines[start : start + 6]:
        lower = line.lower()
        if lower in {"abstract", "keywords", "introduction"}:
            break
        if any(word in lower for word in ("university", "institute", "department", "college", "school")):
            continue
        if YEAR_PATTERN.search(line):
            continue
        if "," in line or " and " in lower:
            authors = re.split(r",|\band\b", line)
            return [author.strip() for author in authors if len(author.strip()) > 1]
        if 2 <= len(line.split()) <= 12:
            return [line]

    return []


def extract_year(text: str) -> int | None:
    """Return the first plausible publication year found in the paper text."""
    match = YEAR_PATTERN.search(text[:5000])
    return int(match.group(0)) if match else None


def extract_doi(text: str) -> str | None:
    match = DOI_PATTERN.search(text[:8000])
    return match.group(0).rstrip(".") if match else None


def extract_journal(text: str) -> str | None:
    match = JOURNAL_PATTERN.search(text[:8000])
    if not match:
        return None
    return _clean_line(match.group(0)).rstrip(".")


def extract_affiliations(text: str) -> list[str]:
    affiliations: list[str] = []
    for raw_line in text.splitlines()[:80]:
        line = _clean_line(raw_line)
        lower = line.lower()
        if any(word in lower for word in AFFILIATION_WORDS):
            if line and line not in affiliations:
                affiliations.append(line)
    return affiliations


def extract_funding_bodies(text: str) -> list[str]:
    bodies: list[str] = []
    for match in FUNDING_PATTERN.finditer(text[:12000]):
        body = _clean_line(match.group(1))
        if body and body not in bodies:
            bodies.append(body)
    return bodies


def extract_entities(text: str) -> dict[str, list[str]]:
    """
    Optional SciSpacy/spaCy entity extraction.

    Set USE_SPACY_NER=1 after installing a scientific model. Without that,
    deterministic rule-based fields still work.
    """
    import os

    if os.getenv("USE_SPACY_NER") != "1":
        return {"organizations": [], "locations": [], "scientific_terms": []}

    try:
        import spacy

        model_name = os.getenv("SPACY_MODEL", "en_core_sci_sm")
        nlp = spacy.load(model_name)
        doc = nlp(text[:20000])
    except Exception:
        return {"organizations": [], "locations": [], "scientific_terms": []}

    organizations: list[str] = []
    locations: list[str] = []
    scientific_terms: list[str] = []
    for ent in doc.ents:
        value = _clean_line(ent.text)
        if not value:
            continue
        if ent.label_ in {"ORG"} and value not in organizations:
            organizations.append(value)
        elif ent.label_ in {"GPE", "LOC"} and value not in locations:
            locations.append(value)
        elif value.lower() not in {"abstract", "introduction"} and value not in scientific_terms:
            scientific_terms.append(value)

    return {
        "organizations": organizations[:20],
        "locations": locations[:20],
        "scientific_terms": scientific_terms[:30],
    }


def extract_metadata(text: str) -> dict:
    """Extract PRD metadata fields from paper text."""
    entities = extract_entities(text)
    return {
        "title": extract_title(text),
        "authors": extract_authors(text),
        "year": extract_year(text),
        "journal": extract_journal(text),
        "doi": extract_doi(text),
        "affiliations": extract_affiliations(text),
        "funding_bodies": extract_funding_bodies(text),
        "entities": entities,
    }
