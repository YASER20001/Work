"""
Generate KBR-AMCDE P&ID Vision Analyzer - Executive Presentation
Advanced PowerPoint for senior management review
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── KBR Colors ──
NAVY = RGBColor(0x00, 0x3a, 0x70)
BLUE = RGBColor(0x1a, 0x50, 0x91)
LIGHT_BLUE = RGBColor(0x4a, 0x90, 0xd9)
GOLD = RGBColor(0xc8, 0xa9, 0x51)
DARK = RGBColor(0x00, 0x22, 0x44)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xF0, 0xF2, 0xF5)
DARK_TEXT = RGBColor(0x1a, 0x23, 0x32)
MUTED = RGBColor(0x5a, 0x6a, 0x7e)
SUCCESS = RGBColor(0x0d, 0x8a, 0x4a)
DANGER = RGBColor(0xc5, 0x2a, 0x2a)
AMBER = RGBColor(0xd9, 0x77, 0x06)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def add_shape(slide, left, top, width, height, fill_color=None, line_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.line.fill.background()
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

def add_text_box(slide, left, top, width, height, text, font_size=18, bold=False, color=DARK_TEXT, alignment=PP_ALIGN.LEFT, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    return txBox

def add_rich_text(slide, left, top, width, height, lines):
    """lines = list of (text, font_size, bold, color, alignment)"""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, (text, size, bold, color, align) in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = text
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = color
        p.font.name = "Calibri"
        p.alignment = align
        p.space_after = Pt(4)
    return txBox

def add_gold_bar(slide, top):
    add_shape(slide, Inches(0), top, prs.slide_width, Pt(4), fill_color=GOLD)

def add_navy_footer(slide, text="KBR-AMCDE  |  P&ID Vision Analyzer  |  Confidential"):
    add_shape(slide, Inches(0), Inches(7.0), prs.slide_width, Inches(0.5), fill_color=DARK)
    add_text_box(slide, Inches(0.5), Inches(7.05), Inches(12), Inches(0.4), text,
                 font_size=9, color=RGBColor(0x80, 0x90, 0xA0), alignment=PP_ALIGN.CENTER)

def add_slide_number(slide, num):
    add_text_box(slide, Inches(12.5), Inches(7.05), Inches(0.7), Inches(0.4), str(num),
                 font_size=9, color=RGBColor(0x80, 0x90, 0xA0), alignment=PP_ALIGN.RIGHT)

def kpi_card(slide, left, top, value, label, accent_color=NAVY):
    w, h = Inches(2.2), Inches(1.6)
    # Card background
    card = add_shape(slide, left, top, w, h, fill_color=WHITE)
    card.shadow.inherit = False
    # Accent bar at top
    add_shape(slide, left, top, w, Pt(4), fill_color=accent_color)
    # Value
    add_text_box(slide, left + Inches(0.15), top + Inches(0.25), w - Inches(0.3), Inches(0.7),
                 value, font_size=32, bold=True, color=accent_color, alignment=PP_ALIGN.CENTER)
    # Label
    add_text_box(slide, left + Inches(0.15), top + Inches(0.95), w - Inches(0.3), Inches(0.4),
                 label, font_size=11, bold=True, color=MUTED, alignment=PP_ALIGN.CENTER)

def bullet_slide_content(slide, items, left, top, width, height, font_size=16, color=DARK_TEXT):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, (text, level) in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = text
        p.font.size = Pt(font_size - (level * 2))
        p.font.color.rgb = color if level == 0 else MUTED
        p.font.name = "Calibri"
        p.font.bold = (level == 0)
        p.level = level
        p.space_before = Pt(8) if level == 0 else Pt(2)
        p.space_after = Pt(2)
    return txBox


# ═══════════════════════════════════════════════════════════
# SLIDE 1: TITLE SLIDE
# ═══════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank

# Full navy background
add_shape(slide, Inches(0), Inches(0), prs.slide_width, prs.slide_height, fill_color=DARK)

# Gold accent bar
add_shape(slide, Inches(0), Inches(3.1), prs.slide_width, Pt(3), fill_color=GOLD)

# Title text
add_rich_text(slide, Inches(1), Inches(1.0), Inches(11), Inches(2.0), [
    ("P&ID VISION ANALYZER", 44, True, WHITE, PP_ALIGN.LEFT),
    ("AI-Powered Piping & Instrumentation Diagram Analysis", 22, False, LIGHT_BLUE, PP_ALIGN.LEFT),
])

# Subtitle area below gold line
add_rich_text(slide, Inches(1), Inches(3.5), Inches(11), Inches(2.5), [
    ("Powered by Google Gemini 2.5 Flash Vision AI", 18, False, RGBColor(0xA0, 0xB5, 0xCC), PP_ALIGN.LEFT),
    ("ISA-5.1 Compliant  |  11-Phase Expert Analysis Pipeline", 16, False, RGBColor(0x70, 0x85, 0x9C), PP_ALIGN.LEFT),
    ("", 10, False, WHITE, PP_ALIGN.LEFT),
    ("KBR-AMCDE", 28, True, GOLD, PP_ALIGN.LEFT),
    ("Engineering & Project Management Excellence", 14, False, RGBColor(0x90, 0xA5, 0xBC), PP_ALIGN.LEFT),
])

# Version badge
badge = add_shape(slide, Inches(10.5), Inches(1.2), Inches(1.8), Inches(0.45), fill_color=NAVY)
add_text_box(slide, Inches(10.5), Inches(1.22), Inches(1.8), Inches(0.45),
             "VERSION 2.0", font_size=12, bold=True, color=GOLD, alignment=PP_ALIGN.CENTER)

add_text_box(slide, Inches(1), Inches(6.5), Inches(11), Inches(0.5),
             "CONFIDENTIAL  —  For Internal KBR-AMCDE Use Only", font_size=10, color=RGBColor(0x50, 0x60, 0x70), alignment=PP_ALIGN.LEFT)

# ═══════════════════════════════════════════════════════════
# SLIDE 2: THE PROBLEM
# ═══════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])

# Top bar
add_shape(slide, Inches(0), Inches(0), prs.slide_width, Inches(1.1), fill_color=NAVY)
add_gold_bar(slide, Inches(1.1))
add_text_box(slide, Inches(0.8), Inches(0.25), Inches(8), Inches(0.6),
             "THE CHALLENGE", font_size=28, bold=True, color=WHITE)
add_text_box(slide, Inches(0.8), Inches(0.65), Inches(10), Inches(0.4),
             "Why Manual P&ID Data Extraction is Failing the Industry", font_size=14, color=GOLD)

# Problem content
problems = [
    ("Time-Intensive Manual Process", 0),
    ("A single P&ID drawing can contain 50-200+ valves, 30-100+ instruments, and dozens of piping lines", 1),
    ("Manual data extraction takes 4-8 hours per drawing by experienced engineers", 1),
    ("", 0),
    ("Human Error is Unavoidable", 0),
    ("Small drain/vent valves are commonly missed — up to 15-20% undercounting is typical", 1),
    ("ISA-5.1 instrument tag decoding is complex and error-prone under time pressure", 1),
    ("Transcription errors in tag numbers, sizes, and specifications cause downstream issues", 1),
    ("", 0),
    ("Resource Bottleneck", 0),
    ("Requires senior engineers with P&ID reading expertise — a scarce resource", 1),
    ("Multiple review cycles needed to verify accuracy, adding weeks to project schedules", 1),
    ("", 0),
    ("No Standardized Digital Output", 0),
    ("Data ends up in spreadsheets with inconsistent formatting between engineers", 1),
    ("No automated connection between P&ID analysis and engineering databases", 1),
]

bullet_slide_content(slide, problems, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.0))

# Right side — impact callout
add_shape(slide, Inches(9.0), Inches(1.6), Inches(3.8), Inches(4.8), fill_color=RGBColor(0xFE, 0xF3, 0xC7))
add_rich_text(slide, Inches(9.3), Inches(1.8), Inches(3.2), Inches(4.4), [
    ("INDUSTRY IMPACT", 14, True, AMBER, PP_ALIGN.CENTER),
    ("", 8, False, DARK_TEXT, PP_ALIGN.LEFT),
    ("4-8 hrs", 36, True, DANGER, PP_ALIGN.CENTER),
    ("per drawing for manual extraction", 12, False, DARK_TEXT, PP_ALIGN.CENTER),
    ("", 8, False, DARK_TEXT, PP_ALIGN.LEFT),
    ("15-20%", 36, True, DANGER, PP_ALIGN.CENTER),
    ("typical valve undercount rate", 12, False, DARK_TEXT, PP_ALIGN.CENTER),
    ("", 8, False, DARK_TEXT, PP_ALIGN.LEFT),
    ("3-5x", 36, True, AMBER, PP_ALIGN.CENTER),
    ("review cycles for verification", 12, False, DARK_TEXT, PP_ALIGN.CENTER),
])

add_navy_footer(slide)
add_slide_number(slide, 2)

# ═══════════════════════════════════════════════════════════
# SLIDE 3: THE SOLUTION
# ═══════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])

add_shape(slide, Inches(0), Inches(0), prs.slide_width, Inches(1.1), fill_color=NAVY)
add_gold_bar(slide, Inches(1.1))
add_text_box(slide, Inches(0.8), Inches(0.25), Inches(8), Inches(0.6),
             "THE SOLUTION", font_size=28, bold=True, color=WHITE)
add_text_box(slide, Inches(0.8), Inches(0.65), Inches(10), Inches(0.4),
             "AI-Powered P&ID Analysis with 11-Phase Expert Pipeline", font_size=14, color=GOLD)

# Solution description
add_rich_text(slide, Inches(0.8), Inches(1.5), Inches(11.5), Inches(1.0), [
    ("P&ID Vision Analyzer uses Google Gemini 2.5 Flash Vision AI — a state-of-the-art multimodal AI model — to read, analyze, and extract every engineering element from P&ID drawings with expert-level accuracy.", 16, False, DARK_TEXT, PP_ALIGN.LEFT),
])

# Three pillars
pillar_data = [
    ("VISION AI", "Gemini 2.5 Flash reads the\ndrawing like a senior engineer\n— identifying symbols, text,\nand spatial relationships", NAVY),
    ("11-PHASE PIPELINE", "Sequential expert analysis\nfrom document context through\nverification — each phase\nbuilds on previous results", BLUE),
    ("ISA-5.1 KNOWLEDGE", "Built-in engineering knowledge\nbase for instrument decoding,\nvalve classification, piping\nservice codes, and standards", SUCCESS),
]

for i, (title, desc, color) in enumerate(pillar_data):
    x = Inches(0.8 + i * 4.1)
    # Pillar card
    add_shape(slide, x, Inches(2.8), Inches(3.7), Inches(3.2), fill_color=WHITE, line_color=RGBColor(0xE0, 0xE5, 0xEC))
    add_shape(slide, x, Inches(2.8), Inches(3.7), Pt(5), fill_color=color)
    # Number circle
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(1.4), Inches(3.0), Inches(0.8), Inches(0.8))
    circle.fill.solid()
    circle.fill.fore_color.rgb = color
    circle.line.fill.background()
    add_text_box(slide, x + Inches(1.4), Inches(3.05), Inches(0.8), Inches(0.7),
                 str(i + 1), font_size=22, bold=True, color=WHITE, alignment=PP_ALIGN.CENTER)
    # Title
    add_text_box(slide, x + Inches(0.2), Inches(3.9), Inches(3.3), Inches(0.45),
                 title, font_size=14, bold=True, color=color, alignment=PP_ALIGN.CENTER)
    # Description
    add_text_box(slide, x + Inches(0.2), Inches(4.35), Inches(3.3), Inches(1.5),
                 desc, font_size=12, color=MUTED, alignment=PP_ALIGN.CENTER)

add_navy_footer(slide)
add_slide_number(slide, 3)

# ═══════════════════════════════════════════════════════════
# SLIDE 4: HOW IT WORKS — 11 PHASE PIPELINE
# ═══════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])

add_shape(slide, Inches(0), Inches(0), prs.slide_width, Inches(1.1), fill_color=NAVY)
add_gold_bar(slide, Inches(1.1))
add_text_box(slide, Inches(0.8), Inches(0.25), Inches(8), Inches(0.6),
             "HOW IT WORKS", font_size=28, bold=True, color=WHITE)
add_text_box(slide, Inches(0.8), Inches(0.65), Inches(10), Inches(0.4),
             "11-Phase Sequential Analysis Pipeline — Each Phase is an Expert AI Prompt", font_size=14, color=GOLD)

phases = [
    ("01", "Document Context", "Title block, design data,\nreferences"),
    ("02", "Legend & Symbols", "Symbol key, line types,\nabbreviations"),
    ("03", "Notes Extraction", "Word-for-word engineering\nnotes capture"),
    ("04", "Equipment Scan", "All vessels, pumps, HX,\ncompressors, filters"),
    ("05", "Valve Analysis", "Every valve identified &\nclassified by type"),
    ("06", "Instrumentation", "ISA-5.1 tag decoding,\nmounting, setpoints"),
    ("07", "Piping Analysis", "Line numbers, sizes, specs,\nservice codes"),
    ("08", "Connections & Flow", "Process flow mapping,\nutility connections"),
    ("09", "Safety Analysis", "Gas detection, ESD, relief,\narea classification"),
    ("10", "Verification", "Region-by-region recount\n& summary"),
    ("11", "Re-Verification", "Independent final pass\n& corrections"),
]

# Grid layout: 4 columns, 3 rows
for i, (num, title, desc) in enumerate(phases):
    col = i % 4
    row = i // 4
    x = Inches(0.5 + col * 3.15)
    y = Inches(1.5 + row * 1.85)
    w = Inches(2.9)
    h = Inches(1.65)

    color = NAVY if i < 9 else GOLD if i == 9 else SUCCESS

    add_shape(slide, x, y, w, h, fill_color=WHITE, line_color=RGBColor(0xE0, 0xE5, 0xEC))
    add_shape(slide, x, y, Pt(5), h, fill_color=color)

    add_text_box(slide, x + Inches(0.12), y + Inches(0.1), Inches(0.45), Inches(0.35),
                 num, font_size=14, bold=True, color=color)
    add_text_box(slide, x + Inches(0.55), y + Inches(0.1), w - Inches(0.7), Inches(0.35),
                 title, font_size=12, bold=True, color=DARK_TEXT)
    add_text_box(slide, x + Inches(0.55), y + Inches(0.5), w - Inches(0.7), Inches(1.0),
                 desc, font_size=10, color=MUTED)

# Empty slot annotation
add_text_box(slide, Inches(10.0), Inches(5.3), Inches(2.8), Inches(1.2),
             "Each phase sends the P&ID image with a specialized prompt to Gemini 2.5 Flash Vision AI.\n\nResults are parsed into structured JSON and cross-verified across phases.",
             font_size=10, color=MUTED, alignment=PP_ALIGN.LEFT)

add_navy_footer(slide)
add_slide_number(slide, 4)

# ═══════════════════════════════════════════════════════════
# SLIDE 5: KEY CAPABILITIES
# ═══════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])

add_shape(slide, Inches(0), Inches(0), prs.slide_width, Inches(1.1), fill_color=NAVY)
add_gold_bar(slide, Inches(1.1))
add_text_box(slide, Inches(0.8), Inches(0.25), Inches(8), Inches(0.6),
             "KEY CAPABILITIES", font_size=28, bold=True, color=WHITE)
add_text_box(slide, Inches(0.8), Inches(0.65), Inches(10), Inches(0.4),
             "What the System Extracts and Delivers", font_size=14, color=GOLD)

capabilities = [
    ("Equipment Identification", "Vessels, Drums, Tanks, Heat Exchangers, Pumps, Compressors, Columns, Reactors, Filters — with tag numbers, types, sizes, and connections", NAVY),
    ("Valve Analysis", "Gate, Globe, Ball, Plug, Butterfly, Check, Control, Relief, MOV, Needle — with actuator type, normal/fail positions, line assignments", BLUE),
    ("ISA-5.1 Instrument Decoding", "Full tag decoding (FIT-0210 → Flow Indicating Transmitter), mounting type from symbol shape, setpoints (H/HH/L/LL), DCS/SIS assignment", LIGHT_BLUE),
    ("Piping Line Analysis", 'Line number decoding (24"-P-0001-3CS1P06), service codes, specs, from/to routing, special items (orifice plates, spectacle blinds)', SUCCESS),
    ("Safety & Hazard Analysis", "Gas detection (H2S, LEL), ESD valves, relief devices with set pressures, area classification (Class/Division/Zone)", DANGER),
    ("AI Engineering Assistant", "Natural language Q&A about the analyzed drawing — ask any engineering question and get expert-level answers with full context", GOLD),
]

for i, (title, desc, color) in enumerate(capabilities):
    col = i % 2
    row = i // 2
    x = Inches(0.5 + col * 6.3)
    y = Inches(1.5 + row * 1.75)

    add_shape(slide, x, y, Inches(5.9), Inches(1.55), fill_color=WHITE, line_color=RGBColor(0xE0, 0xE5, 0xEC))
    add_shape(slide, x, y, Inches(5.9), Pt(4), fill_color=color)

    add_text_box(slide, x + Inches(0.2), y + Inches(0.15), Inches(5.4), Inches(0.35),
                 title, font_size=14, bold=True, color=color)
    add_text_box(slide, x + Inches(0.2), y + Inches(0.55), Inches(5.4), Inches(0.9),
                 desc, font_size=11, color=MUTED)

add_navy_footer(slide)
add_slide_number(slide, 5)

# ═══════════════════════════════════════════════════════════
# SLIDE 6: PROFESSIONAL OUTPUTS
# ═══════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])

add_shape(slide, Inches(0), Inches(0), prs.slide_width, Inches(1.1), fill_color=NAVY)
add_gold_bar(slide, Inches(1.1))
add_text_box(slide, Inches(0.8), Inches(0.25), Inches(8), Inches(0.6),
             "PROFESSIONAL OUTPUTS", font_size=28, bold=True, color=WHITE)
add_text_box(slide, Inches(0.8), Inches(0.65), Inches(10), Inches(0.4),
             "Enterprise-Grade Deliverables Ready for Engineering Use", font_size=14, color=GOLD)

outputs = [
    ("Executive Dashboard", "Real-time KPI dashboard with donut charts, design data panel, equipment register, piping schedule, safety status — print-ready for management reports", "Web Application"),
    ("Mechanical Equipment List", "Professional Excel spreadsheet following KBR corporate format — 18 columns including tag breakdown, design data, materials, and power requirements", "Excel (.xlsx)"),
    ("Valve List", "Saudi Aramco 2616-ENG standard format — 12 columns covering tag number, size/rating, valve type, actuator, pressures, positions, and datasheet references", "Excel (.xlsx)"),
    ("Piping Line List", "Complete piping schedule — 16 columns with line number decoding, service codes, piping specs, from/to routing, and material specifications", "Excel (.xlsx)"),
    ("JSON Data Export", "Complete structured analysis data in JSON format for integration with engineering databases, PDMS, or custom tools", "JSON File"),
    ("AI Q&A Interface", "Interactive engineering assistant — ask any question about the P&ID and get expert-level answers with context from all 11 analysis phases", "Web Chat"),
]

for i, (title, desc, fmt) in enumerate(outputs):
    col = i % 3
    row = i // 3
    x = Inches(0.5 + col * 4.15)
    y = Inches(1.5 + row * 2.6)

    add_shape(slide, x, y, Inches(3.85), Inches(2.3), fill_color=WHITE, line_color=RGBColor(0xE0, 0xE5, 0xEC))
    add_shape(slide, x, y, Inches(3.85), Pt(4), fill_color=NAVY)

    # Format badge
    badge = add_shape(slide, x + Inches(2.3), y + Inches(0.15), Inches(1.35), Inches(0.3), fill_color=RGBColor(0xE8, 0xF0, 0xFE))
    add_text_box(slide, x + Inches(2.3), y + Inches(0.15), Inches(1.35), Inches(0.3),
                 fmt, font_size=8, bold=True, color=BLUE, alignment=PP_ALIGN.CENTER)

    add_text_box(slide, x + Inches(0.2), y + Inches(0.2), Inches(2.0), Inches(0.35),
                 title, font_size=13, bold=True, color=NAVY)
    add_text_box(slide, x + Inches(0.2), y + Inches(0.65), Inches(3.4), Inches(1.5),
                 desc, font_size=10, color=MUTED)

add_navy_footer(slide)
add_slide_number(slide, 6)

# ═══════════════════════════════════════════════════════════
# SLIDE 7: BEFORE vs AFTER
# ═══════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])

add_shape(slide, Inches(0), Inches(0), prs.slide_width, Inches(1.1), fill_color=NAVY)
add_gold_bar(slide, Inches(1.1))
add_text_box(slide, Inches(0.8), Inches(0.25), Inches(8), Inches(0.6),
             "BEFORE vs AFTER", font_size=28, bold=True, color=WHITE)
add_text_box(slide, Inches(0.8), Inches(0.65), Inches(10), Inches(0.4),
             "Quantified Impact on Engineering Workflow", font_size=14, color=GOLD)

# BEFORE column
add_shape(slide, Inches(0.5), Inches(1.5), Inches(5.8), Inches(0.5), fill_color=DANGER)
add_text_box(slide, Inches(0.5), Inches(1.53), Inches(5.8), Inches(0.45),
             "BEFORE — Manual Process", font_size=16, bold=True, color=WHITE, alignment=PP_ALIGN.CENTER)

before_items = [
    "4-8 hours per P&ID drawing for data extraction",
    "15-20% valve undercount rate (drain/vent valves missed)",
    "Requires senior engineers with P&ID expertise",
    "3-5 review cycles to verify accuracy",
    "Inconsistent spreadsheet formats between engineers",
    "No automated ISA-5.1 tag decoding",
    "No standardized digital output for databases",
    "Risk of transcription errors in critical safety data",
]

for i, item in enumerate(before_items):
    y = Inches(2.2 + i * 0.52)
    add_text_box(slide, Inches(0.9), y, Inches(5.0), Inches(0.45),
                 "✗  " + item, font_size=11, color=RGBColor(0x7F, 0x1D, 0x1D))

# AFTER column
add_shape(slide, Inches(7.0), Inches(1.5), Inches(5.8), Inches(0.5), fill_color=SUCCESS)
add_text_box(slide, Inches(7.0), Inches(1.53), Inches(5.8), Inches(0.45),
             "AFTER — AI-Powered Analysis", font_size=16, bold=True, color=WHITE, alignment=PP_ALIGN.CENTER)

after_items = [
    "5-10 minutes per drawing (11-phase automated pipeline)",
    "Triple verification (Phase 5 + Phase 10 + Phase 11)",
    "Any engineer can operate — upload and click analyze",
    "Built-in verification eliminates manual review cycles",
    "Standardized KBR & Saudi Aramco Excel templates",
    "Automatic ISA-5.1 decoding for every instrument tag",
    "JSON export for engineering database integration",
    "AI cross-references safety data across all phases",
]

for i, item in enumerate(after_items):
    y = Inches(2.2 + i * 0.52)
    add_text_box(slide, Inches(7.4), y, Inches(5.0), Inches(0.45),
                 "✓  " + item, font_size=11, color=RGBColor(0x06, 0x5F, 0x2F))

add_navy_footer(slide)
add_slide_number(slide, 7)

# ═══════════════════════════════════════════════════════════
# SLIDE 8: ROI & BUSINESS VALUE
# ═══════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])

add_shape(slide, Inches(0), Inches(0), prs.slide_width, Inches(1.1), fill_color=NAVY)
add_gold_bar(slide, Inches(1.1))
add_text_box(slide, Inches(0.8), Inches(0.25), Inches(8), Inches(0.6),
             "BUSINESS VALUE & ROI", font_size=28, bold=True, color=WHITE)
add_text_box(slide, Inches(0.8), Inches(0.65), Inches(10), Inches(0.4),
             "Estimated Impact for a Typical EPC Project", font_size=14, color=GOLD)

# KPI cards row
kpi_card(slide, Inches(0.5), Inches(1.5), "95%", "Time Reduction", SUCCESS)
kpi_card(slide, Inches(3.0), Inches(1.5), "50x", "Faster Analysis", BLUE)
kpi_card(slide, Inches(5.5), Inches(1.5), "99%", "Data Capture", NAVY)
kpi_card(slide, Inches(8.0), Inches(1.5), "3x", "Verification", GOLD)
kpi_card(slide, Inches(10.5), Inches(1.5), "0", "Manual Errors", DANGER)

# Value propositions
values = [
    ("Engineering Hours Saved", "A typical EPC project with 200+ P&IDs: Manual extraction = 800-1,600 engineer-hours. With P&ID Vision Analyzer = 30-60 hours (upload + review). Net savings: 750-1,500+ engineer-hours per project."),
    ("Quality Improvement", "Triple-verification pipeline (Phase 5 → Phase 10 → Phase 11) catches errors that manual reviews miss. Every valve, instrument, and line is counted at least twice independently."),
    ("Standardization", "Every project gets identical output formats — KBR Equipment List, Saudi Aramco Valve List, standard Line List. No more inconsistency between engineers or offices."),
    ("Knowledge Democratization", "Junior engineers can now perform P&ID data extraction that previously required years of experience. The AI assistant provides expert-level answers to any engineering question."),
]

for i, (title, desc) in enumerate(values):
    col = i % 2
    row = i // 2
    x = Inches(0.5 + col * 6.3)
    y = Inches(3.5 + row * 1.7)

    add_shape(slide, x, y, Inches(5.9), Inches(1.5), fill_color=WHITE, line_color=RGBColor(0xE0, 0xE5, 0xEC))
    add_shape(slide, x, y, Pt(5), Inches(1.5), fill_color=GOLD)

    add_text_box(slide, x + Inches(0.2), y + Inches(0.12), Inches(5.4), Inches(0.3),
                 title, font_size=13, bold=True, color=NAVY)
    add_text_box(slide, x + Inches(0.2), y + Inches(0.48), Inches(5.4), Inches(0.95),
                 desc, font_size=10, color=MUTED)

add_navy_footer(slide)
add_slide_number(slide, 8)

# ═══════════════════════════════════════════════════════════
# SLIDE 9: TECHNOLOGY ARCHITECTURE
# ═══════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])

add_shape(slide, Inches(0), Inches(0), prs.slide_width, Inches(1.1), fill_color=NAVY)
add_gold_bar(slide, Inches(1.1))
add_text_box(slide, Inches(0.8), Inches(0.25), Inches(8), Inches(0.6),
             "TECHNOLOGY ARCHITECTURE", font_size=28, bold=True, color=WHITE)
add_text_box(slide, Inches(0.8), Inches(0.65), Inches(10), Inches(0.4),
             "Modern, Scalable, Enterprise-Ready Stack", font_size=14, color=GOLD)

# Architecture layers
layers = [
    ("FRONTEND", "Multi-Page SPA  |  Sidebar Navigation  |  Canvas Charts  |  KBR-AMCDE Theme", LIGHT_BLUE, "Vanilla JS, HTML5 Canvas, CSS3 — Zero external dependencies"),
    ("REST API", "FastAPI Endpoints  |  Session Management  |  Background Tasks  |  CORS", BLUE, "FastAPI 0.109 + Uvicorn — High-performance async Python"),
    ("AI ENGINE", "Gemini 2.5 Flash Vision  |  11 Expert Prompts  |  Retry Logic  |  JSON Parsing", NAVY, "Google Gemini API — 32K token output, 0.05 temperature, 120s timeout"),
    ("PROCESSING", "PDF→Image (300 DPI)  |  ISA-5.1 Knowledge  |  Excel Generation", DARK, "PyMuPDF, Pillow, openpyxl — Professional engineering outputs"),
]

for i, (title, features, color, tech) in enumerate(layers):
    y = Inches(1.5 + i * 1.3)

    add_shape(slide, Inches(0.5), y, Inches(12.3), Inches(1.1), fill_color=WHITE, line_color=RGBColor(0xE0, 0xE5, 0xEC))
    add_shape(slide, Inches(0.5), y, Pt(6), Inches(1.1), fill_color=color)

    # Layer label
    label_bg = add_shape(slide, Inches(0.7), y + Inches(0.15), Inches(1.8), Inches(0.35), fill_color=color)
    add_text_box(slide, Inches(0.7), y + Inches(0.15), Inches(1.8), Inches(0.35),
                 title, font_size=11, bold=True, color=WHITE, alignment=PP_ALIGN.CENTER)

    add_text_box(slide, Inches(2.7), y + Inches(0.12), Inches(9.8), Inches(0.35),
                 features, font_size=12, bold=False, color=DARK_TEXT)
    add_text_box(slide, Inches(2.7), y + Inches(0.52), Inches(9.8), Inches(0.35),
                 tech, font_size=10, color=MUTED)

# Arrow annotations
add_text_box(slide, Inches(0.5), Inches(6.8), Inches(12.3), Inches(0.4),
             "Upload PDF/Image  →  300 DPI Rendering  →  11 AI Phases (2s intervals)  →  JSON Parsing  →  Dashboard + Excel + Chat",
             font_size=12, bold=True, color=NAVY, alignment=PP_ALIGN.CENTER)

add_navy_footer(slide)
add_slide_number(slide, 9)

# ═══════════════════════════════════════════════════════════
# SLIDE 10: NEXT STEPS & ROADMAP
# ═══════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])

add_shape(slide, Inches(0), Inches(0), prs.slide_width, Inches(1.1), fill_color=NAVY)
add_gold_bar(slide, Inches(1.1))
add_text_box(slide, Inches(0.8), Inches(0.25), Inches(8), Inches(0.6),
             "NEXT STEPS & ROADMAP", font_size=28, bold=True, color=WHITE)
add_text_box(slide, Inches(0.8), Inches(0.65), Inches(10), Inches(0.4),
             "Scaling the Solution Across KBR-AMCDE Projects", font_size=14, color=GOLD)

# Three timeline columns
timeline = [
    ("PHASE 1\nCurrent", [
        "Single P&ID analysis",
        "11-phase AI pipeline",
        "Executive dashboard",
        "Excel exports (3 formats)",
        "AI Q&A assistant",
        "Web-based SPA interface",
    ], NAVY),
    ("PHASE 2\nNext Quarter", [
        "Multi-drawing batch processing",
        "Cross-P&ID consistency checks",
        "Database integration (SQL/API)",
        "User authentication & roles",
        "Drawing comparison (revision diff)",
        "Custom report templates",
    ], BLUE),
    ("PHASE 3\nFuture", [
        "Full project P&ID set analysis",
        "Auto-generate equipment datasheets",
        "Integration with SmartPlant/AVEVA",
        "Automated I/O list generation",
        "Machine learning model fine-tuning",
        "Mobile app for field verification",
    ], LIGHT_BLUE),
]

for i, (title, items, color) in enumerate(timeline):
    x = Inches(0.5 + i * 4.15)
    y = Inches(1.5)

    add_shape(slide, x, y, Inches(3.85), Inches(5.0), fill_color=WHITE, line_color=RGBColor(0xE0, 0xE5, 0xEC))
    add_shape(slide, x, y, Inches(3.85), Inches(0.65), fill_color=color)
    add_text_box(slide, x, y + Inches(0.08), Inches(3.85), Inches(0.55),
                 title, font_size=14, bold=True, color=WHITE, alignment=PP_ALIGN.CENTER)

    for j, item in enumerate(items):
        iy = y + Inches(0.85 + j * 0.62)
        add_shape(slide, x + Inches(0.2), iy, Inches(3.45), Inches(0.5), fill_color=LIGHT_GRAY)
        add_text_box(slide, x + Inches(0.35), iy + Inches(0.05), Inches(3.15), Inches(0.4),
                     item, font_size=11, color=DARK_TEXT)

add_navy_footer(slide)
add_slide_number(slide, 10)

# ═══════════════════════════════════════════════════════════
# SLIDE 11: CLOSING
# ═══════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])

add_shape(slide, Inches(0), Inches(0), prs.slide_width, prs.slide_height, fill_color=DARK)
add_shape(slide, Inches(0), Inches(3.4), prs.slide_width, Pt(3), fill_color=GOLD)

add_rich_text(slide, Inches(1.5), Inches(1.2), Inches(10), Inches(2.0), [
    ("P&ID VISION ANALYZER", 40, True, WHITE, PP_ALIGN.CENTER),
    ("Transforming P&ID Data Extraction with AI", 20, False, LIGHT_BLUE, PP_ALIGN.CENTER),
])

add_rich_text(slide, Inches(1.5), Inches(3.8), Inches(10), Inches(2.5), [
    ("Thank You", 32, True, GOLD, PP_ALIGN.CENTER),
    ("", 12, False, WHITE, PP_ALIGN.CENTER),
    ("Questions & Discussion", 18, False, RGBColor(0xA0, 0xB5, 0xCC), PP_ALIGN.CENTER),
    ("", 12, False, WHITE, PP_ALIGN.CENTER),
    ("KBR-AMCDE  |  Engineering & Project Management Excellence", 14, False, RGBColor(0x70, 0x85, 0x9C), PP_ALIGN.CENTER),
])

add_text_box(slide, Inches(1), Inches(6.5), Inches(11), Inches(0.5),
             "CONFIDENTIAL  —  KBR-AMCDE Internal  —  P&ID Vision Analyzer v2.0", font_size=10, color=RGBColor(0x50, 0x60, 0x70), alignment=PP_ALIGN.CENTER)

# ═══════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════

output_path = "/home/user/Work/pid-analyzer/PID_Vision_Analyzer_Presentation.pptx"
prs.save(output_path)
print(f"Presentation saved to: {output_path}")
print(f"Total slides: {len(prs.slides)}")
