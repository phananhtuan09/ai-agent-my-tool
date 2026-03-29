# Web Analyst: midnight-ai-theme-rollout

## Source Inventory

### Behavior Sources
- [docs/ai/planning/feature-midnight-ai-theme-rollout.md](/home/anh-tuan/source_code/ai-agent-tool/docs/ai/planning/feature-midnight-ai-theme-rollout.md) provides goal statements, acceptance criteria, risks, and the implementation plan that anchors the rollout to the dashboard, config page, daily scheduler, and crypto airdrop page while warning against touching backend behavior or additional agent views.
- [backend/api/pages.py](/home/anh-tuan/source_code/ai-agent-tool/backend/api/pages.py) confirms the only server routes relevant to this scope are `/`, `/config`, and `/agents/{agent_name}`, so any UI review must inspect the dashboard, config surface, and the two agent templates that fall under the rollout.

### UI Sources
- [frontend/templates/base.html](/home/anh-tuan/source_code/ai-agent-tool/frontend/templates/base.html) is the shell that needs the Midnight AI sidebar, topbar, mobile drawer, overlay, navigation links, connection badge, and buttons in place for all pages.
- [frontend/templates/dashboard.html](/home/anh-tuan/source_code/ai-agent-tool/frontend/templates/dashboard.html) surfaces the hero, grid of cards, status pills, and card actions that must reflect the cyan/purple accents and typography.
- [frontend/templates/config.html](/home/anh-tuan/source_code/ai-agent-tool/frontend/templates/config.html) describes the connection settings hero, form, CTA cluster, feedback slot, and side panel that the new theme must cover without breaking HTMX targets.
- [frontend/templates/daily_scheduler.html](/home/anh-tuan/source_code/ai-agent-tool/frontend/templates/daily_scheduler.html) defines the planner hero, chat/timeline panels, controls accordion, and settings partial that the Midnight AI shell should frame.
- [frontend/templates/crypto_airdrop.html](/home/anh-tuan/source_code/ai-agent-tool/frontend/templates/crypto_airdrop.html) outlines the radar hero, filter sidebar, toggle, chat partial, and results panel that require the theme’s gradients and spacing.
- The partials under `frontend/templates/partials/` (daily/crypto chat, timeline, controls, airdrop cards) supply the micro-layouts—chat feeds, forms, tables, empty states—that HTMX swaps must keep consistent with the new surface.

### Runtime Sources
- Base URL note `http://127.0.0.1:8000` from the handoff sets the launch target for screenshots and Playwright probes.
- Auth note “no auth” clarifies every page can be reached without credential flows.
- [docs/ai/project/PROJECT_STRUCTURE.md](/home/anh-tuan/source_code/ai-agent-tool/docs/ai/project/PROJECT_STRUCTURE.md) and [docs/ai/project/CODE_CONVENTIONS.md](/home/anh-tuan/source_code/ai-agent-tool/docs/ai/project/CODE_CONVENTIONS.md) document the zero-build stack (FastAPI + HTMX + Jinja), minimal JS glue, and the expectation that styling changes happen in CSS/templates only.
- [pyproject.toml](/home/anh-tuan/source_code/ai-agent-tool/pyproject.toml) confirms there is no browser test harness baked in and that any engine hints must be inferred from runtime docs rather than an existing Playwright project.

### Constraints
- Primary validation is screenshot-based UI/theme verification across the four named pages; focus on user-visible layout mismatches, missing states, and theme drift rather than backend or auth flows.
- No other agent pages or workflows beyond dashboard, config, daily scheduler, and crypto airdrop are in scope per the rollout boundary.

## Behavior Map

**Dashboard (`/`)** – The base shell must present the 260px sidebar, connection badge, and gradient topbar before the hero row (`page-hero accent-blue`) paints the “Unified control room” messaging. Each `.dashboard-card` should be checked for proper accent strips (cyan/purple gradient), status pills with semi-transparent backgrounds (ready/warn/error), and the metric list typography. Card hover states and ghost CTA (“Open …”) should match the button/transition rules from the spec because they form the hero deck that defines the Midnight AI surface.

**Config page (`/config`)** – The hero must match the shared runtime message with a hero badge reflecting API key status. The form under `.config-form` needs to keep the base URL and API key inputs at the new height/rounding, the loading text on the primary “Save settings” button, and the HTMX `hx-post` targets for feedback and modal swaps. The “Test API” and “Fetch models” actions also need to look like ghost/secondary buttons, and the side-panel tag list/empty-state copy must stay in the theme’s muted background, providing another full-screen area with the new tokens.

