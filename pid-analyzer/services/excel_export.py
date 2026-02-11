"""
Excel Export Service for P&ID Analysis Results.
Generates 3 professional engineering spreadsheets:
1. Mechanical Equipment List (KBR format)
2. Valve List (Saudi Aramco format)
3. Line List
"""

import io
import json
import re
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter


# ── Shared style constants ──

THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)
MEDIUM_BORDER = Border(
    left=Side(style="medium"),
    right=Side(style="medium"),
    top=Side(style="medium"),
    bottom=Side(style="medium"),
)

NAVY_FILL = PatternFill(start_color="0A1628", end_color="0A1628", fill_type="solid")
DARK_BLUE_FILL = PatternFill(start_color="1E3A5F", end_color="1E3A5F", fill_type="solid")
YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
LIGHT_GRAY_FILL = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
WHITE_FILL = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
LIGHT_BLUE_FILL = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")

HEADER_FONT = Font(name="Arial", bold=True, size=10, color="FFFFFF")
TITLE_FONT = Font(name="Arial", bold=True, size=14)
SUB_TITLE_FONT = Font(name="Arial", bold=True, size=11)
DATA_FONT = Font(name="Arial", size=9)
DATA_FONT_BOLD = Font(name="Arial", size=9, bold=True)
SMALL_FONT = Font(name="Arial", size=8)

CENTER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT_ALIGN = Alignment(horizontal="left", vertical="center", wrap_text=True)
RIGHT_ALIGN = Alignment(horizontal="right", vertical="center", wrap_text=True)


