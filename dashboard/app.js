(function () {
  const data = window.PORTFOLIO_DATA;

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function statusLabel(status) {
    const labels = {
      candidate_hit: "Bounded Hit",
      no_hit_in_bounded_scan: "No Hit In Box",
      system_generated: "System Ready",
      exact_examples_found: "Exact Examples",
      no_examples_in_bounded_x_scan: "No Examples In Box",
    };
    return labels[status] || status;
  }

  function renderHero() {
    const side = document.getElementById("hero-side");
    side.append(
      metricCard("Equation", data.equation.slug),
      metricCard("Open Status", data.equation.status),
      metricCard("Priority Lane", data.overview.recommended_next_step.lane)
    );
  }

  function metricCard(label, value) {
    const card = el("div", "metric-card");
    card.append(el("p", "metric-label", label), el("p", "metric-value", value));
    return card;
  }

  function renderWorkflow() {
    document.getElementById("generated-at").textContent = "Generated " + data.generated_at;
    const workflow = document.getElementById("workflow");
    data.overview.workflow.forEach((step, index) => {
      const item = el("li", "workflow-step");
      item.append(el("span", "workflow-index", String(index + 1)), el("span", "workflow-text", step));
      workflow.append(item);
    });
  }

  function renderNextAction() {
    const root = document.getElementById("next-action");
    root.append(
      el("p", "next-lane", "Promote: " + data.overview.recommended_next_step.lane),
      el("p", "next-text", data.overview.recommended_next_step.action)
    );
  }

  function renderEquation() {
    const root = document.getElementById("equation-card");
    root.append(
      detailRow("Equation", data.equation.equation),
      detailRow("Parameters", `a=${data.equation.a}, b=${data.equation.b}, c=${data.equation.c}`),
      detailRow("Source", data.equation.source)
    );
  }

  function renderSeed() {
    const root = document.getElementById("seed-card");
    const seed = data.seed;
    root.append(
      detailRow("Seed", `(${seed.x}, ${seed.y}, ${seed.z})`),
      detailRow("Ranked Index", String(seed.ranked_seed_index)),
      detailRow("Seed Source", seed.seed_source)
    );
  }

  function detailRow(label, value) {
    const row = el("div", "detail-row");
    row.append(el("span", "detail-label", label), el("span", "detail-value", value));
    return row;
  }

  function renderLanes() {
    const grid = document.getElementById("lane-grid");
    data.lanes.forEach((lane, index) => {
      const card = el("article", "lane-card");
      card.append(
        el("p", "lane-order", `Lane ${index + 1}`),
        el("h3", "lane-title", lane.title)
      );

      const badge = el("span", "status-badge status-" + lane.status, statusLabel(lane.status));
      card.append(badge);
      card.append(el("p", "lane-summary", lane.summary));

      if (lane.seed_formula) {
        const formulaBox = el("div", "formula-box");
        Object.entries(lane.seed_formula).forEach(([label, value]) => {
          formulaBox.append(detailRow(label, value));
        });
        card.append(formulaBox);
      }

      if (lane.equation_count) {
        card.append(detailRow("Equation Count", String(lane.equation_count)));
      }
      if (lane.unknown_count) {
        card.append(detailRow("Unknown Count", String(lane.unknown_count)));
      }
      if (lane.bounded_scan) {
        card.append(detailRow("Bounded Hit Count", String(lane.bounded_scan.hit_count)));
        card.append(detailRow("Scan Box", `[-${lane.bounded_scan.bound}, ${lane.bounded_scan.bound}]`));
      }
      if (lane.bounded_x_scan) {
        card.append(detailRow("Example Count", String(lane.bounded_x_scan.example_count)));
        card.append(detailRow("x Scan", `[-${lane.bounded_x_scan.bound}, ${lane.bounded_x_scan.bound}]`));
      }

      const action = el("div", "next-box");
      action.append(el("p", "next-box-label", "Next"), el("p", "next-box-text", lane.next_action));
      card.append(action);

      if (lane.low_degree_equations && lane.low_degree_equations.length) {
        const pre = el("pre", "mini-pre");
        pre.textContent = lane.low_degree_equations
          .slice(0, 4)
          .map((row) => `t^${row.power}: ${row.equation}`)
          .join("\n");
        card.append(pre);
      }

      if (lane.bounded_scan && lane.bounded_scan.hits.length) {
        const pre = el("pre", "mini-pre");
        pre.textContent = lane.bounded_scan.hits
          .slice(0, 3)
          .map((hit) => JSON.stringify(hit.params))
          .join("\n");
        card.append(pre);
      }

      if (lane.bounded_x_scan && lane.bounded_x_scan.examples.length) {
        const pre = el("pre", "mini-pre");
        pre.textContent = lane.bounded_x_scan.examples
          .slice(0, 4)
          .map((row) => `(${row.x}, ${row.y}, ${row.z})  p=${row.p} q=${row.q}`)
          .join("\n");
        card.append(pre);
      }

      grid.append(card);
    });
  }

  renderHero();
  renderWorkflow();
  renderNextAction();
  renderEquation();
  renderSeed();
  renderLanes();
})();
