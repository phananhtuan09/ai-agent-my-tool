const AppShell = (() => {
  let stream;
  let listenersBound = false;
  const submitters = new WeakMap();

  function init() {
    bindInteractions();
    connectStream();
    syncResponsivePanels();
  }

  function closeModal(event) {
    if (event && event.target !== event.currentTarget) {
      return;
    }
    const modalRoot = document.getElementById("modal-root");
    if (modalRoot) {
      modalRoot.innerHTML = "";
    }
  }

  function requestNotifications() {
    if (!("Notification" in window)) {
      appendActivity("warn", "Browser notifications are unavailable in this browser.");
      return;
    }

    if (Notification.permission === "granted") {
      appendActivity("info", "Browser notifications are already enabled.");
      return;
    }

    Notification.requestPermission().then((permission) => {
      const message =
        permission === "granted"
          ? "Browser notifications enabled for live agent events."
          : "Browser notifications remain disabled; in-page activity feed is still active.";
      appendActivity("info", message);
    });
  }

  function bindInteractions() {
    if (listenersBound) {
      return;
    }

    document.addEventListener("click", handleDocumentClick);
    document.addEventListener("change", handleDocumentChange);
    document.addEventListener("submit", handleFormSubmit, true);
    document.addEventListener("htmx:beforeRequest", handleBeforeRequest);
    document.addEventListener("htmx:beforeSwap", handleBeforeSwap);
    document.addEventListener("htmx:afterRequest", handleAfterRequest);
    document.addEventListener("htmx:responseError", handleAfterRequest);
    window.addEventListener("resize", syncResponsivePanels);
    listenersBound = true;
  }

  function connectStream() {
    const agentName = document.body.dataset.agentName;
    const streamUrl = document.body.dataset.streamUrl;

    if (!agentName || !streamUrl || typeof EventSource === "undefined") {
      updateConnectionStatus("idle");
      return;
    }

    if (stream) {
      stream.close();
    }

    updateConnectionStatus("connecting");
    stream = new EventSource(streamUrl);

    stream.onopen = () => updateConnectionStatus("connected");
    stream.onerror = () => updateConnectionStatus("error");

    stream.addEventListener("status", (event) => {
      const payload = parsePayload(event.data);
      if (!payload) {
        return;
      }
      if (payload.snapshot) {
        updateStatus(payload.snapshot);
        appendActivity("status", `${payload.snapshot.title} status refreshed.`);
        return;
      }
      updateStatus(payload);
      appendActivity("status", `${payload.title} is ready for configuration changes.`);
    });

    stream.addEventListener("notify", (event) => {
      const payload = parsePayload(event.data);
      if (!payload) {
        return;
      }
      appendActivity("notify", payload.message);
      if ("Notification" in window && Notification.permission === "granted") {
        new Notification("AI Agent Tool", { body: payload.message });
      }
    });

    stream.addEventListener("chat", (event) => handleGenericEvent("chat", event.data));
    stream.addEventListener("ui_update", (event) => handleUiUpdate(event.data));
  }

  function updateConnectionStatus(state) {
    const badge = document.getElementById("connection-status");
    if (!badge) {
      return;
    }

    const labels = {
      connected: "Live connection",
      connecting: "Connecting...",
      error: "Connection interrupted",
      idle: "No live stream",
    };

    badge.dataset.state = state;
    const label = badge.querySelector(".conn-label");
    if (label) {
      label.textContent = labels[state] || labels.connecting;
    }
  }

  function handleGenericEvent(tag, rawData) {
    const payload = parsePayload(rawData);
    if (!payload) {
      return;
    }
    const message = payload.message || payload.content || "Received a live update.";
    appendActivity(tag, message);
  }

  function parsePayload(rawData) {
    try {
      return JSON.parse(rawData);
    } catch (error) {
      console.error("Failed to parse event payload", error);
      return null;
    }
  }

  function handleUiUpdate(rawData) {
    const payload = parsePayload(rawData);
    if (!payload) {
      return;
    }

    appendActivity("ui", `Updated ${payload.panel || "panel"} with the latest state.`);

    if (payload.panel === "job_results") {
      renderJobResults(payload);
      return;
    }

    if (payload.panel === "daily_schedule") {
      renderDailySchedule(payload.data || payload);
      return;
    }

    if (payload.panel === "airdrop_results") {
      renderAirdropResults(payload.data || payload);
      return;
    }

    handleGenericEvent("ui", rawData);
  }

  function updateStatus(snapshot) {
    const statusChip = document.getElementById("agent-status-chip");
    if (statusChip && snapshot.status) {
      statusChip.textContent = formatLabel(snapshot.status);
      if (typeof snapshot.is_configured === "boolean") {
        statusChip.classList.toggle("is-ready", snapshot.is_configured);
        statusChip.classList.toggle("is-warn", !snapshot.is_configured);
      }
    }

    document.querySelectorAll("[data-role='agent-model']").forEach((node) => {
      if (snapshot.model) {
        node.textContent = snapshot.model;
      }
    });

    document.querySelectorAll("[data-role='agent-model-source']").forEach((node) => {
      if (snapshot.model_source) {
        node.textContent =
          snapshot.model_source === "default" ? "Default model" : "Custom override";
      }
    });
  }

  function appendActivity(tag, message) {
    const feed =
      document.getElementById("agent-activity-feed") ||
      document.getElementById("daily-schedule-chat-list") ||
      document.getElementById("crypto-airdrop-chat-list");

    if (!feed) {
      return;
    }

    const entry = document.createElement("li");
    entry.className = getFeedItemClass(tag);
    const label = document.createElement("span");
    const body = document.createElement("p");

    label.className = "feed-tag";
    label.textContent = tag;
    body.textContent = message;

    entry.appendChild(label);
    entry.appendChild(body);
    feed.prepend(entry);

    while (feed.children.length > 6) {
      feed.removeChild(feed.lastElementChild);
    }
  }

  function renderJobResults(payload) {
    const panel = document.getElementById("job-results-panel");
    if (!panel) {
      return;
    }

    const jobs = payload.data || [];
    const warningsHtml = buildWarningsHtml(payload.warnings || []);
    const summaryItems = [
      { label: "Last trigger", value: payload.trigger || "live" },
      { label: "Matched", value: payload.matched_count ?? jobs.length },
    ];

    if (payload.crawled_count != null) {
      summaryItems.splice(1, 0, { label: "Crawled", value: payload.crawled_count });
    }

    if (!jobs.length) {
      panel.innerHTML = `
        ${buildSummaryStrip(summaryItems)}
        ${warningsHtml}
        ${buildEmptyState({
          icon: "💼",
          eyebrow: "No matches",
          title: "No jobs passed the hard filters yet.",
          copy: "Adjust salary, location, or must-have frameworks, then run the crawl again.",
          actionLabel: "Run crawl",
          triggerClick: "#job-filter-panel [data-run-job]",
        })}
      `;
      return;
    }

    const rowsHtml = jobs
      .map((job) => {
        const techStack = buildTagList(job.tech_stack || []);
        const salaryLabel =
          job.salary_label || buildSalaryLabel(job.salary_min, job.salary_max);

        return `
          <tr tabindex="0" data-reason="${escapeHtml(job.ai_reason || "")}">
            <td class="cell-score">${escapeHtml(String(job.ai_score ?? 0))}</td>
            <td class="cell-title">
              ${escapeHtml(job.title)}
              <small>${escapeHtml(job.company)}</small>
            </td>
            <td>${escapeHtml(job.location || "Remote")}</td>
            <td class="cell-nowrap">${escapeHtml(salaryLabel)}</td>
            <td class="cell-tags">${techStack}</td>
            <td>${escapeHtml(formatSource(job.source))}</td>
            <td class="cell-link">
              <a href="${escapeHtml(job.url)}" target="_blank" rel="noreferrer">Open ↗</a>
            </td>
          </tr>
        `;
      })
      .join("");

    panel.innerHTML = `
      ${buildSummaryStrip(summaryItems)}
      ${warningsHtml}
      <div class="data-table-wrap">
        <table class="data-table" id="job-table">
          <thead>
            <tr>
              <th data-sort="score">Score</th>
              <th data-sort="title">Title / Company</th>
              <th data-sort="location">Location</th>
              <th data-sort="salary">Salary</th>
              <th>Stack</th>
              <th data-sort="source">Source</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>${rowsHtml}</tbody>
        </table>
      </div>
    `;
  }

  function renderDailySchedule(payload) {
    renderScheduleTimeline(payload.tasks || []);
    renderScheduleMessages(
      payload.messages || [],
      Boolean(payload.awaiting_overdue_resolution)
    );
  }

  function renderAirdropResults(payload) {
    renderAirdropCards(payload.airdrops || [], payload.warnings || [], payload.trigger || "chat");
    renderAirdropMessages(payload.messages || []);
  }

  function renderScheduleTimeline(tasks) {
    const panel = document.getElementById("daily-schedule-timeline");
    if (!panel) {
      return;
    }

    if (!tasks.length) {
      panel.innerHTML = buildEmptyState({
        icon: "📋",
        eyebrow: "No tasks yet",
        title: "Start the day from the chat panel.",
        copy:
          "Paste a task list separated by commas, semicolons, or new lines and the planner will build a timeline.",
        actionLabel: "Start planning",
        focusTarget: "#daily-schedule-chat-panel textarea[name='message']",
      });
      return;
    }

    const activeCount = tasks.filter((task) =>
      ["pending", "in_progress"].includes(task.status)
    ).length;

    const rowsHtml = tasks
      .map((task, index) => {
        const status = String(task.status || "pending").replaceAll("_", "-");
        return `
          <tr tabindex="0">
            <td class="cell-score cell-index">${String(index + 1).padStart(2, "0")}</td>
            <td class="cell-title">${escapeHtml(task.title)}</td>
            <td class="cell-nowrap cell-muted">${escapeHtml(task.time_range || "TBD")}</td>
            <td class="cell-muted">${escapeHtml(String(task.estimated_minutes || 0))} min</td>
            <td>
              <span class="task-status status-${escapeHtml(status)}">${escapeHtml(
                formatLabel(task.status || "pending")
              )}</span>
            </td>
          </tr>
        `;
      })
      .join("");

    panel.innerHTML = `
      ${buildSummaryStrip([
        { label: "Scheduled", value: `${tasks.length} tasks` },
        { label: "Active", value: activeCount },
      ])}
      <div class="data-table-wrap">
        <table class="data-table" id="schedule-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Task</th>
              <th>Time</th>
              <th>Duration</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>${rowsHtml}</tbody>
        </table>
      </div>
    `;
  }

  function renderScheduleMessages(messages, awaitingOverdueResolution) {
    const feed = document.getElementById("daily-schedule-chat-list");
    if (!feed) {
      return;
    }

    const items = messages.length
      ? messages
      : [{ role: "assistant", content: "Send a morning task list to create today's timeline." }];

    feed.innerHTML = items
      .map((item) => buildFeedItemHtml(item.role, item.content))
      .join("");

    const badge = document.querySelector("#daily-schedule-chat-panel .warning-pill");
    if (badge) {
      badge.style.display = awaitingOverdueResolution ? "" : "none";
    }
  }

  function renderAirdropCards(airdrops, warnings, trigger) {
    const panel = document.getElementById("airdrop-results-panel");
    if (!panel) {
      return;
    }

    const warningsHtml = buildWarningsHtml(warnings);
    const summaryItems = [
      { label: "Last trigger", value: trigger },
      { label: "Ranked", value: airdrops.length },
    ];

    if (!airdrops.length) {
      panel.innerHTML = `
        ${buildSummaryStrip(summaryItems)}
        ${warningsHtml}
        ${buildEmptyState({
          icon: "🪂",
          eyebrow: "No opportunities yet",
          title: "No ranked airdrops are stored for the latest cycle.",
          copy: "Run a crawl or adjust the source selection to populate the radar.",
          actionLabel: "Run crawl",
          triggerClick: "#crypto-airdrop-controls [data-run-airdrop]",
        })}
      `;
      return;
    }

    const rowsHtml = airdrops
      .map(
        (airdrop) => `
          <tr tabindex="0" data-requirements="${escapeHtml(airdrop.requirements_summary || "")}">
            <td class="cell-score">${escapeHtml(String(airdrop.ai_score ?? 0))}</td>
            <td class="cell-title">${escapeHtml(airdrop.name)}</td>
            <td>${escapeHtml(airdrop.chain || "Unknown")}</td>
            <td class="cell-nowrap cell-muted">${escapeHtml(airdrop.deadline || "—")}</td>
            <td class="cell-reason">${escapeHtml(airdrop.ai_reason || "")}</td>
            <td>${escapeHtml(formatSource(airdrop.source))}</td>
            <td class="cell-link">
              <a href="${escapeHtml(airdrop.source_url)}" target="_blank" rel="noreferrer">Open ↗</a>
            </td>
          </tr>
        `
      )
      .join("");

    panel.innerHTML = `
      ${buildSummaryStrip(summaryItems)}
      ${warningsHtml}
      <div class="data-table-wrap">
        <table class="data-table" id="airdrop-table">
          <thead>
            <tr>
              <th data-sort="score">Score</th>
              <th data-sort="name">Name</th>
              <th data-sort="chain">Chain</th>
              <th data-sort="deadline">Deadline</th>
              <th>AI Reason</th>
              <th data-sort="source">Source</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>${rowsHtml}</tbody>
        </table>
      </div>
    `;
  }

  function renderAirdropMessages(messages) {
    const feed = document.getElementById("crypto-airdrop-chat-list");
    if (!feed) {
      return;
    }

    const items = messages.length
      ? messages
      : [
          {
            role: "assistant",
            content: "Run a crawl, then ask for a filter like `show only Ethereum airdrops`.",
          },
        ];

    feed.innerHTML = items
      .map((item) => buildFeedItemHtml(item.role, item.content))
      .join("");
  }

  function handleDocumentClick(event) {
    const sidebarOpen = event.target.closest("[data-sidebar-open]");
    if (sidebarOpen) {
      setSidebarOpen(true);
      return;
    }

    const sidebarClose = event.target.closest("[data-sidebar-close]");
    if (sidebarClose) {
      setSidebarOpen(false);
      return;
    }

    const sortHeader = event.target.closest("th[data-sort]");
    if (sortHeader) {
      sortTable(sortHeader);
      return;
    }

    const navLink = event.target.closest(".sidebar .nav-link");
    if (navLink && window.innerWidth <= 767) {
      setSidebarOpen(false);
    }

    const triggerButton = event.target.closest("[data-trigger-click]");
    if (triggerButton) {
      const target = document.querySelector(triggerButton.dataset.triggerClick);
      if (target) {
        target.click();
      }
      return;
    }

    const focusButton = event.target.closest("[data-focus-target]");
    if (focusButton) {
      const target = document.querySelector(focusButton.dataset.focusTarget);
      if (target) {
        target.focus();
      }
      return;
    }

    const filterToggle = event.target.closest("[data-filter-toggle]");
    if (filterToggle) {
      const target = document.querySelector(filterToggle.dataset.filterToggle);
      if (!target) {
        return;
      }
      const isOpen = target.classList.toggle("is-open");
      filterToggle.setAttribute("aria-expanded", String(isOpen));
    }
  }

  function handleDocumentChange(event) {
    const preset = event.target.closest(".cron-preset");
    if (!preset || !preset.dataset.cronTarget) {
      return;
    }

    const input = document.getElementById(preset.dataset.cronTarget);
    if (!input || !preset.value) {
      return;
    }

    input.value = preset.value;
    input.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function handleBeforeRequest(event) {
    const button = findLoadingButton(event.detail.elt);
    setButtonLoading(button, true);
  }

  function handleAfterRequest(event) {
    const button = findLoadingButton(event.detail.elt, true);
    setButtonLoading(button, false);
    if (event.detail.elt instanceof HTMLFormElement) {
      submitters.delete(event.detail.elt);
    }
  }

  function handleBeforeSwap(event) {
    const xhr = event.detail.xhr;
    const target = event.detail.target;

    if (!xhr || !target) {
      return;
    }

    const isClientError = xhr.status >= 400 && xhr.status < 500;
    const isHtmlResponse = xhr.getResponseHeader("Content-Type")?.includes("text/html");

    if (!isClientError || !isHtmlResponse) {
      return;
    }

    event.detail.shouldSwap = true;
    event.detail.isError = false;
  }

  function handleFormSubmit(event) {
    if (!(event.target instanceof HTMLFormElement)) {
      return;
    }

    const submitter =
      event.submitter ||
      event.target.querySelector("button[data-loading-text], input[data-loading-text]");

    if (submitter) {
      submitters.set(event.target, submitter);
    }
  }

  function findLoadingButton(triggerElement, preferLoading = false) {
    if (!triggerElement) {
      return null;
    }

    if (triggerElement.matches?.("button[data-loading-text], input[data-loading-text]")) {
      return triggerElement;
    }

    if (triggerElement.matches?.("button.is-loading, input.is-loading")) {
      return triggerElement;
    }

    if (triggerElement instanceof HTMLFormElement && submitters.has(triggerElement)) {
      return submitters.get(triggerElement) || null;
    }

    if (triggerElement.querySelector) {
      const selector = preferLoading
        ? "button.is-loading, input.is-loading"
        : "button[data-loading-text], input[data-loading-text]";

      const existing = triggerElement.querySelector(selector);
      if (existing) {
        return existing;
      }
    }

    const active = document.activeElement;
    if (
      active &&
      active.form === triggerElement &&
      active.matches?.("button[data-loading-text], input[data-loading-text], button.is-loading")
    ) {
      return active;
    }

    return null;
  }

  function setButtonLoading(button, isLoading) {
    if (!button) {
      return;
    }

    if (isLoading) {
      if (!button.dataset.originalText) {
        button.dataset.originalText = button.textContent;
      }
      button.classList.add("is-loading");
      button.textContent = button.dataset.loadingText || "Loading...";
      return;
    }

    button.classList.remove("is-loading");
    if (button.dataset.originalText) {
      button.textContent = button.dataset.originalText;
    }
  }

  function syncResponsivePanels() {
    const desktopFilterLayout = window.innerWidth > 1024;
    document.querySelectorAll("[data-filter-toggle]").forEach((button) => {
      const target = document.querySelector(button.dataset.filterToggle);
      if (!target) {
        return;
      }
      if (desktopFilterLayout) {
        target.classList.remove("is-open");
        button.setAttribute("aria-expanded", "false");
      } else if (target.classList.contains("is-open")) {
        button.setAttribute("aria-expanded", "true");
      }
    });

    if (window.innerWidth > 767) {
      setSidebarOpen(false);
    }
  }

  function sortTable(header) {
    const table = header.closest("table");
    const body = table?.querySelector("tbody");
    if (!table || !body) {
      return;
    }

    const headers = Array.from(table.querySelectorAll("thead th"));
    const columnIndex = headers.indexOf(header);
    if (columnIndex < 0) {
      return;
    }

    const nextDirection = header.dataset.dir === "asc" ? "desc" : "asc";
    headers.forEach((item) => {
      item.dataset.dir = "";
      item.classList.remove("sort-asc", "sort-desc");
    });
    header.dataset.dir = nextDirection;
    header.classList.add(nextDirection === "asc" ? "sort-asc" : "sort-desc");

    const rows = Array.from(body.querySelectorAll("tr"));
    rows.sort((rowA, rowB) => {
      const valueA = getSortableValue(rowA, columnIndex, header.dataset.sort);
      const valueB = getSortableValue(rowB, columnIndex, header.dataset.sort);

      if (valueA < valueB) {
        return nextDirection === "asc" ? -1 : 1;
      }
      if (valueA > valueB) {
        return nextDirection === "asc" ? 1 : -1;
      }
      return 0;
    });

    rows.forEach((row) => body.appendChild(row));
  }

  function getSortableValue(row, columnIndex, key) {
    const cell = row.children[columnIndex];
    const text = cell ? cell.textContent.trim() : "";

    if (key === "score" || key === "salary") {
      const numeric = Number(text.replaceAll(",", "").match(/-?\d+(\.\d+)?/)?.[0] || 0);
      return Number.isNaN(numeric) ? 0 : numeric;
    }

    return text.toLowerCase();
  }

  function buildWarningsHtml(warnings) {
    if (!warnings.length) {
      return "";
    }

    return `
      <div class="warning-stack">
        ${warnings
          .map((warning) => `<div class="warning-banner">${escapeHtml(warning)}</div>`)
          .join("")}
      </div>
    `;
  }

  function buildSummaryStrip(items) {
    const visibleItems = items.filter((item) => item.value !== null && item.value !== undefined);
    if (!visibleItems.length) {
      return "";
    }

    return `
      <div class="summary-strip">
        ${visibleItems
          .map(
            (item) => `
              <div>
                <span class="summary-label">${escapeHtml(item.label)}</span>
                <strong>${escapeHtml(String(item.value))}</strong>
              </div>
            `
          )
          .join("")}
      </div>
    `;
  }

  function buildEmptyState({
    icon,
    eyebrow,
    title,
    copy,
    actionLabel,
    triggerClick,
    focusTarget,
  }) {
    const actionAttr = triggerClick
      ? `data-trigger-click="${escapeHtml(triggerClick)}"`
      : `data-focus-target="${escapeHtml(focusTarget || "")}"`;

    return `
      <article class="empty-state compact-empty-state">
        <div class="empty-icon">${icon}</div>
        <p class="eyebrow">${escapeHtml(eyebrow)}</p>
        <h3>${escapeHtml(title)}</h3>
        <p>${escapeHtml(copy)}</p>
        ${
          actionLabel
            ? `<button type="button" class="btn btn-primary" ${actionAttr}>${escapeHtml(
                actionLabel
              )}</button>`
            : ""
        }
      </article>
    `;
  }

  function buildTagList(items) {
    const tags = items.slice(0, 3);
    const overflow = items.length - tags.length;

    return `
      <div class="tag-list">
        ${tags.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
        ${overflow > 0 ? `<span class="tag-overflow">+${overflow}</span>` : ""}
      </div>
    `;
  }

  function buildSalaryLabel(min, max) {
    if (min == null && max == null) {
      return "Negotiable";
    }
    if (min == null) {
      return `Up to ${Number(max).toLocaleString()} USD`;
    }
    if (max == null) {
      return `From ${Number(min).toLocaleString()} USD`;
    }
    return `${Number(min).toLocaleString()}-${Number(max).toLocaleString()} USD`;
  }

  function formatLabel(value) {
    return String(value).replaceAll("_", " ");
  }

  function buildFeedItemHtml(role, content) {
    return `
      <li class="${getFeedItemClass(role)}">
        <span class="feed-tag">${escapeHtml(role)}</span>
        <p>${escapeHtml(content)}</p>
      </li>
    `;
  }

  function getFeedItemClass(tag) {
    const normalized = String(tag || "assistant").toLowerCase().replaceAll("_", "-");

    if (normalized === "user") {
      return "is-user";
    }
    if (normalized === "assistant" || normalized === "chat") {
      return "is-assistant";
    }
    if (normalized === "notify") {
      return "is-notify";
    }
    if (normalized === "status") {
      return "is-status";
    }
    if (normalized === "ui") {
      return "is-ui";
    }
    if (normalized === "warn" || normalized === "warning" || normalized === "error") {
      return "is-warn";
    }

    return `is-${normalized}`;
  }

  function setSidebarOpen(isOpen) {
    document.body.classList.toggle("sidebar-open", isOpen);
    document.querySelectorAll("[data-sidebar-open]").forEach((button) => {
      button.setAttribute("aria-expanded", String(isOpen));
    });
  }

  function formatSource(value) {
    const normalized = String(value || "").replaceAll("_", " ").trim();
    if (!normalized) {
      return "Manual";
    }

    return normalized.replace(/\b\w/g, (char) => char.toUpperCase());
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  window.addEventListener("beforeunload", () => {
    if (stream) {
      stream.close();
    }
  });

  return {
    closeModal,
    requestNotifications,
    init,
  };
})();

window.AppShell = AppShell;
document.addEventListener("DOMContentLoaded", AppShell.init);
