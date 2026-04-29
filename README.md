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

## Tech Stack

### Backend

- Python
- FastAPI
- Uvicorn
- PyMuPDF and pdfplumber
- Transformers and KeyBERT
- Sentence Transformers or hashing-based fallback embeddings
- In-memory vector retrieval

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Zustand
- React Router

## Project Structure

```text
research paper analyser/
├── backend/
│   └── bkend/
│       ├── main.py
│       ├── requirements.txt
│       ├── services/
│       ├── tests/
│       └── data/
├── frontend/
│   └── rpa-ui/
│       ├── package.json
│       ├── vite.config.ts
│       └── src/
└── README.md
```

## Active App Paths

Use these folders when running the project:

- Backend: `backend/bkend`
- Frontend: `frontend/rpa-ui`

There is another nested frontend copy in the repository, but the active app currently uses `frontend/rpa-ui`.

## Backend Setup

Open a terminal in the backend folder:

```powershell
cd "c:\Users\ravi\Desktop\Khushi AI ML\sem 6\nlp\research paper analyser\backend\bkend"
```

If you need to install dependencies:

```powershell
pip install -r requirements.txt
```

If you already have the local virtual environment, activate it with:

```powershell
.\venv\Scripts\Activate.ps1
```

## Frontend Setup

Open a second terminal in the frontend folder:

```powershell
cd "c:\Users\ravi\Desktop\Khushi AI ML\sem 6\nlp\research paper analyser\frontend\rpa-ui"
```

Install frontend dependencies if needed:

```powershell
npm install
```

## Running the Application

Start the backend:

```powershell
cd "c:\Users\ravi\Desktop\Khushi AI ML\sem 6\nlp\research paper analyser\backend\bkend"
.\venv\Scripts\Activate.ps1
python main.py
```

Start the frontend:

```powershell
cd "c:\Users\ravi\Desktop\Khushi AI ML\sem 6\nlp\research paper analyser\frontend\rpa-ui"
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

## How It Works

1. Upload a PDF through the frontend.
2. The backend saves the file and processes the paper.
3. Metadata, summaries, keywords, concepts, and extracted text are generated.
4. The paper text is chunked and embedded for retrieval.
5. The frontend displays summary and keyword results.
6. The chat panel uses retrieved chunks to answer questions about the uploaded paper.

## API Endpoints

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

- Raw PDFs: `backend/bkend/data/raw_papers`
- Processed JSON: `backend/bkend/data/processed_text`

## Chat Notes

The chat flow retrieves relevant chunks from the uploaded paper and then tries to generate a final answer.

- If a local Ollama server is available at `http://localhost:11434`, chat can use it for response generation.
- If Ollama is not running, the backend falls back to returning the most relevant retrieved text instead of failing.

## Development Notes

- The frontend uses a Vite proxy so requests to `/api` are forwarded to the FastAPI backend.
- The backend currently keeps the active paper and vector store in memory for the running session.
- Restarting the backend clears the active in-memory chat index.

## Testing

Backend tests are located in:

```text
backend/bkend/tests
```

If you want to run them:

```powershell
cd "c:\Users\ravi\Desktop\Khushi AI ML\sem 6\nlp\research paper analyser\backend\bkend"
pytest
```

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
