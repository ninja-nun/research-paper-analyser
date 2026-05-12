import json
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.chat_engine import answer_question
from services.embedding_store import chunk_by_sections, chunk_text, create_embeddings
from services.paper_processor import process_paper
from services.vector_db import clear_db, store_embeddings


app = FastAPI(title="Research Paper Analyzer - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("data")
RAW_PAPERS_DIR = DATA_DIR / "raw_papers"
PROCESSED_DIR = DATA_DIR / "processed_text"
MAX_STORED_UPLOADS = 2

RAW_PAPERS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

CURRENT_PAPER: dict | None = None


class ChatRequest(BaseModel):
    paper_id: str | None = None
    question: str
    top_k: int = 3


def _save_processed_paper(paper_data: dict) -> None:
    output_path = PROCESSED_DIR / f"{paper_data['paper_id']}.json"
    output_path.write_text(json.dumps(paper_data, indent=2), encoding="utf-8")


def _set_current_paper(paper_data: dict) -> None:
    global CURRENT_PAPER
    CURRENT_PAPER = paper_data


def _load_processed_paper(paper_id: str) -> dict:
    file_path = PROCESSED_DIR / f"{paper_id}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Paper not found")
    return json.loads(file_path.read_text(encoding="utf-8"))


def _get_paper_by_id(paper_id: str) -> dict:
    global CURRENT_PAPER

    if CURRENT_PAPER is not None and CURRENT_PAPER.get("paper_id") == paper_id:
        return CURRENT_PAPER

    paper_data = _load_processed_paper(paper_id)
    _set_current_paper(paper_data)
    return paper_data


