import numpy as np

from services.embedding_store import create_embeddings


_stored_chunks: list[str] = []
_stored_embeddings: np.ndarray | None = None


def store_embeddings(chunks: list[str], embeddings: np.ndarray) -> None:
    """Store embeddings and text chunks in a lightweight in-memory index."""
    global _stored_chunks, _stored_embeddings

    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings must have the same length")

    _stored_chunks = list(chunks)
    _stored_embeddings = np.array(embeddings, dtype="float32")
    print(f"[VectorDB] Stored {len(chunks)} vectors")


def retrieve(query: str, top_k: int = 3) -> list[str]:
    """Retrieve the most similar chunks using cosine similarity."""
    if not _stored_chunks or _stored_embeddings is None or len(_stored_embeddings) == 0:
        raise RuntimeError("Vector DB is empty. Call store_embeddings() first.")

    query_embedding = np.array(create_embeddings([query]), dtype="float32")[0]

    chunk_norms = np.linalg.norm(_stored_embeddings, axis=1)
    query_norm = np.linalg.norm(query_embedding)
    denom = np.clip(chunk_norms * query_norm, a_min=1e-8, a_max=None)
    scores = (_stored_embeddings @ query_embedding) / denom

    top_indices = np.argsort(scores)[::-1][:top_k]
    return [_stored_chunks[int(index)] for index in top_indices]


def clear_db() -> None:
    """Reset the active in-memory collection."""
    global _stored_chunks, _stored_embeddings

    _stored_chunks = []
    _stored_embeddings = None
    print("[VectorDB] Cleared.")
