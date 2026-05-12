# Research Paper Analyzer - Project Handoff Document

**Project Name:** Research Paper Analyzer (RPA)  
**Created:** Semester 6, NLP Course  
**Last Updated:** April 23, 2026

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
- **LLM Integration:** Ollama (local) or OpenAI API (fallback)

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
- **Python Version:** 3.10+
- **Node Version:** 16+
- **Package Managers:** pip, npm/yarn

---

## 3. Project Structure

```
research paper analyser/
├── README.md
├── HANDOFF.md (this file)
│
├── backend/
│   └── bkend/                          # Main backend directory
│       ├── main.py                     # FastAPI app entry point
│       ├── requirements.txt            # Python dependencies
│       │
│       ├── services/                   # Core NLP services
│       │   ├── paper_processor.py      # Main NLP pipeline
│       │   ├── pdf_parser.py           # PDF text extraction
│       │   ├── metadata_extractor.py   # Extract paper metadata
│       │   ├── summarizer.py           # Summarization (BART-based)
│       │   ├── extractive_model_summarizer.py  # Extractive summaries
│       │   ├── keyword_extractor.py    # KeyBERT-based extraction
│       │   ├── embedding_store.py      # Text chunking & embeddings
│       │   ├── vector_db.py            # ChromaDB management
│       │   └── chat_engine.py          # RAG chat functionality
│       │
│       ├── data/                       # Data storage
│       │   ├── raw_papers/             # Uploaded PDF files
│       │   └── processed_text/         # Processed JSON outputs
│       │
│       ├── training/                   # Model training scripts
│       │   ├── README.md               # Training instructions
│       │   ├── train_summarizer.py     # Fine-tune BART
│       │   ├── train_extractive_summarizer.py
│       │   └── checkpoints/            # Saved model weights
│       │
│       ├── tests/                      # Unit tests
│       │   ├── test_chat_engine.py
│       │   ├── test_embedding_store.py
│       │   ├── test_person_a_pipeline.py
│       │   └── test_vector_db.py
│       │
│       └── arxiv/                      # Pre-downloaded dataset (optional)
│           ├── train/
│           ├── validation/
│           └── test/
│
├── frontend/
│   └── frontend/
│       └── rpa-ui/                     # React application
│           ├── package.json
│           ├── vite.config.ts
│           ├── tailwind.config.js
│           ├── tsconfig.json
│           ├── index.html
│           │
│           ├── src/
│           │   ├── App.tsx             # Main App component
│           │   ├── index.tsx           # React root
│           │   ├── index.css           # Global styles
│           │   │
│           │   ├── pages/              # Page components
│           │   │   ├── HomePage.tsx
│           │   │   ├── PapersPage.tsx
│           │   │   ├── UploadPage.tsx
│           │   │   └── PaperDetailPage.tsx
│           │   │
│           │   ├── components/         # Reusable components
│           │   │   ├── layout/
│           │   │   ├── upload/
│           │   │   ├── paper/
│           │   │   ├── chat/
│           │   │   ├── keywords/
│           │   │   └── ui/
│           │   │
│           │   ├── store/              # Zustand state management
│           │   │   └── paperStore.ts
│           │   │
│           │   ├── hooks/              # Custom React hooks
│           │   │   └── useApi.ts
│           │   │
│           │   ├── lib/                # Utilities
│           │   │   ├── api.ts          # API client
│           │   │   └── utils.ts        # Helper functions
│           │   │
│           │   └── types/              # TypeScript types
│           │       └── index.ts
│           │
│           └── README.md
```

---

## 4. Setup & Installation

### 4.1 Backend Setup

#### Prerequisites
- Python 3.10 or higher
- pip
- Virtual environment tool (venv)

#### Steps

```bash
# Navigate to backend directory
cd backend/bkend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** If you encounter issues with `faiss-cpu`, you can comment it out in `requirements.txt` as ChromaDB is the primary vector DB.

#### Optional: Ollama Setup (for local LLM)

If using local Ollama instead of OpenAI:

```bash
# Install Ollama from https://ollama.ai
# Pull a model (e.g., Mistral)
ollama pull mistral

# Start Ollama server (default port: 11434)
ollama serve
```

### 4.2 Frontend Setup

#### Prerequisites
- Node.js 16+ and npm/yarn

#### Steps

```bash
# Navigate to frontend directory
cd frontend/frontend/rpa-ui

# Install dependencies
npm install
# or
yarn install
```

---

## 5. Running the Application

### 5.1 Start Backend

```bash
# From backend/bkend directory (with .venv activated)
python main.py
```

The backend will start at **http://localhost:8000**

#### Environment Variables (Optional)

Create a `.env` file in `backend/bkend/` for configuration:

```env
# Use Transformer-based summarization
USE_TRANSFORMER_SUMMARY=1
SUMMARIZER_MODEL=training/checkpoints/bart-arxiv

