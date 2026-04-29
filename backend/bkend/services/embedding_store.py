import numpy as np
import os
from sklearn.feature_extraction.text import HashingVectorizer

MODEL_NAME = "all-MiniLM-L6-v2"
model = None


def _get_model():
    """Load the embedding model only when embeddings are first requested."""
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(MODEL_NAME)
    return model


def _fallback_embeddings(text_chunks: list[str]) -> np.ndarray:
    """Create deterministic local embeddings when torch/sentence-transformers is unavailable."""
    vectorizer = HashingVectorizer(
        n_features=384,
        alternate_sign=False,
        norm="l2",
    )
    vectors = vectorizer.transform(text_chunks).toarray()
    return np.array(vectors, dtype="float32")


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """
    Split a long text into overlapping chunks.
    Overlap ensures context isn't lost at chunk boundaries.
    
    Args:
        text: Full document text
        chunk_size: Words per chunk
        overlap: Words shared between consecutive chunks
    
    Returns:
        List of text chunk strings
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # Move forward with overlap

    return chunks


def chunk_by_sections(
    sections: dict[str, str],
    *,
    max_words: int = 220,
    overlap: int = 40,
) -> list[str]:
    """
    Build retrieval chunks from semantic sections first, then split oversized
    sections with the existing overlapping word chunker.
    """
    chunks: list[str] = []
    ordered_section_names = [
        "abstract",
        "introduction",
        "background",
        "related_work",
        "methodology",
        "experiments",
        "results",
        "discussion",
        "conclusion",
        "unknown",
    ]

    for section_name in ordered_section_names:
        section_text = sections.get(section_name, "").strip()
        if not section_text:
            continue

        section_words = section_text.split()
        if len(section_words) <= max_words:
            chunks.append(f"{section_name.replace('_', ' ').title()}: {section_text}")
            continue

        for chunk in chunk_text(section_text, chunk_size=max_words, overlap=overlap):
            chunks.append(f"{section_name.replace('_', ' ').title()}: {chunk}")

    return chunks


def create_embeddings(text_chunks: list[str]) -> np.ndarray:
    """
    Convert a list of text chunks into embedding vectors.
    
    Args:
        text_chunks: List of strings to embed
    
    Returns:
        2D numpy array of shape (num_chunks, embedding_dim)
    """
    if not text_chunks:
        raise ValueError("text_chunks cannot be empty")

    if os.getenv("USE_SENTENCE_TRANSFORMERS") == "1":
        try:
            embeddings = _get_model().encode(text_chunks, show_progress_bar=False)
            return np.array(embeddings, dtype="float32")
        except Exception:
            return _fallback_embeddings(text_chunks)

    return _fallback_embeddings(text_chunks)
