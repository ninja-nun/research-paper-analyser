"""Local-first summarization helpers for paper text and sections."""

from __future__ import annotations

import re
import os
from functools import lru_cache


MAX_MODEL_INPUT_CHARS = 3500
STRUCTURED_FIELDS = ("problem", "method", "dataset", "results", "contribution")


def _sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]


@lru_cache(maxsize=1)
def _get_summarizer():
    if os.getenv("USE_TRANSFORMER_SUMMARY") != "1":
        return None

    try:
        from transformers import pipeline

        model_name = os.getenv("SUMMARIZER_MODEL", "sshleifer/distilbart-cnn-12-6")
        return pipeline("summarization", model=model_name)
    except Exception:
        return None


def _fallback_summary(text: str, max_sentences: int = 5) -> str:
    sentences = _sentences(text)
    return " ".join(sentences[:max_sentences]).strip()


def _truncate(text: str, max_sentences: int = 2) -> str:
    return _fallback_summary(text, max_sentences=max_sentences)


def _section_text(sections_dict: dict[str, str], *names: str) -> str:
    return " ".join(sections_dict.get(name, "") for name in names).strip()


def _extract_dataset_signal(text: str) -> str:
    sentences = _sentences(text)
    matches = [
        sentence
        for sentence in sentences
        if re.search(r"\b(dataset|datasets|corpus|data|samples?|participants?|images?)\b", sentence, re.IGNORECASE)
    ]
    return " ".join(matches[:2]).strip()


def _extract_results_signal(text: str) -> str:
    sentences = _sentences(text)
    matches = [
        sentence
        for sentence in sentences
        if re.search(r"\b(result|results|improv|outperform|accuracy|f1|precision|recall|score)\b", sentence, re.IGNORECASE)
    ]
    return " ".join(matches[:2]).strip()


def _clean_structured_field(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value.rstrip(":,; ")


def build_structured_summary(
    sections_dict: dict[str, str],
    *,
    title: str = "",
    keywords: list[str] | None = None,
    abstract: str = "",
) -> dict[str, str]:
    """Build a stable research-paper summary with fixed semantic fields."""
    keywords = keywords or []
    abstract_text = abstract or sections_dict.get("abstract", "")
    intro_text = _section_text(sections_dict, "introduction", "background", "related_work")
    method_text = _section_text(sections_dict, "methodology", "experiments")
    results_text = _section_text(sections_dict, "results", "discussion", "conclusion")
    body_text = " ".join(
        sections_dict.get(name, "")
        for name in ("abstract", "introduction", "background", "methodology", "experiments", "results", "discussion", "conclusion")
    ).strip()

    structured = {
        "problem": _clean_structured_field(_truncate(abstract_text or intro_text or body_text, max_sentences=2)),
        "method": _clean_structured_field(_truncate(method_text or abstract_text or body_text, max_sentences=2)),
        "dataset": _clean_structured_field(
            _truncate(
                _extract_dataset_signal(_section_text(sections_dict, "methodology", "experiments", "results", "abstract"))
                or method_text
                or body_text,
                max_sentences=2,
            )
        ),
        "results": _clean_structured_field(
            _truncate(_extract_results_signal(results_text or body_text) or results_text or body_text, max_sentences=2)
        ),
        "contribution": _clean_structured_field(
            _truncate(_section_text(sections_dict, "conclusion", "discussion") or abstract_text or body_text, max_sentences=2)
        ),
    }
    return apply_consistency_layer(
        structured,
        title=title,
        keywords=keywords,
        abstract=abstract_text,
    )


def apply_consistency_layer(
    summary: dict[str, str],
    *,
    title: str,
    keywords: list[str],
    abstract: str,
) -> dict[str, str]:
    """Re-check structured output against title, keywords, and abstract."""
    abstract_sentences = _sentences(abstract)
    normalized_keywords = [keyword.strip() for keyword in keywords if keyword.strip()]

    if title and not summary.get("contribution"):
        summary["contribution"] = title.strip()

    if normalized_keywords:
        keyword_hint = ", ".join(normalized_keywords[:5])
        if keyword_hint and keyword_hint.lower() not in summary.get("contribution", "").lower():
            base = summary.get("contribution", "").strip()
            summary["contribution"] = f"{base} Key terms: {keyword_hint}.".strip()

    if abstract_sentences:
        for field in ("problem", "method"):
            if not summary.get(field):
                summary[field] = abstract_sentences[0]
        if not summary.get("results") and len(abstract_sentences) > 1:
            summary["results"] = abstract_sentences[1]

    return {key: _clean_structured_field(value) for key, value in summary.items()}


def summarize_text(text: str) -> str:
    """
    Summarize text with a transformer when available, otherwise use a quick
    extractive fallback so the pipeline remains demo-ready offline.
    """
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""

    if len(text.split()) < 80:
        return text

    if os.getenv("USE_EXTRACTIVE_MODEL") == "1":
        try:
            from services.extractive_model_summarizer import summarize_with_extractive_model

            model_path = os.getenv("EXTRACTIVE_SUMMARIZER_MODEL", "training/checkpoints/extractive_summarizer.pkl")
            return summarize_with_extractive_model(text, model_path=model_path)
        except Exception:
            pass

    summarizer = _get_summarizer()
    if summarizer is None:
        return _fallback_summary(text)

    try:
        result = summarizer(
            text[:MAX_MODEL_INPUT_CHARS],
            max_length=180,
            min_length=40,
            do_sample=False,
        )
        return result[0]["summary_text"].strip()
    except Exception:
        return _fallback_summary(text)


def summarize_sections(sections_dict: dict[str, str]) -> dict[str, str]:
    """Summarize each detected section independently."""
    return {
        section_name: summarize_text(section_text)
        for section_name, section_text in sections_dict.items()
        if section_text.strip()
    }


def build_one_page_brief(section_summaries: dict[str, str]) -> str:
    """Merge important section summaries into a compact paper brief."""
    structured_fields = [
        ("problem", "Problem"),
        ("method", "Method"),
        ("dataset", "Dataset"),
        ("results", "Results"),
        ("contribution", "Contribution"),
    ]
    structured_parts = [
        f"{label}: {section_summaries.get(field, '').strip()}"
        for field, label in structured_fields
        if section_summaries.get(field, "").strip()
    ]
    if structured_parts:
        return "\n\n".join(structured_parts)

    preferred_order = [
        "abstract",
        "introduction",
        "methodology",
        "experiments",
        "results",
        "discussion",
        "conclusion",
    ]
    parts: list[str] = []
    for section_name in preferred_order:
        summary = section_summaries.get(section_name, "").strip()
        if summary:
            label = section_name.replace("_", " ").title()
            parts.append(f"{label}: {summary}")

    if not parts:
        parts = [summary for summary in section_summaries.values() if summary.strip()]

    return "\n\n".join(parts)
