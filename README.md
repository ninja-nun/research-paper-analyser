# Research Paper Analyzer

Research Paper Analyzer is a full-stack NLP application for uploading research papers in PDF format, extracting structured information, generating summaries, surfacing keywords, and enabling question-answering over the uploaded paper.

The project uses a FastAPI backend for document processing and a React + Vite frontend for the user interface.

## Features

- Upload research papers as PDF files
- Extract metadata such as title, authors, year, journal, and DOI
- Parse and organize paper text into sections
- Generate a brief summary plus section-wise summaries
- Extract keywords and concepts
- Ask questions about the uploaded paper through a retrieval-based chat flow

---

## 1. Project Overview

The Research Paper Analyzer is an end-to-end NLP system designed to process PDF research papers and extract structured insights. It combines multiple NLP techniques to:

- **Extract Metadata** - Title, authors, year, journal, DOI
- **Parse Text** - Extract full text and organize by sections
- **Summarize** - Generate section-level and full-paper summaries
- **Extract Keywords** - Identify key terms and concepts
- **Enable Chat** - Allow users to ask questions about papers using RAG (Retrieval-Augmented Generation)

The system features a **FastAPI backend** for NLP processing and a **React frontend** with TypeScript for user interaction.

---

## 2. Technology Stack

### Backend
- **Framework:** FastAPI (Python)
- **Server:** Uvicorn
- **Vector DB:** ChromaDB (for semantic search)
- **Embeddings:** Sentence-Transformers
- **PDF Processing:** PyMuPDF (pymupdf), pdfplumber
- **NLP Models:** 
  - Hugging Face Transformers
  - BART (for summarization)
  - KeyBERT (for keyword extraction)
  - spaCy-like models
- **LLM Integration:** Ollama (local) or Gemini API (fallback)

### Frontend
- **Framework:** React 18.3.1
- **Language:** TypeScript
- **Routing:** React Router v6
- **Styling:** Tailwind CSS + PostCSS
- **Build Tool:** Vite
- **UI Components:** Lucide React icons
- **Charts:** Recharts
- **State Management:** Zustand
- **Styling Utilities:** Emotion, clsx, tailwind-merge

### Development
- **Python Version:** 3.11+
- **Node Version:** 16+
- **Package Managers:** pip, npm/yarn

---

## 3. Project Structure

```
research paper analyser/
├── README.md
│
├── backend/
│   ├── main.py                     # FastAPI app entry point
│   ├── requirements.txt            # Python dependencies
│   │
│   ├── services/                   # Core NLP services
│   │   ├── paper_processor.py      # Main NLP pipeline
│   │   ├── pdf_parser.py           # PDF text extraction
│   │   ├── metadata_extractor.py   # Extract paper metadata
│   │   ├── summarizer.py           # Summarization (BART-based)
│   │   ├── extractive_model_summarizer.py  # Extractive summaries
│   │   ├── keyword_extractor.py    # KeyBERT-based extraction
│   │   ├── embedding_store.py      # Text chunking & embeddings
│   │   ├── vector_db.py            # ChromaDB management
│   │   └── chat_engine.py          # RAG chat functionality
│   │
│   └── data/                       # Data storage
│       ├── raw_papers/             # Uploaded PDF files
│       └── processed_text/         # Processed JSON outputs 
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── index.html
│   │
│   ├── src/
│   │   ├── App.tsx             # Main App component
│   │   ├── index.tsx           # React root
│   │   ├── index.css           # Global styles
│   │   │
│   │   ├── pages/              # Page components
│   │   │   ├── HomePage.tsx
│   │   │   ├── PapersPage.tsx
│   │   │   ├── UploadPage.tsx
│   │   │   └── PaperDetailPage.tsx
│   │   │
│   │   ├── components/         # Reusable components
│   │   │   ├── layout/
│   │   │   ├── upload/
│   │   │   ├── paper/
│   │   │   ├── chat/
│   │   │   ├── keywords/
│   │   │   └── ui/
│   │   │
│   │   ├── store/              # Zustand state management
│   │   │   └── paperStore.ts
│   │   │
│   │   ├── hooks/              # Custom React hooks
│   │   │   └── useApi.ts
│   │   │
│   │   ├── lib/                # Utilities
│   │   │   ├── api.ts          # API client
│   │   │   └── utils.ts        # Helper functions
│   │   │
│   │   └── types/              # TypeScript types
│   │       └── index.ts
│   │
│   └── README.md
```

---

## 4. Setup and Installation

### 4.1 Backend Setup

#### Prerequisites
- Python 3.11 or higher
- pip
- Virtual environment tool (venv)

#### Steps

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4.2 Frontend Setup

#### Prerequisites
- Node.js 16+ and npm/yarn

#### Steps

```bash
# Navigate to frontend directory from root
cd frontend

# Install dependencies
npm install
# or
yarn install
```

---

## 5. Running the Application

### 5.1 Start Backend

```bash
# From backend directory (with .venv activated)
python main.py
```

The backend will start at **http://localhost:8000**

#### Environment Variables (Optional)

Create a `.env` file in `backend` for configuration:

```env
# Use Transformer-based summarization
USE_TRANSFORMER_SUMMARY=1
SUMMARIZER_MODEL=training/checkpoints/bart-arxiv

# Gemini API
GEMINI_API_KEY=your_key_here
```

### 5.2 Start Frontend

```bash
# From frontend directory
npm run dev
```

The frontend will start at **http://localhost:5173** (or another port if 5173 is busy)

### 5.3 Full Development Setup

Run both services simultaneously in separate terminals:

```bash
# Terminal 1: Backend
cd backend
.\.venv\Scripts\Activate.ps1
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

Open the app at:

```text
http://127.0.0.1:5173
```

The backend runs at:

```text
http://127.0.0.1:8000
```

## 5.4 How It Works

1. Upload a PDF through the frontend.
2. The backend saves the file and processes the paper.
3. Metadata, summaries, keywords, concepts, and extracted text are generated.
4. The paper text is chunked and embedded for retrieval.
5. The frontend displays summary and keyword results.
6. The chat panel uses retrieved chunks to answer questions about the uploaded paper.

---

## 6. API Endpoints

- `POST /upload`  
  Upload and process a PDF file.

- `POST /chat`  
  Ask a question about the currently uploaded paper.

- `GET /paper`  
  Return the current processed paper payload.

- `POST /summarize`  
  Return generated summaries for the current paper.

- `GET /keywords`  
  Return extracted keywords and concepts.

- `GET /metadata`  
  Return extracted metadata.

- `GET /health`  
  Health check endpoint.

## Data Storage

Uploaded and processed files are stored here:

- Raw PDFs: `backend/data/raw_papers`
- Processed JSON: `backend/data/processed_text`

## Chat Notes

The chat flow retrieves relevant chunks from the uploaded paper and then tries to generate a final answer.


## Development Notes

- The frontend uses a Vite proxy so requests to `/api` are forwarded to the FastAPI backend.
- The backend currently keeps the active paper and vector store in memory for the running session.
- Restarting the backend clears the active in-memory chat index.


## Known Limitations

- Only PDF uploads are supported.
- Chat is scoped to the currently active uploaded paper.
- The current vector retrieval is in-memory and resets when the backend restarts.
- If no local LLM is available, chat falls back to retrieved context instead of a fully generated answer.

## Future Improvements

- Add persistent vector storage
- Support multiple saved papers in the UI
- Add paper deletion endpoint
- Improve generated chat responses with a configured LLM provider
- Add stronger frontend and backend validation
