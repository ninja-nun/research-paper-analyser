"""Person A public pipeline: PDF in, structured paper JSON out."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from services.keyword_extractor import extract_concepts, extract_keyword_details
from services.metadata_extractor import extract_metadata
from services.pdf_parser import parse_pdf
from services.summarizer import build_one_page_brief, build_structured_summary, summarize_sections, summarize_text


def process_paper(file_path: str | Path) -> dict:
    """
    Process a research paper PDF into the shared backend JSON contract.

    Returns:
        {
            "metadata": {},
            "sections": {},
            "summaries": {},
            "keywords": []
        }
    """
    parsed = parse_pdf(file_path)
    full_text = parsed["full_text"]
    body_text = parsed.get("body_text", "").strip() or full_text
    sections = parsed["sections"]
    summary_sections = {
        section_name: section_text
        for section_name, section_text in sections.items()
        if section_name != "references"
    }

    metadata = extract_metadata(full_text)
    keyword_details = extract_keyword_details(body_text)

    summaries = summarize_sections(summary_sections)
    summaries.update(
        build_structured_summary(
            summary_sections,
            title=metadata.get("title", ""),
            keywords=[item["term"] for item in keyword_details],
            abstract=summary_sections.get("abstract", ""),
        )
    )
    if "full_text" not in summaries:
        summaries["full_text"] = summarize_text(body_text)
    summaries["brief"] = build_one_page_brief(summaries)

    return {
        "paper_id": str(uuid4()),
        "metadata": metadata,
        "title": metadata["title"],
        "authors": metadata["authors"],
        "year": metadata["year"],
        "journal": metadata["journal"],
        "doi": metadata["doi"],
        "sections": sections,
        "full_text": full_text,
        "body_text": body_text,
        "page_count": parsed["page_count"],
        "extraction_method": parsed["extraction_method"],
        "quality": parsed["quality"],
        "summaries": summaries,
        "keywords": [item["term"] for item in keyword_details],
        "keyword_details": keyword_details,
        "concepts": extract_concepts(body_text),
    }
