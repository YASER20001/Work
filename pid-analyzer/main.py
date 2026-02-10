"""
P&ID Vision Analyzer - FastAPI Application
Expert-level P&ID analysis using Gemini Vision AI with 11-phase pipeline.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.requests import Request
import uvicorn
import os
import uuid
import json
import base64
import asyncio
from datetime import datetime
from typing import Dict

from models.schemas import QueryRequest
from services.gemini_vision import GeminiVisionService, EXPERT_ANALYSIS_PHASES
from services.pdf_processor import PDFProcessor
from services.pid_knowledge import PID_ENGINEERING_KNOWLEDGE

app = FastAPI(
    title="P&ID Vision Analyzer API",
    description="Expert-level P&ID analysis using Gemini Vision AI",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

gemini_service = GeminiVisionService()
pdf_processor = PDFProcessor()

# In-memory storage for analysis sessions
ANALYSIS_SESSIONS: Dict[str, dict] = {}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main UI."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload P&ID file (PDF or image)."""

    allowed_types = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/webp",
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Allowed: PDF, PNG, JPG, WEBP",
        )

    session_id = str(uuid.uuid4())

    file_path = os.path.join(UPLOAD_DIR, f"{session_id}_{file.filename}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        if file.content_type == "application/pdf":
            image_base64, mime_type = pdf_processor.pdf_to_image_base64(file_path)
        else:
            image_base64 = base64.b64encode(content).decode("utf-8")
            mime_type = file.content_type

        ANALYSIS_SESSIONS[session_id] = {
            "file_path": file_path,
            "filename": file.filename,
            "image_base64": image_base64,
            "mime_type": mime_type,
            "upload_time": datetime.now().isoformat(),
            "analysis_results": None,
            "analysis_status": "pending",
        }

        return {
            "status": "success",
            "session_id": session_id,
            "filename": file.filename,
            "message": "File uploaded successfully. Ready for analysis.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing file: {str(e)}"
        )


@app.post("/api/analyze/{session_id}")
async def start_analysis(session_id: str, background_tasks: BackgroundTasks):
    """Start 11-phase P&ID analysis."""

    if session_id not in ANALYSIS_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    session = ANALYSIS_SESSIONS[session_id]

    if session["analysis_status"] == "in_progress":
        raise HTTPException(status_code=400, detail="Analysis already in progress")

    session["analysis_status"] = "in_progress"
    session["analysis_progress"] = {"current_phase": 0, "total_phases": 11}

    background_tasks.add_task(
        run_analysis,
        session_id,
        session["image_base64"],
        session["mime_type"],
    )

    return {
        "status": "started",
        "session_id": session_id,
        "message": "Analysis started. Poll /api/status/{session_id} for progress.",
    }


async def run_analysis(session_id: str, image_base64: str, mime_type: str):
    """Run the 11-phase analysis."""

    session = ANALYSIS_SESSIONS[session_id]
    results = {
        "phases": {},
        "statistics": {},
        "errors": [],
        "confidence": 100,
        "start_time": datetime.now().isoformat(),
    }

    context = {"valve_count": 0}
    phases = list(EXPERT_ANALYSIS_PHASES.keys())

    for i, phase_key in enumerate(phases):
        try:
            session["analysis_progress"] = {
                "current_phase": i + 1,
                "total_phases": 11,
                "phase_name": phase_key,
            }

            prompt = EXPERT_ANALYSIS_PHASES[phase_key]

            if phase_key == "phase11_reverification":
                prompt = prompt.format(
                    previous_valve_count=context.get("valve_count", 0)
                )

            response = await gemini_service.analyze_image(
                image_base64=image_base64,
                mime_type=mime_type,
                prompt=prompt,
            )

            parsed = gemini_service.parse_response(response)
            results["phases"][phase_key] = {
                "result": parsed,
                "raw": response,
                "timestamp": datetime.now().isoformat(),
            }

            if phase_key == "phase5_valve_analysis":
                context["valve_count"] = parsed.get(
                    "GRAND TOTAL", 0
                ) or parsed.get("total", 0)

            # Delay between phases to avoid rate limiting
            await asyncio.sleep(1.5)

        except Exception as e:
            results["errors"].append({"phase": phase_key, "error": str(e)})
            results["confidence"] -= 10

    results["statistics"] = extract_statistics(results["phases"])
    results["confidence"] = max(0, results["confidence"])
    results["end_time"] = datetime.now().isoformat()

    session["analysis_results"] = results
    session["analysis_status"] = "completed"


def extract_statistics(phases: dict) -> dict:
    """Extract summary statistics from phase results."""
    stats = {
        "equipment": 0,
        "valves": 0,
        "instruments": 0,
        "piping_lines": 0,
        "notes": 0,
    }

    if "phase4_equipment_scan" in phases:
        r = phases["phase4_equipment_scan"].get("result", {})
        if isinstance(r, list):
            stats["equipment"] = len(r)
        elif isinstance(r, dict):
            stats["equipment"] = len(r.get("equipment", []))

    if "phase5_valve_analysis" in phases:
        r = phases["phase5_valve_analysis"].get("result", {})
        stats["valves"] = r.get("GRAND TOTAL", 0) or r.get("total", 0)

    if "phase6_instrumentation" in phases:
        r = phases["phase6_instrumentation"].get("result", {})
        stats["instruments"] = r.get("total", 0)

    if "phase3_notes_extraction" in phases:
        r = phases["phase3_notes_extraction"].get("result", {})
        if isinstance(r, list):
            stats["notes"] = len(r)
        elif isinstance(r, dict):
            stats["notes"] = len(r.get("notes", []))

    return stats


@app.get("/api/status/{session_id}")
async def get_status(session_id: str):
    """Get analysis status and progress."""

    if session_id not in ANALYSIS_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    session = ANALYSIS_SESSIONS[session_id]

    return {
        "session_id": session_id,
        "status": session["analysis_status"],
        "progress": session.get("analysis_progress"),
        "has_results": session["analysis_results"] is not None,
    }


@app.get("/api/results/{session_id}")
async def get_results(session_id: str):
    """Get analysis results."""

    if session_id not in ANALYSIS_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    session = ANALYSIS_SESSIONS[session_id]

    if session["analysis_results"] is None:
        raise HTTPException(status_code=400, detail="Analysis not completed yet")

    return session["analysis_results"]


@app.post("/api/query")
async def query_pid(request: QueryRequest):
    """Ask a question about the analyzed P&ID."""

    if request.session_id not in ANALYSIS_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    session = ANALYSIS_SESSIONS[request.session_id]

    if session["analysis_results"] is None:
        raise HTTPException(status_code=400, detail="Complete analysis first")

    # Build context from analysis results (truncate to avoid token limits)
    analysis_summary = json.dumps(session["analysis_results"]["phases"], indent=2)
    if len(analysis_summary) > 60000:
        analysis_summary = analysis_summary[:60000] + "\n... (truncated)"

    prompt = f"""You are a SENIOR P&ID ENGINEER.

ANALYZED DATA FROM THIS P&ID:
{analysis_summary}

ENGINEERING KNOWLEDGE:
{json.dumps(PID_ENGINEERING_KNOWLEDGE, indent=2)}

USER QUESTION: {request.question}

Provide an expert engineering answer with specific tag numbers and values.
If counting items, list each one.
If explaining symbols, reference ISA-5.1 standards."""

    try:
        response = await gemini_service.analyze_image(
            image_base64=session["image_base64"],
            mime_type=session["mime_type"],
            prompt=prompt,
        )

        return {
            "question": request.question,
            "answer": response,
            "session_id": request.session_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/api/export/{session_id}")
async def export_results(session_id: str):
    """Export analysis results as JSON file."""

    if session_id not in ANALYSIS_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    session = ANALYSIS_SESSIONS[session_id]

    if session["analysis_results"] is None:
        raise HTTPException(status_code=400, detail="No results to export")

    return JSONResponse(
        content=session["analysis_results"],
        headers={
            "Content-Disposition": f"attachment; filename=pid_analysis_{session_id}.json"
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
