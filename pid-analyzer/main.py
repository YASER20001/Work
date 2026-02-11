"""
P&ID Vision Analyzer - FastAPI Application
Expert-level P&ID analysis using Gemini Vision AI with 11-phase pipeline.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
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
from services.excel_export import generate_equipment_list, generate_valve_list, generate_line_list

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

ANALYSIS_SESSIONS: Dict[str, dict] = {}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Helpers for deep JSON value extraction ──


def _deep_find_int(obj, keys, default=0):
    """
    Search a nested dict/list for the first integer value matching any of the
    given keys. This handles any JSON structure Gemini might return.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            k_lower = k.lower().replace(" ", "_").replace("-", "_")
            for target in keys:
                if k_lower == target.lower():
                    if isinstance(v, (int, float)):
                        return int(v)
                    if isinstance(v, str):
                        try:
                            return int(v)
                        except ValueError:
                            pass
            # Recurse
            result = _deep_find_int(v, keys, None)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = _deep_find_int(item, keys, None)
            if result is not None:
                return result
    return default


def _deep_find_list(obj, keys):
    """Find the first list value matching any of the given keys."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            k_lower = k.lower().replace(" ", "_").replace("-", "_")
            for target in keys:
                if k_lower == target.lower():
                    if isinstance(v, list):
                        return v
            result = _deep_find_list(v, keys)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = _deep_find_list(item, keys)
            if result is not None:
                return result
    return None


# ── Routes ──


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
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

            # Extract valve count for re-verification phase
            if phase_key == "phase5_valve_analysis":
                vc = _deep_find_int(parsed, [
                    "total_valve_count", "grand_total", "total",
                    "total_valves",
                ])
                # Fallback: count items in valves array
                if vc == 0:
                    valves_list = _deep_find_list(parsed, ["valves"])
                    if valves_list:
                        vc = len(valves_list)
                context["valve_count"] = vc

            # Rate limit delay
            await asyncio.sleep(2)

        except Exception as e:
            results["errors"].append({"phase": phase_key, "error": str(e)})
            results["confidence"] -= 10

    results["statistics"] = extract_statistics(results["phases"])
    results["confidence"] = max(0, results["confidence"])
    results["end_time"] = datetime.now().isoformat()

    session["analysis_results"] = results
    session["analysis_status"] = "completed"


def extract_statistics(phases: dict) -> dict:
    """
    Extract summary statistics from phase results using deep search.
    This handles any JSON structure Gemini returns.
    """
    stats = {
        "equipment": 0,
        "valves": 0,
        "instruments": 0,
        "piping_lines": 0,
        "notes": 0,
        "gas_detectors": 0,
        "relief_devices": 0,
        "esd_valves": 0,
    }

    # ── Equipment (Phase 4) ──
    if "phase4_equipment_scan" in phases:
        r = phases["phase4_equipment_scan"].get("result", {})
        count = _deep_find_int(r, ["total_equipment_count", "total_equipment", "total"])
        if count == 0:
            eq_list = _deep_find_list(r, ["equipment"])
            if eq_list:
                count = len(eq_list)
        stats["equipment"] = count

    # ── Valves (Phase 5) ──
    if "phase5_valve_analysis" in phases:
        r = phases["phase5_valve_analysis"].get("result", {})
        count = _deep_find_int(r, [
            "total_valve_count", "grand_total", "total_valves", "total",
        ])
        if count == 0:
            v_list = _deep_find_list(r, ["valves"])
            if v_list:
                count = len(v_list)
        stats["valves"] = count

    # ── Instruments (Phase 6) ──
    if "phase6_instrumentation" in phases:
        r = phases["phase6_instrumentation"].get("result", {})
        count = _deep_find_int(r, [
            "total_instrument_count", "total_instruments", "total",
        ])
        if count == 0:
            i_list = _deep_find_list(r, ["instruments"])
            if i_list:
                count = len(i_list)
        stats["instruments"] = count

    # ── Piping Lines (Phase 7) ──
    if "phase7_piping_analysis" in phases:
        r = phases["phase7_piping_analysis"].get("result", {})
        count = _deep_find_int(r, [
            "total_line_count", "total_piping_lines", "total_lines", "total",
        ])
        if count == 0:
            l_list = _deep_find_list(r, ["piping_lines", "lines"])
            if l_list:
                count = len(l_list)
        stats["piping_lines"] = count

    # ── Notes (Phase 3) ──
    if "phase3_notes_extraction" in phases:
        r = phases["phase3_notes_extraction"].get("result", {})
        count = _deep_find_int(r, ["total_notes_count", "total_notes", "total"])
        if count == 0:
            n_list = _deep_find_list(r, ["notes"])
            if n_list:
                count = len(n_list)
        stats["notes"] = count

    # ── Safety (Phase 9) ──
    if "phase9_safety_analysis" in phases:
        r = phases["phase9_safety_analysis"].get("result", {})
        stats["gas_detectors"] = _deep_find_int(r, [
            "total_gas_detectors",
        ])
        if stats["gas_detectors"] == 0:
            gd_list = _deep_find_list(r, ["gas_detectors"])
            if gd_list:
                stats["gas_detectors"] = len(gd_list)

        stats["relief_devices"] = _deep_find_int(r, ["total_relief_devices"])
        if stats["relief_devices"] == 0:
            rd_list = _deep_find_list(r, ["relief_devices"])
            if rd_list:
                stats["relief_devices"] = len(rd_list)

        stats["esd_valves"] = _deep_find_int(r, ["total_esd_valves"])

    # ── Use Phase 10 verified counts as override if available ──
    if "phase10_verification_summary" in phases:
        r10 = phases["phase10_verification_summary"].get("result", {})
        verified = r10.get("verified_counts", r10)

        for stat_key, search_keys in [
            ("equipment", ["total_equipment"]),
            ("valves", ["total_valves"]),
            ("instruments", ["total_instruments"]),
            ("piping_lines", ["total_piping_lines"]),
            ("notes", ["total_notes"]),
        ]:
            v = _deep_find_int(verified, search_keys)
            if v > 0:
                stats[stat_key] = v

    return stats


@app.get("/api/status/{session_id}")
async def get_status(session_id: str):
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
    if session_id not in ANALYSIS_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    session = ANALYSIS_SESSIONS[session_id]

    if session["analysis_results"] is None:
        raise HTTPException(status_code=400, detail="Analysis not completed yet")

    return session["analysis_results"]


@app.post("/api/query")
async def query_pid(request: QueryRequest):
    if request.session_id not in ANALYSIS_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    session = ANALYSIS_SESSIONS[request.session_id]

    if session["analysis_results"] is None:
        raise HTTPException(status_code=400, detail="Complete analysis first")

    # Build a focused context from the parsed results (not raw text)
    phase_summaries = {}
    for phase_key, phase_data in session["analysis_results"]["phases"].items():
        phase_summaries[phase_key] = phase_data.get("result", {})

    context_json = json.dumps(phase_summaries, indent=2)
    if len(context_json) > 80000:
        context_json = context_json[:80000] + "\n... (truncated)"

    prompt = f"""You are a SENIOR P&ID ENGINEER answering questions about an analyzed P&ID drawing.