def _list_processed_papers() -> list[dict]:
    papers: list[dict] = []
    for file_path in sorted(PROCESSED_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True):
        try:
            papers.append(json.loads(file_path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return papers


def _paper_list_item(paper: dict) -> dict:
    """Return a lightweight paper summary for list pages."""
    metadata = paper.get("metadata", {})
    return {
        "paper_id": paper.get("paper_id"),
        "title": paper.get("title") or metadata.get("title") or "Untitled",
        "authors": paper.get("authors") or metadata.get("authors") or [],
        "year": paper.get("year") or metadata.get("year"),
        "journal": paper.get("journal") or metadata.get("journal"),
        "doi": paper.get("doi") or metadata.get("doi"),
        "affiliations": metadata.get("affiliations", []),
        "original_filename": paper.get("original_filename"),
        "status": "Embedded",
    }


def _get_current_paper() -> dict:
    if CURRENT_PAPER is None:
        raise HTTPException(status_code=404, detail="No paper uploaded yet")
    return CURRENT_PAPER


def _index_paper_for_chat(paper_data: dict) -> int:
    sections = {
        section_name: section_text
        for section_name, section_text in paper_data.get("sections", {}).items()
        if section_name != "references"
    }
    body_text = paper_data.get("body_text", "").strip()
    full_text = paper_data.get("full_text", "").strip()

    chunks = chunk_by_sections(sections) if sections else []
    if not chunks and body_text:
        chunks = chunk_text(body_text, chunk_size=300, overlap=50)
    if not chunks and full_text:
        chunks = chunk_text(full_text, chunk_size=300, overlap=50)

    if not chunks:
        raise HTTPException(status_code=400, detail="No extractable text found in uploaded paper")

    clear_db()
    embeddings = create_embeddings(chunks)
    store_embeddings(chunks, embeddings)
    return len(chunks)


def _get_pdf_path(paper_id: str) -> Path:
    file_path = RAW_PAPERS_DIR / f"{paper_id}.pdf"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    return file_path


def _delete_paper_files(paper_id: str) -> None:
    processed_path = PROCESSED_DIR / f"{paper_id}.json"
    raw_path = RAW_PAPERS_DIR / f"{paper_id}.pdf"

    if processed_path.exists():
        processed_path.unlink()
    if raw_path.exists():
        raw_path.unlink()


def _prune_saved_uploads(max_uploads: int = MAX_STORED_UPLOADS) -> None:
    saved_files = sorted(PROCESSED_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    keep_ids = {file_path.stem for file_path in saved_files[:max_uploads]}

    for file_path in saved_files[max_uploads:]:
        _delete_paper_files(file_path.stem)

    for raw_path in RAW_PAPERS_DIR.glob("*.pdf"):
        if raw_path.stem not in keep_ids:
            raw_path.unlink()


@app.post("/upload")
async def upload_paper(file: UploadFile = File(...)):
    """Upload a PDF, run Person A's NLP pipeline, and index it for chat."""
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    paper_id = str(uuid4())
    file_path = RAW_PAPERS_DIR / f"{paper_id}.pdf"
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded PDF is empty")

    file_path.write_bytes(file_bytes)

    try:
        paper_data = process_paper(file_path)
        paper_data["paper_id"] = paper_id
        paper_data["original_filename"] = filename
        quality = paper_data.get("quality", {})
        if quality.get("likely_scanned"):
            raise HTTPException(
                status_code=400,
                detail=(
                    "This PDF appears to have poor extractable text. "
                    "Please upload a text-based research paper PDF, not a scanned or image-only document."
                ),
            )
        chunks_stored = _index_paper_for_chat(paper_data)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {exc}") from exc

    _save_processed_paper(paper_data)
    _set_current_paper(paper_data)
    _prune_saved_uploads()

    return {
        "status": "success",
        "paper_id": paper_id,
        "original_filename": filename,
        "chunks_stored": chunks_stored,
        "metadata": paper_data.get("metadata", {}),
        "quality": paper_data.get("quality", {}),
        "summaries": paper_data.get("summaries", {}),
        "keywords": paper_data.get("keywords", []),
        "concepts": paper_data.get("concepts", []),
    }


@app.post("/chat")
def chat(request: ChatRequest):
    """Answer a question about the uploaded paper."""
    paper = _get_paper_by_id(request.paper_id) if request.paper_id else _get_current_paper()
    try:
        if not request.paper_id and CURRENT_PAPER is None:
            raise HTTPException(status_code=404, detail="No paper uploaded yet")

        if request.paper_id and (
            CURRENT_PAPER is None or CURRENT_PAPER.get("paper_id") != request.paper_id
        ):
            _index_paper_for_chat(paper)

        result = answer_question(request.question, top_k=request.top_k)
        return {
            "paper_id": paper["paper_id"],
            "question": request.question,
            "answer": result["answer"],
            "sources": result["context"],
        }
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Chat model failed: {exc}") from exc


@app.get("/metadata")
def get_metadata():
    """Return metadata for the currently loaded paper."""
    paper = _get_current_paper()
    return {
        "paper_id": paper["paper_id"],
        "metadata": paper.get("metadata", {}),
    }


@app.post("/summarize")
def summarize():
    """Return summaries generated by Person A during upload."""
    paper = _get_current_paper()
    return {
        "paper_id": paper["paper_id"],
        "summaries": paper.get("summaries", {}),
    }


@app.get("/keywords")
def get_keywords():
    """Return keywords and concepts for the currently loaded paper."""
    paper = _get_current_paper()
    return {
        "paper_id": paper["paper_id"],
        "keywords": paper.get("keywords", []),
        "keyword_details": paper.get("keyword_details", []),
        "concepts": paper.get("concepts", []),
    }


@app.get("/paper")
def get_paper():
    """Return the full processed JSON for the currently loaded paper."""
    return _get_current_paper()


@app.get("/papers")
def list_papers():
    """Return all saved processed papers."""
    return [_paper_list_item(paper) for paper in _list_processed_papers()]


@app.get("/paper/{paper_id}")
def get_paper_by_id(paper_id: str):
    """Return a processed paper JSON payload by id."""
    return _get_paper_by_id(paper_id)


@app.post("/paper/{paper_id}/summarize")
def summarize_by_id(paper_id: str):
    """Return summaries for a saved paper by id."""
    paper = _get_paper_by_id(paper_id)
    return {
        "paper_id": paper["paper_id"],
        "summaries": paper.get("summaries", {}),
    }


@app.get("/paper/{paper_id}/keywords")
def get_keywords_by_id(paper_id: str):
    """Return keywords and concepts for a saved paper by id."""
    paper = _get_paper_by_id(paper_id)
    return {
        "paper_id": paper["paper_id"],
        "keywords": paper.get("keywords", []),
        "keyword_details": paper.get("keyword_details", []),
        "concepts": paper.get("concepts", []),
    }


@app.get("/paper/{paper_id}/pdf")
def get_paper_pdf(paper_id: str):
    """Return the raw uploaded PDF for preview/download."""
    paper = _get_paper_by_id(paper_id)
    file_path = _get_pdf_path(paper_id)
    filename = paper.get("original_filename") or f"{paper_id}.pdf"
    return FileResponse(file_path, media_type="application/pdf", filename=filename)


@app.get("/health")
def health():
    """Simple health endpoint for local development."""
    return {
        "status": "ok",
        "paper_loaded": CURRENT_PAPER is not None,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
