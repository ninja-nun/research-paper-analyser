"""Local-first summarization helpers for paper text and sections."""

from __future__ import annotations

import re
import os
from functools import lru_cache


MAX_MODEL_INPUT_CHARS = 3500


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
