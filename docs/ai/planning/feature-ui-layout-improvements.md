# Plan: UI Layout & Component Display Improvements

Note: All content in this document must be written in English.

---
epic_plan: null
requirement: null
---

## 1. Codebase Context

### Key Files to Reference
- `frontend/templates/partials/job_cards.html` — Current card grid; full replacement with table
- `frontend/templates/partials/airdrop_cards.html` — Current card grid reusing job-card CSS; full replacement with table
- `frontend/templates/partials/daily_schedule_timeline.html` — Current `<ol>` list; replace with table
- `frontend/static/app.js:160-227` — `renderJobResults()` builds job card HTML inline; must be rewritten to render table rows
- `frontend/static/app.js:239-293` — `renderScheduleTimeline()` builds timeline HTML inline; must be rewritten for table
- `frontend/static/app.js:322-385` — `renderAirdropCards()` builds airdrop card HTML inline; must be rewritten for table
- `frontend/templates/job_finder.html` — workspace-grid layout `1.5fr 0.9fr` needs restructure
- `frontend/templates/daily_scheduler.html` — schedule-grid `1.2fr 1fr` needs restructure
- `frontend/templates/crypto_airdrop.html` — workspace-grid needs restructure
- `frontend/static/style.css` — New CSS classes needed: `.data-table`, `.result-table`, `.page-layout`, `.filter-sidebar`

### Architectural Patterns
- **HTMX partial swaps**: `hx-target="#job-results-panel"`, `hx-target="#airdrop-results-panel"`, `hx-target="#daily-schedule-timeline"` — these IDs must be preserved on wrapper elements; only inner HTML structure changes
- **JS inline rendering**: `renderJobResults()`, `renderAirdropCards()`, `renderScheduleTimeline()` render full HTML strings via `innerHTML`; these must produce table HTML matching the new CSS
- **Jinja2 server-side render**: Partial templates (`job_cards.html`, `airdrop_cards.html`, `daily_schedule_timeline.html`) also render the initial page-load state; both JS and template must produce identical table structure

---

## 2. Problem Analysis per Page

### Page 1: Job Finder (`/agents/job_finder`)

**Current layout:**
```
[Hero Panel — large, accent-copper]
[workspace-grid: 1.5fr | 0.9fr]
  Left (bigger): Filters form + sources checkboxes
  Right (smaller): Activity feed (usually empty) + insight mini-cards
[Full-width results panel]
  Job card grid: auto-fit, minmax 260px
```

**Problems:**
1. **Tỷ lệ layout ngược**: Filter panel (secondary action) to hơn activity feed (secondary info). Results (primary content) bị đẩy xuống dưới màn hình.
2. **Card grid**: 50+ jobs → vô số cards, không thể so sánh. Mỗi card cao ~200px, phải cuộn rất nhiều. Không biết job nào có score cao hơn nếu không cuộn hết.
3. **Activity feed panel**: Thường chỉ có 0–3 items. Chiếm ~40% màn hình mà chứa ít thông tin. Insight mini-cards là placeholder content.
4. **Hero panel**: Text dài 3 dòng, badge provider/model. Mỗi lần vào trang phải nhìn thấy nhưng không thêm giá trị gì cho daily use.

**New layout:**
```
[Compact page header: title + status chip + "Run crawl" button]
[Two-column: filter-sidebar (280px fixed) | main-content (flex: 1)]
  Left sidebar: Filters form (sticky, scrollable)
  Right main: Results table
    [Summary strip: Crawled N | Matched N | Last trigger: ...]
    [Table: Score | Title | Company | Location | Salary | Source | Link]
[Activity feed: collapsed by default, expandable via "Show activity" toggle]
```

---

### Page 2: Daily Scheduler (`/agents/daily_scheduler`)

**Current layout:**
```
[Hero Panel — accent-teal]
[workspace-grid schedule-grid: 1.2fr | 1fr]
  Left: Timeline panel (today's schedule as <ol> numbered cards)
  Right: Controls (cron settings form) + Chat (planner transcript + textarea)
```

