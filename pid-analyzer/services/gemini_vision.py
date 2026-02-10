"""
Gemini Vision API integration for P&ID analysis.
Includes 11-phase expert analysis prompts and API communication.
"""

import aiohttp
import json
import re
import os

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY", "AIzaSyCKBOJHBU3f5VKxb7RdrKhD2xJ2gRUwADk"
)
GEMINI_VISION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

EXPERT_ANALYSIS_PHASES = {
    "phase1_document_context": """You are a SENIOR P&ID ENGINEER with 25+ years experience.

PHASE 1: DOCUMENT IDENTIFICATION (Be extremely precise)

Examine the title block (usually bottom right) and extract:

1. **TITLE BLOCK**:
   - Drawing Number (exact alphanumeric)
   - Sheet Number
   - Revision (letter or number)
   - Title/Description
   - Project/Plant Name
   - Company Name
   - Date
   - Area Classification

2. **DESIGN DATA** (look for data block):
   - Design Pressure & units
   - Design Temperature & units
   - MAOP (Maximum Allowable Operating Pressure)
   - Design Code (ASME, API, etc.)
   - Service (Sour Gas, Sweet Gas, Oil, etc.)
   - Material/Grade
   - Flange Rating (150#, 300#, 600#)
   - Flow Rate

3. **REFERENCES**:
   - Other P&IDs referenced
   - Standards mentioned (SAES, ASME, API, etc.)

Return as structured JSON. If text unclear, mark as "[unclear]".""",
    "phase2_legend_symbols": """PHASE 2: LEGEND & SYMBOL EXTRACTION

Find and extract ALL symbol definitions from the drawing:

1. **VALVE SYMBOLS** - Describe exact appearance of each:
   - Gate Valve symbol
   - Globe Valve symbol
   - Ball Valve symbol
   - Check Valve symbol
   - Control Valve symbol
   - MOV (Motor Operated Valve) symbol
   - Relief/Safety Valve symbol

2. **INSTRUMENT SYMBOLS**:
   - Local mounted (circle)
   - Panel mounted (circle with horizontal line)
   - DCS connected (circle with vertical line)
   - PLC connected (square)
   - Field mounted (hexagon)

3. **LINE TYPES**:
   - Process line (thick solid)
   - Instrument signal (thin solid)
   - Electrical signal (dashed)
   - Software/data link (dotted)

4. **ABBREVIATIONS DEFINED**:
   - NC, NO, LO, LC meanings
   - D (Drain), V (Vent), SC (Sample Connection)
   - All others shown in legend

If NO legend exists, state "NO LEGEND FOUND - Using ISA/ISO standards"
Return as JSON.""",
    "phase3_notes_extraction": """PHASE 3: ENGINEERING NOTES - WORD FOR WORD EXTRACTION

CRITICAL: Notes contain vital safety and design information. Extract EVERY note with 100% accuracy.

For EACH note on the P&ID:
1. **Note Number** (exactly as shown: 1, 2, Note 1, etc.)
2. **Complete Text** - WORD FOR WORD transcription, DO NOT PARAPHRASE OR SUMMARIZE
3. **Category**: Classify as:
   - DESIGN: Sizing, calculations, design basis
   - SAFETY: Safety requirements, interlocks
   - MATERIAL: Material specifications
   - CONSTRUCTION: Installation requirements
   - REFERENCE: References to other documents
   - DELETED: Notes marked as deleted

Also extract:
- Referenced standards (SAES-xxx, ASME, API, etc.)
- General notes (unnumbered)
- Warnings/cautions

If note says "DELETED" record as: "Note X: DELETED"
If text partially visible: "[partially visible: visible text...]"

Return as JSON array with: noteNumber, fullText, category, referencedStandards""",
    "phase4_equipment_scan": """PHASE 4: EQUIPMENT IDENTIFICATION - SYSTEMATIC SCAN

Scan the ENTIRE drawing systematically from LEFT to RIGHT, TOP to BOTTOM.

For EACH piece of equipment found:

1. **Tag Number** (exact tag, e.g., R11-L-0001, V-101, P-201-A/B)
2. **Equipment Type**:
   - Vessel / Drum / Accumulator
   - Tank (atmospheric storage)
   - Heat Exchanger (shell & tube, plate, air cooler)
   - Pump (centrifugal, positive displacement)
   - Compressor (centrifugal, reciprocating)
   - Column / Tower
   - Reactor
   - Filter / Strainer
   - Scraper Trap (Launcher / Receiver)
   - Other (specify)
3. **Size/Rating** if shown (diameter, capacity, pressure rating)
4. **Service** - what fluid/process it handles
5. **Design Conditions** shown near equipment
6. **Connected To** - inlet/outlet connections
7. **Location on Drawing** (left/center/right, top/middle/bottom)
8. **Applicable Notes** - which notes reference this equipment

Count ALL equipment items. Do not miss any.
Return as JSON array.""",
    "phase5_valve_analysis": """PHASE 5: VALVE ANALYSIS - CRITICAL SYMBOL-BY-SYMBOL IDENTIFICATION

This is a CRITICAL phase requiring maximum attention. Valves are essential for safety and operation.

METHODOLOGY:
1. Start at the left side of the drawing
2. Follow each process line from left to right
3. Identify EVERY valve on each line
4. Then scan utility lines
5. Then scan instrument connections
6. Do NOT miss small valves on drain/vent branches

For EACH VALVE found:

A. **Tag Number** (MOV-0710, XV-101, PCV-201, HV-301)
   - If no tag visible, assign position ID like "VALVE-LINE-001"

B. **Valve Type** (analyze the symbol CAREFULLY):
   - Gate Valve: Two triangles meeting at points
   - Globe Valve: Circle between triangles
   - Ball Valve: Filled circle in line
   - Plug Valve: Rectangle between triangles
   - Butterfly Valve: Triangles with vertical line
   - Check Valve: Triangle pointing in flow direction with bar
   - Control Valve: Globe with diaphragm actuator on top
   - Relief/Safety Valve: Angle body with spring symbol
   - Needle Valve: Small with tapered symbol
   - 3-Way Valve: Three port connections

C. **Actuator Type**:
   - Manual (handwheel symbol or none)
   - Motor Operated (M in circle) = MOV
   - Pneumatic (diaphragm symbol)
   - Solenoid (coil symbol)
   - Hydraulic (H symbol)
   - Gear Operated (G symbol)

D. **Normal Position**:
   - NC = Normally Closed
   - NO = Normally Open
   - LC = Locked Closed
   - LO = Locked Open

E. **Fail Position** (for control/automated valves):
   - FC = Fail Closed
   - FO = Fail Open
   - FL = Fail Last

F. **Size**: Read from line size or explicit marking (1", 2", 4", 24")

G. **Line/Location**: Which line number, near which equipment

H. **Reference Notes**: Which notes apply to this valve

**PROVIDE COUNT SUMMARY**:
- Total Gate Valves: X
- Total Globe Valves: X
- Total Ball Valves: X
- Total Plug Valves: X
- Total Check Valves: X
- Total Control Valves: X
- Total MOVs: X
- Total Relief Valves: X
- Other: X
- **GRAND TOTAL: X**

Return detailed JSON with all valves and count summary.""",
    "phase6_instrumentation": """PHASE 6: INSTRUMENTATION - DECODE EVERY TAG USING ISA-5.1

For EVERY instrument bubble/tag on the P&ID:

A. **Tag Number** (e.g., PI-0210, TIT-0410, PDIS-0101, LAH-0501)

B. **Decode Tag** using ISA-5.1 standard:
   Example: "PIT-0210"
   - P = Pressure (measured variable - first letter)
   - I = Indicator (function)
   - T = Transmitter (function)
   - 0210 = Loop number

   Decode EACH letter:
   - First Letter = Measured variable
   - Succeeding Letters = Functions

C. **Instrument Type**:
   - Indicator (local or remote display)
   - Transmitter (4-20mA, HART, Fieldbus)
   - Controller (PID control)
   - Switch (discrete on/off)
   - Alarm (H, HH, L, LL)
   - Element (sensor)
   - Gauge (local visual)
   - Recorder

D. **Mounting Type** (from symbol shape):
   - Plain Circle = Local field mounted
   - Circle with horizontal line = Panel/board mounted
   - Circle with vertical line = DCS accessible
   - Square = PLC/Safety system
   - Hexagon = Field auxiliary location
   - Diamond = Computer/shared display

E. **Range** if shown (0-800 PSIG, 32-250 deg F, etc.)

F. **Setpoints** for alarms/switches:
   - H (High) setpoint value
   - HH (High-High) setpoint value
   - L (Low) setpoint value
   - LL (Low-Low) setpoint value

G. **Connected to**: DCS? PLC/SIS? Local only?

H. **What it measures**: Which equipment or line

**GROUP BY TYPE**:
- Pressure: PI, PT, PG, PIC, PS, PDI, PDT...
- Temperature: TI, TT, TE, TW, TIC, TS...
- Flow: FI, FT, FE, FIC, FO (orifice)...
- Level: LI, LT, LG, LIC, LS, LA...
- Analyzers: AI, AT, AIT (including H2S, LEL)
- Corrosion: CME, CMT, CMS, CC
- Scraper: SPI, SPIS
- Other: Vibration, Speed, etc.

Return detailed JSON grouped by type with total counts.""",
    "phase7_piping_analysis": """PHASE 7: PIPING LINE ANALYSIS - TRACE EACH LINE

For EVERY piping line on the P&ID:

A. **Line Number Decoding**
   Example: "24"-P-0001-3CS1P06"
   - 24" = Nominal Pipe Size (NPS)
   - P = Service Code (P=Process)
   - 0001 = Sequential line number
   - 3CS1P06 = Piping Specification/Class

B. **Line Properties**:
   1. Size (nominal diameter: 1", 2", 4", 8", 24")
   2. Service Code:
      - P = Process
      - BD = Blowdown
      - RL = Relief
      - FL = Flare
      - IA = Instrument Air
      - N2 = Nitrogen
      - ST = Steam
      - CW = Cooling Water
      - UW = Utility Water
      - DR = Drain
   3. Piping Spec/Class (material and rating indicator)

C. **Line Routing**:
   - FROM: Origin point (equipment tag, drawing reference)
   - TO: Destination point (equipment tag, drawing reference)
   - FLOW DIRECTION: Indicated by arrows?

D. **Components on This Line**:
   - Valves (list all tags)
   - Instruments (list all tags)
   - Reducers (note sizes)
   - Orifice plates
   - Strainers/filters
   - Spectacle blinds

E. **Branches**: What branches off this line?

F. **Connections to Other P&IDs**: Drawing numbers referenced

G. **Special Requirements** (from notes):
   - Insulation
   - Heat tracing
   - Slope requirements
   - Testing requirements

Return JSON with each line traced and a summary table of all lines.""",
    "phase8_connections_flow": """PHASE 8: PROCESS FLOW & CONNECTION MAPPING

A. **MAIN PROCESS FLOW PATH**
   Trace the PRIMARY flow from inlet to outlet:
   1. Where does main process stream ENTER this P&ID? (source/drawing)
   2. What is the flow SEQUENCE through equipment? (list in order)
   3. Where does main process stream EXIT? (destination/drawing)

B. **SECONDARY FLOW PATHS**
   - Bypass lines (around what?)
   - Recycle streams
   - Sample streams
   - Vent streams
   - Drain streams

C. **UTILITY CONNECTIONS**
   1. Instrument Air (IA): Connected to what?
   2. Nitrogen (N2): Purge points, blanketing
   3. Steam (ST): Heating, cleaning
   4. Cooling Water (CW): Where used
   5. Utility Water (UW): Flushing, cleaning
   6. Chemical Injection: What chemical, where injected

D. **RELIEF/SAFETY PATHS**
   1. Relief valves discharge to: Flare? Atmospheric? Blowdown?
   2. Blowdown lines go to: Burn pit? Flare? Closed drain?

E. **DRAIN SYSTEM**
   1. Process drains go to?
   2. Utility drains go to?
   3. Open drains vs closed drains?

F. **REFERENCE DRAWINGS TABLE**
   | Drawing Number | Description | What Connects |
   |----------------|-------------|---------------|

G. **TIE-IN POINTS**: Any tie-ins to existing systems?

Return JSON with all flow paths mapped.""",
    "phase9_safety_analysis": """PHASE 9: SAFETY SYSTEMS & HAZARD ANALYSIS

A. **AREA CLASSIFICATION**
   1. What hazardous area classifications are shown?
      - Class I, II, or III
      - Division 1 or 2
      - Zone 0, 1, or 2
   2. Where are classified areas marked?
   3. What are the boundaries?

B. **GAS DETECTION SYSTEM**
   For EACH gas detector found:
   1. Tag number (XA-0911, AI-0910, etc.)
   2. Type: H2S / LEL / CO / O2
   3. Alarm setpoints:
      - Warning (H) level: X PPM or X% LEL
      - Critical (HH) level: X PPM or X% LEL
   4. Indicator light color (RED for H2S, BLUE for LEL typical)
   5. Physical location
   6. Connected to: DCS? ESD system? Both?

C. **EMERGENCY SHUTDOWN (ESD) SYSTEM**
   1. Emergency shutdown valves: Tags, what they isolate, fail position
   2. ESD pushbuttons/initiators
   3. Interlock logic references

D. **PRESSURE RELIEF DEVICES**
   For EACH relief device:
   1. Tag number (PSV, PRV, RV)
   2. Protected equipment
   3. Set pressure (if shown)
   4. Discharge destination
   5. Sizing basis (from notes)

E. **SAFETY INTERLOCKS**
   List any interlocks shown or referenced:
   - Interlock cause
   - Interlock effect
   - Reference to C&E diagram

F. **FIRE PROTECTION**: Deluge, fire monitors, firewater connections

G. **SAFETY-RELATED NOTES**: List note numbers about safety

Return JSON with complete safety analysis.""",
    "phase10_verification_summary": """PHASE 10: VERIFICATION & COMPREHENSIVE SUMMARY

A. **VERIFICATION CHECKLIST**
   - Document identification complete?
   - All notes extracted (count: ___)?
   - All equipment identified (count: ___)?
   - All valves identified (count: ___)?
   - All instruments identified (count: ___)?
   - All piping lines traced (count: ___)?
   - Flow paths mapped?
   - Safety systems analyzed?

B. **FINAL STATISTICS**
   - Total Equipment Items: X
   - Total Valves: X
     - Gate Valves: X
     - Globe Valves: X
     - Ball Valves: X
     - Check Valves: X
     - Control Valves: X
     - MOVs: X
     - Relief Valves: X
     - Other: X
   - Total Instruments: X
     - Pressure: X
     - Temperature: X
     - Flow: X
     - Level: X
     - Analyzers: X
     - Other: X
   - Total Piping Lines: X
   - Total Notes: X (including X deleted)

C. **KEY DESIGN DATA SUMMARY**
   - Pipeline Size:
   - Service:
   - MAOP:
   - Design Pressure:
   - Design Temperature:
   - Material:
   - Flange Rating:
   - Design Code:

D. **CRITICAL SAFETY ITEMS LIST**
   1. Emergency shutdown valves
   2. Relief devices
   3. Gas detectors
   4. Critical alarms

E. **GAPS/UNCERTAINTIES**: List items that were unclear

Return comprehensive JSON summary.""",
    "phase11_reverification": """PHASE 11: CRITICAL RE-VERIFICATION PASS

Go back through the drawing and DOUBLE-CHECK critical items:

A. **RE-COUNT ALL VALVES**
   - Go through drawing again systematically
   - Count every valve symbol from left to right
   - Previous count was: {previous_valve_count}
   - New count: ___
   - If counts differ, list what was missed or double-counted

B. **RE-VERIFY GAS DETECTION**
   - How many H2S detectors total?
   - How many LEL detectors total?
   - Confirm all setpoints are correctly captured

C. **RE-VERIFY CRITICAL NOTES**
   Read these notes again word-for-word:
   - Any notes about safety
   - Any notes about valve sizing
   - Any notes about valve requirements
   - Note 1 through Note 5 at minimum

D. **RE-VERIFY DESIGN CONDITIONS**
   - MAOP: Confirm value and units
   - Design Temperature: Confirm value and units
   - Design Code: Confirm

E. **RE-VERIFY MAIN LINE NUMBERS**
   - Main process line number
   - At least 3 other important line numbers

F. **CORRECTIONS LIST**
   If any corrections needed:
   - Item:
   - Was:
   - Should be:

Return JSON with verification results and any corrections.""",
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
    ) -> str:
        """Send image to Gemini Vision API for analysis."""

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
                "temperature": 0.1,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 16384,
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(
                        f"Gemini API Error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                    )

                data = await response.json()

                if data.get("candidates") and data["candidates"][0].get("content"):
                    return data["candidates"][0]["content"]["parts"][0]["text"]

                raise Exception("Invalid response structure from Gemini API")

    def parse_response(self, response: str) -> dict:
        """Parse JSON from Gemini response."""

        try:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r"```json\n?([\s\S]*?)\n?```", response)
            if json_match:
                return json.loads(json_match.group(1))

            # Try to find raw JSON object
            json_match = re.search(r"(\{[\s\S]*\})", response)
            if json_match:
                return json.loads(json_match.group(1))

            # Try to find JSON array
            json_match = re.search(r"(\[[\s\S]*\])", response)
            if json_match:
                return json.loads(json_match.group(1))

            # Return raw text if no JSON found
            return {"rawText": response}

        except json.JSONDecodeError:
            return {"rawText": response, "parseError": "Could not parse JSON"}
