"""
Gemini Vision API integration for P&ID analysis.
Includes 11-phase expert analysis prompts with strict JSON output schemas,
retry logic, and robust response parsing.
"""

import aiohttp
import json
import re
import os
import asyncio

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY", "AIzaSyCKBOJHBU3f5VKxb7RdrKhD2xJ2gRUwADk"
)
GEMINI_VISION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# ──────────────────────────────────────────────────────────────────────────────
# Every prompt now ends with an exact JSON schema the model MUST return.
# This eliminates the ambiguity that caused 0-count statistics.
# ──────────────────────────────────────────────────────────────────────────────

EXPERT_ANALYSIS_PHASES = {
    "phase1_document_context": """You are a SENIOR P&ID ENGINEER with 25+ years of experience reading industrial Piping & Instrumentation Diagrams.

PHASE 1: DOCUMENT IDENTIFICATION — Be extremely precise.

Examine EVERY part of the drawing. Look at:
- Title block (usually bottom-right corner)
- Data blocks, revision blocks, stamp areas
- Drawing borders and margin text
- Any text anywhere on the sheet

Extract:
1. TITLE BLOCK: Drawing Number, Sheet Number, Revision, Title/Description, Project/Plant Name, Company/Client, Date, Area/Unit
2. DESIGN DATA: Design Pressure & units, Design Temperature & units, MAOP, Design Code (ASME/API/etc.), Service description, Material/Grade, Flange Rating, Flow Rate
3. REFERENCES: Other P&ID drawing numbers referenced (continuations, tie-ins), Standards mentioned (SAES, ASME, API, ISO, etc.)

If a field is not visible or not present, use null. If text is partially readable, prefix with "[partial]".

YOU MUST RETURN ONLY THIS JSON (no other text):
```json
{
  "title_block": {
    "drawing_number": "",
    "sheet_number": "",
    "revision": "",
    "title": "",
    "project_name": "",
    "company": "",
    "date": "",
    "area_unit": ""
  },
  "design_data": {
    "design_pressure": "",
    "design_temperature": "",
    "maop": "",
    "design_code": "",
    "service": "",
    "material_grade": "",
    "flange_rating": "",
    "flow_rate": ""
  },
  "references": {
    "other_pids": [],
    "standards": []
  }
}
```""",

    "phase2_legend_symbols": """You are a SENIOR P&ID ENGINEER.

PHASE 2: LEGEND & SYMBOL EXTRACTION

Carefully scan the ENTIRE drawing for:
1. A legend/symbol key area (often on the left side, bottom, or a separate section)
2. Valve symbols used — describe each one you see and what it represents
3. Instrument symbols — circles, squares, hexagons, with/without lines
4. Line types — solid, dashed, dotted, thick, thin
5. Abbreviations defined on the drawing (NC, NO, LO, LC, D, V, SC, etc.)
6. Any special symbols or notations unique to this drawing

If NO legend section exists, state that and infer from ISA/ISO standards based on symbols you see in the drawing.

YOU MUST RETURN ONLY THIS JSON:
```json
{
  "has_legend": true,
  "valve_symbols": [
    {"type": "Gate Valve", "description": "Two triangles meeting at points", "seen_on_drawing": true}
  ],
  "instrument_symbols": [
    {"type": "Local field mounted", "shape": "Plain circle", "seen_on_drawing": true}
  ],
  "line_types": [
    {"type": "Process line", "appearance": "Thick solid line", "seen_on_drawing": true}
  ],
  "abbreviations": [
    {"abbr": "NC", "meaning": "Normally Closed"}
  ],
  "special_symbols": []
}
```""",

    "phase3_notes_extraction": """You are a SENIOR P&ID ENGINEER.

PHASE 3: ENGINEERING NOTES — WORD FOR WORD EXTRACTION

This is CRITICAL. Notes contain vital safety and design information.

Scan the ENTIRE drawing for notes. They are typically found:
- In a notes section (numbered list, often left side or bottom)
- Near specific equipment (local notes)
- In the title block area
- General notes, warnings, cautions anywhere

For EACH note:
- Copy the EXACT text word-for-word. Do NOT paraphrase.
- If a note says "DELETED", record it as deleted.
- If text is partially visible, mark with "[partial]".

Also extract any referenced standards (SAES-xxx, ASME, API, etc.)

YOU MUST RETURN ONLY THIS JSON:
```json
{
  "notes": [
    {
      "note_number": "1",
      "full_text": "Exact word-for-word text of the note",
      "category": "DESIGN",
      "referenced_standards": ["ASME B31.3"]
    }
  ],
  "general_notes": [],
  "warnings": [],
  "total_notes_count": 0
}
```
Categories: DESIGN, SAFETY, MATERIAL, CONSTRUCTION, REFERENCE, DELETED""",

    "phase4_equipment_scan": """You are a SENIOR P&ID ENGINEER.

PHASE 4: EQUIPMENT IDENTIFICATION — SYSTEMATIC SCAN

Scan the ENTIRE drawing systematically from LEFT to RIGHT, TOP to BOTTOM.
Look for ALL equipment symbols including:
- Vessels, Drums, Accumulators (cylindrical shapes)
- Tanks (rectangular/cylindrical with flat top)
- Heat Exchangers (shell & tube symbol, plate, air coolers)
- Pumps (circle with arrow/triangle)
- Compressors (circle with inlet/outlet)
- Columns/Towers (tall cylindrical with trays)
- Reactors
- Filters/Strainers (Y-shape or basket symbol)
- Scraper Traps (Launcher/Receiver — barrel shapes)
- Any other process equipment

For EACH piece of equipment, record the tag number EXACTLY as shown.

YOU MUST RETURN ONLY THIS JSON:
```json
{
  "equipment": [
    {
      "tag_number": "V-101",
      "equipment_type": "Vessel",
      "size_rating": "",
      "service": "",
      "design_conditions": "",
      "connected_to": [],
      "location_on_drawing": "left-center",
      "applicable_notes": []
    }
  ],
  "total_equipment_count": 0
}
```""",

    "phase5_valve_analysis": """You are a SENIOR P&ID ENGINEER. This is the MOST CRITICAL phase.

PHASE 5: VALVE ANALYSIS — SYMBOL-BY-SYMBOL IDENTIFICATION

METHODOLOGY — Follow this EXACT procedure:
1. Start at the LEFT side of the drawing
2. Follow EACH process line from left to right
3. At EVERY valve symbol, STOP and record it
4. Then scan ALL utility lines (IA, N2, ST, CW, drain, vent)
5. Then scan ALL small branch connections
6. Do NOT miss small valves on drain/vent stubs (these are commonly overlooked)

VALVE SYMBOL RECOGNITION GUIDE:
- Gate Valve: Two triangles meeting at points (bowtie shape)
- Globe Valve: Two triangles with a circle between them
- Ball Valve: Two triangles with filled/solid circle
- Plug Valve: Two triangles with rectangle between
- Butterfly Valve: Two triangles with vertical line through center
- Check Valve: Triangle pointing in flow direction with a bar/stop
- Control Valve: Globe valve shape with actuator (diaphragm) on top
- Relief/Safety Valve: Angle body with spring symbol, usually on a branch
- Needle Valve: Very small, tapered symbol
- 3-Way Valve: Three-port connection symbol

For EACH valve record: tag number (or assign VALVE-001, VALVE-002 if untagged), type, actuator type (Manual/MOV/Pneumatic/Solenoid/Hydraulic/Gear), normal position (NC/NO/LC/LO), fail position (FC/FO/FL), size, which line it is on.

YOU MUST RETURN ONLY THIS JSON:
```json
{
  "valves": [
    {
      "tag_number": "",
      "valve_type": "Gate",
      "actuator_type": "Manual",
      "normal_position": "",
      "fail_position": "",
      "size": "",
      "line_number": "",
      "location_description": "",
      "reference_notes": []
    }
  ],
  "count_by_type": {
    "gate": 0,
    "globe": 0,
    "ball": 0,
    "plug": 0,
    "butterfly": 0,
    "check": 0,
    "control": 0,
    "mov": 0,
    "relief_safety": 0,
    "needle": 0,
    "other": 0
  },
  "total_valve_count": 0
}
```""",

    "phase6_instrumentation": """You are a SENIOR P&ID ENGINEER.

PHASE 6: INSTRUMENTATION — DECODE EVERY TAG USING ISA-5.1

Scan for ALL instrument bubbles (circles, squares, hexagons, diamonds) on the drawing.

ISA-5.1 TAG DECODING:
- First Letter = Measured Variable: F=Flow, L=Level, P=Pressure, T=Temperature, A=Analysis, X=Unclassified(H2S/LEL), etc.
- Succeeding Letters = Functions: I=Indicator, T=Transmitter, C=Controller, S=Switch, A=Alarm, E=Element, G=Gauge, R=Recorder, V=Valve, H=High, L=Low, etc.

Example: "PIT-0210" → P=Pressure, I=Indicator, T=Transmitter, Loop 0210
Example: "LAHH-0501" → L=Level, A=Alarm, H=High, H=High (Level Alarm High-High)

MOUNTING TYPE from symbol shape:
- Plain Circle = Local field mounted
- Circle with horizontal line through middle = Panel/board mounted
- Circle with vertical line through middle = DCS accessible
- Square = PLC/Safety system (SIS)
- Hexagon = Field auxiliary
- Diamond = Computer/shared display

For EACH instrument, decode the tag completely.

YOU MUST RETURN ONLY THIS JSON:
```json
{
  "instruments": [
    {
      "tag_number": "PIT-0210",
      "decoded": {
        "measured_variable": "Pressure",
        "functions": ["Indicator", "Transmitter"],
        "loop_number": "0210"
      },
      "instrument_type": "Transmitter",
      "mounting_type": "DCS accessible",
      "range": "",
      "setpoints": {"H": "", "HH": "", "L": "", "LL": ""},
      "connected_to_system": "DCS",
      "measures_on": "Line or equipment tag"
    }
  ],
  "count_by_category": {
    "pressure": 0,
    "temperature": 0,
    "flow": 0,
    "level": 0,
    "analysis": 0,
    "other": 0
  },
  "total_instrument_count": 0
}
```""",

    "phase7_piping_analysis": """You are a SENIOR P&ID ENGINEER.

PHASE 7: PIPING LINE ANALYSIS — TRACE EACH LINE

For EVERY piping line visible on the P&ID, decode its line number.

LINE NUMBER FORMAT (typical): "SIZE-SERVICE-NUMBER-SPEC"
Example: 24"-P-0001-3CS1P06
- 24" = Nominal Pipe Size
- P = Service Code (Process)
- 0001 = Sequential number
- 3CS1P06 = Piping Spec/Class

SERVICE CODES: P=Process, BD=Blowdown, RL=Relief, FL=Flare, FG=Fuel Gas, IA=Instrument Air, PA=Plant Air, N2=Nitrogen, ST=Steam, CW=Cooling Water, BW=Boiler Water, FW=Firewater, UW=Utility Water, OW=Oily Water, CD=Condensate, DR=Drain

For each line trace: FROM (origin) → TO (destination), list all valves and instruments on it, note any reducers, orifice plates, spectacle blinds.

YOU MUST RETURN ONLY THIS JSON:
```json
{
  "piping_lines": [
    {
      "line_number": "24\"-P-0001-3CS1P06",
      "size": "24\"",
      "service_code": "P",
      "service_description": "Process",
      "piping_spec": "3CS1P06",
      "from": "",
      "to": "",
      "flow_direction": "",
      "valves_on_line": [],
      "instruments_on_line": [],
      "special_items": [],
      "connections_to_other_pids": []
    }
  ],
  "total_line_count": 0
}
```""",

    "phase8_connections_flow": """You are a SENIOR P&ID ENGINEER.

PHASE 8: PROCESS FLOW & CONNECTION MAPPING

A. MAIN PROCESS FLOW: Trace the primary flow path from where it enters the drawing to where it exits. List equipment in sequence.

B. SECONDARY FLOWS: Bypass lines, recycle streams, sample points, vent lines, drain lines.

C. UTILITY CONNECTIONS: Instrument Air (IA), Nitrogen (N2), Steam (ST), Cooling Water (CW), Utility Water (UW), Chemical Injection.

D. RELIEF/SAFETY PATHS: Where do relief valves discharge to? (Flare, atmosphere, blowdown drum)

E. DRAIN SYSTEM: Process drains, utility drains, open vs closed drain.

F. REFERENCE DRAWINGS: List all other drawing numbers referenced as continuations or tie-ins.

YOU MUST RETURN ONLY THIS JSON:
```json
{
  "main_process_flow": {
    "entry_point": "",
    "entry_from_drawing": "",
    "equipment_sequence": [],
    "exit_point": "",
    "exit_to_drawing": ""
  },
  "secondary_flows": {
    "bypass_lines": [],
    "recycle_streams": [],
    "sample_points": [],
    "vent_lines": [],
    "drain_lines": []
  },
  "utility_connections": {
    "instrument_air": [],
    "nitrogen": [],
    "steam": [],
    "cooling_water": [],
    "utility_water": [],
    "chemical_injection": []
  },
  "relief_paths": [],
  "drain_system": {
    "process_drains": [],
    "utility_drains": [],
    "drain_destination": ""
  },
  "reference_drawings": [
    {"drawing_number": "", "description": "", "connection_type": ""}
  ],
  "tie_in_points": []
}
```""",

    "phase9_safety_analysis": """You are a SENIOR P&ID ENGINEER.

PHASE 9: SAFETY SYSTEMS & HAZARD ANALYSIS

A. AREA CLASSIFICATION: Look for Class I/II/III, Division 1/2, Zone 0/1/2 markings.

B. GAS DETECTION: Find all gas detectors (H2S, LEL, CO, O2). They typically have tags starting with X (XA, XT) or A (AT, AIT). Record tag, type, alarm setpoints.

C. EMERGENCY SHUTDOWN (ESD): Find ESD valves (XV, SDV tags), ESD pushbuttons, interlock references.

D. PRESSURE RELIEF DEVICES: Find all PSV, PRV, RV tags. Record set pressure, protected equipment, discharge destination.

E. SAFETY INTERLOCKS: Any interlock logic references, cause & effect references.

F. FIRE PROTECTION: Deluge valves, fire monitors, firewater connections.

YOU MUST RETURN ONLY THIS JSON:
```json
{
  "area_classification": {
    "class": "",
    "division_or_zone": "",
    "details": ""
  },
  "gas_detectors": [
    {
      "tag_number": "",
      "type": "H2S",
      "alarm_h": "",
      "alarm_hh": "",
      "location": "",
      "connected_to": ""
    }
  ],
  "esd_system": {
    "esd_valves": [],
    "esd_pushbuttons": [],
    "interlock_references": []
  },
  "relief_devices": [
    {
      "tag_number": "",
      "protected_equipment": "",
      "set_pressure": "",
      "discharge_to": "",
      "sizing_basis": ""
    }
  ],
  "safety_interlocks": [],
  "fire_protection": [],
  "safety_related_notes": [],
  "total_gas_detectors": 0,
  "total_relief_devices": 0,
  "total_esd_valves": 0
}
```""",

    "phase10_verification_summary": """You are a SENIOR P&ID ENGINEER.

PHASE 10: VERIFICATION & COMPREHENSIVE SUMMARY

Go through the ENTIRE drawing one more time and compile final verified counts.
Count every single item carefully. Do not estimate — count precisely.

For the statistics, go through the drawing region by region:
- Top-left, top-center, top-right
- Middle-left, middle-center, middle-right
- Bottom-left, bottom-center, bottom-right

Count each valve symbol, each instrument bubble, each equipment item, each line number.

YOU MUST RETURN ONLY THIS JSON:
```json
{
  "verified_counts": {
    "total_equipment": 0,
    "total_valves": 0,
    "valve_breakdown": {
      "gate": 0,
      "globe": 0,
      "ball": 0,
      "plug": 0,
      "butterfly": 0,
      "check": 0,
      "control": 0,
      "mov": 0,
      "relief_safety": 0,
      "needle": 0,
      "other": 0
    },
    "total_instruments": 0,
    "instrument_breakdown": {
      "pressure": 0,
      "temperature": 0,
      "flow": 0,
      "level": 0,
      "analysis": 0,
      "other": 0
    },
    "total_piping_lines": 0,
    "total_notes": 0,
    "deleted_notes": 0
  },
  "design_data_summary": {
    "pipeline_size": "",
    "service": "",
    "maop": "",
    "design_pressure": "",
    "design_temperature": "",
    "material": "",
    "flange_rating": "",
    "design_code": ""
  },
  "critical_safety_items": {
    "esd_valves": [],
    "relief_devices": [],
    "gas_detectors": [],
    "critical_alarms": []
  },
  "gaps_uncertainties": []
}
```""",

    "phase11_reverification": """You are a SENIOR P&ID ENGINEER performing a FINAL QUALITY CHECK.

PHASE 11: CRITICAL RE-VERIFICATION PASS

The previous analysis counted {previous_valve_count} valves. Now go through the drawing ONE MORE TIME and independently verify:

A. RE-COUNT ALL VALVES: Go left-to-right through every line. Count each valve symbol individually. If your count differs from {previous_valve_count}, list what was missed or double-counted.

B. RE-VERIFY GAS DETECTION: Count H2S and LEL detectors separately. Confirm setpoints.

C. RE-VERIFY CRITICAL NOTES: Re-read notes 1-5 (at minimum) word-for-word. Re-read any safety-related notes.

D. RE-VERIFY DESIGN CONDITIONS: Confirm MAOP, design temperature, design code values.

E. RE-VERIFY LINE NUMBERS: Confirm main process line number and at least 3 other important line numbers.

F. List any CORRECTIONS to previous phases.

YOU MUST RETURN ONLY THIS JSON:
```json
{{
  "valve_recount": {{
    "previous_count": {previous_valve_count},
    "new_count": 0,
    "discrepancy_notes": ""
  }},
  "gas_detection_verification": {{
    "h2s_detector_count": 0,
    "lel_detector_count": 0,
    "setpoints_confirmed": true
  }},
  "critical_notes_reverified": [
    {{"note_number": "1", "text_confirmed": ""}}
  ],
  "design_conditions_confirmed": {{
    "maop": "",
    "design_temperature": "",
    "design_code": ""
  }},
  "line_numbers_confirmed": [],
  "corrections": [
    {{"item": "", "was": "", "should_be": ""}}
  ],
  "final_confidence_percent": 0
}}
```""",
}