**Problems:**
1. **Chat bị chia nhỏ**: Controls và Chat nhét vào cùng right panel. User phải cuộn trong panel nhỏ để thấy cả hai.
2. **Timeline as fancy list**: `<ol>` với numbered cards không thể so sánh status của nhiều tasks. A table makes it scannable: # | Task | Time Range | Duration | Status — 5 tasks visible above the fold.
3. **Cron label text**: "Reminder cron", "Reset cron" — người dùng không biết đây là gì. No description.
4. **Workday start**: Text input with value like "09:00" — no time picker, no description.
5. **Controls + Chat đều trong right panel**: Controls thực ra ít dùng (chỉ setup once). Chat là primary interaction. Họ nên được tách riêng, không chồng lên nhau.

**New layout:**
```
[Compact page header: title + status chip + "Send to planner" action shortcut]
[Full-width chat bar: textarea + Send button — primary action always visible]
[Two-column: main-content (flex: 1) | right-panel (320px)]
  Left main: Timeline table
    [Summary: N scheduled | N active]
    [Table: # | Task | Time | Duration | Status]
  Right panel: Schedule settings (collapsible section)
    [Reminder cron + helper text]
    [Reset cron + helper text]
    [Workday start time input]
    [Break / Default minutes]
    [Save button]
```

---

### Page 3: Crypto Airdrop (`/agents/crypto_airdrop`)

**Current layout:**
```
[Hero Panel — accent-amber]
[workspace-grid: 1.5fr | 0.9fr]
  Left: Source controls (cron input + source checkboxes)
  Right: Chat panel (radar transcript + chat form)
[Full-width results panel]
  Airdrop card grid: reuses .job-card-grid and .job-card CSS
```

**Problems:**
1. **Results use wrong CSS classes**: `.job-card-grid`, `.job-card`, `.airdrop-card` — airdrop cards are built on top of job card styles. Semantically wrong and visually indistinguishable.
2. **Card grid**: Same problem as jobs. Name | Chain | Score | Deadline is better as table columns.
3. **Controls panel (left, 1.5fr)**: Cron + checkboxes don't need 1.5fr of width. A narrow sidebar (240px) is enough.
4. **Chat panel (right, 0.9fr)**: The chat (filter commands like "show only Ethereum airdrops") is more important than source config. It should be more prominent.
5. **`requirements_summary` and `ai_reason`**: Currently 2 separate `<p class="card-copy">` elements stacked inside the card. In a table row, they can be a single truncated column with a tooltip/expand.

**New layout:**
```
[Compact page header: title + status chip + "Run crawl" button]
[Two-column: left-panel (260px) | main-content (flex: 1)]
  Left panel:
    Source settings (cron + checkboxes + save button)
    ——— divider ———
    Chat filter (transcript + textarea + apply)
  Right main: Results table
    [Summary: Crawled N | Ranked N | Trigger: ...]
    [Table: Score | Name | Chain | Deadline | AI Reason | Source | Link]
```

---

### Page 4: Dashboard (`/`)

**Current layout:**
```
[Hero Panel — long description text + "Platform First" badge]
[3-column dashboard-grid]
  Agent cards: Provider | Title | Status | Model | API key | Storage | Link
```

**Problems:**
1. **Hero panel is too heavy**: 3 lines of description text + badge for an overview page. On first visit it's helpful, but daily users don't need it.
2. **Dashboard cards are fine** — 3 cards is appropriate for card layout. No change needed structurally.
3. **Card metric-list**: Shows "API key" as the env var name (e.g. `OPENAI_API_KEY`). This is a config detail, not a status. Could be shown on hover or removed from daily view.

**Minimal fix:** Reduce hero panel to compact 1-line header. Optionally collapse the hero panel into a `<details>` element.

---

## 3. Goal & Acceptance Criteria

### Goal
Restructure the page layouts and replace card grids with data tables so that information-dense result sets (jobs, airdrops, schedule tasks) are scannable and comparable at a glance, without changing any backend logic or HTMX attributes.

### Acceptance Criteria

- Given I am on the Job Finder page with 10+ results, When the results load, Then I see a table with rows (not cards) where I can see Score, Title, Company, Location, Salary in the same horizontal line per job.
- Given I am on the Daily Scheduler page, When today's schedule has 8 tasks, Then I can see all 8 tasks in a table above the fold without scrolling (table rows are compact ~44px each).
- Given I am on the Crypto Airdrop page, When airdrops are loaded, Then the results display as a table distinct from job styling, with Name, Chain, Score, Deadline visible per row.
- Given I am on the Job Finder page, When I look at the filter area, Then the filter panel is on the left in a narrow sidebar (~280px) and the results table takes the remaining screen width.
- Given I resize to 900px wide, Then the filter sidebar collapses to a toggleable filter drawer above the table (not a permanent sidebar).

