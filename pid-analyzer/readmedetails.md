# P&ID Vision Analyzer — Complete Technical Reference

## KBR-AMCDE | Powered by Gemini 2.5 Flash Vision AI | ISA-5.1 Compliant

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [The Idea](#2-the-idea)
3. [System Architecture](#3-system-architecture)
4. [Technology Stack](#4-technology-stack)
5. [The 11-Phase Analysis Pipeline](#5-the-11-phase-analysis-pipeline)
6. [Frontend — Multi-Page SPA](#6-frontend--multi-page-spa)
7. [Backend — FastAPI REST API](#7-backend--fastapi-rest-api)
8. [Services](#8-services)
9. [ISA-5.1 Knowledge Base](#9-isa-51-knowledge-base)
10. [Excel Export Feature](#10-excel-export-feature)
11. [Data Flow & User Journey](#11-data-flow--user-journey)
12. [API Endpoints Reference](#12-api-endpoints-reference)
13. [Data Models & Schemas](#13-data-models--schemas)
14. [Session Management](#14-session-management)
15. [Error Handling & Reliability](#15-error-handling--reliability)
16. [Configuration & Environment](#16-configuration--environment)
17. [File Structure](#17-file-structure)
18. [Dependencies](#18-dependencies)
19. [Running the Application](#19-running-the-application)

---

## 1. Project Overview

The **P&ID Vision Analyzer** is an advanced AI-powered engineering tool that performs comprehensive analysis of Piping and Instrumentation Diagrams (P&IDs). It uses Google's Gemini 2.5 Flash Vision AI to extract, decode, and verify every engineering element from P&ID drawings — equipment, valves, instruments, piping lines, safety devices, engineering notes, and process flow paths.

The system runs an **11-phase sequential analysis pipeline**, where each phase is a specialized expert-level prompt that extracts specific engineering data. The results are presented through a professional **KBR-AMCDE branded multi-page SPA** (Single Page Application) with an executive dashboard, detailed results view, AI engineering assistant, and professional Excel export capabilities.

### Key Capabilities

- Upload and analyze P&ID drawings in PDF, PNG, JPG, or WEBP format
- Automatic PDF-to-image conversion at 300 DPI for maximum detail extraction
- 11-phase deep analysis covering every aspect of a P&ID
- ISA-5.1 standard-compliant instrument tag decoding
- Executive dashboard with KPI cards, donut charts, and data panels
- Natural language Q&A about the analyzed P&ID
- Professional Excel exports: Mechanical Equipment List (KBR format), Valve List (Saudi Aramco 2616-ENG format), Piping Line List
- JSON export of complete analysis results
- Print-optimized dashboard for engineering reports

---

## 2. The Idea

### The Problem

P&ID drawings are among the most information-dense engineering documents in the oil & gas, petrochemical, and process industries. A single P&ID sheet can contain:
- 20–50+ equipment items
- 50–200+ valves of various types
- 30–100+ instruments with ISA-5.1 coded tags
- Dozens of piping lines with service codes, specs, and sizes
- Safety devices (relief valves, ESD valves, gas detectors)
- Engineering notes, design data, and cross-references

Traditionally, extracting this data requires experienced engineers to manually read and catalog every element — a process that takes hours per drawing and is prone to human error, especially for small items like drain valves, vent valves, and instrument taps.

### The Solution

This tool uses **computer vision AI** (Gemini 2.5 Flash) combined with **structured engineering knowledge** (ISA-5.1, valve symbol recognition, piping service codes) to automate P&ID analysis. The 11-phase pipeline ensures thoroughness by:

1. First understanding the document context (title block, design data)
2. Learning the drawing's symbol legend
3. Extracting engineering notes for context
4. Systematically scanning for each category of components
5. Cross-verifying counts and data in a dedicated verification phase
6. Re-verifying critical items (valves, safety devices) in a final pass

The result is a comprehensive, structured dataset that would take an engineer hours to compile manually — delivered in minutes.

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (SPA)                        │
│  ┌──────────┐ ┌───────────┐ ┌─────────┐ ┌───────────┐  │
│  │ Upload & │ │ Executive │ │Detailed │ │    AI     │  │
│  │ Analyze  │ │ Dashboard │ │ Results │ │ Assistant │  │
│  └────┬─────┘ └─────┬─────┘ └────┬────┘ └─────┬─────┘  │
│       │             │            │             │         │
│  ┌────┴─────────────┴────────────┴─────────────┴──────┐  │
│  │              Sidebar Navigation (SPA Router)        │  │
│  └─────────────────────────┬───────────────────────────┘  │
└────────────────────────────┼──────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────┼──────────────────────────────┐
│                    BACKEND (FastAPI)                       │
│  ┌─────────────────────────┴───────────────────────────┐  │
│  │              REST API Endpoints                      │  │
│  │  /api/upload  /api/analyze  /api/status              │  │
│  │  /api/results /api/query   /api/export               │  │
│  └────┬──────────────┬──────────────┬──────────────────┘  │
│       │              │              │                      │
│  ┌────┴────┐  ┌──────┴──────┐  ┌───┴────────────┐        │
│  │  PDF    │  │   Gemini    │  │  Excel Export   │        │
│  │Processor│  │   Vision    │  │  Service        │        │
│  │(PyMuPDF)│  │  Service    │  │  (openpyxl)     │        │
│  └─────────┘  └──────┬──────┘  └────────────────┘        │
│                      │                                    │
│              ┌───────┴──────┐                             │
│              │  ISA-5.1     │                             │
│              │  Knowledge   │                             │
│              │  Base        │                             │
│              └──────────────┘                             │
└───────────────────────┬───────────────────────────────────┘
                        │ HTTPS
              ┌─────────┴──────────┐
              │  Google Gemini     │
              │  2.5 Flash Vision  │
              │  API               │
              └────────────────────┘
```

---

## 4. Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Backend Framework** | FastAPI | 0.109.0 | High-performance async REST API |
| **ASGI Server** | Uvicorn | 0.27.0 | Production-grade ASGI server |
| **AI Vision** | Google Gemini 2.5 Flash | Preview | Image analysis and text generation |
| **HTTP Client** | aiohttp | 3.9.1 | Async HTTP for Gemini API calls |
| **PDF Processing** | PyMuPDF (fitz) | 1.23.8 | PDF-to-image at 300 DPI |
| **Image Processing** | Pillow (PIL) | 10.2.0 | Image resizing and optimization |
| **Data Validation** | Pydantic | 2.5.3 | Request/response schemas |
| **HTML Templates** | Jinja2 | 3.1.3 | Server-side HTML rendering |
| **Excel Generation** | openpyxl | 3.1.2 | Professional Excel spreadsheets |
| **File Upload** | python-multipart | 0.0.6 | Multipart form data handling |
| **Environment** | python-dotenv | 1.0.0 | .env configuration support |
| **Frontend** | Vanilla JS + CSS | — | SPA with zero dependencies |
| **Charts** | HTML5 Canvas | — | Custom donut charts (no libraries) |

---

## 5. The 11-Phase Analysis Pipeline

Each phase is a carefully crafted expert-level prompt sent to Gemini 2.5 Flash Vision API with the P&ID image. Every prompt enforces a strict JSON output schema to ensure structured, parseable results.

### Phase 1: Document Identification & Context

**Purpose**: Read the title block, design data block, and document metadata.

**What it extracts**:
- **Title Block**: Drawing number, sheet number, revision, title, project name, company, date, area/unit
- **Design Data**: Design pressure, design temperature, MAOP (Maximum Allowable Operating Pressure), design code, service description, material/grade, flange rating, flow rate
- **References**: Other referenced P&ID drawing numbers, applicable standards

**Why it matters**: The title block and design data provide essential context that all subsequent phases use. Design pressure and temperature are critical for understanding equipment ratings.

### Phase 2: Legend & Symbol Extraction

**Purpose**: Read the drawing's legend/symbol key to understand the specific symbols used.

**What it extracts**:
- Whether the drawing has a legend section
- Valve symbols and their descriptions (e.g., "bowtie = gate valve")
- Instrument symbols and their shapes
- Line types and their appearances (process, utility, instrument air, etc.)
- Abbreviations and their meanings
- Special symbols unique to this drawing

**Why it matters**: P&ID symbol standards can vary between companies and projects. Reading the legend first ensures accurate identification of components in later phases.

### Phase 3: Engineering Notes (Word-for-Word)

**Purpose**: Extract every engineering note exactly as written on the drawing.

**What it extracts**:
- Each note with its number, full text (verbatim), category, and referenced standards
- Categories: DESIGN, SAFETY, MATERIAL, CONSTRUCTION, REFERENCE, DELETED
- Marks partially visible notes with "[partial]"
- Total notes count

**Why it matters**: Engineering notes contain critical design requirements, safety instructions, and construction specifications. They must be captured word-for-word because even small details (like "MINIMUM" vs "MAXIMUM") can have major engineering implications.

### Phase 4: Equipment Identification

**Purpose**: Systematically scan the entire drawing for all major equipment.

**What it identifies**:
- Vessels, Drums, Accumulators, Tanks
- Heat Exchangers (shell-and-tube, plate, air-cooled)
- Pumps (centrifugal, positive displacement)
- Compressors
- Columns/Towers
- Reactors
- Filters, Strainers
- Scraper Traps (pig launchers/receivers)

**Per equipment item**:
- Tag number (exactly as shown)
- Equipment type
- Size/rating
- Service description
- Design conditions
- Connected equipment tags
- Location on drawing (e.g., "left-center", "right-top")
- Applicable engineering notes

**Scan method**: Left-to-right, top-to-bottom systematic scan to avoid missing items.

### Phase 5: Valve Analysis (Most Critical Phase)

**Purpose**: Identify and classify every single valve on the drawing.

**Scan method**: Traces each process line left-to-right, including:
- Main process lines
- Drain stubs (small lines going downward)
- Vent stubs (small lines going upward)
- Bypass lines
- Instrument connections

**Valve symbol recognition guide** (built into the prompt):

| Valve Type | Symbol Description |
|------------|-------------------|
| Gate | Two triangles meeting at points (bowtie shape) |
| Globe | Two triangles with circle between them |
| Ball | Filled/solid circle between triangles |
| Plug | Rectangle between triangles |
| Butterfly | Two triangles with vertical line through center |
| Check | Triangle pointing in flow direction with bar |
| Control | Globe valve body with diaphragm actuator on top |
| Relief/Safety | Angle body with spring symbol |
| Needle | Very small, tapered symbol |
| 3-Way | Three-port connection symbol |

**Per valve**:
- Tag number (or auto-assigns VALVE-001, VALVE-002 for untagged valves)
- Valve type (Gate, Globe, Ball, Plug, Butterfly, Check, Control, Relief/Safety, Needle, Other)
- Actuator type (Manual, MOV, Pneumatic, Solenoid, Hydraulic, Gear)
- Normal position (NC, NO, LC, LO)
- Fail position (FC, FO, FL)
- Size
- Line number (which piping line it's installed on)
- Location description
- Reference notes

**Also returns**: Count by type breakdown and total valve count.

**Why it's critical**: Valves are the most numerous components on a P&ID and the most commonly missed in manual reviews. Small drain and vent valves are particularly easy to overlook.

### Phase 6: Instrumentation (ISA-5.1 Decoding)

**Purpose**: Identify all instruments and decode their ISA-5.1 tags.

**ISA-5.1 Tag Structure**:
```
FIT-0210A
│││  ││││
│││  ││││
│││  └┴┴┴─ Loop Number (0210) + Suffix (A)
│││
│└┴─ Succeeding Letters: I=Indicator, T=Transmitter
│
└── First Letter: F=Flow (Measured Variable)
```

**First Letter Meanings** (selected):
| Letter | Measured Variable |
|--------|------------------|
| A | Analysis (composition, pH, conductivity) |
| F | Flow |
| L | Level |
| P | Pressure |
| T | Temperature |
| X | Unclassified (H2S detectors, LEL detectors) |

**Succeeding Letter Meanings** (selected):
| Letter | Function |
|--------|----------|
| A | Alarm |
| C | Controller |
| I | Indicator |
| T | Transmitter |
| S | Switch |
| V | Valve (control valve) |
| H | High |
| L | Low |

**Instrument Mounting from Symbol Shape**:
| Symbol Shape | Mounting Type |
|-------------|---------------|
| Plain circle | Local field mounted |
| Circle with horizontal line | Panel/board mounted |
| Circle with vertical line | DCS accessible |
| Square | PLC/Safety system (SIS) |
| Hexagon | Field auxiliary |
| Diamond | Computer/shared display |

**Per instrument**:
- Tag number
- Decoded tag: measured variable, functions (array), loop number
- Instrument type (e.g., "Pressure Indicating Transmitter")
- Mounting type
- Range
- Setpoints: High (H), High-High (HH), Low (L), Low-Low (LL)
- Connected system (DCS, SIS, local)
- Measures on (line number or equipment tag)

**Also returns**: Count by category (pressure, temperature, flow, level, analysis, other).

### Phase 7: Piping Line Analysis

**Purpose**: Trace and document every piping line on the drawing.

**Line Number Format Decoding**:
```
24"-P-0001-3CS1P06
│    │ │     │
│    │ │     └── Piping Spec/Class
│    │ └── Sequential Number
│    └── Service Code
└── Nominal Pipe Size (inches)
```

**Service Codes**:
| Code | Service |
|------|---------|
| P | Process |
| BD | Blowdown |
| RL | Relief |
| FL | Flare |
| FG | Fuel Gas |
| IA | Instrument Air |
| PA | Plant Air |
| N2 | Nitrogen |
| ST | Steam |
| CW | Cooling Water |
| FW | Firewater |
| DR | Drain |

**Per line**:
- Line number
- Nominal size
- Service code and description
- Piping spec/class
- Origin (from) and destination (to) equipment
- Flow direction
- Valves installed on this line
- Instruments on this line
- Special items (reducers, orifice plates, spectacle blinds)
- Connections to other P&IDs

### Phase 8: Process Flow & Connection Mapping

**Purpose**: Map the complete process flow path and all interconnections.

**What it maps**:
- **Main Process Flow**: Entry point → Equipment sequence → Exit point
- **Secondary Flows**: Bypass lines, recycle streams, sample points, vent lines, drain lines
- **Utility Connections**: Instrument air, nitrogen, steam, cooling water, utility water, chemical injection
- **Relief Paths**: Where do relief valves discharge to?
- **Drain System**: Process drains, utility drains, and drain destinations
- **Reference Drawings**: Connected P&IDs with drawing numbers and connection types
- **Tie-in Points**: Where new connections meet existing systems

### Phase 9: Safety Systems & Hazard Analysis

**Purpose**: Identify all safety-critical systems and devices.

**What it analyzes**:
- **Area Classification**: Class I/II/III, Division 1/2, Zone 0/1/2 (hazardous area rating)
- **Gas Detection**: H2S detectors, LEL detectors, CO detectors, O2 analyzers — each with tag, type, alarm setpoints, location
- **Emergency Shutdown (ESD)**: ESD valves, ESD pushbuttons, interlock references
- **Pressure Relief**: Relief valves with tag, protected equipment, set pressure, discharge destination, sizing basis
- **Safety Interlocks**: Logic descriptions
- **Fire Protection**: Fire detection and suppression systems
- **Safety-Related Notes**: Notes with safety implications

### Phase 10: Verification & Comprehensive Summary

**Purpose**: Cross-verify all counts and create a final summary.

**Method**: Divides the drawing into 9 regions (3x3 grid: top-left, top-center, top-right, middle-left, etc.) and re-counts items in each region.

**Verified counts include**:
- Total equipment, valves (with full type breakdown), instruments (with category breakdown)
- Total piping lines, notes, deleted notes
- Design data summary
- Critical safety items recap
- Gaps and uncertainties list

**Why it matters**: This phase catches counting errors from earlier phases by using a different methodology (region-based vs. line-tracing).

### Phase 11: Critical Re-Verification Pass

**Purpose**: Final independent re-count of the most commonly miscounted items.

**What it re-verifies**:
1. **Valve recount**: Independent left-to-right re-trace of every line, comparing new count with Phase 5/10 counts
2. **Gas detection**: Separate counts for H2S and LEL detectors, with setpoint confirmation
3. **Critical notes**: Word-for-word re-read of notes 1–5
4. **Design conditions**: MAOP, design temperature, design code confirmation
5. **Line numbers**: Main process line number + at least 3 other important lines
6. **Corrections**: List of any discrepancies found between this phase and earlier phases
7. **Final confidence percentage**: AI's self-assessed confidence in the analysis accuracy

---

## 6. Frontend — Multi-Page SPA

The frontend is a professional **Single Page Application** with sidebar navigation, built with vanilla JavaScript (no frameworks or libraries).

### Layout Structure

```
┌────────────┬──────────────────────────────────┐
│            │        TOP BAR                    │
│  SIDEBAR   │  Page Title     Status Badge      │
│            ├──────────────────────────────────┤
│  Logo      │                                  │
│            │                                  │
│  Upload &  │       ACTIVE PAGE CONTENT        │
│  Analyze   │                                  │
│            │  (Only one page visible at a     │
│  Executive │   time. Pages switch without     │
│  Dashboard │   full page reload.)             │
│            │                                  │
│  Detailed  │                                  │
│  Results   │                                  │
│            │                                  │
│  AI Engg.  │                                  │
│  Assistant │                                  │
│            │                                  │
│  ──────── │                                  │
│  v2.0      │                                  │
│  Gemini AI │                                  │
│  ISA-5.1   │                                  │
└────────────┴──────────────────────────────────┘
```

### Page 1: Upload & Analyze

- **Drop Zone**: Drag-and-drop or click to browse for P&ID files
- **Supported formats**: PDF, PNG, JPG, WEBP
- **File info bar**: Shows selected filename with remove option
- **Analyze button**: Full-width primary button to start analysis
- **Progress card**: Appears during analysis
  - Animated progress bar with shimmer effect
  - Percentage indicator in card header
  - 2-column grid of 11 phases with status indicators:
    - Gray dot = pending
    - Amber dot (pulsing) = active
    - Green dot = completed
    - Red dot = failed
  - Each phase shows a 2-digit number (01–11) and name

### Page 2: Executive Dashboard

A comprehensive KBR-style executive dashboard with:

- **Dashboard Header Bar**: Navy gradient with KBR-AMCDE logo (inverted white), drawing title, drawing number, revision, date, confidence ring (canvas donut), export/print buttons, Excel dropdown
- **KPI Strip**: 6 metric cards — Equipment, Valves, Instruments, Piping Lines, Safety Devices, Eng. Notes — each with colored icon
- **Dashboard Grid** (3-column):
  - Design Data table (8 rows of key engineering parameters)
  - Valve Breakdown donut chart with legend
  - Instrument Breakdown donut chart with legend
  - Safety & Hazard Status (4 indicators: gas detectors, relief devices, ESD valves, area classification)
  - Equipment Register table
  - Piping Line Schedule table
  - Process Flow Summary (visual flow arrows)
  - Engineering Notes list with category badges
  - Reference Drawings list
- **Dashboard Footer**: KBR-AMCDE branding, generation timestamp, technology credit

### Page 3: Detailed Results

- **Stats Strip**: 8 horizontal metric chips showing key counts + confidence score (gold accent chip)
- **Export Actions**: JSON export button + 3 Excel export buttons
- **Tabbed View**:
  - **Structured View**: Expandable accordion with one section per phase. Data rendered as tables (for arrays of objects), key-value pairs (for simple values), and nested sections (for complex objects)
  - **Raw AI Output**: Expandable accordion showing raw JSON/text from each phase

### Page 4: AI Engineering Assistant

- **Suggestion chips**: 6 pre-built engineering questions (control valves, flow path, relief valves, design conditions, instrument decoding, piping specs)
- **Welcome message**: Centered introductory text with chat icon
- **Chat area**: Scrollable message area with:
  - User messages: Navy-to-blue gradient bubbles (right-aligned)
  - AI responses: Light gray bubbles with pre-formatted text (left-aligned)
  - Loading indicator during AI processing
  - Slide-in animation for new messages
- **Input form**: Text input + send button in a contained card

### Navigation Behavior

- **Initial state**: Only "Upload & Analyze" is clickable; other pages are disabled (grayed out)
- **After analysis completes**: Dashboard, Results, and Assistant pages become enabled
- **Auto-navigation**: After analysis finishes, the app automatically navigates to the Executive Dashboard
- **Status badge**: Shows "Ready" → "Analyzing" (pulsing amber) → "Complete" (blue)
- **Mobile**: Sidebar collapses off-screen, toggled by hamburger button in topbar

### Theming — KBR-AMCDE Corporate

| Token | Color | Usage |
|-------|-------|-------|
| `--kbr-navy` | #003a70 | Primary brand, headers, sidebar |
| `--kbr-blue` | #1a5091 | Buttons, links, active states |
| `--kbr-light` | #4a90d9 | Accents, progress bar gradient |
| `--kbr-gold` | #c8a951 | Active nav indicator, confidence ring, tab underline |
| `--kbr-dark` | #002244 | Sidebar gradient, dashboard header |
| `--kbr-bg` | #f0f2f5 | Page background |
| `--kbr-surface` | #ffffff | Cards, panels |
| `--kbr-success` | #0d8a4a | Completed phases, success states |
| `--kbr-warning` | #d97706 | Active phases, analyzing state |
| `--kbr-danger` | #c52a2a | Errors, failed phases |

---

## 7. Backend — FastAPI REST API

The backend is a FastAPI application serving both the HTML frontend and the REST API.

### Key Architectural Decisions

1. **In-memory session storage**: Analysis sessions are stored in a Python dictionary (`ANALYSIS_SESSIONS`). This is suitable for single-server deployment and avoids database dependencies.

2. **Background tasks**: The 11-phase analysis runs as a FastAPI `BackgroundTask`, allowing the client to poll for progress without blocking.

3. **Rate limiting**: 2-second delays between Gemini API calls to prevent 429 (Too Many Requests) errors.

4. **Deep JSON search**: Custom `_deep_find_int()` and `_deep_find_list()` functions handle the variable JSON structures that Gemini produces, searching recursively through nested dicts and arrays.

5. **Confidence scoring**: Starts at 100, decreases by 10 points for each phase that fails.

### Static File Serving

- `/static/css/style.css` — Complete CSS
- `/static/js/app.js` — SPA navigation and logic
- `/static/js/dashboard.js` — Dashboard charts and data population
- `/static/images/kbr-amcde-logo.svg` — Logo (viewBox: 0 0 520 110)

---

## 8. Services

### 8.1 Gemini Vision Service (`services/gemini_vision.py`)

**Class**: `GeminiVisionService`

**API Configuration**:
- Model: `gemini-2.5-flash-preview-05-20`
- Temperature: 0.05 (near-deterministic for engineering accuracy)
- Top-K: 20
- Top-P: 0.9
- Max Output Tokens: 32,768
- Safety Settings: All categories set to `BLOCK_NONE` (engineering content may trigger false positives)

**Methods**:

- `analyze_image(image_base64, mime_type, prompt, max_retries=2)` — Sends image + prompt to Gemini API. Handles 429 rate limits with exponential backoff (3 * (attempt + 1) seconds). Returns raw text response.

- `parse_response(response)` — Robust 4-strategy JSON parser:
  1. Extract from ` ```json ... ``` ` code blocks
  2. Extract from ` ``` ... ``` ` code blocks (without json tag)
  3. Find largest JSON object using brace matching
  4. Try entire response as JSON
  5. Fallback: `{"raw_text": response}`

### 8.2 PDF Processor (`services/pdf_processor.py`)

**Class**: `PDFProcessor`

**Key Parameters**:
- Default DPI: 300 (minimum for P&ID density)
- Max Pixels: 20,000,000 (20 MP limit to prevent memory issues)
- Downscale method: LANCZOS (highest quality)

**Methods**:

- `pdf_to_image_base64(pdf_path, page_number=0, dpi=300)` — Converts a single PDF page to a base64-encoded PNG image.
  - Renders at specified DPI (zoom = dpi / 72)
  - If the result exceeds 20 MP, scales down while preserving aspect ratio
  - Returns: (base64_string, "image/png")

- `pdf_to_all_pages_base64(pdf_path, dpi=300)` — Converts all pages.

- `get_pdf_info(pdf_path)` — Returns page count, metadata, and dimensions.

### 8.3 Excel Export Service (`services/excel_export.py`)

Three professional export generators — see [Section 10](#10-excel-export-feature).

---

## 9. ISA-5.1 Knowledge Base

The file `services/pid_knowledge.py` contains a comprehensive engineering reference dictionary:

### Instrument First Letters (ISA-5.1)

All 26 letters mapped to measured variables:

| Letter | Variable | Description |
|--------|----------|-------------|
| A | Analysis | Composition, pH, conductivity, moisture |
| B | Burner/Combustion | Flame, combustion parameters |
| C | Conductivity | Electrical conductivity |
| D | Density/Specific Gravity | Fluid density |
| E | Voltage | Electrical voltage |
| F | Flow | Flow rate |
| G | Gauging/Position | Dimensional measurement |
| H | Hand/Manual | Manual actuation |
| I | Current | Electrical current |
| J | Power | Wattage, horsepower |
| K | Time/Schedule | Time-based events |
| L | Level | Liquid or interface level |
| M | Moisture/Humidity | Moisture content |
| N | User's Choice | Project-specific |
| O | User's Choice | Project-specific |
| P | Pressure/Vacuum | Pressure measurement |
| Q | Quantity/Event | Totalization, event counting |
| R | Radiation/Radioactivity | Nuclear radiation |
| S | Speed/Frequency | Rotational speed, vibration |
| T | Temperature | Temperature measurement |
| U | Multivariable | Multiple measured variables |
| V | Vibration | Mechanical analysis |
| W | Weight/Force | Weight, load, force |
| X | Unclassified | H2S, LEL, special detectors |
| Y | Event/State | On/off, open/closed |
| Z | Position/Dimension | Travel, stroke position |

### Instrument Succeeding Letters (ISA-5.1)

| Letter | Function |
|--------|----------|
| A | Alarm |
| C | Controller |
| D | Differential |
| E | Element/Sensor |
| F | Ratio |
| G | Glass/Gauge |
| H | High |
| I | Indicator |
| K | Control Station |
| L | Low |
| M | Middle/Intermediate |
| N | User's Choice |
| O | Orifice/Restriction |
| P | Point/Test Connection |
| Q | Integrate/Totalize |
| R | Recorder |
| S | Switch |
| T | Transmitter |
| U | Multifunction |
| V | Valve/Damper |
| W | Well/Probe |
| X | Unclassified |
| Y | Relay/Compute |
| Z | Driver/Final Element |

### Valve Types

| Type | Symbol | Application |
|------|--------|-------------|
| Gate | Two triangles meeting at points | On/off service, full bore |
| Globe | Circle between two triangles | Throttling service |
| Ball | Filled circle between triangles | Quick on/off, tight shutoff |
| Plug | Rectangle between triangles | Multi-port, tight shutoff |
| Butterfly | Triangles with vertical line | Large diameter, low pressure |
| Check | Triangle with bar | Prevent reverse flow |
| Relief | Angle body with spring | Overpressure protection |
| Control | Globe body with diaphragm | Automated flow regulation |
| Motor Operated (MOV) | Valve with M designation | Remote on/off operation |
| Solenoid | Valve with S designation | Fast-acting on/off |

### Valve Positions

| Code | Meaning |
|------|---------|
| NC | Normally Closed |
| NO | Normally Open |
| LC | Locked Closed |
| LO | Locked Open |
| FC | Fail Closed |
| FO | Fail Open |
| FL | Fail Last (stays in last position) |
| CSC | Car Sealed Closed |
| CSO | Car Sealed Open |
| TSO | Tight Shut Off |

### Service Codes (16 total)

P (Process), BD (Blowdown), RL (Relief), FL (Flare), FG (Fuel Gas), IA (Instrument Air), PA (Plant Air), N2 (Nitrogen), ST (Steam), CW (Cooling Water), BW (Boiler Water), FW (Firewater), UW (Utility Water), OW (Oily Water), CD (Condensate), DR (Drain)

### Area Classification

| Classification | Description |
|---------------|-------------|
| Class I | Flammable gases, vapors, or liquids |
| Class II | Combustible dust |
| Class III | Ignitable fibers |
| Division 1 | Hazardous during normal operation |
| Division 2 | Hazardous only under abnormal conditions |
| Zone 0 | Explosive atmosphere continuously present |
| Zone 1 | Explosive atmosphere likely during normal operation |
| Zone 2 | Explosive atmosphere unlikely, short duration |

---

## 10. Excel Export Feature

Three professional engineering Excel spreadsheets can be generated from analysis results.

### 10.1 Mechanical Equipment List (KBR Format)

**Standard**: KBR corporate engineering format

**Layout**:
- Rows 1–4: Project header (Client, Title, Location, Description) + Document info
- Rows 6–7: Two-row merged column headers
- Row 8: Area/unit separator (yellow highlight)
- Rows 9+: Equipment data with alternating row colors

**18 Columns**:
Qty, Plant No, Equip Marking, Seq No, Suffix, Equipment Title, Type, Datasheet Specifications, P&ID/Plot Plan, Capacity, Service, Design Pressure, Design Temperature, Dimensions/Weight, Driver Type, Power Requirements, Materials of Construction, Remarks

**Styling**: Dark blue headers, thin borders, landscape orientation, fit-to-page printing.

### 10.2 Valve List (Saudi Aramco 2616-ENG Format)

**Standard**: Saudi Aramco Engineering Standard 2616-ENG (11/2010)

**Layout**:
- Row 1: Standard reference
- Rows 2–3: "SAUDI ARABIAN OIL COMPANY" header
- Row 4: Project/Document/Rev/Date
- Rows 6–7: Two-row merged column headers
- Rows 8+: Valve data

**12 Columns**:
No, Tag Number, Size Rating, Valve Type, Actuator, Reference P&ID, Service/Location, Upstream Pressure/Pressure Drop, Temperature, Normal Position, Fail Position, Reference Valve Datasheet

**Summary row**: Total valve count. Disclaimer row at bottom.

### 10.3 Piping Line List

**Layout**:
- Row 1: Company name
- Row 2: "PIPING LINE LIST" title
- Row 3–4: Project info
- Rows 6–7: Two-row merged column headers
- Rows 8+: Line data

**16 Columns**:
No, Line Number, Nominal Size, Service Code, Service Description, Piping Spec/Class, From, To, Flow Direction, Design Pressure, Design Temperature, Material/Grade, Insulation Type, Test Pressure, P&ID Reference, Remarks

**Summary row**: Total line count. Standard notes section at bottom.

---

## 11. Data Flow & User Journey

### Complete Workflow

```
1. USER UPLOADS FILE
   │
   ├─ Frontend: Drag-drop or browse → file validation
   │
   ├─ POST /api/upload
   │   ├─ Generate session_id (UUID)
   │   ├─ Save file to disk
   │   ├─ If PDF: Convert to image at 300 DPI (PyMuPDF)
   │   │   └─ Scale down if > 20 megapixels (LANCZOS)
   │   ├─ Encode to base64
   │   └─ Store session: {filename, image_base64, mime_type, status: "pending"}
   │
   ├─ Response: {session_id, filename}
   │
2. USER CLICKS "START 11-PHASE ANALYSIS"
   │
   ├─ POST /api/analyze/{session_id}
   │   ├─ Status → "in_progress"
   │   └─ Launch BackgroundTask: run_analysis()
   │
   ├─ BACKGROUND: run_analysis() loops through 11 phases:
   │   │
   │   ├─ For each phase (1-11):
   │   │   ├─ Build prompt from EXPERT_ANALYSIS_PHASES dict
   │   │   ├─ Phase 11 gets previous_valve_count injected
   │   │   ├─ Call gemini_service.analyze_image()
   │   │   │   ├─ POST to Gemini API with image + prompt
   │   │   │   ├─ Handle 429 rate limits (exponential backoff)
   │   │   │   ├─ Retry up to 2 times on failures
   │   │   │   └─ Return raw text response
   │   │   ├─ Parse response with 4-strategy JSON parser
   │   │   ├─ Store result in phases dict
   │   │   ├─ Update progress: {current_phase, total_phases, phase_name}
   │   │   ├─ Wait 2 seconds (rate limit protection)
   │   │   └─ On error: Record in errors list, confidence -= 10
   │   │
   │   ├─ Extract statistics from all phase results
   │   │   ├─ Deep search for counts in variable JSON structures
   │   │   └─ Phase 10 verified counts override earlier counts
   │   │
   │   └─ Status → "completed"
   │
3. FRONTEND POLLS FOR PROGRESS
   │
   ├─ GET /api/status/{session_id} (every 2.5 seconds)
   │   └─ Returns: {status, progress: {current_phase, total_phases, phase_name}}
   │
   ├─ Frontend updates:
   │   ├─ Progress bar width + percentage
   │   ├─ Phase dots (pending → active → completed)
   │   ├─ Topbar status badge
   │   └─ When status = "completed": stop polling, load results
   │
4. LOAD AND DISPLAY RESULTS
   │
   ├─ GET /api/results/{session_id}
   │   └─ Returns: {phases, statistics, errors, confidence, timestamps}
   │
   ├─ Frontend:
   │   ├─ Enable Dashboard, Results, Assistant pages in sidebar
   │   ├─ Populate executive dashboard (charts, tables, KPIs)
   │   ├─ Build structured and raw result accordions
   │   ├─ Fill stats chips
   │   └─ Auto-navigate to Executive Dashboard page
   │
5. USER INTERACTS WITH RESULTS
   │
   ├─ Dashboard: View KPIs, charts, tables, print, export
   ├─ Results: Expand phase accordions, switch structured/raw tabs
   ├─ Assistant: Ask questions via chat
   │   │
   │   ├─ POST /api/query {session_id, question}
   │   │   ├─ Build context prompt with all analysis results
   │   │   ├─ Include ISA-5.1 knowledge base
   │   │   ├─ Send to Gemini with the question
   │   │   └─ Return answer
   │   │
   │   └─ Display AI response in chat bubble
   │
   └─ Export:
       ├─ GET /api/export/{id} → JSON download
       ├─ GET /api/export/{id}/equipment-list → Excel (.xlsx)
       ├─ GET /api/export/{id}/valve-list → Excel (.xlsx)
       └─ GET /api/export/{id}/line-list → Excel (.xlsx)
```

---

## 12. API Endpoints Reference

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/` | GET | Serve HTML frontend | — | HTML page |
| `/api/upload` | POST | Upload P&ID file | `multipart/form-data` with `file` field | `{status, session_id, filename, message}` |
| `/api/analyze/{session_id}` | POST | Start 11-phase analysis | — | `{status, message}` |
| `/api/status/{session_id}` | GET | Check analysis progress | — | `{session_id, status, progress, has_results}` |
| `/api/results/{session_id}` | GET | Get full analysis results | — | `{phases, statistics, errors, confidence, timestamps}` |
| `/api/query` | POST | Ask engineering question | `{session_id, question}` | `{question, answer, session_id}` |
| `/api/export/{session_id}` | GET | Export results as JSON | — | JSON file download |
| `/api/export/{session_id}/equipment-list` | GET | Equipment List Excel | — | `.xlsx` file download |
| `/api/export/{session_id}/valve-list` | GET | Valve List Excel | — | `.xlsx` file download |
| `/api/export/{session_id}/line-list` | GET | Line List Excel | — | `.xlsx` file download |

---

## 13. Data Models & Schemas

### Pydantic Models (`models/schemas.py`)

```python
class QueryRequest:
    session_id: str
    question: str

class UploadResponse:
    status: str
    session_id: str
    filename: str
    message: str

class AnalysisProgress:
    current_phase: int
    total_phases: int
    phase_name: Optional[str]

class StatusResponse:
    session_id: str
    status: str           # "pending" | "in_progress" | "completed"
    progress: Optional[AnalysisProgress]
    has_results: bool

class QueryResponse:
    question: str
    answer: str
    session_id: str

class PhaseResult:
    result: Any           # Parsed JSON from Gemini
    raw: str              # Raw text response
    timestamp: str        # ISO datetime

class AnalysisResults:
    phases: Dict[str, PhaseResult]  # 11 phases
    statistics: Dict[str, int]      # Counts
    errors: List[Dict[str, str]]    # Phase errors
    confidence: int                  # 0-100
    start_time: str
    end_time: Optional[str]
```

### Statistics Structure

```python
{
    "equipment": int,       # From Phase 4
    "valves": int,          # From Phase 5 (overridden by Phase 10)
    "instruments": int,     # From Phase 6 (overridden by Phase 10)
    "piping_lines": int,    # From Phase 7
    "notes": int,           # From Phase 3
    "gas_detectors": int,   # From Phase 9
    "relief_devices": int,  # From Phase 9
    "esd_valves": int       # From Phase 9
}
```

---

## 14. Session Management

Sessions are stored in an in-memory Python dictionary:

```python
ANALYSIS_SESSIONS[session_id] = {
    "file_path": str,           # Path to uploaded file
    "filename": str,            # Original filename
    "image_base64": str,        # Base64-encoded image
    "mime_type": str,           # "image/png", "image/jpeg", etc.
    "upload_time": str,         # ISO datetime
    "analysis_results": dict,   # None until analysis completes
    "analysis_status": str,     # "pending" → "in_progress" → "completed"
    "analysis_progress": {
        "current_phase": int,   # 1-11
        "total_phases": 11,
        "phase_name": str       # e.g., "phase5_valve_analysis"
    }
}
```

**Note**: Sessions are lost when the server restarts. This is by design for simplicity — the tool is intended for interactive analysis sessions, not persistent storage.

---

## 15. Error Handling & Reliability

### Gemini API Error Handling

- **429 Rate Limit**: Detected and handled with exponential backoff (3 * (attempt + 1) seconds wait)
- **Network Errors**: Up to 2 retries with exponential backoff
- **Timeout**: 120-second HTTP timeout per API call
- **Invalid JSON**: 4-strategy robust parser with fallback to raw text

### Analysis Resilience

- If a phase fails, the error is recorded and the pipeline continues to the next phase
- Confidence score decreases by 10 points per failed phase
- Phase 10 verified counts can correct Phase 4/5/6/7 miscounts
- Phase 11 provides independent re-verification

### Frontend Error Handling

- Upload errors: Alert dialog with error message, reset upload state
- Analysis errors: Alert dialog, re-enable analyze button
- Polling errors: Silently retry (network glitches)
- Results load failure: Alert dialog

---

## 16. Configuration & Environment

### Environment Variable

| Variable | Purpose | Default |
|----------|---------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Hardcoded fallback |

### Gemini API Generation Config

```python
{
    "temperature": 0.05,        # Near-deterministic
    "topK": 20,
    "topP": 0.9,
    "maxOutputTokens": 32768    # ~32K tokens max per response
}
```

---

## 17. File Structure

```
pid-analyzer/
├── main.py                          # FastAPI application, endpoints, analysis orchestration
├── requirements.txt                 # Python dependencies
├── readmedetails.md                 # This file
│
├── models/
│   └── schemas.py                   # Pydantic data models
│
├── services/
│   ├── gemini_vision.py             # Gemini API client + 11 phase prompts
│   ├── pdf_processor.py             # PDF-to-image at 300 DPI
│   ├── pid_knowledge.py             # ISA-5.1 knowledge base
│   └── excel_export.py              # 3 Excel export generators
│
├── templates/
│   └── index.html                   # Multi-page SPA (sidebar + 4 pages)
│
├── static/
│   ├── css/
│   │   └── style.css                # Complete KBR-AMCDE corporate theme
│   ├── js/
│   │   ├── app.js                   # SPA navigation, upload, analysis, results, chat
│   │   └── dashboard.js             # Executive dashboard charts and data
│   └── images/
│       └── kbr-amcde-logo.svg       # KBR-AMCDE logo (viewBox: 0 0 520 110)
│
└── uploads/                         # Temporary file upload directory
```

---

## 18. Dependencies

```
fastapi==0.109.0          # Async web framework
uvicorn==0.27.0           # ASGI server
python-multipart==0.0.6   # File upload support
aiohttp==3.9.1            # Async HTTP client for Gemini API
Pillow==10.2.0            # Image processing and resizing
PyMuPDF==1.23.8           # PDF rendering (fitz library)
pydantic==2.5.3           # Data validation and serialization
jinja2==3.1.3             # HTML template engine
python-dotenv==1.0.0      # Environment variable management
openpyxl==3.1.2           # Excel file generation
```

---

## 19. Running the Application

### Install Dependencies

```bash
cd pid-analyzer
pip install -r requirements.txt
```

### Set API Key

```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

Or create a `.env` file:
```
GEMINI_API_KEY=your-gemini-api-key-here
```

### Start the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Access the Application

Open `http://localhost:8000` in your browser.

---

*P&ID Vision Analyzer v2.0 — KBR-AMCDE*
*Powered by Gemini 2.5 Flash Vision AI — ISA-5.1 Compliant*
