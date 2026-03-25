# Plan: UI Redesign — Dark Professional Theme

Note: All content in this document must be written in English.

---
epic_plan: null
requirement: null
---

## 1. Codebase Context

### Similar Features
- `frontend/static/style.css` — Current CSS design system using warm cream palette; full rewrite target
- `frontend/templates/base.html` — App shell with sidebar + main layout; structure retained, class names updated
- `frontend/static/app.js` — IIFE module rendering job/airdrop/schedule updates dynamically; JS HTML strings must use new class names

### Reusable Components/Utils
- `frontend/templates/partials/` — 12 partial templates; each needs class updates, no logic changes
- HTMX `hx-get`, `hx-target`, `hx-swap` attributes on all forms — must NOT be modified, only surrounding HTML/classes change
- `AppShell.closeModal`, `AppShell.requestNotifications`, `AppShell.init` — public JS API must remain unchanged

### Architectural Patterns
- **Server-side rendering**: All HTML rendered by Jinja2; no client-side component framework
- **HTMX partial swaps**: Forms swap partial HTML into target divs; partial templates must use new CSS classes
- **IIFE module pattern**: `app.js` renders dynamic content via innerHTML string concatenation; new CSS class names must match
- **CSS custom properties**: All styling via `--var` tokens in `:root`; replacing the token set is the primary theming mechanism
- **No build step**: CSS and JS served as static files; changes take effect on browser reload

### Key Files to Reference
- `frontend/static/style.css:1-22` — Current `:root` token block (full replacement target)
- `frontend/static/app.js:160-227` — `renderJobResults()` builds job card HTML inline; update class names here
- `frontend/static/app.js:239-293` — `renderScheduleTimeline()` builds timeline HTML inline; update class names
- `frontend/static/app.js:322-385` — `renderAirdropCards()` builds airdrop card HTML inline; update class names
- `frontend/templates/base.html:26-52` — Sidebar HTML structure; sticky positioning added here

---

## 2b. Theme Specification

### Selected Theme
- **Name**: Dark Professional (Internal Tool)
- **Personality**: Focused, high-contrast, data-dense, minimal decoration

### Color Palette

**Background**:
- `--bg`: #0f1117 (page background)
- `--bg-alt`: #0d1117 (slightly deeper, for gradients)

**Surface**:
- `--surface`: #161b27 (cards, panels)
- `--surface-raised`: #1e2535 (elevated cards, dropdowns)
- `--surface-overlay`: rgba(22, 27, 39, 0.96) (modal, overlay)

**Text**:
- `--ink`: #e2e8f0 (primary text)
- `--ink-soft`: #94a3b8 (secondary/muted text)
- `--ink-faint`: #475569 (disabled, placeholder)

**Border**:
- `--border`: rgba(148, 163, 184, 0.12) (default)
- `--border-strong`: rgba(148, 163, 184, 0.24) (hover, focus)

**Primary Accent — Blue**:
- `--blue`: #3b82f6 (primary actions, links, active states)
- `--blue-hover`: #2563eb (hover)
- `--blue-soft`: rgba(59, 130, 246, 0.12) (soft badge backgrounds)
- `--blue-glow`: rgba(59, 130, 246, 0.20) (focus ring, glow)

**Secondary Accent — Teal**:
- `--teal`: #14b8a6 (Job Finder accent)
- `--teal-soft`: rgba(20, 184, 166, 0.12)

**Tertiary Accent — Amber**:
- `--amber`: #f59e0b (Crypto Airdrop accent, warnings)
- `--amber-soft`: rgba(245, 158, 11, 0.12)

**Semantic**:
- `--success`: #10b981 (green)
- `--success-soft`: rgba(16, 185, 129, 0.12)
- `--danger`: #ef4444 (red)
- `--danger-soft`: rgba(239, 68, 68, 0.12)
- `--warning`: #f59e0b (amber — same as `--amber`)
- `--warning-soft`: rgba(245, 158, 11, 0.12)
- `--info`: #3b82f6 (blue — same as `--blue`)
- `--info-soft`: rgba(59, 130, 246, 0.12)

### Typography

**Font Families** (unchanged — existing Google Fonts link kept):
- Display/Heading: `"Space Grotesk", system-ui, sans-serif`
- Body: `"IBM Plex Sans", system-ui, sans-serif`
- Mono: `"IBM Plex Mono", ui-monospace, monospace`