---

## 4. Risks & Assumptions

### Risks
- `app.js` renders job/airdrop/schedule HTML inline via template strings — both `renderJobResults()`, `renderAirdropCards()`, and `renderScheduleTimeline()` must be rewritten to produce `<tr>` rows inside a `<tbody>`; the table `<thead>` wrapper is rendered server-side (Jinja2 partial), not by JS. This creates a split responsibility: JS injects rows into a pre-existing `<table>` element rather than replacing the full panel.
- HTMX `hx-swap-oob="innerHTML"` in `daily_schedule_chat.html:53` targets `#daily-schedule-timeline` — the table wrapper element must keep this ID
- Long text in `ai_reason` field (can be 2–4 sentences): in table cells, needs `max-width` + `overflow: hidden; text-overflow: ellipsis` or a two-line clamp; full text accessible on row hover/expand
- Tech stack tags in job table: currently rendered as multiple `<span>` pills. In a table cell, truncate to first 3 items + "+N more" badge
- Chat panel in Daily Scheduler currently uses `hx-target="#daily-schedule-chat-panel"` with `hx-swap="innerHTML"` — panel ID must be preserved after restructure

### Assumptions
- No changes to Python/FastAPI backend data models or response shapes
- HTMX `hx-*` attributes are untouchable
- Table sorting is client-side only (JS), not server-side; sort state is not persisted
- Mobile breakpoint (≤900px): tables get horizontal scroll, not reformatted to cards
- The activity feed in Job Finder is preserved but moved to a collapsible section (not removed, since it receives SSE events via `id="agent-activity-feed"`)

---

## 5. Definition of Done
- [x] Job Finder results render as `<table>` with columns: Score | Title | Company | Location | Salary | Tech Stack | Source | Link
- [x] Airdrop results render as `<table>` with columns: Score | Name | Chain | Deadline | AI Reason | Source | Link
- [x] Daily schedule renders as `<table>` with columns: # | Task | Time | Duration | Status
- [x] `app.js` JS rendering functions (`renderJobResults`, `renderAirdropCards`, `renderScheduleTimeline`) produce table rows that match the server-side Jinja2 table structure
- [x] Job Finder layout: filter sidebar is 280px, results table takes remaining width
- [x] Daily Scheduler: chat textarea is always visible without scrolling; settings are in a collapsible section
- [x] Crypto Airdrop: no `.job-card` or `.job-card-grid` classes used in airdrop results
- [x] Hero panels on agent pages are compact (single heading + badge row, no long description paragraph)
- [x] Activity feed in Job Finder preserved with same element ID but placed in a collapsible section
- [x] Client-side sort works on Score column (at minimum) for job and airdrop tables
- [x] No HTMX `hx-*` attributes are modified
- [x] All table elements are keyboard navigable (tab through rows/links)

---

## 6. Implementation Plan

### Summary
Replace card grids with `<table>` elements in all three agent result panels, restructure page layouts to give filter panels a fixed sidebar width, move chat to a prominent position in Daily Scheduler, and add client-side sort to result tables. Both the Jinja2 partials (server-render) and `app.js` inline renderers must produce matching table HTML.

Execution note:
- Implemented together with `feature-ui-redesign-dark-theme.md` as one merged frontend pass.
- Responsive contract used in code: `1200px` tighten layout, `900px` app shell becomes top-nav and filter sidebars collapse behind toggle buttons, `768px` stack topbar/forms, `480px` compress spacing and expand actions full-width.
- Jinja and `app.js` both render full table HTML so HTMX partial swaps and SSE-driven updates share one structure.
- Cron preset helper work landed in the partials that own the form controls.

---

### Phase 1: CSS — Add Table & Layout Styles