def _deep_find(obj, keys):
    """Recursively search nested dict/list for first value matching any key."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            k_lower = k.lower().replace(" ", "_").replace("-", "_")
            for target in keys:
                if k_lower == target.lower():
                    return v
            result = _deep_find(v, keys)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = _deep_find(item, keys)
            if result is not None:
                return result
    return None


def _get_list(obj, keys):
    """Find a list value from nested structure."""
    val = _deep_find(obj, keys)
    if isinstance(val, list):
        return val
    return []


def _get_str(obj, keys, default=""):
    """Find a string value from nested structure."""
    val = _deep_find(obj, keys)
    if val is not None:
        return str(val)
    return default


def _safe_get(d, key, default=""):
    """Safely get a value from a dict."""
    if isinstance(d, dict):
        return d.get(key, default) or default
    return default


def _apply_border_range(ws, min_row, max_row, min_col, max_col, border=THIN_BORDER):
    """Apply border to a range of cells."""
    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            ws.cell(row=row, column=col).border = border


def _set_cell(ws, row, col, value, font=DATA_FONT, fill=None, alignment=LEFT_ALIGN, border=THIN_BORDER):
    """Set cell value and style."""
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = font
    if fill:
        cell.fill = fill
    cell.alignment = alignment
    cell.border = border
    return cell


# ═══════════════════════════════════════════════════════════════════════
# 1. MECHANICAL EQUIPMENT LIST (KBR Format)
# ═══════════════════════════════════════════════════════════════════════

def generate_equipment_list(analysis_results: dict) -> io.BytesIO:
    """Generate Mechanical Equipment List Excel file in KBR format."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Mechanical Equipment List"
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    phases = analysis_results.get("phases", {})
    p1 = phases.get("phase1_document_context", {}).get("result", {})
    p4 = phases.get("phase4_equipment_scan", {}).get("result", {})
    p9 = phases.get("phase9_safety_analysis", {}).get("result", {})

    title_block = _deep_find(p1, ["title_block"]) or {}
    design_data = _deep_find(p1, ["design_data"]) or {}
    equipment_list = _get_list(p4, ["equipment"])

    # ── Column widths (A=1 to T=20) ──
    col_widths = [5, 6, 6, 7, 6, 22, 22, 14, 12, 10, 10, 10, 18, 12, 12, 14, 14, 20]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # ── Row 1-5: Header block ──
    # Client info (left side)
    _set_cell(ws, 1, 1, "Client:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    ws.merge_cells("B1:F1")
    _set_cell(ws, 1, 2, _safe_get(title_block, "company", "SAUDI ARAMCO"), font=DATA_FONT_BOLD)

    _set_cell(ws, 2, 1, "Project\nTitle:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    ws.merge_cells("B2:F2")
    _set_cell(ws, 2, 2, _safe_get(title_block, "title", ""), font=DATA_FONT_BOLD)

    _set_cell(ws, 3, 1, "Location:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    ws.merge_cells("B3:F3")
    _set_cell(ws, 3, 2, _safe_get(title_block, "area_unit", ""), font=DATA_FONT_BOLD)

    _set_cell(ws, 4, 1, "Description:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    ws.merge_cells("B4:F4")
    _set_cell(ws, 4, 2, _safe_get(title_block, "project_name", ""), font=DATA_FONT_BOLD)

    # Title (center)
    ws.merge_cells("G2:L3")
    title_cell = _set_cell(ws, 2, 7, "MECHANICAL EQUIPMENT LIST",
                           font=TITLE_FONT, alignment=CENTER_ALIGN)

    # Document info (right side)
    _set_cell(ws, 1, 16, "Document No.:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    ws.merge_cells("Q1:R1")
    _set_cell(ws, 1, 17, _safe_get(title_block, "drawing_number", ""), font=DATA_FONT_BOLD)

    _set_cell(ws, 2, 16, "Revision No.:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    ws.merge_cells("Q2:R2")
    _set_cell(ws, 2, 17, _safe_get(title_block, "revision", ""), font=DATA_FONT_BOLD)

    _set_cell(ws, 3, 16, "Date:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    ws.merge_cells("Q3:R3")
    _set_cell(ws, 3, 17, _safe_get(title_block, "date", ""), font=DATA_FONT_BOLD)

    # ── Row 6-7: Column headers (two rows merged) ──
    headers_row1 = [
        "Qty.", "Equipment Tag No.", None, None, None,
        "Equipment Title", "Type", "Datasheet\nSpecifications",
        "P&ID\nPlot Plan", "Capacity", "Service",
        "Design Pressure\n(psig)", "Design\nTemperature\n(°F)",
        "Dimensions\nWeight", "Driver Type",
        "Power\nRequirements", "Materials of\nConstruction",
        "Remarks"
    ]

    headers_row2 = [
        None, "Plant\nNo.", "Equip.\nMarking", "Seq. No.", "Suffix",
        None, None, None, None, None, None, None, None, None, None, None, None, None
    ]

    row = 6
    for ci, h in enumerate(headers_row1, 1):
        if h is not None:
            cell = _set_cell(ws, row, ci, h, font=HEADER_FONT,
                             fill=DARK_BLUE_FILL, alignment=CENTER_ALIGN, border=MEDIUM_BORDER)
    # Merge "Equipment Tag No." across B6:E6
    ws.merge_cells("B6:E6")
    # Merge single-row headers across rows 6-7
    for col_idx in [1, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]:
        col_letter = get_column_letter(col_idx)
        ws.merge_cells(f"{col_letter}6:{col_letter}7")

    row = 7
    for ci, h in enumerate(headers_row2, 1):
        if h is not None:
            _set_cell(ws, row, ci, h, font=HEADER_FONT,
                      fill=DARK_BLUE_FILL, alignment=CENTER_ALIGN, border=MEDIUM_BORDER)

    # ── Row 8: Area/unit separator ──
    row = 8
    area_name = _safe_get(title_block, "area_unit", "")
    if area_name:
        ws.merge_cells(f"A{row}:R{row}")
        _set_cell(ws, row, 1, area_name, font=DATA_FONT_BOLD,
                  fill=YELLOW_FILL, alignment=LEFT_ALIGN, border=THIN_BORDER)
        for ci in range(2, 19):
            _set_cell(ws, row, ci, None, fill=YELLOW_FILL, border=THIN_BORDER)

    # ── Equipment data rows ──
    data_start = 9
    for idx, eq in enumerate(equipment_list):
        r = data_start + idx
        tag = _safe_get(eq, "tag_number", "")

        # Parse tag into components (e.g., "V-101" -> plant="", marking="V", seq="101")
        tag_parts = tag.replace("-", " ").split()
        plant_no = ""
        equip_marking = tag_parts[0] if len(tag_parts) > 0 else ""
        seq_no = tag_parts[1] if len(tag_parts) > 1 else ""
        suffix = tag_parts[2] if len(tag_parts) > 2 else ""

        _set_cell(ws, r, 1, idx + 1, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 2, plant_no, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 3, equip_marking, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 4, seq_no, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 5, suffix, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 6, _safe_get(eq, "service", ""), font=DATA_FONT)
        _set_cell(ws, r, 7, _safe_get(eq, "equipment_type", ""), font=DATA_FONT)
        _set_cell(ws, r, 8, "", font=DATA_FONT)  # Datasheet
        _set_cell(ws, r, 9, _safe_get(title_block, "drawing_number", ""), font=DATA_FONT)
        _set_cell(ws, r, 10, _safe_get(eq, "size_rating", ""), font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 11, _safe_get(eq, "service", ""), font=DATA_FONT)
        _set_cell(ws, r, 12, _safe_get(design_data, "design_pressure", ""), font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 13, _safe_get(design_data, "design_temperature", ""), font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 14, _safe_get(eq, "design_conditions", ""), font=DATA_FONT)
        _set_cell(ws, r, 15, "", font=DATA_FONT)  # Driver Type
        _set_cell(ws, r, 16, "", font=DATA_FONT)  # Power Requirements
        _set_cell(ws, r, 17, _safe_get(design_data, "material_grade", ""), font=DATA_FONT)
        _set_cell(ws, r, 18, "", font=DATA_FONT)  # Remarks

        # Alternate row fill
        if idx % 2 == 1:
            for ci in range(1, 19):
                ws.cell(row=r, column=ci).fill = LIGHT_GRAY_FILL

    # ── Notes section ──
    notes_row = data_start + max(len(equipment_list), 1) + 2
    _set_cell(ws, notes_row, 1, "NOTE:", font=DATA_FONT_BOLD)
    _set_cell(ws, notes_row + 1, 1,
              "1. Equipment tag numbers are temporary and shall be finalized during detailed design stage.",
              font=SMALL_FONT)
    _set_cell(ws, notes_row + 2, 1,
              "2. Motor ratings are preliminary and shall be confirmed by Vendor.",
              font=SMALL_FONT)
    _set_cell(ws, notes_row + 3, 1,
              "3. VTC: VENDOR TO CONFIRM / N/A: NOT APPLICABLE",
              font=SMALL_FONT)

    # Print setup
    ws.print_area = f"A1:R{notes_row + 4}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# ═══════════════════════════════════════════════════════════════════════
# 2. VALVE LIST (Saudi Aramco Format)
# ═══════════════════════════════════════════════════════════════════════

def generate_valve_list(analysis_results: dict) -> io.BytesIO:
    """Generate Valve List Excel file in Saudi Aramco format."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Valve List"
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    phases = analysis_results.get("phases", {})
    p1 = phases.get("phase1_document_context", {}).get("result", {})
    p5 = phases.get("phase5_valve_analysis", {}).get("result", {})

    title_block = _deep_find(p1, ["title_block"]) or {}
    design_data = _deep_find(p1, ["design_data"]) or {}
    valve_list = _get_list(p5, ["valves"])

    # Column widths: A-L (12 columns)
    col_widths = [6, 20, 12, 12, 10, 18, 24, 20, 18, 12, 12, 18]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # ── Row 1: Standard reference ──
    ws.merge_cells("A1:L1")
    _set_cell(ws, 1, 1, "Saudi Aramco 2616-ENG (11/2010)", font=SMALL_FONT)

    # ── Row 2-3: Company title ──
    ws.merge_cells("A2:L3")
    _set_cell(ws, 2, 1, "SAUDI ARABIAN OIL COMPANY",
              font=Font(name="Arial", bold=True, size=16), alignment=CENTER_ALIGN)

    # ── Row 4: Project / document info ──
    _set_cell(ws, 4, 1, "Project:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    ws.merge_cells("B4:D4")
    _set_cell(ws, 4, 2, _safe_get(title_block, "project_name", ""), font=DATA_FONT_BOLD)
    _set_cell(ws, 4, 6, "Document No.:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    _set_cell(ws, 4, 7, _safe_get(title_block, "drawing_number", ""), font=DATA_FONT_BOLD)
    _set_cell(ws, 4, 9, "Rev:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    _set_cell(ws, 4, 10, _safe_get(title_block, "revision", ""), font=DATA_FONT_BOLD)
    _set_cell(ws, 4, 11, "Date:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    _set_cell(ws, 4, 12, _safe_get(title_block, "date", ""), font=DATA_FONT_BOLD)

    # ── Row 6-7: Column headers ──
    headers = [
        "NO.", "TAG NUMBER", "SIZE\nRATING", "VALVE\nTYPE",
        "ACTUATOR", "REFERENCE P&ID", "SERVICE /\nLOCATION",
        "UPSTREAM PRESSURE P1\nPRESSURE DROP \u0394P",
        "TEMPERATURE", "NORMAL\nPOSITION", "FAIL\nPOSITION",
        "REFERENCE\nVALVE DATASHEET"
    ]

    header_row = 6
    for ci, h in enumerate(headers, 1):
        cl = get_column_letter(ci)
        ws.merge_cells(f"{cl}{header_row}:{cl}{header_row + 1}")
        _set_cell(ws, header_row, ci, h, font=HEADER_FONT,
                  fill=DARK_BLUE_FILL, alignment=CENTER_ALIGN, border=MEDIUM_BORDER)

    # ── Valve data rows ──
    data_start = 8
    for idx, valve in enumerate(valve_list):
        r = data_start + idx
        tag = _safe_get(valve, "tag_number", "")
        v_type = _safe_get(valve, "valve_type", "")
        size = _safe_get(valve, "size", "")
        line_no = _safe_get(valve, "line_number", "")
        location = _safe_get(valve, "location_description", "")
        fail_pos = _safe_get(valve, "fail_position", "")
        normal_pos = _safe_get(valve, "normal_position", "")
        actuator = _safe_get(valve, "actuator_type", "")

        # Get pressure/temp from design data
        pressure = _safe_get(design_data, "design_pressure", "")
        temperature = _safe_get(design_data, "design_temperature", "")
        pid_ref = _safe_get(title_block, "drawing_number", "")

        service_desc = location if location else line_no
        pressure_str = f"P1: {pressure}" if pressure else ""
        temp_str = temperature if temperature else ""

        _set_cell(ws, r, 1, idx + 1, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 2, tag, font=DATA_FONT_BOLD)
        _set_cell(ws, r, 3, size, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 4, v_type.upper(), font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 5, actuator, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 6, pid_ref, font=DATA_FONT)
        _set_cell(ws, r, 7, service_desc, font=DATA_FONT)
        _set_cell(ws, r, 8, pressure_str, font=DATA_FONT)
        _set_cell(ws, r, 9, temp_str, font=DATA_FONT)
        _set_cell(ws, r, 10, normal_pos, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 11, fail_pos, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 12, "", font=DATA_FONT)  # Reference datasheet

        # Alternate shading
        if idx % 2 == 1:
            for ci in range(1, 13):
                ws.cell(row=r, column=ci).fill = LIGHT_GRAY_FILL

    # ── Summary row ──
    summary_row = data_start + max(len(valve_list), 1) + 1
    ws.merge_cells(f"A{summary_row}:B{summary_row}")
    _set_cell(ws, summary_row, 1, f"Total Valves: {len(valve_list)}",
              font=DATA_FONT_BOLD, fill=LIGHT_BLUE_FILL, alignment=LEFT_ALIGN, border=MEDIUM_BORDER)

    # ── Disclaimer text ──
    disclaimer_row = summary_row + 2
    ws.merge_cells(f"A{disclaimer_row}:L{disclaimer_row}")
    _set_cell(ws, disclaimer_row, 1,
              "THIS REVISION IS NOT TO BE USED FOR CONSTRUCTION UNTIL CERTIFIED AND DATED",
              font=Font(name="Arial", size=7, italic=True))

    # Print setup
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def _stringify_list(items):
    """Convert a list of mixed str/dict items into a joined string."""
    if not isinstance(items, list):
        return str(items) if items else ""
    parts = []
    for item in items:
        if isinstance(item, dict):
            parts.append(", ".join(str(v) for v in item.values() if v))
        else:
            parts.append(str(item))
    return ", ".join(parts)


# ═══════════════════════════════════════════════════════════════════════
# 3. LINE LIST
# ═══════════════════════════════════════════════════════════════════════

def generate_line_list(analysis_results: dict) -> io.BytesIO:
    """Generate Piping Line List Excel file."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Line List"
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    phases = analysis_results.get("phases", {})
    p1 = phases.get("phase1_document_context", {}).get("result", {})
    p7 = phases.get("phase7_piping_analysis", {}).get("result", {})

    title_block = _deep_find(p1, ["title_block"]) or {}
    design_data = _deep_find(p1, ["design_data"]) or {}
    piping_lines = _get_list(p7, ["piping_lines"])

    # Column widths
    col_widths = [5, 22, 8, 10, 14, 12, 16, 16, 12, 10, 10, 14, 14, 14, 12, 20]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # ── Row 1-2: Title ──
    ws.merge_cells("A1:P1")
    _set_cell(ws, 1, 1, _safe_get(title_block, "company", "SAUDI ARABIAN OIL COMPANY"),
              font=Font(name="Arial", bold=True, size=14), alignment=CENTER_ALIGN)

    ws.merge_cells("A2:P2")
    _set_cell(ws, 2, 1, "PIPING LINE LIST",
              font=Font(name="Arial", bold=True, size=16), alignment=CENTER_ALIGN)

    # ── Row 3: Project info ──
    _set_cell(ws, 3, 1, "Project:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    ws.merge_cells("B3:F3")
    _set_cell(ws, 3, 2, _safe_get(title_block, "project_name", ""), font=DATA_FONT_BOLD)

    _set_cell(ws, 3, 10, "Document No.:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    ws.merge_cells("K3:L3")
    _set_cell(ws, 3, 11, _safe_get(title_block, "drawing_number", ""), font=DATA_FONT_BOLD)

    _set_cell(ws, 3, 14, "Rev:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    _set_cell(ws, 3, 15, _safe_get(title_block, "revision", ""), font=DATA_FONT_BOLD)

    # ── Row 4: Location ──
    _set_cell(ws, 4, 1, "Location:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    ws.merge_cells("B4:F4")
    _set_cell(ws, 4, 2, _safe_get(title_block, "area_unit", ""), font=DATA_FONT_BOLD)

    _set_cell(ws, 4, 10, "Date:", font=DATA_FONT_BOLD, fill=LIGHT_GRAY_FILL)
    ws.merge_cells("K4:L4")
    _set_cell(ws, 4, 11, _safe_get(title_block, "date", ""), font=DATA_FONT_BOLD)

    # ── Row 6-7: Column headers ──
    headers = [
        "No.", "Line Number", "Nominal\nSize", "Service\nCode",
        "Service\nDescription", "Piping\nSpec/Class",
        "From", "To", "Flow\nDirection",
        "Design\nPressure", "Design\nTemperature",
        "Material /\nGrade", "Insulation\nType",
        "Test\nPressure", "P&ID\nReference",
        "Remarks"
    ]

    header_row = 6
    for ci, h in enumerate(headers, 1):
        cl = get_column_letter(ci)
        ws.merge_cells(f"{cl}{header_row}:{cl}{header_row + 1}")
        _set_cell(ws, header_row, ci, h, font=HEADER_FONT,
                  fill=DARK_BLUE_FILL, alignment=CENTER_ALIGN, border=MEDIUM_BORDER)

    # ── Line data rows ──
    data_start = 8
    for idx, line in enumerate(piping_lines):
        r = data_start + idx
        line_no = _safe_get(line, "line_number", "")
        size = _safe_get(line, "size", "")
        svc_code = _safe_get(line, "service_code", "")
        svc_desc = _safe_get(line, "service_description", "")
        spec = _safe_get(line, "piping_spec", "")
        from_eq = _safe_get(line, "from", "")
        to_eq = _safe_get(line, "to", "")
        flow_dir = _safe_get(line, "flow_direction", "")

        # Get design data
        pressure = _safe_get(design_data, "design_pressure", "")
        temperature = _safe_get(design_data, "design_temperature", "")
        material = _safe_get(design_data, "material_grade", "")

        # Special items
        specials = _safe_get(line, "special_items", [])
        special_str = _stringify_list(specials)

        # Connection to other P&IDs
        connections = _safe_get(line, "connections_to_other_pids", [])
        conn_str = _stringify_list(connections)

        pid_ref = _safe_get(title_block, "drawing_number", "")

        _set_cell(ws, r, 1, idx + 1, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 2, line_no, font=DATA_FONT_BOLD)
        _set_cell(ws, r, 3, size, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 4, svc_code, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 5, svc_desc, font=DATA_FONT)
        _set_cell(ws, r, 6, spec, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 7, from_eq, font=DATA_FONT)
        _set_cell(ws, r, 8, to_eq, font=DATA_FONT)
        _set_cell(ws, r, 9, flow_dir, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 10, pressure, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 11, temperature, font=DATA_FONT, alignment=CENTER_ALIGN)
        _set_cell(ws, r, 12, material, font=DATA_FONT)
        _set_cell(ws, r, 13, "", font=DATA_FONT)  # Insulation
        _set_cell(ws, r, 14, "", font=DATA_FONT, alignment=CENTER_ALIGN)  # Test pressure
        _set_cell(ws, r, 15, pid_ref, font=DATA_FONT)
        remarks = special_str if special_str else conn_str
        _set_cell(ws, r, 16, remarks, font=DATA_FONT)

        # Alternate row fill
        if idx % 2 == 1:
            for ci in range(1, 17):
                ws.cell(row=r, column=ci).fill = LIGHT_GRAY_FILL

    # ── Summary row ──
    summary_row = data_start + max(len(piping_lines), 1) + 1
    ws.merge_cells(f"A{summary_row}:B{summary_row}")
    _set_cell(ws, summary_row, 1, f"Total Lines: {len(piping_lines)}",
              font=DATA_FONT_BOLD, fill=LIGHT_BLUE_FILL, alignment=LEFT_ALIGN, border=MEDIUM_BORDER)

    # ── Notes ──
    notes_row = summary_row + 2
    _set_cell(ws, notes_row, 1, "NOTES:", font=DATA_FONT_BOLD)
    _set_cell(ws, notes_row + 1, 1,
              "1. All dimensions are nominal unless stated otherwise.", font=SMALL_FONT)
    _set_cell(ws, notes_row + 2, 1,
              "2. Service codes per project piping specification.", font=SMALL_FONT)
    _set_cell(ws, notes_row + 3, 1,
              "3. This list is extracted from P&ID analysis and shall be verified against detailed engineering.",
              font=SMALL_FONT)

    # Print setup
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
