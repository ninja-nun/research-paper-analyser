"""Use the locally trained extractive summarizer."""

from __future__ import annotations

import pickle
import re
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def _split_sentences(text: str) -> list[str]:
    sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text)]
    return [sentence for sentence in sentences if sentence]


def _features(sentence: str, index: int, count: int, doc_vector, vectorizer) -> list[float]:
    sentence_vector = vectorizer.transform([sentence])
    similarity = cosine_similarity(sentence_vector, doc_vector)[0][0]
    words = sentence.split()
    position = index / max(count - 1, 1)
    return [
        similarity,
        1.0 - position,
        min(len(words) / 40.0, 2.0),
        float(any(char.isdigit() for char in sentence)),
    ]


def summarize_with_extractive_model(
    text: str,
    model_path: str | Path = "training/checkpoints/extractive_summarizer.pkl",
    max_sentences: int = 5,
) -> str:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Extractive summarizer model not found: {path}")

    with path.open("rb") as file:
        artifact = pickle.load(file)

    model = artifact["model"]
    vectorizer = artifact["vectorizer"]
    sentences = _split_sentences(text)
    if not sentences:
        return ""

    doc_vector = vectorizer.transform([text])
    feature_matrix = np.array(
        [_features(sentence, index, len(sentences), doc_vector, vectorizer) for index, sentence in enumerate(sentences)]
    )
    scores = model.predict(feature_matrix)
    selected_indexes = sorted(scores.argsort()[::-1][:max_sentences])
    return " ".join(sentences[index] for index in selected_indexes)