- [x] MODIFIED `frontend/static/style.css` — Add new layout and table component classes
  ```
  New classes to add (do not remove existing classes):

  Section: Page layout system
    .page-layout
      display: grid
      grid-template-columns: 280px 1fr
      gap: 0
      min-height: calc(100vh - topbar-height)

    .filter-sidebar
      padding: 20px 16px
      border-right: 1px solid var(--border)
      overflow-y: auto
      /* Sticky when parent is page-layout */
      position: sticky
      top: 0
      max-height: 100vh

    .page-main
      padding: 20px 24px
      overflow-x: auto   /* allows table horizontal scroll */

    .page-header
      display: flex
      align-items: center
      justify-content: space-between
      gap: 16px
      padding-bottom: 16px
      border-bottom: 1px solid var(--border)
      margin-bottom: 20px

    .page-header h2
      margin: 0
      font: 600 20px/1.3 var(--display)

    /* Compact hero: replaces the large hero-panel on agent pages */
    .page-hero
      display: flex
      align-items: center
      gap: 16px
      padding: 12px 16px
      background: var(--surface)
      border: 1px solid var(--border)
      border-radius: 10px
      margin-bottom: 20px

    .page-hero .hero-badge
      margin-left: auto
      flex-shrink: 0
      padding: 8px 12px
      border-radius: 8px
      font: 500 12px var(--mono)

  Section: Data table
    .data-table-wrap
      overflow-x: auto      /* horizontal scroll on small screens */
      border: 1px solid var(--border)
      border-radius: 10px

    .data-table
      width: 100%
      border-collapse: collapse
      font-size: 14px

    .data-table thead th
      padding: 10px 14px
      text-align: left
      font: 600 11px var(--mono)
      letter-spacing: 0.08em
      text-transform: uppercase
      color: var(--ink-soft)
      border-bottom: 1px solid var(--border)
      white-space: nowrap
      background: var(--surface)   /* sticky header bg */
      cursor: pointer              /* sortable columns */
      user-select: none

    .data-table thead th:hover
      color: var(--ink)

    .data-table thead th.sort-asc::after
      content: " ↑"
      color: var(--blue)

    .data-table thead th.sort-desc::after
      content: " ↓"
      color: var(--blue)

    .data-table tbody tr
      border-bottom: 1px solid var(--border)
      transition: background 120ms

    .data-table tbody tr:last-child
      border-bottom: none

    .data-table tbody tr:hover
      background: rgba(255, 255, 255, 0.03)

    .data-table td
      padding: 12px 14px
      vertical-align: middle

    .data-table td.cell-score
      font: 700 16px var(--display)
      color: var(--blue)
      width: 56px
      text-align: center

    .data-table td.cell-title
      font-weight: 600
      max-width: 240px

    .data-table td.cell-title small
      display: block
      font: 400 12px var(--body)
      color: var(--ink-soft)
      margin-top: 2px

    .data-table td.cell-reason
      max-width: 280px
      color: var(--ink-soft)
      font-size: 13px
      /* Clamp to 2 lines */
      display: -webkit-box
      -webkit-line-clamp: 2
      -webkit-box-orient: vertical
      overflow: hidden

    .data-table td.cell-tags
      max-width: 180px

    .tag-list
      display: flex
      flex-wrap: wrap
      gap: 4px

    .tag-list span
      padding: 3px 8px
      border-radius: 4px
      background: rgba(255, 255, 255, 0.06)
      border: 1px solid var(--border)
      font: 500 11px var(--mono)
      color: var(--ink-soft)
      white-space: nowrap

    .tag-overflow
      padding: 3px 8px
      border-radius: 4px
      background: var(--blue-soft)
      font: 500 11px var(--mono)
      color: var(--blue)

    .cell-link a
      font: 500 13px var(--body)
      color: var(--blue)
      text-decoration: underline
      text-underline-offset: 3px
      white-space: nowrap

  Section: Collapsible activity feed
    .collapsible-section
      margin-top: 20px
      border: 1px solid var(--border)
      border-radius: 10px
      overflow: hidden

    .collapsible-toggle
      width: 100%
      padding: 12px 16px
      display: flex
      align-items: center
      justify-content: space-between
      background: var(--surface)
      border: none
      cursor: pointer
      font: 500 13px var(--body)
      color: var(--ink-soft)
      text-align: left

    .collapsible-toggle:hover
      color: var(--ink)

    .collapsible-toggle::after
      content: "▸"
      transition: transform 200ms

    .collapsible-toggle[aria-expanded="true"]::after
      transform: rotate(90deg)

    .collapsible-body
      display: none
      padding: 12px 16px
      border-top: 1px solid var(--border)

    .collapsible-body.is-open
      display: block

  Section: Responsive table
    @media (max-width: 900px):
      .page-layout
        grid-template-columns: 1fr

      .filter-sidebar
        position: static
        max-height: none
        border-right: none
        border-bottom: 1px solid var(--border)

      /* Filter sidebar collapsible on mobile */
      .filter-sidebar[data-collapsed="true"]
        display: none

      .filter-toggle
        display: flex    /* show toggle button on mobile */

    @media (min-width: 901px):
      .filter-toggle
        display: none   /* hide toggle button on desktop */
  ```

