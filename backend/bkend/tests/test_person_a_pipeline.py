import fitz

from services.embedding_store import chunk_by_sections
from services.keyword_extractor import extract_concepts, extract_keyword_details, extract_keywords
from services.metadata_extractor import extract_metadata
from services.paper_processor import process_paper
from services.pdf_parser import parse_pdf, split_sections
from services.summarizer import build_structured_summary, summarize_sections, summarize_text


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

INLINE_FRONT_MATTER_TEXT = """Hybrid CNN-YOLO-DeiT Model for Real-Time Driver Drowsiness Detection Ashwin Singh Tanwar Department of Computer Science and Technology Manav Rachna University Faridabad, India ashwinsingh.tanwar@gmail.com Ishika Gupta Department of Computer Science and Technology Manav Rachna University Faridabad, India ishika@example.com Khushi Yadav Department of Computer Science and Technology Manav Rachna University Faridabad, India khushi@example.com Abstract This paper presents a hybrid model for driver drowsiness detection."""


def _create_sample_pdf(path):
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), SAMPLE_TEXT)
    document.save(path)
    document.close()


def _create_multpage_cleanup_pdf(path):
    page_one = """Conference on Example Systems 2024
1
A Study on Transformer Models
Alice Smith, Bob Kumar

Abstract
This paper studies transformer mod-
els for natural language processing.

Introduction
Transformers use attention
mechanisms to model relationships between tokens.
"""
    page_two = """Conference on Example Systems 2024
2
Methodology
We evaluate the model on a benchmark dataset
with 10,000 samples.

Results
The proposed system improves accuracy by 12%.

References
[1] Example citation.
"""
    document = fitz.open()
    for text in (page_one, page_two):
        page = document.new_page()
        page.insert_text((72, 72), text)
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


def test_extract_metadata_from_inline_front_matter():
    metadata = extract_metadata(INLINE_FRONT_MATTER_TEXT)

    assert metadata["title"] == "Hybrid CNN-YOLO-DeiT Model for Real-Time Driver Drowsiness Detection"
    assert metadata["authors"] == ["Ashwin Singh Tanwar", "Ishika Gupta", "Khushi Yadav"]
    assert metadata["affiliations"] == [
        "Department of Computer Science and Technology Manav Rachna University Faridabad, India"
    ]


def test_summarize_sections_uses_local_fallback():
    summary = summarize_text(SAMPLE_TEXT)
    summaries = summarize_sections({"abstract": SAMPLE_TEXT})

    assert summary
    assert summaries["abstract"]


def test_build_structured_summary():
    sections = split_sections(SAMPLE_TEXT)
    structured = build_structured_summary(
        sections,
        title="A Study on Transformer Models",
        keywords=["transformers", "attention", "retrieval"],
        abstract=sections.get("abstract", ""),
    )

    assert {"problem", "method", "dataset", "results", "contribution"} <= set(structured)
    assert structured["problem"]
    assert structured["method"]
    assert "transform" in structured["contribution"].lower()


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
        "body_text",
        "page_count",
        "extraction_method",
        "quality",
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
    assert result["summaries"]["problem"]
    assert result["summaries"]["method"]
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


def test_parse_pdf_cleans_headers_footers_references_and_broken_lines(tmp_path):
    pdf_path = tmp_path / "cleanup.pdf"
    _create_multpage_cleanup_pdf(pdf_path)

    parsed = parse_pdf(pdf_path)

    assert "Conference on Example Systems 2024" not in parsed["body_text"]
    assert "transformer models" in parsed["body_text"].lower()
    assert "attention mechanisms" in parsed["body_text"].lower()
    assert "references" in parsed["sections"]
    assert "[1] Example citation." not in parsed["body_text"]


def test_chunk_by_sections_prefers_semantic_chunks():
    sections = split_sections(SAMPLE_TEXT)
    chunks = chunk_by_sections(sections, max_words=8, overlap=2)

    assert chunks
    assert any(chunk.startswith("Abstract:") for chunk in chunks)
    assert any(chunk.startswith("Methodology:") for chunk in chunks)
