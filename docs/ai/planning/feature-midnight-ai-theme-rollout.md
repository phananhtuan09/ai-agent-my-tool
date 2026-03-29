# Plan: Midnight AI Theme Rollout

Note: All content in this document must be written in English.

---
epic_plan: null
requirement: docs/ai/requirements/figma-midnight-ai.md
---

## 0. Related Documents

| Type | Document |
|------|----------|
| Requirement | [figma-midnight-ai.md](../requirements/figma-midnight-ai.md) |

---

## 1. Codebase Context

### Similar Features
- `frontend/static/style.css` - Existing shared token system and all global component styles live here, so the theme rollout should stay centralized.
- `frontend/templates/base.html` - Global shell, sidebar, topbar, font loading, and modal root already define the app-wide frame.
- `frontend/static/app.js` - Dynamic tables, empty states, activity feeds, connection badge, and responsive sidebar behavior are rendered here and must stay visually aligned with the templates.

### Reusable Components/Utils
- `frontend/templates/partials/*.html` - Server-rendered HTMX partials already split chat, controls, feedback, and data views by feature.
- `window.AppShell` in `frontend/static/app.js` - Public modal and notification helpers already exist and should be preserved while extending shell interactions.
- CSS custom properties in `frontend/static/style.css` - The current layout already depends on theme tokens, so replacing token values is the lowest-risk path for the redesign.

### Architectural Patterns
- Server-rendered Jinja templates own the structural HTML; the redesign must preserve existing route output and HTMX targets.
- HTMX partial swaps replace sections in place, so shared class names must remain consistent between static templates and JS-generated HTML.
- The frontend has no build step; all styling and interaction changes must remain plain CSS and vanilla JS.

### Key Files to Reference
- `frontend/templates/base.html` - Global font imports, shell landmarks, sidebar navigation, and topbar actions.
- `frontend/templates/dashboard.html` - Dashboard card layout and hero treatment.
- `frontend/templates/config.html` - Settings form, tag list, and side panel layout.
- `frontend/templates/daily_scheduler.html` - Chat + timeline layout and settings side panel.
- `frontend/templates/crypto_airdrop.html` - Control sidebar + results layout.
- `frontend/templates/partials/daily_schedule_chat.html` - Transcript markup and CTA state.
- `frontend/templates/partials/daily_scheduler_controls.html` - Dense form fields that need updated spacing and responsive behavior.
- `frontend/templates/partials/crypto_airdrop_controls.html` - Checkbox grid, cron inputs, and run CTA.
- `frontend/templates/partials/airdrop_cards.html` - Shared table and empty state markup used by first paint and HTMX refreshes.
- `frontend/static/app.js` - Dynamic HTML builders for schedule tables, airdrop tables, empty states, loading states, and responsive navigation behavior.

---

## 2a. Design Specifications

- **Figma specs**: [figma-midnight-ai.md](../requirements/figma-midnight-ai.md)
- **Frame**: Midnight AI Dark Theme
- **Status**: complete

> Use the linked design document as the source of truth for tokens, gradients, typography, component states, and responsive breakpoints.

---

## 3. Goal & Acceptance Criteria

### Goal
- Replace the current dark theme with the new Midnight AI visual system across the full app shell, dashboard, config page, and agent pages without changing backend behavior or breaking HTMX/SSE flows.

### Acceptance Criteria (Given/When/Then)
- Given I open any page in the app, When the shell loads, Then I see the Midnight AI sidebar, topbar, background glow, typography, and cyan-purple accent system from the design spec.
- Given I open the dashboard, When the agent cards render, Then the cards use the updated surface, accent strip, status pill, typography, and hover behavior defined in the design spec.
- Given I use the config page or any agent controls, When I focus inputs or submit forms, Then fields, buttons, feedback blocks, and loading states match the new tokens and remain readable at desktop and mobile sizes.
- Given I use pages with live data, When HTMX or SSE updates replace content, Then the injected tables, empty states, warnings, and activity feeds keep the same Midnight AI styling as the initial server-rendered markup.
- Given I resize the viewport below the mobile breakpoint, When navigation and page layouts adapt, Then the sidebar collapses into a toggleable drawer, actions remain reachable, and no page requires horizontal scrolling.