**Type Scale**:
- xs: 11px
- sm: 12px
- base: 14px (body default — increased from implied ~12px)
- md: 15px
- lg: 16px
- xl: 18px
- 2xl: 20px
- 3xl: 24px
- 4xl: 28px
- 5xl: 32px

**Font Weights**:
- normal: 400
- medium: 500
- semibold: 600
- bold: 700

### Spacing Scale

**Scale** (8px grid): 4, 8, 12, 16, 20, 24, 32, 40, 48, 64px

**Usage**:
- xs: 4px (tight gaps within components)
- sm: 8px (icon-to-text gap, tight padding)
- md: 16px (standard component padding)
- lg: 24px (section spacing)
- xl: 32px (page-level spacing)
- 2xl: 48px (large section gaps)

### Visual Style

**Border Radius**:
- sm: 6px (inputs, small tags)
- md: 8px (buttons)
- lg: 12px (cards, panels)
- xl: 16px (modals, hero panels)
- full: 9999px (pills, badges)

**Shadows** (dark-theme aware — subtle uplift, no bright halos):
- sm: `0 1px 3px rgba(0, 0, 0, 0.4)`
- md: `0 4px 12px rgba(0, 0, 0, 0.4)`
- lg: `0 8px 24px rgba(0, 0, 0, 0.5)`
- xl: `0 16px 48px rgba(0, 0, 0, 0.6)`

**Removed from current design**:
- `backdrop-filter: blur()` on most elements (kept ONLY on modal overlay)
- `radial-gradient` body backgrounds
- `grid-pattern` `::before` overlay on body
- `transform: translateX/Y` on nav-link hover (replaced with background highlight)

---

## 3. Goal & Acceptance Criteria

### Goal
Replace the current warm-cream light theme with a dark professional UI that is readable, accessible, and production-ready for daily internal use as an AI automation control room. The redesign must not break any existing HTMX interactions or backend logic.

### Acceptance Criteria

