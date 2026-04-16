(function () {
  const form = document.getElementById("queue-form");
  if (!form) return;

  const FIXED_LANE_COUNT = 4;
  const note = document.getElementById("control-note");
  const queueStatusBody = document.getElementById("queue-status-body");
  const sectionGrid = document.getElementById("section-grid");
  const summaryGrid = document.getElementById("summary-grid");
  const refreshButton = document.getElementById("refresh-control");
  const stopButton = document.getElementById("autopilot-stop");
  const autopilotState = document.getElementById("autopilot-state");
  const liveEquation = document.getElementById("live-equation");
  const liveStage = document.getElementById("live-stage");
  const liveFrontier = document.getElementById("live-frontier");
  const liveDirections = document.getElementById("live-directions");
  const liveEvolution = document.getElementById("live-evolution");
  const liveOutcomes = document.getElementById("live-outcomes");

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function detailRow(label, value) {
    const row = el("div", "detail-row");
    row.append(el("span", "detail-label", label), el("span", "detail-value", value));
    return row;
  }

  function laneLabel(index) {
    return String.fromCharCode(64 + index);
  }

  function clearNode(node) {
    if (node) node.innerHTML = "";
  }

  async function fetchJson(url, options) {
    const response = await fetch(url, options);
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.error || `Request failed (${response.status})`);
    }
    return response.json();
  }

  function renderQueueStatus(payload) {
    queueStatusBody.innerHTML = "";
    const cleared = payload.queue_size - payload.remaining_count;
    queueStatusBody.append(
      detailRow("Status", payload.remaining_count ? "running search space" : "complete"),
      detailRow("Cleared", String(cleared)),
      detailRow("Remaining", String(payload.remaining_count)),
      detailRow(
        "Next Point",
        payload.next_unresolved ? `(${payload.next_unresolved.join(", ")})` : "complete"
      ),
      detailRow("Mode", "automatic background search")
    );
  }

  function renderAutopilot(payload) {
    autopilotState.innerHTML = "";
    const state = payload.state || {};
    autopilotState.append(
      detailRow("Status", payload.status),
      detailRow("Started", payload.started_at || "not running"),
      detailRow("Last Update", state.generated_at || "not started"),
      detailRow(
        "Next Point",
        state.next_unresolved ? `(${state.next_unresolved.join(", ")})` : "n/a"
      )
    );
    if (state.cycle_results && state.cycle_results.length) {
      const pre = el("pre", "mini-pre");
      pre.textContent = state.cycle_results
        .map((row) => `tested: (${row.leading_point.join(", ")})`)
        .join("\n");
      autopilotState.append(pre);
    }
  }

  function renderSnapshotCards(queuePayload) {
    sectionGrid.innerHTML = "";
    const cleared = queuePayload.queue_size - queuePayload.remaining_count;
    const cards = [
      {
        title: "Search Space",
        lines: [
          `Total queued points: ${queuePayload.queue_size}`,
          `Points cleared: ${cleared}`,
          `Points remaining: ${queuePayload.remaining_count}`,
        ],
      },
      {
        title: "Next Target",
        lines: [
          queuePayload.next_unresolved
            ? `Next unresolved point: (${queuePayload.next_unresolved.join(", ")})`
            : "No unresolved points remain.",
          "The background search advances this automatically.",
        ],
      },
      {
        title: "How It Runs",
        lines: [
          "A fixed set of internal workers keeps taking the next unresolved points.",
          "That splitting stays behind the scenes so the same point does not get retested.",
        ],
      },
    ];

    cards.forEach((cardData) => {
      const card = el("div", "section-card static");
      card.append(el("p", "section-title", cardData.title));
      cardData.lines.forEach((line) => {
        card.append(el("p", "section-meta", line));
      });
      sectionGrid.append(card);
    });
  }

  function renderSummaries(payload) {
    summaryGrid.innerHTML = "";
    if (!payload.summaries.length) {
      summaryGrid.append(el("p", "empty-note", "No saved backup results yet."));
      return;
    }

    payload.summaries
      .slice()
      .sort((a, b) => new Date(b.generated_at) - new Date(a.generated_at))
      .slice(0, 8)
      .forEach((summary) => {
      const card = el("div", "job-card");
      card.append(detailRow("Updated", summary.generated_at || "n/a"));
      if (summary.recent_results && summary.recent_results.length) {
        const latest = summary.recent_results[summary.recent_results.length - 1];
        card.append(
          detailRow("Tested", `(${latest.leading_point.join(", ")})`),
          detailRow("Result", latest.result || "recorded")
        );
        const pre = el("pre", "mini-pre");
        pre.textContent = latest.proof_summary || `odd gcd: ${latest.odd_branch_gcd}`;
        card.append(pre);
      } else {
        card.append(el("p", "empty-note", "No recorded point in this recent summary."));
      }
      summaryGrid.append(card);
    });
  }

  function renderLiveState(payload) {
    clearNode(liveEquation);
    clearNode(liveStage);
    clearNode(liveFrontier);
    clearNode(liveDirections);
    clearNode(liveEvolution);
    clearNode(liveOutcomes);

    const equation = payload.equation || {};
    const factorFormulation = equation.factor_formulation || {};
    liveEquation.append(
      detailRow("Equation", equation.display || "n/a"),
      detailRow(
        "Seed",
        equation.seed && equation.seed.every((value) => value !== null && value !== undefined)
          ? `(${equation.seed.join(", ")})`
          : "n/a"
      )
    );
    if (factorFormulation.product) {
      liveEquation.append(detailRow("Product", factorFormulation.product));
    }
    if (factorFormulation.sum) {
      liveEquation.append(detailRow("Square Shell", factorFormulation.sum));
    }

    const stage = payload.current_stage || {};
    const counts = stage.counts || {};
    liveStage.append(
      el("p", "stage-title", stage.title || "n/a"),
      el("p", "stage-summary", stage.summary || ""),
      detailRow("Exact no-go families", String(counts.template_no_go_count || 0)),
      detailRow("Symbolic reductions", String(counts.symbolic_reduction_count || 0)),
      detailRow("Cleared points", String(counts.exact_branch_kill_count || 0))
    );

    const frontier = payload.frontier || {};
    liveFrontier.append(
      detailRow("Search Status", frontier.autopilot_status || "stopped"),
      detailRow("Remaining Points", String(frontier.remaining_count || 0)),
      detailRow(
        "Next Point",
        frontier.next_unresolved ? `(${frontier.next_unresolved.join(", ")})` : "complete"
      ),
      detailRow("Cycle", frontier.cycle_index ? String(frontier.cycle_index) : "idle")
    );

    if ((payload.directions || []).length) {
      payload.directions.slice(0, 3).forEach((text) => {
        liveDirections.append(el("p", "direction-item", text));
      });
    } else {
      liveDirections.append(el("p", "empty-note", "No current direction recorded."));
    }

    (payload.evolution || []).forEach((step, index) => {
      const card = el("div", "timeline-card");
      card.append(
        el("p", "lane-order", `Stage ${index + 1}`),
        el("h4", "timeline-title", step.title),
        el("span", "status-badge status-" + step.result, step.result.replaceAll("_", " ")),
        el("p", "timeline-detail", step.detail || "")
      );
      liveEvolution.append(card);
    });

    if ((payload.recent_outcomes || []).length) {
      payload.recent_outcomes.slice(0, 8).forEach((row) => {
        const card = el("div", "job-card");
        card.append(
          detailRow("Time", row.generated_at || "n/a"),
          detailRow("Point", `(${row.leading_point.join(", ")})`),
          detailRow("Result", row.result || "recorded")
        );
        const summary = Array.isArray(row.summary) ? row.summary[0] : row.summary;
        if (summary) {
          card.append(el("p", "timeline-detail", summary));
        }
        liveOutcomes.append(card);
      });
    } else {
      liveOutcomes.append(el("p", "empty-note", "No exact outcomes recorded yet."));
    }
  }

  async function refreshControl() {
    try {
      const [queueStatus, summaries, autopilot, liveState] = await Promise.all([
        fetchJson(`/api/queue-status?section_count=${FIXED_LANE_COUNT}`),
        fetchJson("/api/section-summaries"),
        fetchJson("/api/autopilot-status"),
        fetchJson("/api/live-state"),
      ]);

      note.textContent =
        "Main math stays in chat. This page only handles the background search.";
      renderQueueStatus(queueStatus);
      renderSnapshotCards(queueStatus);
      renderSummaries(summaries);
      renderAutopilot(autopilot);
      renderLiveState(liveState);
    } catch (error) {
      note.textContent =
        "Start the local control server with open_primitive_queue_control.command to enable this page.";
      queueStatusBody.innerHTML = "";
      sectionGrid.innerHTML = "";
      summaryGrid.innerHTML = "";
      autopilotState.innerHTML = "";
      clearNode(liveEquation);
      clearNode(liveStage);
      clearNode(liveFrontier);
      clearNode(liveDirections);
      clearNode(liveEvolution);
      clearNode(liveOutcomes);
    }
  }

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    try {
      await fetchJson("/api/autopilot-start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      note.textContent = "Background search started.";
      await refreshControl();
    } catch (error) {
      note.textContent = error.message;
    }
  });

  stopButton.addEventListener("click", async function () {
    try {
      await fetchJson("/api/autopilot-stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      note.textContent = "Background search stopped.";
      await refreshControl();
    } catch (error) {
      note.textContent = error.message;
    }
  });

  refreshButton.addEventListener("click", refreshControl);
  refreshControl();
  window.setInterval(refreshControl, 4000);
})();