## 4. Risks & Assumptions

### Risks
- `frontend/static/app.js` builds HTML strings inline, so any class or structural changes must be mirrored exactly between JS and Jinja templates.
- The mobile drawer behavior is not fully implemented in the current shell, so adding it can regress navigation if state handling is incomplete.
- The spec updates fonts from `IBM Plex Sans` body text to `Inter`, which requires a font import change in the global layout.
- Large CSS token changes can unintentionally reduce contrast in dense tables or muted text if component-level overrides are missed.

### Assumptions
- This is a behavior-preserving frontend refactor; backend routes, data payloads, and HTMX endpoints stay unchanged.
- The Midnight AI theme is dark-only; no theme toggle is required.
- Existing partial boundaries remain valid, so the redesign can be shipped by updating templates, shared CSS, and `app.js` only.
- Validation will rely on focused frontend smoke checks plus automated tests available in the repository rather than pixel-diff tooling.

## 5. Definition of Done
- [x] The feature plan is updated as tasks complete and remains the execution source of truth.
- [x] The global shell, shared tokens, and responsive navigation match the Midnight AI spec.
- [x] Dashboard, config, daily scheduler, and crypto airdrop pages render with the new theme and no broken HTMX targets.
- [x] JS-rendered tables, warnings, empty states, and activity feeds match the new visual system.
- [x] Focused validation passes for the touched frontend surfaces.

---

## 6. Implementation Plan

### Summary
Apply the Midnight AI redesign as a frontend-only refactor centered on a new tokenized CSS system, a refreshed app shell, and consistent page/component markup. Keep the existing route structure, HTMX hooks, and SSE behaviors intact while bringing both server-rendered and JS-rendered UI into the same visual language.

### Phase 1: Refresh Global Theme Foundations

- [x] [MODIFIED] frontend/templates/base.html - Load the Midnight AI font stack and update the shared shell markup for the new sidebar, topbar, connection badge, and mobile navigation controls.
  ```
  Function: Jinja base shell layout

  Input validation:
    - Preserve `current_page`, `current_agent`, and `agents` template variables exactly.
    - Preserve all existing `hx-*` attributes and `window.AppShell` entry points.

  Logic flow:
    1. Replace the body font import with the Midnight AI font stack from the design spec.
    2. Add shell structure needed for the mobile drawer toggle and overlay.
    3. Keep semantic landmarks (`aside`, `main`, `header`, `nav`) intact.
    4. Preserve current action buttons and stream status element IDs.

  Return: Rendered shell HTML with unchanged backend bindings.

  Edge cases:
    - No current agent -> connection badge remains optional.
    - Long agent titles -> shell layout must wrap without overflow.

  Dependencies: `frontend/static/style.css`, `frontend/static/app.js`
  ```

- [x] [MODIFIED] frontend/static/style.css - Replace the current token set and shared component styling with Midnight AI colors, gradients, typography, shadows, glow states, and responsive shell/layout rules.
  ```
  Function: Global CSS theme system

  Input validation:
    - Keep CSS custom properties centralized in `:root`.
    - Reuse existing component selectors where possible to minimize template churn.

  Logic flow:
    1. Map the design-spec tokens into CSS variables.
    2. Rebuild body, sidebar, topbar, cards, panels, forms, badges, tables, and modal styles around the new tokens.
    3. Add ambient background glows and restrained motion states from the spec.
    4. Add responsive rules for desktop, tablet, and mobile shell behavior, including drawer navigation.

  Return: Shared visual system that all templates and JS-rendered fragments consume.

  Edge cases:
    - Dense tables must remain readable with horizontal overflow handling.
    - Button loading states must stay legible in all variants.

  Dependencies: All frontend templates and `frontend/static/app.js`
  ```

### Phase 2: Update Page and Partial Markup

- [x] [MODIFIED] frontend/templates/dashboard.html - Align hero, agent cards, metrics, and CTA layout with the Midnight AI card and banner spec.
  ```
  Function: Dashboard page markup

  Input validation:
    - Preserve `agents`, `agent.build_snapshot()`, and all navigation links.

  Logic flow:
    1. Update hero structure and supporting copy for the new banner treatment.
    2. Adjust dashboard cards to expose accent strips, status chips, and metric grouping expected by the new CSS.
    3. Keep current data fields and agent links unchanged.

  Return: Server-rendered dashboard with updated visual hierarchy.

  Edge cases:
    - Missing API key/configuration states still surface through status pills.

  Dependencies: `frontend/static/style.css`
  ```

