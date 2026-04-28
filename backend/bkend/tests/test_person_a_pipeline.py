import fitz

from services.keyword_extractor import extract_concepts, extract_keyword_details, extract_keywords
from services.metadata_extractor import extract_metadata
from services.paper_processor import process_paper
from services.pdf_parser import parse_pdf, split_sections
from services.summarizer import summarize_sections, summarize_text


SAMPLE_TEXT = """A Study on Transformer Models
Alice Smith, Bob Kumar
Department of Computer Science, Example University
2024
Journal of Machine Learning Research
doi: 10.1234/example.2024.001

Abstract
This paper studies transformer models for natural language processing.

Introduction
Transformers use attention mechanisms to model relationships between tokens.

Methodology
We compare transformer-based embeddings and baseline machine learning methods.

Results
The transformer model improves retrieval quality in research paper analysis.

Conclusion
Transformer methods are useful for analyzing academic documents."""


def _create_sample_pdf(path):
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), SAMPLE_TEXT)
    document.save(path)
    document.close()


def test_split_sections():
    sections = split_sections(SAMPLE_TEXT)

    assert "abstract" in sections
    assert "introduction" in sections
    assert "methodology" in sections
    assert "attention mechanisms" in sections["introduction"]


def test_extract_metadata():
    metadata = extract_metadata(SAMPLE_TEXT)

    assert metadata["title"] == "A Study on Transformer Models"
    assert metadata["authors"] == ["Alice Smith", "Bob Kumar"]
    assert metadata["year"] == 2024
    assert metadata["doi"] == "10.1234/example.2024.001"
    assert metadata["journal"] == "Journal of Machine Learning Research"
    assert metadata["affiliations"] == ["Department of Computer Science, Example University"]


def test_summarize_sections_uses_local_fallback():
    summary = summarize_text(SAMPLE_TEXT)
    summaries = summarize_sections({"abstract": SAMPLE_TEXT})

    assert summary
    assert summaries["abstract"]


def test_extract_keywords():
    keywords = extract_keywords(SAMPLE_TEXT, top_n=5)
    keyword_details = extract_keyword_details(SAMPLE_TEXT, top_n=5)
    concepts = extract_concepts(SAMPLE_TEXT, top_n=5)

    assert len(keywords) > 0
    assert any("transformer" in keyword for keyword in keywords)
    assert {"term", "score", "method"} <= set(keyword_details[0])
    assert concepts


def test_process_paper_contract(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    _create_sample_pdf(pdf_path)

    result = process_paper(pdf_path)

    expected_keys = {
        "paper_id",
        "metadata",
        "title",
        "authors",
        "year",
        "journal",
        "doi",
        "sections",
        "full_text",
        "page_count",
        "extraction_method",
        "summaries",
        "keywords",
        "keyword_details",
        "concepts",
    }
    assert set(result.keys()) == expected_keys
    assert result["metadata"]["title"] == "A Study on Transformer Models"
    assert result["doi"] == "10.1234/example.2024.001"
    assert result["page_count"] == 1
    assert "abstract" in result["sections"]
    assert result["summaries"]["brief"]
    assert result["keywords"]
    assert result["keyword_details"]
    assert result["concepts"]


def test_parse_pdf_returns_full_text_and_sections(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    _create_sample_pdf(pdf_path)

    parsed = parse_pdf(pdf_path)

    assert "Transformer Models" in parsed["full_text"]
    assert "abstract" in parsed["sections"]
    assert parsed["page_count"] == 1
    assert parsed["extraction_method"] in {"pymupdf", "pdfplumber"}