**Daily scheduler agent page (`/agents/daily_scheduler`)** – The hero, chat panel (`#daily-schedule-chat-panel`), and timeline feed are the key surfaces for this route. Verify the “Planner transcript” list, warning pill (`awaiting_overdue_resolution`), and sample prompt text show the new chat bubble shapes, typography, and background surfaces described in the design tokens. The chat form’s textarea plus the “Send to planner” primary CTA must follow the 40px height/rounded corner rules. Timeline table (`partials/daily_schedule_timeline.html`, reused via HTMX) and controls panel (accordion, cron presets) must retain layout and token cohesion when refreshed out of band.

**Crypto airdrop agent page (`/agents/crypto_airdrop`)** – The route must showcase the filter sidebar (`#airdrop-sidebar` plus `filter-toggle` button), chat panel, and results panel defined in the partials. Confirm the toggle button, sidebar heading, status pill, and control checkboxes respect the Glow and accent token rules (cyan/purple). The `.results-panel` (airdrop cards partial) should match the card/shadow system and table/empty-state styling so that both server-rendered and HTMX-updated tables look identical when refreshed.

**Dynamic states** – Across all routes, the `btn-primary`, `btn-ghost`, and `btn-secondary` classes referenced in templates must render the gradient vs. ghost behaviors. The sidebar open/close buttons with `data-sidebar-open`/`data-sidebar-close`, the overlay, and the connection status dot (pulse in connected state) need to be validated for both desktop and mobile drawer interactions. Since HTMX swaps target `#daily-schedule-chat-panel`, `#daily-schedule-timeline`, and `#airdrop-results-panel`, their post-swap presentation needs to keep the Midnight AI tokens intact.

**Out of scope** – Auth flows, additional agent pages beyond daily scheduler and crypto air drop, and backend changes are not included in this review.

## Runtime Assumptions

Manual or automated screenshots will run against `http://127.0.0.1:8000`. There is no login or storage-state handshake; every route is open when the server is running. The FastAPI + Jinja + HTMX stack means navigation toggles, connection dots, and SSI updates originate from `frontend/static/app.js` and the templates, so any runtime probe must keep HTMX/JS enabled (no static HTML dumps). SSE/HTMX connections power the connection-status badge and the async targets like `#modal-root`, so probes must let the page load the SSE script and not disable JS.

## Coverage Confidence

The provided design/planning docs give pixel-level tokens and behaviors for sidebar, hero, cards, buttons, forms, chat bubbles, and tables, and the templates are already updated to the Midnight AI class names, so confidence is high for verifying the static surfaces. The remaining uncertainty lies in dynamic HTMX refreshes (schedule timeline, chat transcript, airdrop cards) and SSE-powered connection states, so screenshot validation should explicitly include a refreshed timeline/airdrop table and the connection badge in “connected” status. Mobile drawer interactions also need manual verification because they depend on the sidebar toggle buttons and overlay working at widths below 768px.

## Routing Signals

UI Mapping Needed: yes — the rollout touches four routes plus shared partials; create screenshot permutations for desktop hero + card grid, config form + panel, daily scheduler (chat + timeline + controls), and crypto airdrop (sidebar + results) so downstream test authors know which DOM fragments to capture per route.

Runtime Probe Feasible: yes — server runs on `http://127.0.0.1:8000` with no auth; a Playwright/Manual probe can load each route, expand mobile drawer, and trigger HTMX swaps while JS remains enabled.

Authoring Ready: partial — tokens and layout classes are defined, but clarifications are needed on whether the “connected” indicator should be forced into success via SSE or can be simulated, and whether any agent page should exercise warning/error pills beyond the default states.

Verification Ready: partial — most static surfaces are covered, but verifying HTMX swaps (timeline/airdrop refresh) and mobile drawer interactions will require scripting or manual steps beyond a single screenshot.

## Open Questions

- Should the verification plan include scripted HTMX refreshes (e.g., re-posting chat forms) or only rely on the initial server render + manual refresh to confirm the Midnight AI styling for dynamic fragments?

## Handoff Summary

### Decisions
- Scope is limited to the dashboard, config, daily scheduler, and crypto airdrop pages rendered by the routes `/`, `/config`, and `/agents/{agent_name}` plus their partials as outlined by the planning doc.
- Primary flows are the hero/dashboard card grid, the config form/feedback experience, the scheduler chat/timeline/controls, and the crypto airdrop sidebar/results layout, each needing the Midnight AI tokens applied consistently.
- High-confidence assertions: sidebar/topbar shell, card/export hero sections, button styles, and baseline chat/timeline markup already match the new classes, so screenshots of those surfaces should be meaningful.

### Blockers
- Dynamic HTMX updates (timeline, chat, airdrop tables) and SSE-driven status badges still need explicit validation steps or automation hooks before the coverage is complete.

### Open Questions
- Should the connection-status dot be explicitly driven into “connected” for the screenshots, or can the status be inferred from the default SSE state when running locally?
