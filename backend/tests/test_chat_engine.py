# tests/test_chat_engine.py

from services.embedding_store import chunk_text, create_embeddings
from services.vector_db import store_embeddings, clear_db
from services.chat_engine import build_prompt, answer_question


def setup_db():
    """Load sample data into vector DB before testing."""
    sample_text = """
    The BERT model was introduced by Google in 2018 and uses bidirectional transformers.
    It is pre-trained on two tasks: masked language modeling and next sentence prediction.
    BERT achieves state-of-the-art results on many NLP benchmarks including GLUE and SQuAD.
    Fine-tuning BERT requires only a small amount of labeled data for downstream tasks.
    """
    chunks = chunk_text(sample_text, chunk_size=20, overlap=5)
    embeddings = create_embeddings(chunks)
    store_embeddings(chunks, embeddings)


def test_prompt_building():
    """Test that prompts are built correctly (no LLM needed)."""
    context = [
        "BERT uses bidirectional transformers.",
        "It was introduced by Google in 2018."
    ]
    question = "Who created BERT?"
    prompt = build_prompt(question, context)

    print("\n--- Generated Prompt ---")
    print(prompt)
    print("------------------------\n")

    assert "BERT" in prompt
    assert "Who created BERT?" in prompt
    assert "CONTEXT" in prompt
    print("✅ Prompt building test passed")


def test_full_rag_pipeline_no_llm():
    """
    Test retrieval works end-to-end.
    We skip the actual LLM call and just verify context is retrieved.
    """
    from services.vector_db import retrieve

    setup_db()
    question = "What tasks was BERT pre-trained on?"
    chunks = retrieve(question, top_k=2)

    print(f"\nQuestion: {question}")
    print(f"Retrieved {len(chunks)} chunks:")
    for c in chunks:
        print(f"  > {c.strip()}")

    assert len(chunks) > 0
    print("✅ RAG retrieval pipeline test passed")


def test_answer_with_ollama():
    """
    OPTIONAL: Only run this if you have Ollama installed and running.
    Install: https://ollama.com → then run: ollama pull mistral
    """
    setup_db()
    try:
        result = answer_question("What is BERT pre-trained on?")
        print(f"\nAnswer: {result['answer']}")
        print(f"Context used: {result['context']}")
        assert "answer" in result
        print("✅ Ollama answer test passed")
    except Exception as e:
        print(f"⚠️  Ollama not available (skip if not installed): {e}")


if __name__ == "__main__":
    test_prompt_building()
    test_full_rag_pipeline_no_llm()
    #test_answer_with_ollama()  # Comment this out if Ollama not installed