COMPLETE ANALYSIS DATA:
{context_json}

ENGINEERING KNOWLEDGE BASE:
{json.dumps(PID_ENGINEERING_KNOWLEDGE, indent=2)}

USER QUESTION: {request.question}

INSTRUCTIONS:
- Provide a precise, expert-level engineering answer
- Reference specific tag numbers, line numbers, and values from the analysis data
- If counting items, list each one individually
- If explaining instrument tags, decode using ISA-5.1
- If the information is not in the analysis data, say so and explain what would be needed
- Format your answer clearly with sections if needed"""

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


def _get_excel_session(session_id: str):
    """Validate session and return analysis results for Excel export."""
    if session_id not in ANALYSIS_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    session = ANALYSIS_SESSIONS[session_id]
    if session["analysis_results"] is None:
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    return session


@app.get("/api/export/{session_id}/equipment-list")
async def export_equipment_list(session_id: str):
    session = _get_excel_session(session_id)
    filename = f"Mechanical_Equipment_List_{session['filename'].rsplit('.', 1)[0]}.xlsx"
    output = generate_equipment_list(session["analysis_results"])
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/export/{session_id}/valve-list")
async def export_valve_list(session_id: str):
    session = _get_excel_session(session_id)
    filename = f"Valve_List_{session['filename'].rsplit('.', 1)[0]}.xlsx"
    output = generate_valve_list(session["analysis_results"])
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/export/{session_id}/line-list")
async def export_line_list(session_id: str):
    session = _get_excel_session(session_id)
    filename = f"Line_List_{session['filename'].rsplit('.', 1)[0]}.xlsx"
    output = generate_line_list(session["analysis_results"])
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
