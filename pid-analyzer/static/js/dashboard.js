/**
 * P&ID Vision Analyzer — Executive Dashboard (KBR-Style)
 * Canvas-based donut charts, structured data panels, professional layout.
 */

(function () {
  "use strict";

  // KBR-AMCDE color palettes
  var VALVE_COLORS = [
    "#003a70", "#1a5091", "#4a90d9", "#0d8a6a",
    "#b45309", "#c52a2a", "#5b47b0", "#0d8a4a",
    "#7c2d12", "#4a5568", "#c8a951"
  ];
  var INSTRUMENT_COLORS = [
    "#003a70", "#1a5091", "#b45309", "#5b47b0",
    "#c52a2a", "#4a5568"
  ];

  // ── Exposed global function called by app.js after results load ──
  window.renderDashboard = function (data) {
    var section = document.getElementById("dashboard-section");
    section.classList.remove("hidden");

    populateHeader(data);
    populateKPIs(data);
    populateDesignData(data);
    renderDonutChart("db-valve-chart", "db-valve-legend", getValveBreakdown(data), VALVE_COLORS, "db-valve-total");
    renderDonutChart("db-instrument-chart", "db-instrument-legend", getInstrumentBreakdown(data), INSTRUMENT_COLORS, "db-instrument-total");
    populateSafety(data);
    populateEquipmentTable(data);
    populatePipingTable(data);
    populateFlowSummary(data);
    populateNotes(data);
    populateRefs(data);
    renderConfidenceRing(data.confidence || 0);

    var genTime = document.getElementById("db-gen-time");
    if (data.end_time) {
      genTime.textContent = "Generated: " + new Date(data.end_time).toLocaleString();
    }

    // Wire export button
    document.getElementById("db-export-btn").addEventListener("click", function () {
      if (window._pidSessionId) window.open("/api/export/" + window._pidSessionId, "_blank");
    });
  };

  // ── Helpers ──

  function deepFind(obj, keys) {
    if (!obj || typeof obj !== "object") return null;
    if (Array.isArray(obj)) {
      for (var i = 0; i < obj.length; i++) {
        var r = deepFind(obj[i], keys);
        if (r !== null) return r;
      }
      return null;
    }
    for (var k in obj) {
      var kn = k.toLowerCase().replace(/[\s\-]/g, "_");
      for (var j = 0; j < keys.length; j++) {
        if (kn === keys[j].toLowerCase()) return obj[k];
      }
    }
    for (var k2 in obj) {
      if (typeof obj[k2] === "object") {
        var r2 = deepFind(obj[k2], keys);
        if (r2 !== null) return r2;
      }
    }
    return null;
  }

  function phaseResult(data, phase) {
    return (data.phases && data.phases[phase] && data.phases[phase].result) || {};
  }

  function txt(v) { return (v === null || v === undefined || v === "") ? "--" : String(v); }

  // ── Header ──

  function populateHeader(data) {
    var p1 = phaseResult(data, "phase1_document_context");
    var tb = deepFind(p1, ["title_block"]) || {};
    var dd = deepFind(p1, ["design_data"]) || {};

    var title = txt(tb.title || tb.description);
    document.getElementById("db-drawing-title").textContent =
      title !== "--" ? title : "P&ID Analysis Report";
    document.getElementById("db-drawing-number").textContent =
      "Drawing: " + txt(tb.drawing_number);
    document.getElementById("db-revision").textContent =
      "Rev: " + txt(tb.revision);
    document.getElementById("db-date").textContent =
      "Date: " + txt(tb.date);
  }

  // ── KPIs ──

  function populateKPIs(data) {
    var s = data.statistics || {};
    document.getElementById("db-kpi-equipment").textContent = s.equipment || 0;
    document.getElementById("db-kpi-valves").textContent = s.valves || 0;
    document.getElementById("db-kpi-instruments").textContent = s.instruments || 0;
    document.getElementById("db-kpi-lines").textContent = s.piping_lines || 0;
    document.getElementById("db-kpi-notes").textContent = s.notes || 0;
    var safety = (s.gas_detectors || 0) + (s.relief_devices || 0) + (s.esd_valves || 0);
    document.getElementById("db-kpi-safety").textContent = safety;
  }

  // ── Design Data ──

  function populateDesignData(data) {
    var p1 = phaseResult(data, "phase1_document_context");
    var dd = deepFind(p1, ["design_data"]) || {};
    // Also try phase 10 summary
    var p10 = phaseResult(data, "phase10_verification_summary");
    var ds = deepFind(p10, ["design_data_summary"]) || {};

    function pick() {
      for (var i = 0; i < arguments.length; i++) {
        var v = arguments[i];
        if (v && v !== "" && v !== "--" && v !== null) return v;
      }
      return "--";
    }

    document.getElementById("db-dd-service").textContent = pick(dd.service, ds.service);
    document.getElementById("db-dd-size").textContent = pick(ds.pipeline_size, dd.flow_rate);
    document.getElementById("db-dd-pressure").textContent = pick(dd.design_pressure, ds.design_pressure);
    document.getElementById("db-dd-temp").textContent = pick(dd.design_temperature, ds.design_temperature);
    document.getElementById("db-dd-maop").textContent = pick(dd.maop, ds.maop);
    document.getElementById("db-dd-material").textContent = pick(dd.material_grade, ds.material);
    document.getElementById("db-dd-flange").textContent = pick(dd.flange_rating, ds.flange_rating);
    document.getElementById("db-dd-code").textContent = pick(dd.design_code, ds.design_code);
  }

  // ── Valve Breakdown ──

  function getValveBreakdown(data) {
    var p5 = phaseResult(data, "phase5_valve_analysis");
    var cb = deepFind(p5, ["count_by_type"]) || {};
    var items = [];
    var labels = {
      gate: "Gate", globe: "Globe", ball: "Ball", plug: "Plug",
      butterfly: "Butterfly", check: "Check", control: "Control",
      mov: "MOV", relief_safety: "Relief/Safety", needle: "Needle", other: "Other"
    };
    for (var k in labels) {
      var v = cb[k] || 0;
      if (v > 0) items.push({ label: labels[k], value: v });
    }
    // Fallback: count from valves array
    if (items.length === 0) {
      var arr = deepFind(p5, ["valves"]);
      if (arr && Array.isArray(arr)) {
        var counts = {};
        arr.forEach(function (valve) {
          var t = (valve.valve_type || valve.type || "Other").toLowerCase();
          counts[t] = (counts[t] || 0) + 1;
        });
        for (var t in counts) {
          items.push({ label: t.charAt(0).toUpperCase() + t.slice(1), value: counts[t] });
        }
      }
    }
    return items;
  }

  function getInstrumentBreakdown(data) {
    var p6 = phaseResult(data, "phase6_instrumentation");
    var cb = deepFind(p6, ["count_by_category"]) || {};
    var items = [];
    var labels = {
      pressure: "Pressure", temperature: "Temperature", flow: "Flow",
      level: "Level", analysis: "Analysis", other: "Other"
    };
    for (var k in labels) {
      var v = cb[k] || 0;
      if (v > 0) items.push({ label: labels[k], value: v });
    }
    if (items.length === 0) {
      var arr = deepFind(p6, ["instruments"]);
      if (arr && Array.isArray(arr)) {
        var counts = {};
        arr.forEach(function (inst) {
          var mv = (inst.decoded && inst.decoded.measured_variable) || "Other";
          counts[mv] = (counts[mv] || 0) + 1;
        });
        for (var mv in counts) {
          items.push({ label: mv, value: counts[mv] });
        }
      }
    }
    return items;
  }

  // ── Canvas Donut Chart ──

  function renderDonutChart(canvasId, legendId, items, colors, badgeId) {
    var canvas = document.getElementById(canvasId);
    var ctx = canvas.getContext("2d");
    var W = canvas.width, H = canvas.height;
    var cx = W / 2, cy = H / 2, R = Math.min(W, H) / 2 - 10, r = R * 0.55;
    var total = 0;
    items.forEach(function (it) { total += it.value; });

    // Badge
    if (badgeId) {
      document.getElementById(badgeId).textContent = total + " Total";
    }

    // Clear
    ctx.clearRect(0, 0, W, H);

    if (total === 0) {
      ctx.beginPath();
      ctx.arc(cx, cy, R, 0, Math.PI * 2);
      ctx.arc(cx, cy, r, 0, Math.PI * 2, true);
      ctx.fillStyle = "#e2e8f0";
      ctx.fill();
      ctx.font = "600 13px -apple-system, sans-serif";
      ctx.fillStyle = "#94a3b8";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("No Data", cx, cy);
      return;
    }

    var angle = -Math.PI / 2;
    items.forEach(function (it, i) {
      var slice = (it.value / total) * Math.PI * 2;
      ctx.beginPath();
      ctx.arc(cx, cy, R, angle, angle + slice);
      ctx.arc(cx, cy, r, angle + slice, angle, true);
      ctx.closePath();
      ctx.fillStyle = colors[i % colors.length];
      ctx.fill();
      angle += slice;
    });

    // Center text
    ctx.font = "800 22px -apple-system, sans-serif";
    ctx.fillStyle = "#1e293b";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(String(total), cx, cy - 6);
    ctx.font = "600 10px -apple-system, sans-serif";
    ctx.fillStyle = "#64748b";
    ctx.fillText("TOTAL", cx, cy + 12);

    // Legend
    var legend = document.getElementById(legendId);
    legend.innerHTML = "";
    items.forEach(function (it, i) {
      var row = document.createElement("div");
      row.className = "db-legend-item";
      var pct = Math.round((it.value / total) * 100);
      row.innerHTML =
        '<span class="db-legend-dot" style="background:' + colors[i % colors.length] + '"></span>' +
        '<span class="db-legend-label">' + esc(it.label) + '</span>' +
        '<span class="db-legend-val">' + it.value + ' (' + pct + '%)</span>';
      legend.appendChild(row);
    });
  }

  // ── Confidence Ring ──

  function renderConfidenceRing(pct) {
    var canvas = document.getElementById("db-confidence-canvas");
    var ctx = canvas.getContext("2d");
    var W = canvas.width, H = canvas.height;
    var cx = W / 2, cy = H / 2, R = 35, lw = 7;

    ctx.clearRect(0, 0, W, H);

    // Background ring
    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(255,255,255,0.15)";
    ctx.lineWidth = lw;
    ctx.stroke();

    // Value ring
    var color = pct >= 80 ? "#c8a951" : pct >= 50 ? "#4a90d9" : "#c52a2a";
    var endAngle = -Math.PI / 2 + (pct / 100) * Math.PI * 2;
    ctx.beginPath();
    ctx.arc(cx, cy, R, -Math.PI / 2, endAngle);
    ctx.strokeStyle = color;
    ctx.lineWidth = lw;
    ctx.lineCap = "round";
    ctx.stroke();

    document.getElementById("db-confidence-value").textContent = pct;
  }

  // ── Safety Panel ──

  function populateSafety(data) {
    var s = data.statistics || {};
    document.getElementById("db-sf-gas").textContent = s.gas_detectors || 0;
    document.getElementById("db-sf-relief").textContent = s.relief_devices || 0;
    document.getElementById("db-sf-esd").textContent = s.esd_valves || 0;

    var p9 = phaseResult(data, "phase9_safety_analysis");
    var ac = deepFind(p9, ["area_classification"]) || {};
    var areaText = [ac["class"], ac.division_or_zone].filter(Boolean).join(" / ") || "--";
    document.getElementById("db-sf-area").textContent = areaText;

    // Relief devices table
    var rd = deepFind(p9, ["relief_devices"]);
    if (rd && Array.isArray(rd) && rd.length > 0) {
      renderSubTable("db-relief-table-wrapper", rd,
        ["tag_number", "protected_equipment", "set_pressure", "discharge_to"],
        ["Tag", "Protects", "Set Press.", "Discharges To"]
      );
    }
  }

  // ── Equipment Table ──

  function populateEquipmentTable(data) {
    var p4 = phaseResult(data, "phase4_equipment_scan");
    var arr = deepFind(p4, ["equipment"]) || [];
    document.getElementById("db-equip-total").textContent = arr.length + " Items";
    if (arr.length > 0) {
      renderSubTable("db-equipment-table-wrapper", arr,
        ["tag_number", "equipment_type", "service", "size_rating", "location_on_drawing"],
        ["Tag Number", "Type", "Service", "Size/Rating", "Location"]
      );
    } else {
      document.getElementById("db-equipment-table-wrapper").innerHTML =
        '<p style="color:#94a3b8;font-size:0.82rem">No equipment data extracted</p>';
    }
  }

  // ── Piping Table ──

  function populatePipingTable(data) {
    var p7 = phaseResult(data, "phase7_piping_analysis");
    var arr = deepFind(p7, ["piping_lines"]) || [];
    document.getElementById("db-piping-total").textContent = arr.length + " Lines";
    if (arr.length > 0) {
      renderSubTable("db-piping-table-wrapper", arr,
        ["line_number", "size", "service_code", "service_description", "piping_spec", "from", "to"],
        ["Line Number", "Size", "Svc", "Service", "Spec", "From", "To"]
      );
    } else {
      document.getElementById("db-piping-table-wrapper").innerHTML =
        '<p style="color:#94a3b8;font-size:0.82rem">No piping line data extracted</p>';
    }
  }

  // ── Process Flow ──

  function populateFlowSummary(data) {
    var p8 = phaseResult(data, "phase8_connections_flow");
    var mf = deepFind(p8, ["main_process_flow"]) || {};
    var container = document.getElementById("db-flow-content");
    container.innerHTML = "";

    // Main flow
    var sec1 = document.createElement("div");
    sec1.className = "db-flow-section";
    var label1 = document.createElement("div");
    label1.className = "db-flow-label";
    label1.textContent = "Main Process Flow";
    sec1.appendChild(label1);

    var entry = mf.entry_point || mf.entry_from_drawing || "--";
    var exit = mf.exit_point || mf.exit_to_drawing || "--";
    var seq = mf.equipment_sequence || [];

    var flowHtml = '<span class="db-flow-arrow">' + esc(entry) + '</span>';
    seq.forEach(function (item) {
      flowHtml += '<span class="db-flow-arrow-sep"> → </span>';
      flowHtml += '<span class="db-flow-arrow">' + esc(typeof item === "string" ? item : JSON.stringify(item)) + '</span>';
    });
    flowHtml += '<span class="db-flow-arrow-sep"> → </span>';
    flowHtml += '<span class="db-flow-arrow">' + esc(exit) + '</span>';

    var flowDiv = document.createElement("div");
    flowDiv.innerHTML = flowHtml;
    sec1.appendChild(flowDiv);
    container.appendChild(sec1);

    // Utility connections
    var uc = deepFind(p8, ["utility_connections"]) || {};
    var hasUtil = false;
    var utilHtml = "";
    for (var uk in uc) {
      var uv = uc[uk];
      if (uv && ((Array.isArray(uv) && uv.length > 0) || (!Array.isArray(uv) && uv))) {
        hasUtil = true;
        utilHtml += '<div class="db-flow-section"><div class="db-flow-label">' +
          esc(uk.replace(/_/g, " ").toUpperCase()) + '</div><div>' +
          esc(Array.isArray(uv) ? uv.join(", ") : String(uv)) + '</div></div>';
      }
    }
    if (hasUtil) {
      var utilContainer = document.createElement("div");
      utilContainer.innerHTML = utilHtml;
      container.appendChild(utilContainer);
    }
  }

  // ── Notes ──

  function populateNotes(data) {
    var p3 = phaseResult(data, "phase3_notes_extraction");
    var notes = deepFind(p3, ["notes"]) || [];
    document.getElementById("db-notes-total").textContent = notes.length + " Notes";
    var list = document.getElementById("db-notes-list");
    list.innerHTML = "";

    if (notes.length === 0) {
      list.innerHTML = '<p style="color:#94a3b8;font-size:0.82rem">No notes extracted</p>';
      return;
    }

    notes.forEach(function (note) {
      var item = document.createElement("div");
      item.className = "db-note-item";
      var cat = note.category || "REFERENCE";
      item.innerHTML =
        '<div class="db-note-num">Note ' + esc(String(note.note_number || "")) + '</div>' +
        '<div class="db-note-text">' + esc(note.full_text || note.text || "") + '</div>' +
        '<span class="db-note-cat db-note-cat-' + esc(cat) + '">' + esc(cat) + '</span>';
      list.appendChild(item);
    });
  }

  // ── References ──

  function populateRefs(data) {
    var p8 = phaseResult(data, "phase8_connections_flow");
    var refs = deepFind(p8, ["reference_drawings"]) || [];
    var p1 = phaseResult(data, "phase1_document_context");
    var p1refs = deepFind(p1, ["references"]) || {};
    var otherPids = p1refs.other_pids || [];
    var standards = p1refs.standards || [];

    var container = document.getElementById("db-refs-content");
    container.innerHTML = "";

    if (refs.length > 0) {
      renderSubTable("db-refs-content", refs,
        ["drawing_number", "description", "connection_type"],
        ["Drawing", "Description", "Connection"]
      );
    }

    if (otherPids.length > 0) {
      var sec = document.createElement("div");
      sec.className = "db-flow-section";
      sec.innerHTML = '<div class="db-flow-label">Referenced P&IDs</div><div>' +
        otherPids.map(function (p) { return '<span class="db-flow-arrow">' + esc(String(p)) + '</span>'; }).join(" ") +
        '</div>';
      container.appendChild(sec);
    }

    if (standards.length > 0) {
      var sec2 = document.createElement("div");
      sec2.className = "db-flow-section";
      sec2.innerHTML = '<div class="db-flow-label">Standards</div><div style="font-size:0.82rem">' +
        esc(standards.join(", ")) + '</div>';
      container.appendChild(sec2);
    }

    if (refs.length === 0 && otherPids.length === 0 && standards.length === 0) {
      container.innerHTML = '<p style="color:#94a3b8;font-size:0.82rem">No reference drawings found</p>';
    }
  }

  // ── Generic sub-table renderer ──

  function renderSubTable(wrapperId, rows, fields, headers) {
    var wrapper = document.getElementById(wrapperId);
    var table = document.createElement("table");
    table.className = "db-sub-table";

    var thead = document.createElement("thead");
    var hRow = document.createElement("tr");
    headers.forEach(function (h) {
      var th = document.createElement("th");
      th.textContent = h;
      hRow.appendChild(th);
    });
    thead.appendChild(hRow);
    table.appendChild(thead);

    var tbody = document.createElement("tbody");
    rows.forEach(function (row) {
      var tr = document.createElement("tr");
      fields.forEach(function (f) {
        var td = document.createElement("td");
        var val = row[f];
        if (val === undefined || val === null) val = "";
        else if (typeof val === "object") val = JSON.stringify(val);
        td.textContent = String(val);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    wrapper.innerHTML = "";
    wrapper.appendChild(table);
  }

  function esc(str) {
    var div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
})();
