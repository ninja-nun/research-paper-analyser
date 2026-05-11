"""Keyword extraction for research paper text."""

from __future__ import annotations

import os
import re
from collections import Counter
from functools import lru_cache


TFIDF_TOKEN_PATTERN = r"(?u)\b[A-Za-z][A-Za-z-]{2,}\b"  # nosec B105


@lru_cache(maxsize=1)
def _get_keybert():
    if os.getenv("USE_KEYBERT") != "1":
        return None

    try:
        from keybert import KeyBERT

        return KeyBERT()
    except Exception:
        return None


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "we",
    "with",
}


def _simple_keywords(text: str, top_n: int) -> list[dict]:
    words = [
        word
        for word in re.findall(r"[A-Za-z][A-Za-z-]{2,}", text.lower())
        if word not in STOP_WORDS
    ]
    candidates = Counter(words)

    for first, second in zip(words, words[1:]):
        if first != second:
            candidates[f"{first} {second}"] += 2

    if not candidates:
        return []

    max_count = max(candidates.values())
    return [
        {"term": term, "score": round(count / max_count, 4), "method": "frequency"}
        for term, count in candidates.most_common(top_n)
    ]


def _fallback_keywords(text: str, top_n: int) -> list[dict]:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=top_n * 4,
            token_pattern=TFIDF_TOKEN_PATTERN,
        )
        matrix = vectorizer.fit_transform([text])
        scores = matrix.toarray()[0]
        terms = vectorizer.get_feature_names_out()
        ranked_indexes = scores.argsort()[::-1]

        keywords: list[dict] = []
        max_score = float(scores.max()) if scores.size else 1.0
        for index in ranked_indexes:
            term = re.sub(r"\s+", " ", terms[index]).strip()
            if term and not any(item["term"] == term for item in keywords):
                score = float(scores[index] / max_score) if max_score else 0.0
                keywords.append({"term": term, "score": round(score, 4), "method": "tfidf"})
            if len(keywords) == top_n:
                break

        return keywords
    except Exception:
        return _simple_keywords(text, top_n)


def extract_keyword_details(text: str, top_n: int = 20) -> list[dict]:
    """Return scored keyword records matching the PRD keyword format."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    keybert = _get_keybert()
    if keybert is not None:
        try:
            keywords = keybert.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                stop_words="english",
                top_n=top_n,
            )
            return [
                {"term": keyword, "score": round(float(score), 4), "method": "keybert"}
                for keyword, score in keywords
            ]
        except Exception:
            return _fallback_keywords(text, top_n)

    return _fallback_keywords(text, top_n)


def extract_keywords(text: str, top_n: int = 20) -> list[str]:
    """Return top keyword terms for backward compatibility with Person B."""
    return [item["term"] for item in extract_keyword_details(text, top_n=top_n)]


def extract_concepts(text: str, top_n: int = 12) -> list[str]:
    """Extract concept-like multi-word keyphrases from the keyword list."""
    details = extract_keyword_details(text, top_n=top_n * 2)
    concepts = [item["term"] for item in details if " " in item["term"]]
    if len(concepts) < top_n:
        concepts.extend(item["term"] for item in details if item["term"] not in concepts)
    return concepts[:top_n]