---

### Phase 2: Job Finder — Layout Restructure & Table Results

- [x] MODIFIED `frontend/templates/job_finder.html` — Restructure to page-layout
  ```
  Current structure:
    hero-panel (large, full width)
    workspace-grid (1.5fr | 0.9fr)
      Left: filters + activity feed placeholder
      Right: insights mini-cards
    results-panel (full width below)

  New structure:
    page-hero (compact: title + status + "Run crawl" button)
    page-layout (280px sidebar | 1fr main)
      Left filter-sidebar:
        <h3 class="sidebar-heading">Filters</h3>
        [include partials/job_finder_filters.html]
        collapsible-section "Live activity"
          [activity-feed list — id="agent-activity-feed" preserved]
      Right page-main:
        [include partials/job_cards.html]  ← now renders a table

  Key structural changes:
    - Remove large hero-panel, replace with .page-hero div
    - Remove workspace-grid div entirely
    - Filter form moves to .filter-sidebar (left column)
    - Activity feed moves to collapsible-section inside filter-sidebar
    - Remove insight mini-cards (placeholder content)
    - id="job-results-panel" preserved on the page-main section wrapper

  HTMX target preservation:
    - id="job-filter-panel" on the filter sidebar inner div — keep
    - id="job-run-feedback" inside filter form — keep
    - id="agent-activity-feed" on the <ul> — keep (moved to collapsible)
    - id="job-results-panel" on results wrapper — keep
  ```

- [x] MODIFIED `frontend/templates/partials/job_cards.html` — Replace card grid with table
  ```
  New structure:

  {% if job_summary %}
    <div class="summary-strip">
      [same 3 summary items as current: Last trigger | Crawled | Matched]
    </div>
  {% endif %}

  {% if job_warnings %}
    <div class="warning-stack">...</div>
  {% endif %}

  {% if jobs %}
    <div class="data-table-wrap">
      <table class="data-table" id="job-table">
        <thead>
          <tr>
            <th data-sort="ai_score">Score</th>
            <th data-sort="title">Title / Company</th>
            <th data-sort="location">Location</th>
            <th data-sort="salary_min">Salary</th>
            <th>Stack</th>
            <th>Source</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          {% for job in jobs %}
            <tr>
              <td class="cell-score">{{ job.ai_score or 0 }}</td>
              <td class="cell-title">
                {{ job.title }}
                <small>{{ job.company }}</small>
              </td>
              <td>{{ job.location }}</td>
              <td>{{ job.salary_label }}</td>
              <td class="cell-tags">
                <div class="tag-list">
                  {% for item in job.tech_stack[:3] %}
                    <span>{{ item }}</span>
                  {% endfor %}
                  {% if job.tech_stack|length > 3 %}
                    <span class="tag-overflow">+{{ job.tech_stack|length - 3 }}</span>
                  {% endif %}
                </div>
              </td>
              <td>{{ job.source|replace('_', ' ')|title }}</td>
              <td class="cell-link">
                <a href="{{ job.url }}" target="_blank" rel="noreferrer">Open ↗</a>
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  {% else %}
    <article class="empty-state">
      <p class="eyebrow">No matches</p>
      <h3>No jobs passed the hard filters yet.</h3>
      <p>Adjust salary, location, or must-have frameworks, then run the crawl again.</p>
    </article>
  {% endif %}

  NOTE: ai_reason field is removed from the table visible columns.
  It is preserved as a data-reason attribute on each <tr> for potential
  future row-expand feature. This avoids table columns being too wide.
    <tr data-reason="{{ job.ai_reason | e }}">
  ```

