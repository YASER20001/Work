/**
 * P&ID Vision Analyzer - Frontend Application
 */

(function () {
  "use strict";

  // State
  let sessionId = null;
  let pollInterval = null;

  // Elements
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const browseBtn = document.getElementById("browse-btn");
  const fileInfo = document.getElementById("file-info");
  const fileName = document.getElementById("file-name");
  const removeFile = document.getElementById("remove-file");
  const analyzeBtn = document.getElementById("analyze-btn");

  const uploadSection = document.getElementById("upload-section");
  const progressSection = document.getElementById("progress-section");
  const progressBar = document.getElementById("progress-bar");
  const progressText = document.getElementById("progress-text");
  const phaseItems = document.querySelectorAll(".phase-item");

  const statsSection = document.getElementById("stats-section");
  const resultsSection = document.getElementById("results-section");
  const resultsAccordion = document.getElementById("results-accordion");
  const exportBtn = document.getElementById("export-btn");

  const chatSection = document.getElementById("chat-section");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatMessages = document.getElementById("chat-messages");

  // Phase labels
  const PHASE_LABELS = {
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

  // ── Upload Handling ──

  browseBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    fileInput.click();
  });

  dropZone.addEventListener("click", function () {
    fileInput.click();
  });

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
    if (e.dataTransfer.files.length) {
      handleFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", function () {
    if (fileInput.files.length) {
      handleFile(fileInput.files[0]);
    }
  });

  removeFile.addEventListener("click", function () {
    resetUpload();
  });

  function handleFile(file) {
    var allowed = [
      "application/pdf",
      "image/png",
      "image/jpeg",
      "image/webp",
    ];
    if (!allowed.includes(file.type)) {
      alert("Invalid file type. Please upload a PDF, PNG, JPG, or WEBP file.");
      return;
    }

    fileName.textContent = file.name;
    fileInfo.classList.remove("hidden");
    analyzeBtn.classList.remove("hidden");
    dropZone.classList.add("hidden");

    // Upload immediately
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
    analyzeBtn.textContent = "Uploading...";

    var formData = new FormData();
    formData.append("file", file);

    try {
      var res = await fetch("/api/upload", { method: "POST", body: formData });
      var data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      sessionId = data.session_id;
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Start 11-Phase Analysis";
    } catch (err) {
      alert("Upload error: " + err.message);
      resetUpload();
    }
  }

  // ── Analysis ──

  analyzeBtn.addEventListener("click", function () {
    if (!sessionId) return;
    startAnalysis();
  });

  async function startAnalysis() {
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analysis Running...";
    progressSection.classList.remove("hidden");

    try {
      var res = await fetch("/api/analyze/" + sessionId, { method: "POST" });
      var data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to start analysis");
      }

      // Start polling
      pollInterval = setInterval(pollStatus, 2000);
    } catch (err) {
      alert("Analysis error: " + err.message);
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Start 11-Phase Analysis";
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
        progressText.textContent =
          "Phase " + current + " of " + total + ": " + (data.progress.phase_name || "");

        // Update phase indicators
        phaseItems.forEach(function (item) {
          var phase = parseInt(item.getAttribute("data-phase"));
          item.classList.remove("active", "completed");
          if (phase < current) {
            item.classList.add("completed");
          } else if (phase === current) {
            item.classList.add("active");
          }
        });
      }

      if (data.status === "completed") {
        clearInterval(pollInterval);
        pollInterval = null;

        // Mark all phases completed
        phaseItems.forEach(function (item) {
          item.classList.remove("active");
          item.classList.add("completed");
        });
        progressBar.style.width = "100%";
        progressText.textContent = "Analysis complete!";

        loadResults();
      }
    } catch (err) {
      // Silently retry on network errors
    }
  }

  async function loadResults() {
    try {
      var res = await fetch("/api/results/" + sessionId);
      var data = await res.json();

      displayStats(data);
      displayResults(data);

      statsSection.classList.remove("hidden");
      resultsSection.classList.remove("hidden");
      chatSection.classList.remove("hidden");
    } catch (err) {
      alert("Failed to load results: " + err.message);
    }
  }

  function displayStats(data) {
    var stats = data.statistics || {};
    document.getElementById("stat-equipment").textContent = stats.equipment || 0;
    document.getElementById("stat-valves").textContent = stats.valves || 0;
    document.getElementById("stat-instruments").textContent = stats.instruments || 0;
    document.getElementById("stat-lines").textContent = stats.piping_lines || 0;
    document.getElementById("stat-notes").textContent = stats.notes || 0;
    document.getElementById("stat-confidence").textContent =
      (data.confidence || 0) + "%";
  }

  function displayResults(data) {
    resultsAccordion.innerHTML = "";

    var phases = data.phases || {};
    var keys = Object.keys(phases);

    keys.forEach(function (key, idx) {
      var phase = phases[key];
      var label = PHASE_LABELS[key] || key;

      var item = document.createElement("div");
      item.className = "accordion-item";

      var header = document.createElement("div");
      header.className = "accordion-header";
      header.innerHTML =
        "<span>Phase " +
        (idx + 1) +
        ": " +
        label +
        "</span><span class='accordion-arrow'>&#9654;</span>";

      header.addEventListener("click", function () {
        item.classList.toggle("open");
      });

      var body = document.createElement("div");
      body.className = "accordion-body";

      // Show raw response text
      var pre = document.createElement("pre");
      pre.textContent = phase.raw || JSON.stringify(phase.result, null, 2);
      body.appendChild(pre);

      item.appendChild(header);
      item.appendChild(body);
      resultsAccordion.appendChild(item);
    });

    // Show errors if any
    if (data.errors && data.errors.length > 0) {
      var errItem = document.createElement("div");
      errItem.className = "accordion-item";
      var errHeader = document.createElement("div");
      errHeader.className = "accordion-header";
      errHeader.style.background = "#fef2f2";
      errHeader.innerHTML =
        "<span>Errors (" +
        data.errors.length +
        ")</span><span class='accordion-arrow'>&#9654;</span>";
      errHeader.addEventListener("click", function () {
        errItem.classList.toggle("open");
      });
      var errBody = document.createElement("div");
      errBody.className = "accordion-body";
      var errPre = document.createElement("pre");
      errPre.textContent = JSON.stringify(data.errors, null, 2);
      errBody.appendChild(errPre);
      errItem.appendChild(errHeader);
      errItem.appendChild(errBody);
      resultsAccordion.appendChild(errItem);
    }
  }

  // ── Export ──

  exportBtn.addEventListener("click", function () {
    if (!sessionId) return;
    window.open("/api/export/" + sessionId, "_blank");
  });

  // ── Chat ──

  chatForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    var question = chatInput.value.trim();
    if (!question || !sessionId) return;

    addChatMessage(question, "user");
    chatInput.value = "";

    try {
      var res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, question: question }),
      });
      var data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Query failed");
      }

      addChatMessage(data.answer, "assistant");
    } catch (err) {
      addChatMessage("Error: " + err.message, "assistant");
    }
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
  }
})();
