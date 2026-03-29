# Web Runtime Probe: midnight-ai-theme-rollout

## Runtime Resolution

- Engine: `playwright`
  - Resolved from `docs/ai/project/PROJECT_STRUCTURE.md` integration-test guidance plus a working local install of `@playwright/test` and `playwright` CLI in this repository.
- Base URL: `http://127.0.0.1:8000`
- Launch command: `python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`
- Auth strategy: `none`
- First probe route: `/`

## Probe Verdict

- Verdict: `Probe Ready`
- Reason: the FastAPI app was started locally, the target routes were reachable, and Playwright successfully captured screenshots from the live UI with JavaScript enabled.

## Reachability Findings

- `GET /` loaded successfully and produced `dashboard-desktop.png`.
- `GET /config` loaded successfully and produced `config-desktop.png`.
- `GET /agents/daily_scheduler` loaded successfully and produced `daily-scheduler-desktop.png`.
- `GET /agents/crypto_airdrop` loaded successfully and produced `crypto-airdrop-desktop.png`.
- A mobile viewport probe on `/` successfully opened and closed the drawer state and produced `dashboard-mobile-drawer-open.png`.

## Auth Findings

- No login or storage state was required.
- Agent pages were directly reachable from the shared shell without redirects.

## Console and Network Findings

- No app-start blocker was observed once `uvicorn` was running.
- SSE was live enough on agent pages to show the connection badge in a connected state during the screenshot pass.
- The probe uncovered implementation issues in the live DOM:
  - Desktop-only views still render the mobile drawer controls (`.nav-toggle`, `.sidebar-close`) as visible elements.
  - `#daily-schedule-timeline` appears twice in the scheduler page DOM because the OOB block is rendered inline on first paint.
  - `#airdrop-results-panel` appears twice in the crypto airdrop page DOM for the same reason.

## Recommended Runtime Adjustments

- Fix the desktop visibility regression for `.nav-toggle` and `.sidebar-close` before relying on screenshot baselines.
- Remove duplicate first-render OOB containers for scheduler timeline and airdrop results so route-level locators and layout assertions remain unambiguous.
- Keep using Playwright for reruns; the local install and browser runtime are now in place.

## Handoff Summary

### Decisions
- Selected runtime target: `http://127.0.0.1:8000`
- Selected engine command: `npm run test:web:midnight`

### Blockers
- No hard runtime blocker remains for page loading or screenshots.
- Current UI bugs create ambiguous DOM targets and failing assertions, but they do not prevent route access.

### Open Questions
- None. The remaining failures are grounded in the live DOM and screenshots rather than missing runtime information.