---

### Phase 3: Daily Scheduler — Layout Restructure & Table Timeline

- [x] MODIFIED `frontend/templates/daily_scheduler.html` — Restructure layout
  ```
  Current: workspace-grid schedule-grid (1.2fr | 1fr)
    Left: Timeline panel
    Right: Controls + Chat (both stacked in one panel)

  New structure:
    page-hero (compact: title + status)
    Full-width chat panel (primary interaction — always visible at top)
      [include partials/daily_schedule_chat.html]
    Two-column below:
      page-layout (flex: 1 | 320px right panel)
        Left page-main: Timeline table
          [include partials/daily_schedule_timeline.html]
        Right panel:
          collapsible-section "Schedule settings"
            [include partials/daily_scheduler_controls.html]

  Rationale:
    Chat is the PRIMARY action (user pastes tasks to build timeline).
    Making it full-width at the top means it's always accessible.
    Settings (cron, workday start) are secondary — collapsed by default.
    Timeline is the OUTPUT — it gets the most horizontal space.

  HTMX target preservation:
    - id="daily-schedule-timeline" — keep on timeline wrapper
    - id="daily-schedule-controls" — keep on controls wrapper
    - id="daily-schedule-chat-panel" — keep on chat wrapper
    - id="daily-schedule-chat-list" on <ul> — keep
  ```

- [x] MODIFIED `frontend/templates/partials/daily_schedule_timeline.html` — Replace list with table
  ```
  New structure:

  {% if schedule_tasks %}
    <div class="summary-strip">
      [same summary: Scheduled N tasks | Active N]
    </div>

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
        <tbody>
          {% for task in schedule_tasks %}
            <tr>
              <td class="cell-score" style="color: var(--ink-soft); font-size: 13px">
                {{ "%02d"|format(loop.index) }}
              </td>
              <td class="cell-title">{{ task.title }}</td>
              <td style="white-space: nowrap; color: var(--ink-soft); font-size: 13px">
                {{ task.time_range }}
              </td>
              <td style="color: var(--ink-soft); font-size: 13px">
                {{ task.estimated_minutes }} min
              </td>
              <td>
                <span class="task-status status-{{ task.status|replace("_", "-") }}">
                  {{ task.status|replace("_", " ") }}
                </span>
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  {% else %}
    <article class="empty-state">
      [same as current]
    </article>
  {% endif %}
  ```

- [x] MODIFIED `frontend/templates/partials/daily_scheduler_controls.html` — Add helper text to fields
  ```
  Add helper text below each cron field:

  <label>
    Reminder cron
    <input type="text" name="reminder_cron" value="{{ schedule_settings.reminder_cron }}" />
    <small class="field-hint">When to send overdue task reminders. Example: 0 * * * * (every hour)</small>
  </label>
  <label>
    Reset cron
    <input type="text" name="reset_cron" value="{{ schedule_settings.reset_cron }}" />
    <small class="field-hint">When to clear the daily schedule. Example: 0 0 * * * (midnight)</small>
  </label>
  <label>
    Workday start
    <input type="time" name="workday_start" value="{{ schedule_settings.workday_start }}" />
    <small class="field-hint">Earliest time tasks are scheduled from.</small>
  </label>

  Add CSS for .field-hint:
    font: 12px var(--body); color: var(--ink-faint); margin-top: 4px; display: block
  ```

---

### Phase 4: Crypto Airdrop — Layout Restructure & Table Results

- [x] MODIFIED `frontend/templates/crypto_airdrop.html` — Restructure layout
  ```
  Current: workspace-grid (1.5fr | 0.9fr)
    Left: Source controls
    Right: Chat panel
  Below: results-panel (airdrop cards)

  New structure:
    page-hero (compact: title + status + "Run crawl" button)
    page-layout (260px left panel | 1fr main)
      Left panel:
        Source settings (cron + checkboxes + save)
        ——— divider ———
        Chat section (Radar transcript + filter textarea)
      Right page-main:
        [include partials/airdrop_cards.html]  ← now renders a table

  Rationale:
    Both controls and chat are secondary to the results.
    Grouping them in a narrow left panel gives results the full width.
    Chat (filter) is placed below source settings in the same sidebar.

  HTMX target preservation:
    - id="crypto-airdrop-controls" — keep on controls wrapper div
    - id="crypto-airdrop-run-feedback" — keep
    - id="crypto-airdrop-chat-panel" — keep
    - id="crypto-airdrop-chat-list" — keep
    - id="airdrop-results-panel" — keep on results wrapper
  ```

