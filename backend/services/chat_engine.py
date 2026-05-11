import requests

from services.vector_db import retrieve


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"


def _call_ollama(prompt: str) -> str:
    """Call a locally running Ollama model."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["response"].strip()


def _call_openai(prompt: str, api_key: str) -> str:
    """Call OpenAI API as an optional fallback."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def build_prompt(question: str, context_chunks: list[str]) -> str:
    """Build a RAG prompt from retrieved context and the user question."""
    context = "\n\n".join(context_chunks)
    return f"""You are a research paper assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't have enough information to answer that."

--- CONTEXT ---
{context}
--- END CONTEXT ---

Question: {question}
Answer:"""


def answer_question(
    question: str,
    top_k: int = 3,
    use_openai: bool = False,
    openai_api_key: str | None = None,
) -> dict:
    """Retrieve relevant chunks, build a prompt, and generate an answer."""
    context_chunks = retrieve(question, top_k=top_k)
    prompt = build_prompt(question, context_chunks)

    if use_openai:
        if not openai_api_key:
            raise ValueError("openai_api_key is required when use_openai=True")
        answer = _call_openai(prompt, openai_api_key)
    else:
        answer = _call_ollama(prompt)

    return {
        "answer": answer,
        "context": context_chunks,
    }