- [x] [MODIFIED] frontend/templates/config.html - Refresh the config page layout, form grouping, model list treatment, and empty state styling to match the Midnight AI control-room theme.
  ```
  Function: Config page markup

  Input validation:
    - Preserve form IDs, `hx-*` endpoints, and the `openai-model-field` swap target.

  Logic flow:
    1. Update hero metadata block and main/side panel layout.
    2. Refine field grouping, helper copy, and button arrangement for the new visual system.
    3. Keep success/error feedback insertion points unchanged.

  Return: Config page HTML aligned with the new theme and current HTMX flow.

  Edge cases:
    - Empty model catalog still renders a clear empty state and CTA.

  Dependencies: `frontend/static/style.css`, partial feedback templates
  ```

- [x] [MODIFIED] frontend/templates/daily_scheduler.html - Refresh the page hero, transcript panel, timeline panel, and settings container for the new theme and mobile stacking rules.
  ```
  Function: Daily scheduler page markup

  Input validation:
    - Preserve `snapshot`, included partials, IDs, and `hx-*` bindings.

  Logic flow:
    1. Update page-level layout wrappers to fit the new shell spacing and panel hierarchy.
    2. Keep the timeline and settings containers distinct for responsive rearrangement.
    3. Preserve the warning pill and transcript target IDs.

  Return: Updated daily scheduler layout ready for themed partials.

  Edge cases:
    - Overdue warning remains visible without relying on color alone.

  Dependencies: `frontend/static/style.css`, related partials
  ```

- [x] [MODIFIED] frontend/templates/crypto_airdrop.html - Refresh the hero, results stage, and control drawer/sidebar markup to match the Midnight AI radar page layout.
  ```
  Function: Crypto airdrop page markup

  Input validation:
    - Preserve `snapshot`, sidebar IDs, and all HTMX targets.

  Logic flow:
    1. Update page hero and model badge treatment.
    2. Align the filter sidebar with the new control-panel styling.
    3. Keep results panel and chat target structure compatible with HTMX/SSE updates.

  Return: Updated airdrop page layout with preserved behavior.

  Edge cases:
    - Mobile toggle continues to open the control drawer without duplicating content.

  Dependencies: `frontend/static/style.css`, related partials, `frontend/static/app.js`
  ```

