# tests/test_embedding_store.py

from services.embedding_store import chunk_text, create_embeddings

def test_chunking():
    text = " ".join([f"word{i}" for i in range(1000)])  # 1000 fake words
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    
    print(f"Total chunks: {len(chunks)}")
    print(f"First chunk (first 80 chars): {chunks[0][:80]}")
    print(f"Last chunk (first 80 chars): {chunks[-1][:80]}")
    
    assert len(chunks) > 1, "Should produce multiple chunks"
    assert all(isinstance(c, str) for c in chunks), "All chunks must be strings"
    print("✅ Chunking test passed")


def test_embeddings():
    sample_chunks = [
        "The transformer architecture uses self-attention mechanisms.",
        "Neural networks are trained using backpropagation.",
        "BERT is a pre-trained language model from Google."
    ]
    embeddings = create_embeddings(sample_chunks)
    
    print(f"Embedding shape: {embeddings.shape}")
    print(f"Expected: ({len(sample_chunks)}, 384)")  # MiniLM gives 384-dim vectors
    
    assert embeddings.shape[0] == len(sample_chunks), "One embedding per chunk"
    assert embeddings.shape[1] == 384, "MiniLM produces 384-dim vectors"
    print("✅ Embedding test passed")


if __name__ == "__main__":
    test_chunking()
    test_embeddings()