# OpenAI API (if not using Ollama)
OPENAI_API_KEY=your_key_here

# Ollama configuration
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral
```

### 5.2 Start Frontend

```bash
# From frontend/frontend/rpa-ui directory
npm run dev
```

The frontend will start at **http://localhost:5173** (or another port if 5173 is busy)

### 5.3 Full Development Setup

Run both services simultaneously in separate terminals:

```bash
# Terminal 1: Backend
cd backend/bkend
.\.venv\Scripts\Activate.ps1
python main.py

# Terminal 2: Frontend
cd frontend/frontend/rpa-ui
npm run dev
```

---

## 6. Backend API Documentation

### 6.1 Main Endpoints

#### Upload Paper
- **Endpoint:** `POST /upload`
- **Parameters:** `file: UploadFile` (PDF)
- **Response:**
  ```json
  {
    "status": "success",
    "paper_id": "uuid",
    "chunks_stored": 42,
    "metadata": {...},
    "summaries": {...},
    "keywords": [...],
    "concepts": [...]
  }
  ```

#### Chat with Paper
- **Endpoint:** `POST /chat`
- **Body:**
  ```json
  {
    "question": "What is the main contribution?",
    "top_k": 3
  }
  ```
- **Response:**
  ```json
  {
    "answer": "...",
    "sources": [...]
  }
  ```

#### Get Current Paper
- **Endpoint:** `GET /paper`
- **Response:** Full paper JSON with metadata, summaries, keywords

#### Clear Vector DB
- **Endpoint:** `POST /clear`
- **Response:** Confirmation message

### 6.2 API Documentation

Full interactive documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 7. Core Services & Modules

### 7.1 `paper_processor.py` - Main NLP Pipeline
**Purpose:** Orchestrates the entire NLP pipeline  
**Key Function:** `process_paper(file_path)` → returns structured JSON

**Pipeline Steps:**
1. Parse PDF → extract text and sections
2. Summarize sections → generate section summaries
3. Extract metadata → title, authors, year, DOI
4. Extract keywords → using KeyBERT
5. Extract concepts → entity recognition
6. Build one-page brief → condensed summary

**Output Structure:**
```python
{
    "paper_id": "uuid",
    "metadata": {...},
    "title": "...",
    "authors": [...],
    "sections": {"intro": "...", "methods": "..."},
    "full_text": "...",
    "summaries": {"full_text": "...", "brief": "..."},
    "keywords": ["..."],
    "keyword_details": [...],
    "concepts": [...]
}
```

### 7.2 `pdf_parser.py` - PDF Text Extraction
**Purpose:** Extract text and sections from PDFs  
**Methods:** PyMuPDF (fast) and pdfplumber (fallback)  
**Returns:** Full text and section-based organization

### 7.3 `embedding_store.py` - Text Chunking & Embeddings
**Key Function:** `create_embeddings(texts)` → returns vectors  
**Model:** `sentence-transformers/all-MiniLM-L6-v2` (default)  
**Chunking:** Overlapping chunks (size=300, overlap=50)

### 7.4 `vector_db.py` - ChromaDB Vector Storage
**Purpose:** Store and retrieve document embeddings  
**Key Functions:**
- `store_embeddings(chunks, embeddings)` - Add vectors
- `retrieve(query, top_k=3)` - Semantic search
- `clear_db()` - Clear collection

### 7.5 `chat_engine.py` - RAG & Q&A
**Purpose:** Answer questions about papers  
**LLM Options:**
- **Local:** Ollama (Mistral, Llama2, etc.)
- **API:** OpenAI (gpt-3.5-turbo)

**RAG Flow:**
1. Retrieve relevant chunks from vector DB
2. Build prompt with retrieved context
3. Call LLM with prompt
4. Return answer + sources

### 7.6 `metadata_extractor.py` - Paper Metadata
**Extracts:**
- Title
- Authors
- Publication year
- Journal/Conference
- DOI
- Abstract

### 7.7 `keyword_extractor.py` - Key Terms & Concepts
**Uses:** KeyBERT + spaCy  
**Extracts:**
- Keywords with importance scores
- Named entities
- Concepts

### 7.8 `summarizer.py` - Text Summarization
**Models:**
- **BART:** Abstractive summarization (transformer-based)
- **Extractive:** Top-k important sentences
- **One-page brief:** Condensed executive summary

---

## 8. Frontend Architecture

### 8.1 Pages

1. **HomePage.tsx** - Landing page with navigation
2. **UploadPage.tsx** - PDF upload interface
3. **PapersPage.tsx** - List of processed papers
4. **PaperDetailPage.tsx** - Full paper view with chat

### 8.2 State Management (Zustand)

**paperStore.ts** manages:
- Current paper data
- List of papers
- UI state (loading, errors)

```typescript
// Example usage
import { usePaperStore } from '@/store/paperStore';
const { currentPaper, uploadPaper } = usePaperStore();
```

### 8.3 API Client

**lib/api.ts** provides:
- `uploadPaper(file)` - POST /upload
- `askQuestion(question, top_k)` - POST /chat
- `getCurrentPaper()` - GET /paper

### 8.4 Custom Hooks

**useApi.ts** provides:
- `useUploadPaper()` - Handles file upload
- `useChat()` - Chat interaction
- Error handling and loading states

---

## 9. Data Storage

### 9.1 Raw Papers
**Location:** `backend/bkend/data/raw_papers/`  
**Format:** PDF files named by UUID  
**Purpose:** Store original uploaded documents

### 9.2 Processed Data
**Location:** `backend/bkend/data/processed_text/`  
**Format:** JSON files with structure from `paper_processor.py`  
**Purpose:** Cache processed paper data (metadata, summaries, keywords)

### 9.3 Vector Database
**Type:** ChromaDB (in-memory by default)  
**Purpose:** Store embeddings for semantic search  
**Persistence:** Can be configured for disk storage

### 9.4 Model Checkpoints
**Location:** `backend/bkend/training/checkpoints/`  
**Purpose:** Store fine-tuned model weights  
**Models:** BART summarizer, etc.

---

## 10. Training & Model Fine-tuning

### 10.1 Summarizer Training

**Dataset:** ArXiv Summary Dataset (from Kaggle)

```bash
# Download dataset
kaggle datasets download -d syndri224/arxiv-summary-dataset -p data/kaggle/arxiv-summary-dataset --unzip