- [x] [MODIFIED] frontend/templates/partials/daily_schedule_chat.html - Rework transcript list, warning pill, and CTA form markup for the Midnight AI chat surface.
  ```
  Function: Daily scheduler chat partial

  Input validation:
    - Preserve `#daily-schedule-chat-panel`, `#daily-schedule-timeline`, and chat form bindings.

  Logic flow:
    1. Update transcript row wrappers and helper copy for the new message styling.
    2. Keep the warning pill visible in both initial render and HTMX refreshes.
    3. Preserve the OOB timeline update block.

  Return: Chat partial with themed transcript and form markup.

  Edge cases:
    - No messages still shows an accessible starter state.

  Dependencies: `frontend/static/style.css`, `frontend/static/app.js`
  ```

- [x] [MODIFIED] frontend/templates/partials/daily_scheduler_controls.html - Refresh dense form fields, helper text, and inline field groups for the Midnight AI settings panel.
  ```
  Function: Daily scheduler controls partial

  Input validation:
    - Preserve existing field names and settings values.

  Logic flow:
    1. Update control group structure to align labels, hints, and cron presets.
    2. Preserve the form target and submit behavior.
    3. Ensure mobile stacking remains clear for inline number fields.

  Return: Themed settings form markup.

  Edge cases:
    - Validation errors still render via the feedback block without layout collapse.

  Dependencies: `frontend/static/style.css`
  ```

- [x] [MODIFIED] frontend/templates/partials/daily_schedule_timeline.html - Refresh summary strip, task table, and empty state markup for the Midnight AI timeline surface.
  ```
  Function: Daily schedule timeline partial

  Input validation:
    - Preserve task field names and status-derived CSS hooks.

  Logic flow:
    1. Update summary strip markup for the new metric presentation.
    2. Keep the table structure compatible with client-side sorting and CSS.
    3. Rebuild the empty state to match the new CTA styling.

  Return: Timeline partial aligned with first render and JS re-render behavior.

  Edge cases:
    - Empty and populated states both fit narrow screens.

  Dependencies: `frontend/static/style.css`, `frontend/static/app.js`
  ```

- [x] [MODIFIED] frontend/templates/partials/crypto_airdrop_controls.html - Refresh the radar controls form, checkbox rows, and feedback block for the Midnight AI sidebar treatment.
  ```
  Function: Crypto airdrop controls partial

  Input validation:
    - Preserve field names, checkbox names, and run/save action bindings.

  Logic flow:
    1. Rework the control grouping around the new field and button styles.
    2. Keep the run feedback target intact.
    3. Ensure checkbox rows remain touch-friendly on mobile.

  Return: Updated controls partial with preserved HTMX behavior.

  Edge cases:
    - Long source labels wrap without breaking the checkbox alignment.

  Dependencies: `frontend/static/style.css`
  ```

- [x] [MODIFIED] frontend/templates/partials/crypto_airdrop_chat.html - Refresh transcript, filter form, and OOB results wrapper styling for the Midnight AI chat surface.
  ```
  Function: Crypto airdrop chat partial

  Input validation:
    - Preserve `#crypto-airdrop-chat-panel`, `#airdrop-results-panel`, and chat form bindings.

  Logic flow:
    1. Update transcript wrappers and assistant/user message styling hooks.
    2. Preserve the OOB results block for HTMX refreshes.
    3. Keep the filter form compact and readable in the sidebar.

  Return: Themed chat partial with unchanged behavior.

  Edge cases:
    - Empty transcript still offers a clear example prompt.

  Dependencies: `frontend/static/style.css`, `frontend/static/app.js`
  ```

- [x] [MODIFIED] frontend/templates/partials/airdrop_cards.html - Refresh warnings, summary strip, data table, and empty state markup used by both initial render and HTMX swaps.
  ```
  Function: Crypto airdrop result partial

  Input validation:
    - Preserve sortable columns, source links, and existing summary fields.

  Logic flow:
    1. Update summary, warning, and table wrappers for the new surface styling.
    2. Keep table semantics and IDs unchanged for client-side sorting.
    3. Rebuild the empty state to align with the redesigned CTA language.

  Return: Result panel markup compatible with server-rendered and dynamic refresh paths.

  Edge cases:
    - Long AI reasons remain readable without stretching the layout.

  Dependencies: `frontend/static/style.css`, `frontend/static/app.js`
  ```

### Phase 3: Align Dynamic Frontend Behavior

- [x] [MODIFIED] frontend/static/app.js - Update dynamic renderers and shell interactions so JS-generated UI matches the new markup and mobile drawer behavior.
  ```
  Function: AppShell.init(), renderScheduleTimeline(), renderScheduleMessages(), renderAirdropCards(), renderAirdropMessages(), buildSummaryStrip(), buildEmptyState()

  Input validation:
    - Preserve the `window.AppShell` public API and existing SSE/HTMX event wiring.
    - Preserve IDs and data attributes used by the server-rendered templates.

  Logic flow:
    1. Add shell controls for mobile sidebar open/close state and overlay dismissal.
    2. Update generated HTML fragments to use the same card, transcript, warning, summary, and empty-state structure as the templates.
    3. Keep loading-state handling, sorting, and connection badge behavior intact.
    4. Ensure responsive helpers reset drawer state correctly when returning to desktop widths.

  Return: JS-rendered UI fragments and interactions that stay in sync with the Midnight AI theme.

  Edge cases:
    - Event listeners must not duplicate when HTMX swaps content.
    - Empty states and warning banners must remain actionable after dynamic refreshes.

  Dependencies: `frontend/templates/base.html`, themed partials, `frontend/static/style.css`
  ```

## 7. Follow-ups

- Extend browser coverage to stubbed success-path model discovery and deeper SSE-driven live-update assertions.