- [x] MODIFIED `frontend/templates/partials/airdrop_cards.html` — Replace card grid with table
  ```
  New structure:

  {% if airdrop_summary %}
    <div class="summary-strip">...</div>
  {% endif %}

  {% if airdrop_warnings %}
    <div class="warning-stack">...</div>
  {% endif %}

  {% if airdrops %}
    <div class="data-table-wrap">
      <table class="data-table" id="airdrop-table">
        <thead>
          <tr>
            <th data-sort="ai_score">Score</th>
            <th data-sort="name">Name</th>
            <th data-sort="chain">Chain</th>
            <th data-sort="deadline">Deadline</th>
            <th>AI Reason</th>
            <th>Source</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          {% for airdrop in airdrops %}
            <tr>
              <td class="cell-score">{{ airdrop.ai_score or 0 }}</td>
              <td class="cell-title">{{ airdrop.name }}</td>
              <td>{{ airdrop.chain }}</td>
              <td style="white-space: nowrap; font-size: 13px; color: var(--ink-soft)">
                {{ airdrop.deadline or "—" }}
              </td>
              <td class="cell-reason">{{ airdrop.ai_reason }}</td>
              <td>{{ airdrop.source|replace('_', ' ')|title }}</td>
              <td class="cell-link">
                <a href="{{ airdrop.source_url }}" target="_blank" rel="noreferrer">Open ↗</a>
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  {% else %}
    <article class="empty-state">
      <p class="eyebrow">No opportunities yet</p>
      <h3>No ranked airdrops are stored for the latest cycle.</h3>
      <p>Run a crawl or adjust the source selection to populate the radar.</p>
    </article>
  {% endif %}

  NOTE: requirements_summary field is removed from table view.
  Preserved as data-requirements="{{ airdrop.requirements_summary | e }}" on <tr>.
  ```

---

### Phase 5: Dashboard — Compact Hero

- [x] MODIFIED `frontend/templates/dashboard.html` — Replace large hero-panel with compact page-hero
  ```
  Current:
    <section class="hero-panel">
      <div>
        <p class="eyebrow">Foundation slice</p>
        <h2>Three agents, one shell, zero hard-coded page wiring.</h2>
        <p class="hero-copy">The registry, settings document, SSE stream...</p>
      </div>
      <div class="hero-badge">
        <span>Scope</span>
        <strong>Platform First</strong>
      </div>
    </section>

  New:
    <div class="page-hero">
      <div>
        <p class="eyebrow">Unified control room</p>
        <h2 style="margin: 0; font-size: 20px">AI Agent Tool</h2>
      </div>
      <span class="hero-badge">Platform First</span>
    </div>

  Rationale: Dashboard is visited frequently. The 3-line description
  adds no value after the first visit. A compact 1-row header keeps
  the agent cards immediately visible above the fold.
  ```

---

### Phase 6: JavaScript — Update Inline Renderers to Table HTML

