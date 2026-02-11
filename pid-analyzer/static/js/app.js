/**
 * P&ID Vision Analyzer — SPA Frontend Application
 * KBR-AMCDE Corporate Layout with Sidebar Navigation
 */

(function () {
  "use strict";

  var sessionId = null;
  var pollInterval = null;
  var analysisComplete = false;

  // ═══ PAGE TITLES ═══
  var PAGE_TITLES = {
    upload: "Upload & Analyze",
    dashboard: "Executive Dashboard",
    results: "Detailed Results",
    assistant: "AI Engineering Assistant",
  };

  // ═══ PHASE LABELS ═══
  var PHASE_LABELS = {
    phase1_document_context: "Document Context",
    phase2_legend_symbols: "Legend & Symbols",
    phase3_notes_extraction: "Notes Extraction",
    phase4_equipment_scan: "Equipment Scan",
    phase5_valve_analysis: "Valve Analysis",
    phase6_instrumentation: "Instrumentation",
    phase7_piping_analysis: "Piping Analysis",
    phase8_connections_flow: "Connections & Flow",
    phase9_safety_analysis: "Safety Analysis",
    phase10_verification_summary: "Verification Summary",
    phase11_reverification: "Re-verification",
  };

  // ═══ SIDEBAR NAVIGATION ═══

  var sidebar = document.getElementById("sidebar");
  var mainWrapper = document.getElementById("main-wrapper");
  var sidebarToggle = document.getElementById("sidebar-toggle");
  var navItems = document.querySelectorAll(".nav-item");
  var pages = document.querySelectorAll(".page");
  var topbarTitle = document.getElementById("topbar-title");
  var topbarStatus = document.getElementById("topbar-status");

  sidebarToggle.addEventListener("click", function () {
    sidebar.classList.toggle("collapsed");
    mainWrapper.classList.toggle("expanded");
    // On mobile, toggle open class
    if (window.innerWidth <= 1024) {
      sidebar.classList.toggle("open");
    }
  });

  // Close sidebar on mobile when clicking outside
  mainWrapper.addEventListener("click", function () {
    if (window.innerWidth <= 1024 && sidebar.classList.contains("open")) {
      sidebar.classList.remove("open");
    }
  });

  function navigateTo(pageName) {
    pages.forEach(function (p) { p.classList.remove("active"); });
    navItems.forEach(function (n) { n.classList.remove("active"); });

    var page = document.getElementById("page-" + pageName);
    if (page) page.classList.add("active");

    var nav = document.querySelector('.nav-item[data-page="' + pageName + '"]');
    if (nav) nav.classList.add("active");

    topbarTitle.textContent = PAGE_TITLES[pageName] || pageName;

    // Close sidebar on mobile after navigation
    if (window.innerWidth <= 1024) {
      sidebar.classList.remove("open");
    }
  }

  navItems.forEach(function (item) {
    item.addEventListener("click", function (e) {
      e.preventDefault();
      var page = item.getAttribute("data-page");
      if (item.classList.contains("disabled") && !item.classList.contains("enabled")) return;
      navigateTo(page);
    });
  });

  function enableResultPages() {
    document.getElementById("nav-dashboard").classList.add("enabled");
    document.getElementById("nav-results").classList.add("enabled");
    document.getElementById("nav-assistant").classList.add("enabled");
  }

  // ═══ UPLOAD ═══

  var dropZone = document.getElementById("drop-zone");
  var fileInput = document.getElementById("file-input");
  var browseBtn = document.getElementById("browse-btn");
  var fileInfo = document.getElementById("file-info");
  var fileName = document.getElementById("file-name");
  var removeFile = document.getElementById("remove-file");
  var analyzeBtn = document.getElementById("analyze-btn");
  var progressCard = document.getElementById("progress-card");
  var progressBar = document.getElementById("progress-bar");
  var progressText = document.getElementById("progress-text");
  var progressPct = document.getElementById("progress-pct");
  var phaseItems = document.querySelectorAll(".phase-item");

  browseBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    fileInput.click();
  });

  dropZone.addEventListener("click", function () { fileInput.click(); });

  dropZone.addEventListener("dragover", function (e) {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", function () {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", function (e) {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
  });

  fileInput.addEventListener("change", function () {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
  });

  removeFile.addEventListener("click", resetUpload);

  function handleFile(file) {
    var allowed = ["application/pdf", "image/png", "image/jpeg", "image/webp"];
    if (!allowed.includes(file.type)) {
      alert("Invalid file type. Please upload a PDF, PNG, JPG, or WEBP file.");
      return;
    }
    fileName.textContent = file.name;
    fileInfo.classList.remove("hidden");
    analyzeBtn.classList.remove("hidden");
    dropZone.classList.add("hidden");
    uploadFile(file);
  }

  function resetUpload() {
    fileInput.value = "";
    fileInfo.classList.add("hidden");
    analyzeBtn.classList.add("hidden");
    dropZone.classList.remove("hidden");
    sessionId = null;
  }

  async function uploadFile(file) {
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Uploading...';
    var formData = new FormData();
    formData.append("file", file);
    try {
      var res = await fetch("/api/upload", { method: "POST", body: formData });
      var data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      sessionId = data.session_id;
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Start 11-Phase Analysis';
    } catch (err) {
      alert("Upload error: " + err.message);
      resetUpload();
    }
  }

  // ═══ ANALYSIS ═══

  analyzeBtn.addEventListener("click", function () {
    if (!sessionId) return;
    startAnalysis();
  });

  async function startAnalysis() {
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Analysis Running...';
    progressCard.classList.remove("hidden");
    topbarStatus.textContent = "Analyzing";
    topbarStatus.className = "topbar-badge analyzing";

    try {
      var res = await fetch("/api/analyze/" + sessionId, { method: "POST" });
      var data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to start analysis");
      pollInterval = setInterval(pollStatus, 2500);
    } catch (err) {
      alert("Analysis error: " + err.message);
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Start 11-Phase Analysis';
      topbarStatus.textContent = "Ready";
      topbarStatus.className = "topbar-badge";
    }
  }

  async function pollStatus() {
    try {
      var res = await fetch("/api/status/" + sessionId);
      var data = await res.json();
      if (data.progress) {
        var current = data.progress.current_phase;
        var total = data.progress.total_phases;
        var pct = Math.round((current / total) * 100);
        progressBar.style.width = pct + "%";
        progressPct.textContent = pct + "%";
        var phaseName = data.progress.phase_name || "";
        var label = PHASE_LABELS[phaseName] || phaseName;
        progressText.textContent = "Phase " + current + " of " + total + ": " + label;

        phaseItems.forEach(function (item) {
          var phase = parseInt(item.getAttribute("data-phase"));
          item.classList.remove("active", "completed");
          if (phase < current) item.classList.add("completed");
          else if (phase === current) item.classList.add("active");
        });
      }

      if (data.status === "completed") {
        clearInterval(pollInterval);
        pollInterval = null;
        phaseItems.forEach(function (item) {
          item.classList.remove("active");
          item.classList.add("completed");
        });
        progressBar.style.width = "100%";
        progressPct.textContent = "100%";
        progressText.textContent = "Analysis complete!";
        topbarStatus.textContent = "Complete";
        topbarStatus.className = "topbar-badge completed";
        analysisComplete = true;
        enableResultPages();
        loadResults();
      }
    } catch (err) { /* retry silently */ }
  }

  async function loadResults() {
    try {
      var res = await fetch("/api/results/" + sessionId);
      var data = await res.json();
      displayStats(data);
      displayStructuredResults(data);
      displayRawResults(data);

      // Wire executive dashboard
      window._pidSessionId = sessionId;
      if (typeof window.renderDashboard === "function") {
        window.renderDashboard(data);
      }

      // Auto-navigate to dashboard after analysis
      navigateTo("dashboard");
    } catch (err) {
      alert("Failed to load results: " + err.message);
    }
  }

  // ═══ STATS ═══

  function displayStats(data) {
    var s = data.statistics || {};
    document.getElementById("stat-equipment").textContent = s.equipment || 0;
    document.getElementById("stat-valves").textContent = s.valves || 0;
    document.getElementById("stat-instruments").textContent = s.instruments || 0;
    document.getElementById("stat-lines").textContent = s.piping_lines || 0;
    document.getElementById("stat-notes").textContent = s.notes || 0;
    document.getElementById("stat-gas-detectors").textContent = s.gas_detectors || 0;
    document.getElementById("stat-relief").textContent = s.relief_devices || 0;
    document.getElementById("stat-confidence").textContent = (data.confidence || 0) + "%";
  }

  // ═══ STRUCTURED RESULTS ═══

  var resultsAccordion = document.getElementById("results-accordion");
  var resultsRawAccordion = document.getElementById("results-raw-accordion");

  function displayStructuredResults(data) {
    resultsAccordion.innerHTML = "";
    var phases = data.phases || {};
    var keys = Object.keys(phases);
    keys.forEach(function (key, idx) {
      var phase = phases[key];
      var label = PHASE_LABELS[key] || key;
      var item = makeAccordionItem("Phase " + (idx + 1) + ": " + label, function (body) {
        renderStructured(body, phase.result || {}, key);
      });
      resultsAccordion.appendChild(item);
    });
    if (data.errors && data.errors.length > 0) {
      var errItem = makeAccordionItem("Errors (" + data.errors.length + ")", function (body) {
        var pre = document.createElement("pre");
        pre.textContent = JSON.stringify(data.errors, null, 2);
        body.appendChild(pre);
      }, "#fef2f2");
      resultsAccordion.appendChild(errItem);
    }
  }

  function displayRawResults(data) {
    resultsRawAccordion.innerHTML = "";
    var phases = data.phases || {};
    var keys = Object.keys(phases);
    keys.forEach(function (key, idx) {
      var phase = phases[key];
      var label = PHASE_LABELS[key] || key;
      var item = makeAccordionItem("Phase " + (idx + 1) + ": " + label, function (body) {
        var pre = document.createElement("pre");
        pre.textContent = phase.raw || JSON.stringify(phase.result, null, 2);
        body.appendChild(pre);
      });
      resultsRawAccordion.appendChild(item);
    });
  }

  function makeAccordionItem(title, renderFn, bgColor) {
    var item = document.createElement("div");
    item.className = "accordion-item";
    var header = document.createElement("div");
    header.className = "accordion-header";
    if (bgColor) header.style.background = bgColor;
    header.innerHTML = "<span>" + escHtml(title) + "</span><span class='accordion-arrow'>&#9654;</span>";
    header.addEventListener("click", function () { item.classList.toggle("open"); });
    var body = document.createElement("div");
    body.className = "accordion-body";
    renderFn(body);
    item.appendChild(header);
    item.appendChild(body);
    return item;
  }

  function renderStructured(container, result, phaseKey) {
    if (result.raw_text || result.rawText) {
      var pre = document.createElement("pre");
      pre.textContent = result.raw_text || result.rawText;
      container.appendChild(pre);
      return;
    }
    var kvKeys = Object.keys(result);
    kvKeys.forEach(function (k) {
      var v = result[k];
      if (Array.isArray(v) && v.length > 0 && typeof v[0] === "object") {
        renderArrayTable(container, k, v);
      } else if (typeof v === "object" && v !== null && !Array.isArray(v)) {
        renderObjectSection(container, k, v);
      } else {
        var kv = document.createElement("div");
        kv.className = "result-kv";
        kv.innerHTML = "<span class='rk'>" + escHtml(formatKey(k)) + ":</span><span class='rv'>" + escHtml(String(v)) + "</span>";
        container.appendChild(kv);
      }
    });
  }

  function renderObjectSection(container, title, obj) {
    var h = document.createElement("div");
    h.className = "result-section-title";
    h.textContent = formatKey(title);
    container.appendChild(h);
    Object.keys(obj).forEach(function (k) {
      var v = obj[k];
      if (Array.isArray(v) && v.length > 0 && typeof v[0] === "object") {
        renderArrayTable(container, k, v);
      } else if (typeof v === "object" && v !== null && !Array.isArray(v)) {
        Object.keys(v).forEach(function (kk) {
          var kv = document.createElement("div");
          kv.className = "result-kv";
          kv.innerHTML = "<span class='rk'>" + escHtml(formatKey(kk)) + ":</span><span class='rv'>" + escHtml(String(v[kk])) + "</span>";
          container.appendChild(kv);
        });
      } else {
        var kv = document.createElement("div");
        kv.className = "result-kv";
        var displayVal = Array.isArray(v) ? v.join(", ") : String(v);
        kv.innerHTML = "<span class='rk'>" + escHtml(formatKey(k)) + ":</span><span class='rv'>" + escHtml(displayVal) + "</span>";
        container.appendChild(kv);
      }
    });
  }

  function renderArrayTable(container, title, arr) {
    var h = document.createElement("div");
    h.className = "result-section-title";
    h.textContent = formatKey(title) + " (" + arr.length + ")";
    container.appendChild(h);
    if (arr.length === 0) return;
    var table = document.createElement("table");
    table.className = "result-table";
    var allKeys = [];
    arr.forEach(function (item) {
      Object.keys(item).forEach(function (k) {
        if (allKeys.indexOf(k) === -1) allKeys.push(k);
      });
    });
    var thead = document.createElement("thead");
    var headerRow = document.createElement("tr");
    allKeys.forEach(function (k) {
      var th = document.createElement("th");
      th.textContent = formatKey(k);
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    var tbody = document.createElement("tbody");
    arr.forEach(function (item) {
      var row = document.createElement("tr");
      allKeys.forEach(function (k) {
        var td = document.createElement("td");
        var val = item[k];
        if (val === undefined || val === null) val = "";
        else if (typeof val === "object") val = JSON.stringify(val);
        else val = String(val);
        td.textContent = val;
        row.appendChild(td);
      });
      tbody.appendChild(row);
    });
    table.appendChild(tbody);
    container.appendChild(table);
  }

  function formatKey(key) {
    return key.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  function escHtml(str) {
    var div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  // ═══ TABS ═══

  document.querySelectorAll(".tab-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".tab-btn").forEach(function (b) { b.classList.remove("active"); });
      document.querySelectorAll(".tab-content").forEach(function (c) { c.classList.remove("active"); });
      btn.classList.add("active");
      var tabId = "results-" + btn.getAttribute("data-tab");
      document.getElementById(tabId).classList.add("active");
    });
  });

  // ═══ EXPORT ═══

  var exportBtn = document.getElementById("export-btn");
  exportBtn.addEventListener("click", function () {
    if (!sessionId) return;
    window.open("/api/export/" + sessionId, "_blank");
  });

  // ═══ EXCEL DOWNLOADS ═══

  function downloadExcel(type) {
    if (!sessionId) return;
    window.open("/api/export/" + sessionId + "/" + type, "_blank");
  }

  // Dashboard dropdown toggle
  var excelToggle = document.getElementById("db-excel-toggle");
  var excelMenu = document.getElementById("db-excel-menu");
  if (excelToggle) {
    excelToggle.addEventListener("click", function (e) {
      e.stopPropagation();
      excelMenu.classList.toggle("open");
    });
    document.addEventListener("click", function () {
      excelMenu.classList.remove("open");
    });
  }

  // Dashboard Excel buttons
  var dlEq = document.getElementById("dl-equipment-list");
  if (dlEq) dlEq.addEventListener("click", function () { downloadExcel("equipment-list"); });
  var dlVl = document.getElementById("dl-valve-list");
  if (dlVl) dlVl.addEventListener("click", function () { downloadExcel("valve-list"); });
  var dlLl = document.getElementById("dl-line-list");
  if (dlLl) dlLl.addEventListener("click", function () { downloadExcel("line-list"); });

  // Stats section Excel buttons
  var dlEq2 = document.getElementById("dl-equipment-list-2");
  if (dlEq2) dlEq2.addEventListener("click", function () { downloadExcel("equipment-list"); });
  var dlVl2 = document.getElementById("dl-valve-list-2");
  if (dlVl2) dlVl2.addEventListener("click", function () { downloadExcel("valve-list"); });
  var dlLl2 = document.getElementById("dl-line-list-2");
  if (dlLl2) dlLl2.addEventListener("click", function () { downloadExcel("line-list"); });

  // ═══ CHAT / AI ASSISTANT ═══

  var chatForm = document.getElementById("chat-form");
  var chatInput = document.getElementById("chat-input");
  var chatMessages = document.getElementById("chat-messages");
  var chatSubmitBtn = document.getElementById("chat-submit-btn");

  document.querySelectorAll(".suggestion-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var q = btn.getAttribute("data-q");
      chatInput.value = q;
      chatForm.dispatchEvent(new Event("submit"));
    });
  });

  chatForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    var question = chatInput.value.trim();
    if (!question || !sessionId) return;

    // Remove welcome message if present
    var welcome = chatMessages.querySelector(".chat-welcome");
    if (welcome) welcome.remove();

    addChatMessage(question, "user");
    chatInput.value = "";
    chatSubmitBtn.disabled = true;

    var loadingMsg = addChatMessage("Analyzing...", "loading");

    try {
      var res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, question: question }),
      });
      var data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Query failed");
      loadingMsg.remove();
      addChatMessage(data.answer, "assistant");
    } catch (err) {
      loadingMsg.remove();
      addChatMessage("Error: " + err.message, "assistant");
    }
    chatSubmitBtn.disabled = false;
  });

  function addChatMessage(text, role) {
    var msg = document.createElement("div");
    msg.className = "chat-msg " + role;
    if (role === "assistant") {
      var pre = document.createElement("pre");
      pre.textContent = text;
      msg.appendChild(pre);
    } else {
      msg.textContent = text;
    }
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msg;
  }
})();