- Given I open the Dashboard, When the page loads, Then I see a dark background (#0f1117), readable white text, and 3 agent cards with clear status pills that show both a colored dot and text label.
- Given I am on any agent page, When I look at the sidebar, Then it is sticky/fixed in viewport so navigation is always accessible while scrolling main content.
- Given I submit a form (e.g., Job Finder filters), When the request is in flight, Then the submit button is visually disabled with a loading spinner, and restores to normal after completion.
- Given I look at any button in the UI, Then I can distinguish: primary (filled blue), secondary (outlined), ghost (transparent), and danger (red) buttons by appearance alone.
- Given I resize the browser to 768px wide, Then the layout stacks to single column, the sidebar collapses to a top nav bar, and all content is usable without horizontal scroll.
- Given an empty-state panel is shown (no jobs, no tasks, no airdrops), Then I see a clear icon, a headline, a description, and a visible action button to start.

---

## 4. Risks & Assumptions

### Risks
- `app.js` renders HTML inline via template strings — all new CSS class names must be manually kept in sync between `style.css` and `app.js`
- Sidebar sticky positioning requires the `.app-shell` grid to allow the sidebar to be `position: sticky; top: 0; height: 100vh; overflow-y: auto` — this changes the scroll model; test on all 4 pages
- Removing `backdrop-filter: blur()` from topbar/cards may change perceived depth; compensate with subtle border + shadow
- Google Fonts CDN request on page load — acceptable for internal tool, no change needed
- Cron preset select field (new UX addition) requires a small JS snippet to populate the text input on change — must be added to `app.js` without breaking existing `AppShell` module

### Assumptions
- No changes to Python/FastAPI backend, routing, or Jinja2 context variables
- HTMX `hx-*` attributes are treated as untouchable; only surrounding HTML structure and class names change
- Dark theme is the single/only theme (no light/dark toggle required for MVP)
- IBM Plex Mono + IBM Plex Sans + Space Grotesk fonts remain (only existing Google Fonts link in `base.html`)
- "Load more" pagination is out of scope — JS-side `while feed.children.length > 6` limit in `appendActivity` is fine for now

---

## 5. Definition of Done
- [x] `style.css` fully replaces the old design system with dark theme tokens and component styles
- [ ] All 4 main page templates render without layout breakage in browser
- [x] All 12 partial templates use updated CSS class names consistently
- [ ] `app.js` inline HTML strings updated to match new class names; no JS errors in console
- [x] Sidebar is sticky/fixed — remains visible when main content scrolls
- [x] All button variants (primary, secondary, ghost, danger) are visually distinguishable
- [x] Status pills show icon + text, not color alone
- [x] Cron fields have preset dropdown helper
- [x] Form submit buttons show loading state via `.is-loading` CSS class + JS toggle
- [x] Connection status indicator visible in topbar
- [x] Empty states have icon + CTA button
- [x] Responsive layout works at 1200px, 900px, 768px, and 480px breakpoints
- [x] No existing HTMX `hx-*` attribute is modified

---

## 6. Implementation Plan

### Summary
Fully replace `style.css` with a new dark-theme design system, update all Jinja2 templates and partials to use the new class names and structure, then enhance `app.js` to add loading states, connection status indicator, and cron preset helper. Backend is untouched throughout.

Execution note:
- Implemented together with `feature-ui-layout-improvements.md` as one merged frontend pass.
- Responsive contract used in code: `1200px` tighten layout, `900px` app shell becomes top-nav and page sidebars switch to toggleable drawers, `768px` stack topbar/forms, `480px` compress spacing and expand actions full-width.
- Cron preset helpers were implemented in the partials that own the form fields.
- Jinja and `app.js` both render full table HTML so HTMX partial swaps and SSE updates stay aligned.

---

### Phase 1: Design System — Full CSS Rewrite

- [x] MODIFIED `frontend/static/style.css` — Replace entire file with new dark theme design system
  ```
  File: frontend/static/style.css (full replacement)

  Section: CSS Custom Properties (:root)
    - Replace all --bg, --surface, --ink, accent color tokens with dark theme values
    - New tokens: --bg, --bg-alt, --surface, --surface-raised, --surface-overlay,
      --ink, --ink-soft, --ink-faint, --border, --border-strong,
      --blue, --blue-hover, --blue-soft, --blue-glow,
      --teal, --teal-soft, --amber, --amber-soft,
      --success, --success-soft, --danger, --danger-soft,
      --warning, --warning-soft, --info, --info-soft,
      --mono, --body, --display
    - Remove all rgba transparency tricks based on light background

  Section: Base Reset
    - body: background: var(--bg); color: var(--ink); font: 14px/1.6 var(--body)
    - Remove body::before grid pattern overlay
    - Remove radial-gradient background from body

  Section: App Shell Layout
    - .app-shell: grid-template-columns: 260px 1fr (narrower sidebar)
    - .sidebar: position: sticky; top: 0; height: 100vh; overflow-y: auto
      background: var(--surface); border-right: 1px solid var(--border)
      padding: 20px 16px; flex-shrink: 0
    - .main-stage: padding: 24px 28px; overflow-y: auto

  Section: Sidebar
    - .brand: padding-bottom: 20px; border-bottom: 1px solid var(--border)
    - .brand strong: font: 700 22px/1.2 var(--display); color: var(--ink)
    - .brand-kicker: font: 500 11px var(--mono); letter-spacing: 0.12em;
      text-transform: uppercase; color: var(--ink-soft)
    - .nav-link: padding: 10px 12px; border-radius: 8px; color: var(--ink-soft)
      display: flex; align-items: center; gap: 10px; font-weight: 500
      transition: background 150ms, color 150ms
    - .nav-link:hover: background: rgba(255,255,255,0.05); color: var(--ink)
    - .nav-link.is-active: background: var(--blue-soft); color: var(--blue)
      border-left: 2px solid var(--blue)
    - .nav-link small: font-size: 12px; color: var(--ink-faint)
    - Remove: transform: translateX(4px) on hover
    - Remove: .sidebar-note dark box (no longer needed)

  Section: Topbar
    - .topbar: display: flex; align-items: center; justify-content: space-between
      padding: 16px 20px; border-bottom: 1px solid var(--border)
      background: var(--surface); margin-bottom: 0
    - Remove border-radius (topbar is full-width header strip, not a floating card)
    - Remove backdrop-filter, box-shadow
    - .topbar h1: font: 600 20px/1.3 var(--display); margin: 0
    - .eyebrow: font: 500 11px var(--mono); letter-spacing: 0.12em;
      text-transform: uppercase; color: var(--ink-soft)
    - Add: .connection-status indicator (dot + label, injected by JS)

  Section: Buttons
    - .btn (new unified base): display: inline-flex; align-items: center; gap: 8px
      padding: 8px 16px; border-radius: 8px; font: 500 14px var(--body)
      border: 1px solid transparent; cursor: pointer; transition: all 150ms
    - .btn-primary: background: var(--blue); color: #fff; border-color: var(--blue)
    - .btn-primary:hover: background: var(--blue-hover); border-color: var(--blue-hover)
    - .btn-secondary: background: transparent; color: var(--ink)
      border-color: var(--border-strong)
    - .btn-secondary:hover: background: rgba(255,255,255,0.05)
    - .btn-ghost: background: transparent; color: var(--ink-soft); border-color: transparent
    - .btn-ghost:hover: color: var(--ink); background: rgba(255,255,255,0.05)
    - .btn-danger: background: var(--danger-soft); color: var(--danger)
      border-color: rgba(239,68,68,0.24)
    - .btn.is-loading: opacity: 0.6; pointer-events: none; cursor: not-allowed
      (spinner via ::after pseudo-element, 16px border-spin animation)
    - Keep .ghost-button and .primary-button as aliases mapping to .btn-ghost/.btn-primary
      to avoid breaking existing template HTML

  Section: Cards & Panels
    - .panel, .dashboard-card, .mini-card: background: var(--surface)
      border: 1px solid var(--border); border-radius: 12px; padding: 20px
    - .panel:hover, .dashboard-card:hover: border-color: var(--border-strong)
    - Remove backdrop-filter from all cards
    - .hero-panel: background: var(--surface-raised); border-radius: 16px
      padding: 28px; margin-top: 20px; border: 1px solid var(--border)
    - .hero-badge: background: var(--blue-soft); border: 1px solid var(--blue-soft)
      border-radius: 12px; padding: 16px; color: var(--blue)

  Section: Status Pills & Feed Tags
    - .status-pill: display: inline-flex; align-items: center; gap: 6px
      padding: 4px 10px; border-radius: 9999px; font: 500 11px var(--mono)
      letter-spacing: 0.06em; text-transform: uppercase
    - Add ::before pseudo-element dot: width: 6px; height: 6px; border-radius: 50%
      background: currentColor (colored dot before text label)
    - .status-pill.is-ready: background: var(--success-soft); color: var(--success)
    - .status-pill.is-warn: background: var(--warning-soft); color: var(--warning)
    - .feed-tag: same base as status-pill but color: var(--ink-soft)
      background: rgba(255,255,255,0.05)

  Section: Form Components
    - .stack-form label, .config-form label: display: grid; gap: 6px
    - .stack-form label span, .config-form label span: font: 500 13px var(--body)
      color: var(--ink-soft); (label text above input)
    - All inputs, selects, textareas: background: var(--bg); color: var(--ink)
      border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px
      font: 14px var(--body); transition: border-color 150ms
    - input:focus, select:focus, textarea:focus: outline: none
      border-color: var(--blue); box-shadow: 0 0 0 3px var(--blue-glow)
    - .field-error: font: 12px var(--body); color: var(--danger); margin-top: 4px
    - .source-fieldset: border: 1px solid var(--border); border-radius: 10px
      padding: 14px
    - .source-fieldset legend: font: 500 11px var(--mono); text-transform: uppercase
      color: var(--ink-soft); padding: 0 4px

  Section: Activity Feed & Timeline
    - .activity-feed li, .timeline-list li: background: rgba(255,255,255,0.03)
      border: 1px solid var(--border); border-radius: 10px; padding: 12px
      Remove: rgba(255,255,255,0.58) (too light for dark theme)
    - .timeline-index: background: var(--blue-soft); color: var(--blue)
      width: 32px; height: 32px; border-radius: 50%
      font: 500 12px var(--mono)
    - .task-status variants updated:
      .status-pending: background: var(--info-soft); color: var(--info)
      .status-in-progress: background: var(--warning-soft); color: var(--warning)
      .status-done: background: var(--success-soft); color: var(--success)
      .status-deferred: background: var(--amber-soft); color: var(--amber)
      .status-dropped: background: var(--danger-soft); color: var(--danger)

  Section: Job Cards & Airdrop Cards
    - .job-card: background: var(--surface); border: 1px solid var(--border)
      border-radius: 12px; padding: 18px
    - .job-card:hover: border-color: var(--border-strong)
      box-shadow: 0 4px 12px rgba(0,0,0,0.4)
    - .score-pill: background: var(--blue-soft); color: var(--blue)
      font: 700 18px var(--display); border-radius: 10px; padding: 8px 12px
    - .stack-tags span: background: rgba(255,255,255,0.06)
      border: 1px solid var(--border); border-radius: 6px
      color: var(--ink-soft); font: 12px var(--mono)

  Section: Empty States
    - .empty-state: background: var(--surface); border: 1px dashed var(--border)
      border-radius: 12px; padding: 40px 24px; text-align: center
    - .empty-state .empty-icon: font-size: 32px; margin-bottom: 12px (emoji/icon)
    - .empty-state h3: font: 600 18px var(--display); margin: 0 0 8px
    - .empty-state p: color: var(--ink-soft); margin: 0 0 20px
    - .empty-state .btn: (inline CTA button, .btn-primary style)

  Section: Feedback Messages
    - .feedback: background: var(--surface); border: 1px solid var(--border)
      border-radius: 10px; padding: 14px 16px; display: flex; align-items: start; gap: 10px
    - .feedback::before: icon indicator (✓ or ✗) via content pseudo
    - .feedback-success: border-color: rgba(16,185,129,0.3); background: var(--success-soft)
    - .feedback-error: border-color: rgba(239,68,68,0.3); background: var(--danger-soft)

  Section: Modal
    - .modal-backdrop: background: rgba(0,0,0,0.7); backdrop-filter: blur(4px)
      (only place backdrop-filter is used)
    - .modal-card: background: var(--surface-raised); border: 1px solid var(--border-strong)
      border-radius: 16px; padding: 24px; width: min(520px, 100%)
      animation: modal-in 200ms ease (scale + fade)
    - @keyframes modal-in: from {opacity:0; transform:scale(0.96)} to {opacity:1; transform:scale(1)}

  Section: Warning Banner
    - .warning-banner: background: var(--warning-soft); border: 1px solid var(--amber-soft)
      border-radius: 8px; color: var(--amber); padding: 12px 14px

  Section: Summary Strip
    - .summary-strip div: background: var(--surface-raised); border-radius: 8px
      padding: 12px 14px; border: 1px solid var(--border)
    - .summary-label: font: 500 11px var(--mono); text-transform: uppercase
      color: var(--ink-faint); display: block; margin-bottom: 4px

  Section: Accent modifiers (page-level theme)
    - .accent-blue .hero-badge, .accent-blue .nav-link.is-active: use --blue tokens
    - .accent-teal .hero-badge: background: var(--teal-soft); color: var(--teal)
    - .accent-teal .hero-panel: border-color: rgba(20,184,166,0.2)
    - .accent-amber .hero-badge: background: var(--amber-soft); color: var(--amber)

  Section: Responsive (4 breakpoints)
    - @media (max-width: 1200px): workspace-grid → 1fr 320px (slightly tighter)
    - @media (max-width: 900px):
      .app-shell: grid-template-columns: 1fr (sidebar floats to top)
      .sidebar: position: static; height: auto; overflow: visible
        flex-direction: row; display: flex; align-items: center
        border-right: 0; border-bottom: 1px solid var(--border)
      .nav-group: flex-direction: row; overflow-x: auto
      .workspace-grid, .schedule-grid, .dashboard-grid: grid-template-columns: 1fr
    - @media (max-width: 768px):
      .main-stage: padding: 16px
      .hero-panel: flex-direction: column; gap: 16px
      .field-grid, .inline-fields: grid-template-columns: 1fr
      .dashboard-grid: grid-template-columns: 1fr
    - @media (max-width: 480px):
      .topbar: flex-direction: column; align-items: flex-start; gap: 12px
      .topbar-actions: width: 100%; flex-wrap: wrap
      .job-card-grid: grid-template-columns: 1fr
  ```

---

### Phase 2: Base Layout & Navigation Update

- [x] MODIFIED `frontend/templates/base.html` — Update sidebar HTML, topbar, add connection status
  ```
  Changes:
    1. Sidebar nav-link structure: Add icon placeholder <span class="nav-icon">·</span>
       before the <span> text label (CSS styles icon area, even if just a dot for now)

    2. Remove .sidebar-note dark box (no longer needed in dark theme)

    3. Topbar: Add connection status indicator element
       <div class="connection-status" id="connection-status">
         <span class="conn-dot"></span>
         <span class="conn-label">Connecting...</span>
       </div>
       Place this inside .topbar-actions before the existing buttons

    4. Page title structure: Wrap h1 in a .page-header div
       <div class="page-header">
         <p class="eyebrow">{{ page_context | default("Unified control room") }}</p>
         <h1>{{ page_title }}</h1>
       </div>

  No changes to: hx-* attributes, data-agent-name, data-stream-url, modal-root div
  ```

- [x] MODIFIED `frontend/templates/dashboard.html` — Update hero panel and card class names
  ```
  Changes:
    1. hero-panel: Add class "accent-blue" to <section class="hero-panel accent-blue">
    2. dashboard-card: Already uses accent-{{ agent.accent }} — keep as-is
    3. card-link: Change to <a class="btn btn-ghost card-link" ...>
    4. Empty: No structural change; CSS handles appearance
  ```

---

### Phase 3: Agent Page Templates

- [x] MODIFIED `frontend/templates/job_finder.html` — Update class names, add loading state to button
  ```
  Changes:
    1. hero-panel: Add class "accent-teal"
    2. All form submit buttons: Add data-loading-text="Running..." attribute
       (JS will toggle .is-loading class on submit)
    3. Ensure filter form labels have <span> wrapper for label text above input
       (most already do via .stack-form label pattern)
    4. Cron field: Replace plain <input> with a cron preset helper group:
       <div class="cron-field-group">
         <select class="cron-preset" id="cron-preset">
           <option value="">— Select preset —</option>
           <option value="0 * * * *">Every hour</option>
           <option value="0 8 * * *">Every day at 8am</option>
           <option value="0 8 * * 1-5">Weekdays at 8am</option>
           <option value="0 8,20 * * *">Twice daily (8am & 8pm)</option>
         </select>
         <input type="text" name="cron_schedule" id="cron-schedule"
                placeholder="0 8 * * *" title="Cron schedule expression" />
       </div>
       (JS will sync preset → text input on change event)
  ```

- [x] MODIFIED `frontend/templates/daily_scheduler.html` — Same pattern as job_finder
  ```
  Changes:
    1. hero-panel: Add class "accent-blue" (daily scheduler uses blue)
    2. Chat submit button: Add data-loading-text="Planning..."
    3. Schedule button: Add data-loading-text="Scheduling..."
    4. Cron field: Same cron-preset helper group as job_finder
  ```

- [x] MODIFIED `frontend/templates/crypto_airdrop.html` — Same pattern
  ```
  Changes:
    1. hero-panel: Add class "accent-amber"
    2. All submit buttons: Add data-loading-text attribute
    3. Cron field: Same cron-preset helper group
  ```

---

### Phase 4: Partial Templates Update

- [x] MODIFIED `frontend/templates/partials/config_modal.html` — Update button classes
  ```
  Changes:
    - Save/Submit buttons: class="btn btn-primary" (replaces "primary-button")
    - Cancel buttons: class="btn btn-ghost" (replaces "ghost-button")
    - Keep all hx-* attributes unchanged
  ```

- [x] MODIFIED `frontend/templates/partials/config_feedback.html` — Update feedback classes
  ```
  Changes:
    - Success wrapper: class="feedback feedback-success"
    - Error wrapper: class="feedback feedback-error"
    - No content changes
  ```

- [x] MODIFIED `frontend/templates/partials/job_run_feedback.html` — Same feedback class update
  ```
  Same changes as config_feedback.html
  ```

- [x] MODIFIED `frontend/templates/partials/crypto_airdrop_run_feedback.html` — Same
  ```
  Same changes as config_feedback.html
  ```

- [x] MODIFIED `frontend/templates/partials/job_finder_filters.html` — Update button class
  ```
  Changes:
    - Submit button: class="btn btn-primary"
    - Keep all hx-* attributes
  ```

- [x] MODIFIED `frontend/templates/partials/daily_scheduler_controls.html` — Update button class
  ```
  Changes:
    - Submit button: class="btn btn-primary"
    - Keep all hx-* attributes
  ```

- [x] MODIFIED `frontend/templates/partials/crypto_airdrop_controls.html` — Update button class
  ```
  Same as above
  ```

- [x] MODIFIED `frontend/templates/partials/daily_schedule_chat.html` — Update button class
  ```
  Changes:
    - Chat submit button: class="btn btn-primary"
    - .warning-pill stays as-is (existing JS toggles display)
  ```

- [x] MODIFIED `frontend/templates/partials/daily_schedule_timeline.html` — Empty state update
  ```
  Changes:
    - If empty state exists in template: Add .empty-icon emoji (📋) before h3
    - Add class="btn btn-primary" to any CTA button
    - (Most timeline content is rendered by JS, not this template)
  ```

- [x] MODIFIED `frontend/templates/partials/job_cards.html` — Update card structure if needed
  ```
  Changes:
    - job-card link: class="btn btn-ghost card-link"
    - Verify score-pill class is present (should already be)
  ```

- [x] MODIFIED `frontend/templates/partials/airdrop_cards.html` — Same as job_cards
  ```
  Same link class update
  ```

- [x] MODIFIED `frontend/templates/partials/crypto_airdrop_chat.html` — Update button
  ```
  Chat submit button: class="btn btn-primary"
  ```

---

### Phase 5: JavaScript Enhancements

- [x] MODIFIED `frontend/static/app.js` — Add connection status, loading states, cron presets
  ```
  Function additions to AppShell IIFE:

  1. updateConnectionStatus(state: "connected" | "connecting" | "error")
     - Selects #connection-status element
     - Sets .conn-dot background via data-state attribute:
       connected → green (#10b981)
       connecting → amber (#f59e0b), animated pulse
       error → red (#ef4444)
     - Sets .conn-label text accordingly
     - Called from: connectStream() on open/error/close events

  2. setButtonLoading(button: HTMLElement, isLoading: boolean)
     - If isLoading: button.classList.add("is-loading"); store original text
       set button.textContent = button.dataset.loadingText || "Loading..."
     - If !isLoading: button.classList.remove("is-loading"); restore original text
     - Used for HTMX form submissions (listen to htmx:beforeRequest / htmx:afterRequest)

  3. initCronPresets()
     - Selects all .cron-preset selects on the page
     - Adds change event listener: updates corresponding #cron-schedule input value
     - Called from init()

  4. initFormLoadingStates()
     - document.addEventListener("htmx:beforeRequest", handler)
       → find button[data-loading-text] in event.detail.elt (the form)
       → call setButtonLoading(button, true)
     - document.addEventListener("htmx:afterRequest", handler)
       → find the same button → call setButtonLoading(button, false)
     - Called from init()

  5. Update connectStream() to call updateConnectionStatus:
     stream = new EventSource(streamUrl)
     updateConnectionStatus("connecting")
     stream.addEventListener("open", () => updateConnectionStatus("connected"))
     stream.addEventListener("error", () => updateConnectionStatus("error"))

  6. Update inline HTML strings in renderJobResults(), renderScheduleTimeline(),
     renderAirdropCards(), renderScheduleMessages(), renderAirdropMessages():
     - Replace class="card-link" with class="btn btn-ghost card-link"
     - Replace class="empty-state" content: add emoji icon <div class="empty-icon">
       job: 💼, schedule: 📋, airdrop: 🪂
     - Add <button class="btn btn-primary" ...>Run a crawl</button> or
       equivalent CTA inside empty-state HTML where appropriate
       (Note: these CTAs trigger HTMX forms, so just link to form submit via JS click
        or leave as informational — no backend change)

  Updated init() function:
    function init() {
      connectStream();
      initCronPresets();
      initFormLoadingStates();
    }
  ```

---

## 7. Follow-ups
- [ ] Add icons (SVG or icon font like Heroicons) to sidebar nav links for better visual hierarchy
- [ ] Implement light/dark theme toggle with `prefers-color-scheme` media query support
- [ ] Add "Load more" pagination to job-card-grid and airdrop-card-grid (requires backend pagination endpoint)
- [ ] Consider adding a breadcrumb component below topbar for deeper page hierarchy
- [ ] Improve accessibility: add visible `:focus-visible` ring to all interactive elements
- [ ] Add skeleton loading states (CSS-only shimmer) for panels waiting on first SSE data
