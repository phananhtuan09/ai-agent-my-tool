# Web Test Plan: Midnight AI Theme Rollout

Note: All content in this document must be written in English.

## Input Sources

### Behavior Sources
- `docs/ai/planning/feature-midnight-ai-theme-rollout.md` - Defines the accepted page scope, the theme acceptance criteria, and the requirement to preserve HTMX/SSE behavior.
- `backend/api/pages.py` - Confirms the tested routes are `/`, `/config`, and `/agents/{agent_name}`.

### UI Sources
- `docs/ai/requirements/figma-midnight-ai.md` - Source of truth for tokens, shell layout, component states, and responsive behavior.
- `docs/ai/testing/agents/web-analyst-midnight-ai-theme-rollout.md` - Normalized route and behavior inventory for the four-page rollout.
- `docs/ai/testing/agents/web-qc-midnight-ai-theme-rollout.md` - Code-grounded test-case and selector inventory.
- `docs/ai/testing/agents/web-runtime-midnight-ai-theme-rollout.md` - Live runtime probe and screenshot evidence.

### Runtime Sources
- `http://127.0.0.1:8000` - Confirmed base URL used for execution.
- `package.json` - Local test runner scripts for Playwright.
- `tests/web/midnight-ai-theme-rollout.spec.ts` - Generated browser regression suite with screenshot and HTMX refresh coverage.

### Constraints
- Primary goal for this run was browser-based UI/theme validation on the dashboard, config page, daily scheduler page, crypto airdrop page, and mobile drawer behavior.
- No auth flow was required.
- Config-page HTMX coverage uses stable local flows plus unreachable-endpoint error states instead of relying on a live external OpenAI API.

## Runtime Assumptions
- Engine: `playwright`
- Base URL: `http://127.0.0.1:8000`
- Web Server Command: `python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`
- Auth Strategy: `none`
- Probe Status: `pass`

## Routes Under Test
- `/` - Dashboard shell, hero, card grid, and desktop/mobile navigation behavior.
- `/config` - Shared config hero, form cluster, save flow, and model-field HTMX feedback states.
- `/agents/daily_scheduler` - Agent topbar, live connection badge, planner chat, timeline, and controls panel.
- `/agents/crypto_airdrop` - Agent topbar, hero, control sidebar, chat lane, and results panel.
- `/agents/{agent}/config` - Shell-launched model modal and per-agent model save flow.

## Test Files Created
- `tests/web/midnight-ai-theme-rollout.spec.ts` - Playwright regression suite for desktop pages, the mobile drawer, and core HTMX refresh flows.

## Scenario Map

### Happy Path
- ✓ Dashboard renders the Midnight AI shell and card grid.
- ✓ Config page renders the themed hero, form, and side panel.
- ✓ Config save submits via HTMX and returns inline success feedback without leaving the page.
- ✓ Daily scheduler route renders the themed hero, transcript, timeline, and controls.
- ✓ Crypto airdrop route renders the themed hero, sidebar, transcript, and results panel.
- ✓ Mobile drawer opens and closes on narrow viewports.
- ✓ Daily scheduler model modal opens from the shell and saves the selected model override.
- ✓ Daily scheduler HTMX planning refresh updates the themed chat transcript and timeline after submit.
- ✓ Crypto airdrop HTMX crawl and chat-filter refresh preserve the themed results panel and transcript.

### Validation and Error States
- ✓ Desktop-only controls were asserted as hidden and surfaced a real regression when they rendered visibly.
- ✓ Duplicate OOB-rendered sections were surfaced as real DOM issues on scheduler and crypto airdrop pages.
- ✓ Config `Test API` and `Fetch models` actions now render inline error feedback on `422` HTML responses.
- ✓ Dynamic refresh assertions verify that OOB target containers remain unique after HTMX swaps.

### Navigation and UI States
- ✓ Shared shell, sidebar, topbar, hero, and page sections were captured in screenshots.
- ✓ Connected-state badge was observed on agent pages during the browser pass.

### Out of Scope
- Successful external model discovery against a live OpenAI-compatible endpoint was not exercised in this run.
- SSE-driven live content updates beyond connected-state presence were not exercised in this run.

## Selector Strategy
- Primary selectors: role, label, visible text, and code-confirmed IDs from the QC artifact
- Fallback selectors: stable class names and `data-*` attributes already present in templates
- Last-resort selectors: CSS only when no stable semantic option exists
- Confidence: `high` for this suite because the executed selectors came directly from the inspected templates and runtime DOM snapshots

## Run Command
```bash
npm run test:web:midnight
```

## Last Run Results
- Timestamp: `2026-03-28T23:32:20+07:00`
- Total: `10`
- Passed: `10`
- Failed: `0`
- Duration: `26.6s`
- Verification Verdict: `pass`

## Artifacts
- Trace: `none`
- Screenshot: `test-results/midnight-ai-theme-rollout/dashboard-desktop.png`
- Screenshot: `test-results/midnight-ai-theme-rollout/config-desktop.png`
- Screenshot: `test-results/midnight-ai-theme-rollout/config-save-feedback.png`
- Screenshot: `test-results/midnight-ai-theme-rollout/config-model-field-error.png`
- Screenshot: `test-results/midnight-ai-theme-rollout/daily-scheduler-desktop.png`
- Screenshot: `test-results/midnight-ai-theme-rollout/daily-scheduler-change-model-modal.png`
- Screenshot: `test-results/midnight-ai-theme-rollout/crypto-airdrop-desktop.png`
- Screenshot: `test-results/midnight-ai-theme-rollout/dashboard-mobile-drawer-open.png`
- Screenshot: `test-results/midnight-ai-theme-rollout/daily-scheduler-htmx-refresh.png`
- Screenshot: `test-results/midnight-ai-theme-rollout/crypto-airdrop-htmx-refresh.png`
- Video: `none`
- HTML Report: `none`
- Console or Network Log: `none`

## Issues Found
- None in the latest run.
- Resolved before rerun:
  - Desktop nav controls are hidden correctly on non-mobile viewports.
  - Scheduler and crypto airdrop first-render DOM no longer duplicate the OOB target containers.
  - Config-page `422` HTML responses now swap into HTMX targets instead of failing silently.
  - Dynamic HTMX refreshes preserve a single OOB target container per panel.

## Resume Notes
- Current browser regression suite is green across shell, config HTMX, agent modal, and the two core HTMX refresh paths.
- Next useful extension is a stubbed success-path model-discovery flow plus deeper SSE assertions for live panel updates.
