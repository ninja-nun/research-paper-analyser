"""Basic metadata extraction for research papers."""

from __future__ import annotations

import re


YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w.-]+\.\w+\b")
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
AUTHOR_NAME_PATTERN = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-zA-Z.'-]+){1,3}\b")
TITLE_CASE_TOKEN_PATTERN = re.compile(r"\b[A-Z][a-zA-Z.'-]+\b")
JOURNAL_PATTERN = re.compile(
    r"\b(?:journal|proceedings|transactions|conference)\s+(?:of|on|in)?\s*([A-Z][A-Za-z0-9 &-]{3,120})",
    re.IGNORECASE,
)
AFFILIATION_WORDS = ("university", "institute", "department", "college", "school", "laboratory", "lab")
SECTION_MARKERS = ("abstract", "keywords", "introduction")
FUNDING_PATTERN = re.compile(
    r"\b(?:funded by|supported by|grant from|acknowledg(?:e|ement).*?(?:by|from))\s+([^.;\n]+)",
    re.IGNORECASE,
)
AFFILIATION_BLOCK_PATTERN = re.compile(
    r"\b("
    r"(?:Department|School|Institute|College|Laboratory|Lab)"
    r".{0,140}?"
    r"(?:University|Institute|College|School|Laboratory|Lab|[A-Z][a-z]+,\s*[A-Z][a-z]+)"
    r")",
    re.DOTALL,
)


def _clean_line(line: str) -> str:
    line = EMAIL_PATTERN.sub("", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip(" -,\t")


def _front_matter(text: str) -> str:
    """Return the title/author/affiliation region before the paper body starts."""
    limit = 4000
    lowered = text.lower()
    cutoffs = [lowered.find(marker) for marker in ("abstract", "keywords", "introduction") if lowered.find(marker) != -1]
    cutoff = min(cutoffs) if cutoffs else limit
    return text[: min(cutoff, limit)]


def _clean_inline_block(text: str) -> str:
    text = EMAIL_PATTERN.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -,\t")


def _looks_like_person_name(value: str) -> bool:
    parts = value.split()
    if not 2 <= len(parts) <= 4:
        return False
    if any(part.isupper() and len(part) > 1 for part in parts):
        return False
    blocked = {"abstract", "introduction", "keywords", "references", "results", "methodology"}
    return all(part.lower() not in blocked for part in parts)


def _score_author_candidate(candidate: str, email_local_part: str) -> tuple[int, int]:
    tokens = [token.lower() for token in candidate.split()]
    matches = sum(1 for token in tokens if token in email_local_part)
    return matches, len(tokens)


def _best_author_candidate(tokens: list[str], email_local_part: str) -> str | None:
    candidates: list[str] = []
    if len(tokens) >= 2:
        candidates.append(" ".join(tokens[-2:]))
    if len(tokens) >= 3:
        candidates.append(" ".join(tokens[-3:]))

    ranked = sorted(
        (candidate for candidate in candidates if _looks_like_person_name(candidate)),
        key=lambda candidate: _score_author_candidate(candidate, email_local_part),
        reverse=True,
    )
    return ranked[0] if ranked else None


def _extract_authors_from_front_matter(front: str) -> list[str]:
    authors: list[str] = []

    last_email_end = 0
    for email_match in EMAIL_PATTERN.finditer(front):
        segment = front[last_email_end : email_match.start()]
        last_email_end = email_match.end()

        affiliation_match = re.search(r"\b(?:Department|School|Institute|College|University|Laboratory|Lab)\b", segment)
        if not affiliation_match:
            continue

        pre_affiliation = segment[: affiliation_match.start()]
        tokens = TITLE_CASE_TOKEN_PATTERN.findall(pre_affiliation)
        if len(tokens) < 2:
            continue

        email_local_part = email_match.group(0).split("@", 1)[0].lower()
        candidate = _best_author_candidate(tokens, email_local_part)
        if candidate and candidate not in authors:
            authors.append(candidate)

    return authors


def _extract_title_from_front_matter(front: str, authors: list[str]) -> str | None:
    cleaned_front = _clean_inline_block(front)
    if not cleaned_front:
        return None

    if authors:
        first_author = authors[0]
        author_index = cleaned_front.find(first_author)
        if author_index > 8:
            title_candidate = _clean_inline_block(cleaned_front[:author_index])
            if len(title_candidate) >= 8:
                return title_candidate

    return None


def _extract_affiliations_from_front_matter(front: str) -> list[str]:
    affiliations: list[str] = []
    for match in AFFILIATION_BLOCK_PATTERN.finditer(front):
        affiliation = _clean_inline_block(match.group(1))
        word_count = len(affiliation.split())
        if 3 <= word_count <= 18 and affiliation not in affiliations:
            affiliations.append(affiliation)
    return affiliations


def extract_title(text: str) -> str:
    """Use the first substantial non-heading line as a title candidate."""
    front = _front_matter(text)
    front_authors = _extract_authors_from_front_matter(front)
    front_title = _extract_title_from_front_matter(front, front_authors)
    if front_title:
        return front_title

    for raw_line in text.splitlines()[:40]:
        line = _clean_line(raw_line)
        if len(line) < 8:
            continue
        if line.lower() in SECTION_MARKERS:
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
    front = _front_matter(text)
    front_authors = _extract_authors_from_front_matter(front)
    if front_authors:
        return front_authors

    lines = [_clean_line(line) for line in text.splitlines()[:50]]
    lines = [line for line in lines if line]

    title = extract_title(text)
    try:
        start = lines.index(title) + 1
    except ValueError:
        start = 1

    for line in lines[start : start + 6]:
        lower = line.lower()
        if lower in SECTION_MARKERS:
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
    front = _front_matter(text)
    front_affiliations = _extract_affiliations_from_front_matter(front)
    if front_affiliations:
        return front_affiliations

    affiliations: list[str] = []
    for raw_line in text.splitlines()[:80]:
        line = _clean_line(raw_line)
        lower = line.lower()
        if any(word in lower for word in AFFILIATION_WORDS):
            if len(line.split()) > 18:
                continue
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