- [x] MODIFIED `frontend/static/app.js` — Rewrite renderJobResults(), renderScheduleTimeline(), renderAirdropCards()
  ```
  Function: renderJobResults(payload)

  Current behavior:
    Renders job cards as <article class="job-card"> elements inside a .job-card-grid

  New behavior:
    Renders <tr> rows into the <tbody> of the existing #job-table element.
    If #job-table does not exist (empty state was shown), renders the full table structure.

  Logic flow:
    1. const panel = document.getElementById("job-results-panel")
    2. Build summary strip HTML (same as before)
    3. Build warnings HTML (same as before)
    4. If jobs.length === 0: render empty-state HTML (same message)
    5. Else: Build table HTML:
       - Outer: <div class="data-table-wrap"> + <table class="data-table" id="job-table">
       - <thead> with columns: Score | Title / Company | Location | Salary | Stack | Source | Link
       - <tbody> with one <tr> per job:
         - cell-score: job.ai_score
         - cell-title: job.title + <small>job.company</small>
         - location cell
         - salary: buildSalaryLabel(job.salary_min, job.salary_max)
         - cell-tags: first 3 tech_stack items as <span> + overflow badge if > 3
         - source cell: job.source.replaceAll("_", " ")
         - cell-link: <a href="job.url" target="_blank">Open ↗</a>
    6. panel.innerHTML = summaryHtml + warningsHtml + tableHtml

  Note: ai_reason stored as data-reason on <tr> for future expand

  ---

  Function: renderScheduleTimeline(tasks)

  Current behavior:
    Renders <li class="timeline-card"> elements inside <ol class="timeline-list rich-timeline">

  New behavior:
    Renders <tr> rows into <tbody> inside a <table class="data-table"> structure

  Logic flow:
    1. const panel = document.getElementById("daily-schedule-timeline")
    2. If tasks.length === 0: render empty-state (same message as current)
    3. Else:
       - Build summary strip (same: Scheduled N | Active N)
       - Build table HTML:
         <div class="data-table-wrap">
           <table class="data-table" id="schedule-table">
             <thead><tr><th>#</th><th>Task</th><th>Time</th><th>Duration</th><th>Status</th></tr></thead>
             <tbody>
               tasks.map((task, index) => `
                 <tr>
                   <td class="cell-score" style="color:var(--ink-soft);font-size:13px">
                     ${String(index+1).padStart(2,'0')}
                   </td>
                   <td class="cell-title">${escapeHtml(task.title)}</td>
                   <td style="white-space:nowrap;color:var(--ink-soft);font-size:13px">
                     ${escapeHtml(task.time_range || "")}
                   </td>
                   <td style="color:var(--ink-soft);font-size:13px">
                     ${escapeHtml(String(task.estimated_minutes))} min
                   </td>
                   <td>
                     <span class="task-status status-${escapeHtml(task.status.replaceAll('_','-'))}">
                       ${escapeHtml(task.status.replaceAll('_',' '))}
                     </span>
                   </td>
                 </tr>
               `).join("")
             </tbody>
           </table>
         </div>
    4. panel.innerHTML = summaryHtml + tableHtml

  ---

  Function: renderAirdropCards(airdrops, warnings, trigger)

  Current behavior:
    Renders <article class="job-card airdrop-card"> elements

  New behavior:
    Renders <tr> rows into a table. No job-card classes used.

  Logic flow:
    1. const panel = document.getElementById("airdrop-results-panel")
    2. Build warning HTML (same as current)
    3. If airdrops.length === 0: render empty-state (same message)
    4. Else: Build table HTML:
       - Same structure as job table but different columns:
         Score | Name | Chain | Deadline | AI Reason | Source | Link
       - cell-reason for ai_reason column (2-line clamp via CSS)
       - data-requirements on <tr> for requirements_summary
    5. panel.innerHTML = summaryHtml + warningsHtml + tableHtml

  ---

  Function: initTableSort()
    Called from init()
    Selects all [data-sort] th elements
    On click:
      1. Determine current sort direction (asc/desc) from data-dir attribute
      2. Toggle direction, update class (sort-asc / sort-desc), clear other th classes
      3. Get all <tr> rows from <tbody>
      4. Sort rows by td content at column index of clicked th
         - For numeric columns (score, salary): parseFloat(cell.textContent)
         - For text columns: cell.textContent.toLowerCase()
      5. Re-append sorted rows to tbody
    No network request — client-side only

  Updated init():
    function init() {
      connectStream();
      initTableSort();
    }
  ```

---

## 7. Follow-ups
- [ ] Add row-expand for ai_reason / requirements_summary: clicking a row shows a detail drawer below it
- [ ] Add column visibility toggle: let user show/hide columns (e.g., hide Source column)
- [ ] Filter sidebar on mobile: add toggle button to show/hide filter sidebar as a drawer
- [ ] Consider adding a "Copy to clipboard" button on table rows (copy job title + URL)
- [ ] Daily Scheduler: add drag-to-reorder rows in the schedule table (requires backend reorder endpoint)
- [ ] Pagination or virtual scroll for very large result sets (50+ jobs)
