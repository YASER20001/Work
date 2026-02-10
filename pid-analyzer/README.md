# P&ID Vision Analyzer

Advanced P&ID (Piping & Instrumentation Diagram) analysis system powered by Google Gemini 2.5 Flash Vision AI. Upload any P&ID drawing and get a comprehensive 11-phase expert-level analysis with symbol-by-symbol identification, ISA-5.1 compliant instrument decoding, and natural language querying.

## Features

- **11-Phase Expert Analysis Pipeline** — Systematic extraction from document context through re-verification
- **Gemini 2.5 Flash Vision AI** — High-accuracy image analysis with 0.1 temperature for precision
- **ISA-5.1 Compliant** — Built-in engineering knowledge base for instrument tag decoding
- **Natural Language Q&A** — Ask questions about the analyzed P&ID and get expert answers
- **JSON Export** — Download full analysis results for external use
- **Multi-Format Upload** — Supports PDF, PNG, JPG, and WEBP files
- **Real-Time Progress** — Live status updates as each analysis phase completes

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11+ with FastAPI |
| AI Engine | Google Gemini 2.5 Flash Vision API |
| PDF Processing | PyMuPDF (fitz) + Pillow |
| Frontend | HTML / CSS / Vanilla JavaScript |
| Templating | Jinja2 |

## Project Structure

```
pid-analyzer/
├── main.py                      # FastAPI application & API endpoints
├── requirements.txt             # Python dependencies
├── services/
│   ├── __init__.py
│   ├── gemini_vision.py         # Gemini API client + 11 analysis prompts
│   ├── pdf_processor.py         # PDF to image conversion
│   └── pid_knowledge.py         # ISA-5.1 engineering knowledge base
├── models/
│   ├── __init__.py
│   └── schemas.py               # Pydantic request/response models
├── static/
│   ├── css/
│   │   └── style.css            # Application styles
│   └── js/
│       └── app.js               # Frontend logic
├── templates/
│   └── index.html               # Main UI template
└── uploads/                     # Temporary upload directory (auto-created)
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd pid-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API key

The Gemini API key is set in `services/gemini_vision.py`. You can override it with an environment variable:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 4. Run the server

```bash
python main.py
```

Or with auto-reload for development:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open in browser

```
http://localhost:8000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web UI |
| `/api/upload` | POST | Upload a P&ID file (PDF, PNG, JPG, WEBP) |
| `/api/analyze/{session_id}` | POST | Start 11-phase analysis |
| `/api/status/{session_id}` | GET | Poll analysis progress |
| `/api/results/{session_id}` | GET | Get full analysis results |
| `/api/query` | POST | Ask a natural language question about the P&ID |
| `/api/export/{session_id}` | GET | Download results as JSON |

## How It Works

### Upload

1. Open `http://localhost:8000` in your browser
2. Drag and drop a P&ID file onto the upload area, or click to browse
3. Supported formats: **PDF**, **PNG**, **JPG**, **WEBP**
4. PDFs are automatically converted to high-resolution images (200 DPI)

### 11-Phase Analysis Pipeline

Once you click **Start 11-Phase Analysis**, the system runs these phases sequentially:

| Phase | Name | What It Does |
|-------|------|--------------|
| 1 | Document Context | Extracts title block, design data, and references |
| 2 | Legend & Symbols | Identifies valve symbols, instrument symbols, and line types |
| 3 | Notes Extraction | Word-for-word transcription of all engineering notes |
| 4 | Equipment Scan | Systematic left-to-right, top-to-bottom equipment identification |
| 5 | Valve Analysis | Symbol-by-symbol valve identification with type, actuator, and position |
| 6 | Instrumentation | ISA-5.1 tag decoding for every instrument bubble |
| 7 | Piping Analysis | Line number decoding, routing, and component listing |
| 8 | Connections & Flow | Process flow mapping, utility connections, and relief paths |
| 9 | Safety Analysis | Area classification, gas detection, ESD, and relief devices |
| 10 | Verification | Summary statistics and verification checklist |
| 11 | Re-verification | Double-check of valve counts, gas detection, and critical notes |

Each phase passes context to the next. Phase 11 re-verifies the valve count from Phase 5 to catch any discrepancies.

### Query the P&ID

After analysis completes, use the chat interface at the bottom of the page to ask questions like:

- "How many control valves are on this P&ID?"
- "What is the design pressure?"
- "List all safety relief valves and their set pressures"
- "What does tag PIT-0210 measure?"
- "Trace the main process flow path"

### Export Results

Click **Export JSON** to download the complete analysis as a structured JSON file containing all 11 phase results, statistics, confidence score, and timestamps.

## Engineering Knowledge Base

The system includes a built-in knowledge base (`services/pid_knowledge.py`) covering:

- **ISA-5.1 Instrument Letters** — All 26 first letters (measured variable) and succeeding letters (function)
- **Valve Types** — Gate, globe, ball, plug, butterfly, check, relief, control, MOV, solenoid with symbol descriptions
- **Valve Positions** — NC, NO, LC, LO, FC, FO, FL, CSC, CSO, TSO
- **Service Codes** — P, BD, RL, FL, FG, IA, PA, N2, ST, CW, BW, FW, UW, OW, CD, DR
- **Area Classification** — Class I/II/III, Division 1/2, Zone 0/1/2

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| API Key | `services/gemini_vision.py` or `GEMINI_API_KEY` env var | Embedded key |
| Temperature | `services/gemini_vision.py` | 0.1 (high accuracy) |
| Max Output Tokens | `services/gemini_vision.py` | 16384 |
| PDF Render DPI | `services/pdf_processor.py` | 200 |
| Phase Delay | `main.py` | 1.5 seconds (rate limiting) |
| Server Port | `main.py` | 8000 |

## Example API Usage

### Upload a file

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@my-pid-drawing.pdf"
```

Response:
```json
{
  "status": "success",
  "session_id": "abc-123-def",
  "filename": "my-pid-drawing.pdf",
  "message": "File uploaded successfully. Ready for analysis."
}
```

### Start analysis

```bash
curl -X POST http://localhost:8000/api/analyze/abc-123-def
```

### Check progress

```bash
curl http://localhost:8000/api/status/abc-123-def
```

### Ask a question

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc-123-def", "question": "How many valves are there?"}'
```

### Export results

```bash
curl -O http://localhost:8000/api/export/abc-123-def
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.109.0 | Web framework |
| uvicorn | 0.27.0 | ASGI server |
| python-multipart | 0.0.6 | File upload handling |
| aiohttp | 3.9.1 | Async HTTP client for Gemini API |
| Pillow | 10.2.0 | Image processing |
| PyMuPDF | 1.23.8 | PDF rendering |
| pydantic | 2.5.3 | Data validation |
| jinja2 | 3.1.3 | HTML templating |
| python-dotenv | 1.0.0 | Environment variable loading |
