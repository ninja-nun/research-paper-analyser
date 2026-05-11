import chromadb
import numpy as np

from services.embedding_store import create_embeddings


client = chromadb.Client()
collection = client.get_or_create_collection(name="documents")


def store_embeddings(chunks: list[str], embeddings: np.ndarray) -> None:
    """Store embeddings and text chunks in ChromaDB."""
    ids = [str(i) for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        embeddings=embeddings.tolist(),
        ids=ids,
    )

    print(f"[VectorDB] Stored {len(chunks)} vectors")


def retrieve(query: str, top_k: int = 3) -> list[str]:
    """Retrieve the most similar chunks for a query."""
    query_embedding = create_embeddings([query])

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k,
    )

    docs = results.get("documents")
    if (
        docs is None
        or len(docs) == 0
        or len(docs[0]) == 0
        or all(d is None for d in docs[0])
    ):
        raise RuntimeError("Vector DB is empty. Call store_embeddings() first.")

    return docs[0]


def clear_db() -> None:
    """Delete and recreate the active in-memory collection."""
    global collection

    try:
        client.delete_collection("documents")
    except Exception as exc:
        print(f"[VectorDB] Collection reset skipped: {exc}")

    collection = client.get_or_create_collection(name="documents")
    print("[VectorDB] Cleared.")