# Train with custom samples
python training\train_summarizer.py `
  --data-dir data\kaggle\arxiv-summary-dataset `
  --train-samples 2000 `
  --eval-samples 200 `
  --epochs 1
```

### 10.2 Using Trained Models

Set environment variables:
```powershell
$env:USE_TRANSFORMER_SUMMARY="1"
$env:SUMMARIZER_MODEL="training/checkpoints/bart-arxiv"
```

---

## 11. Testing

### 11.1 Test Files

- **test_person_a_pipeline.py** - Full pipeline tests
- **test_chat_engine.py** - RAG & Q&A tests
- **test_vector_db.py** - ChromaDB tests
- **test_embedding_store.py** - Embedding tests

### 11.2 Running Tests

```bash
# From backend/bkend directory
pytest tests/
# or specific test:
pytest tests/test_person_a_pipeline.py -v
```

---

## 12. Key Design Patterns

### 12.1 Backend Architecture
- **Modular Services:** Each NLP task in separate module
- **Pipeline Pattern:** `process_paper()` chains services
- **FastAPI Best Practices:** Async endpoints, Pydantic models
- **Error Handling:** Custom HTTPException with detailed messages

### 12.2 Frontend Architecture
- **Component-Based:** Reusable UI components
- **Centralized State:** Zustand store for global state
- **API Layer:** Abstracted in `lib/api.ts`
- **Type Safety:** Full TypeScript coverage

### 12.3 Data Flow
```
User Upload PDF
    ↓
Backend: PDF Parser → NLP Pipeline → Vector DB
    ↓
Frontend: Display Metadata, Summaries, Keywords
    ↓
User Asks Question
    ↓
Backend: RAG (Vector DB + LLM) → Answer
    ↓
Frontend: Display Answer with Sources
```

---

## 13. Common Tasks & Workflows

### 13.1 Add a New NLP Service

1. Create `backend/bkend/services/new_service.py`
2. Implement service function
3. Import and integrate into `paper_processor.py`
4. Update response schema
5. Test with `pytest`

### 13.2 Modify API Response

1. Update service function return type
2. Update FastAPI response model
3. Update frontend types in `frontend/src/types/index.ts`
4. Update frontend components

### 13.3 Add Frontend Page

1. Create component in `frontend/src/pages/`
2. Add route in `App.tsx`
3. Create corresponding components
4. Add navigation link

### 13.4 Debug Vector DB Issues

```python
# Check ChromaDB collection
from services.vector_db import collection

# Count documents
print(f"Documents in collection: {collection.count()}")