class GeminiVisionService:

    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key
        self.url = f"{GEMINI_VISION_URL}?key={api_key}"

    async def analyze_image(
        self,
        image_base64: str,
        mime_type: str,
        prompt: str,
        max_retries: int = 2,
    ) -> str:
        """Send image to Gemini Vision API with retry logic."""

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_base64,
                            }
                        },
                        {"text": prompt},
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.05,
                "topK": 20,
                "topP": 0.9,
                "maxOutputTokens": 32768,
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ],
        }

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=120),
                    ) as response:
                        if response.status == 429:
                            wait = 3 * (attempt + 1)
                            await asyncio.sleep(wait)
                            continue

                        if response.status != 200:
                            error_data = await response.json()
                            raise Exception(
                                f"Gemini API Error ({response.status}): "
                                f"{error_data.get('error', {}).get('message', 'Unknown error')}"
                            )

                        data = await response.json()

                        if data.get("candidates") and data["candidates"][0].get("content"):
                            return data["candidates"][0]["content"]["parts"][0]["text"]

                        raise Exception("Invalid response structure from Gemini API")

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_error = e
                if attempt < max_retries:
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                raise Exception(f"Network error after {max_retries + 1} attempts: {last_error}")

        raise Exception(f"Failed after {max_retries + 1} attempts: {last_error}")

    def parse_response(self, response: str) -> dict:
        """
        Robustly parse JSON from Gemini response.
        Handles markdown code blocks, raw JSON, and nested structures.
        """
        # Strategy 1: Extract from ```json ... ``` blocks
        json_match = re.search(r"```json\s*([\s\S]*?)\s*```", response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Strategy 2: Extract from ``` ... ``` blocks (no json tag)
        json_match = re.search(r"```\s*([\s\S]*?)\s*```", response)
        if json_match:
            text = json_match.group(1).strip()
            if text.startswith("{") or text.startswith("["):
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    pass

        # Strategy 3: Find the largest JSON object in the response
        best = None
        best_len = 0
        for m in re.finditer(r"\{", response):
            start = m.start()
            depth = 0
            i = start
            while i < len(response):
                if response[i] == "{":
                    depth += 1
                elif response[i] == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = response[start : i + 1]
                        if len(candidate) > best_len:
                            try:
                                parsed = json.loads(candidate)
                                best = parsed
                                best_len = len(candidate)
                            except json.JSONDecodeError:
                                pass
                        break
                i += 1

        if best is not None:
            return best

        # Strategy 4: Try the whole response as JSON
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass

        return {"raw_text": response}
