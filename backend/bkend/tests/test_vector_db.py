# tests/test_vector_db.py

from services.embedding_store import chunk_text, create_embeddings
from services.vector_db import store_embeddings, retrieve, clear_db


def test_store_and_retrieve():
    # Sample text — simulate output from Person A's process_paper()
    sample_text = """
    Transformers use self-attention to process sequences in parallel.
    BERT is pre-trained on masked language modeling tasks.
    GPT uses causal attention for autoregressive text generation.
    Convolutional networks are commonly used for image classification.
    Recurrent networks process sequences step by step with hidden states.
    Self-attention allows each token to attend to all other tokens.
    """

    chunks = chunk_text(sample_text, chunk_size=20, overlap=5)
    embeddings = create_embeddings(chunks)
    store_embeddings(chunks, embeddings)

    query = "How does self-attention work in transformers?"
    results = retrieve(query, top_k=2)

    print(f"\nQuery: {query}")
    print(f"Top {len(results)} results:")
    for i, r in enumerate(results):
        print(f"  [{i+1}] {r.strip()}")

    assert len(results) > 0, "Should return at least one result"
    print("✅ Store and retrieve test passed")


def test_clear():
    clear_db()
    try:
        retrieve("anything")
        assert False, "Should have raised RuntimeError"
    except RuntimeError:
        print("✅ Clear DB test passed")


if __name__ == "__main__":
    test_store_and_retrieve()
    test_clear()