# Clear and restart
from services.vector_db import clear_db
clear_db()
```

---

## 14. Troubleshooting

### 14.1 Backend Issues

| Issue | Solution |
|-------|----------|
| **Ollama connection failed** | Ensure Ollama is running: `ollama serve` |
| **PDF parsing fails** | Try different extraction method in `pdf_parser.py` |
| **ChromaDB empty error** | Upload a paper first via `/upload` endpoint |
| **CUDA/GPU not found** | Ensure PyTorch CPU version or CUDA 11.8+ installed |
| **Memory issues** | Reduce `chunk_size` or `top_k` in config |

### 14.2 Frontend Issues

| Issue | Solution |
|-------|----------|
| **CORS errors** | Check backend is running on 8000 |
| **API calls timeout** | Increase timeout in `lib/api.ts` |
| **State not updating** | Check Zustand store subscription |
| **Build fails** | Delete `node_modules` and `package-lock.json`, then `npm install` |

### 14.3 Model/Training Issues

| Issue | Solution |
|-------|----------|
| **OOM during training** | Reduce batch size in training scripts |
| **Model not found** | Check checkpoint path in `.env` |
| **Slow inference** | Use smaller model or quantized version |

---

## 15. Performance Optimization Tips

### 15.1 Backend Optimization
- **Embeddings:** Use distilled models (all-MiniLM-L6-v2 is good baseline)
- **Chunking:** Tune chunk_size/overlap for your use case
- **Caching:** Cache embeddings between uploads
- **Async:** Use async endpoints for I/O operations
- **Model Quantization:** Quantize models for faster inference

### 15.2 Frontend Optimization
- **Code Splitting:** Lazy load page components
- **Memoization:** Use React.memo for heavy components
- **State:** Keep store lean, derive computed values
- **Images/Assets:** Optimize and lazy load

---

## 16. Deployment Considerations

### 16.1 Backend Deployment
- **Docker:** Create Dockerfile for containerization
- **Environment:** Set all env vars on production server
- **Database:** Configure persistent ChromaDB or upgrade to Elasticsearch
- **Monitoring:** Add logging and error tracking (e.g., Sentry)
- **Scaling:** Use Uvicorn with multiple workers

### 16.2 Frontend Deployment
- **Build:** `npm run build` → creates `dist/` folder
- **Hosting:** Deploy to Vercel, Netlify, or static hosting
- **API URL:** Set API base URL for production environment
- **CDN:** Use CDN for static assets

### 16.3 Production Checklist
- [ ] Environment variables configured
- [ ] Error logging enabled
- [ ] CORS properly configured
- [ ] API rate limiting added
- [ ] Database persistence enabled
- [ ] Backup strategy in place
- [ ] Monitoring/alerting setup
- [ ] Security: HTTPS, auth, input validation

---

## 17. Future Enhancements

### 17.1 Possible Improvements
1. **User Authentication** - Multi-user support
2. **Paper Collections** - Organize papers into groups
3. **Comparison Tool** - Compare multiple papers
4. **Export Formats** - PDF/Word export of summaries
5. **Advanced Search** - Semantic search across multiple papers
6. **Fine-grained Permissions** - Share papers with others
7. **Real-time Collaboration** - Multiple users on same paper
8. **API Rate Limiting** - Prevent abuse
9. **Caching Layer** - Redis for faster responses
10. **Advanced NLP** - Relation extraction, argument mining

### 17.2 Research Directions
- Evaluate different summarization models
- Benchmark embedding models
- Explore domain-specific LLMs
- Integrate citation network analysis
- Add topic modeling capabilities

---

## 18. Important Files Reference

| File | Purpose | Key Functions |
|------|---------|---|
| `main.py` | FastAPI app | `/upload`, `/chat` endpoints |
| `paper_processor.py` | NLP pipeline | `process_paper()` |
| `vector_db.py` | Embeddings storage | `store_embeddings()`, `retrieve()` |
| `chat_engine.py` | Q&A with RAG | `answer_question()` |
| `App.tsx` | React root | Routing, layout |
| `paperStore.ts` | State management | Global paper state |
| `api.ts` | API client | HTTP requests to backend |

---

## 19. Contact & Support

For issues or questions:
1. Check the **Troubleshooting** section (14)
2. Review test files for usage examples
3. Check API documentation at `/docs`
4. Review component prop types in TypeScript files

---

## 20. Quick Reference

### Start Development
```bash
# Terminal 1: Backend
cd backend/bkend
.\.venv\Scripts\Activate.ps1
python main.py

# Terminal 2: Frontend
cd frontend/frontend/rpa-ui
npm run dev
```

### Production Build
```bash
# Frontend
npm run build  # Creates dist/ folder

# Backend
# Use Gunicorn or similar for production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Add Dependencies
```bash
# Backend
pip install <package>
pip freeze > requirements.txt

# Frontend
npm install <package>
```

---

**Document Version:** 1.0  
**Last Updated:** April 23, 2026  
**Status:** Ready for handoff
