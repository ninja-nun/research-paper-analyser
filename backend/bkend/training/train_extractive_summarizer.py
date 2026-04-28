"""Train a local extractive summarizer on the arXiv dataset.

This is a no-internet fallback when Hugging Face model download is unavailable.
It learns sentence-importance weights from article/abstract pairs and saves a
small sklearn model that can rank sentences in new papers.
"""

from __future__ import annotations

import argparse
import pickle
import re
from pathlib import Path

import numpy as np
from datasets import load_from_disk
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def split_sentences(text: str) -> list[str]:
    sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text)]
    return [sentence for sentence in sentences if len(sentence.split()) >= 5]


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[A-Za-z][A-Za-z-]{2,}", text.lower())
        if token not in ENGLISH_STOP_WORDS
    }


def sentence_features(
    sentence: str,
    sentence_index: int,
    sentence_count: int,
    doc_vector,
    vectorizer: TfidfVectorizer,
) -> list[float]:
    sentence_vector = vectorizer.transform([sentence])
    similarity = cosine_similarity(sentence_vector, doc_vector)[0][0]
    words = sentence.split()
    position = sentence_index / max(sentence_count - 1, 1)
    return [
        similarity,
        1.0 - position,
        min(len(words) / 40.0, 2.0),
        float(any(char.isdigit() for char in sentence)),
    ]


def target_score(sentence: str, abstract_terms: set[str]) -> float:
    terms = tokenize(sentence)
    if not terms or not abstract_terms:
        return 0.0
    return len(terms & abstract_terms) / len(terms | abstract_terms)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--output", default="bkend/checkpoints/extractive_summarizer.pkl")
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--max-sentences-per-paper", type=int, default=25)
    parser.add_argument("--n-jobs", type=int, default=1)
    args = parser.parse_args()

    dataset = load_from_disk(args.data_dir)
    train_data = dataset["train"].select(range(min(args.samples, len(dataset["train"]))))

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=50000,
        ngram_range=(1, 2),
        token_pattern=r"(?u)\b[A-Za-z][A-Za-z-]{2,}\b",
    )
    vectorizer.fit(train_data["article"])

    features: list[list[float]] = []
    targets: list[float] = []

    for row in train_data:
        article = str(row["article"])
        abstract = str(row["abstract"])
        sentences = split_sentences(article)[: args.max_sentences_per_paper]
        if not sentences:
            continue

        doc_vector = vectorizer.transform([article])
        abstract_terms = tokenize(abstract)
        sentence_count = len(sentences)

        for index, sentence in enumerate(sentences):
            features.append(sentence_features(sentence, index, sentence_count, doc_vector, vectorizer))
            targets.append(target_score(sentence, abstract_terms))

    model = RandomForestRegressor(
        n_estimators=80,
        max_depth=8,
        random_state=42,
        n_jobs=args.n_jobs,
    )
    model.fit(np.array(features), np.array(targets))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as file:
        pickle.dump(
            {
                "model": model,
                "vectorizer": vectorizer,
                "feature_names": ["doc_similarity", "reverse_position", "length", "has_digit"],
            },
            file,
        )

    print(f"Saved extractive summarizer to {output_path}")
    print(f"Training examples: {len(targets)}")


if __name__ == "__main__":
    main()
