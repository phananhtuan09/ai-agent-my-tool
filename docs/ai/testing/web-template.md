# Web Test Plan: {Feature Name}

Note: All content in this document must be written in English.

## Input Sources

### Behavior Sources
- `{path-or-note}` - Why this source matters

### UI Sources
- `{path-or-note}` - Why this source matters

### Runtime Sources
- `{path-or-note}` - Why this source matters

### Constraints
- `{constraint}`

## Runtime Assumptions
- Engine: `{playwright|cypress|webdriverio}`
- Base URL: `{url or unknown}`
- Web Server Command: `{command or none}`
- Auth Strategy: `{storageState|login-flow|api-login|none|unknown}`
- Probe Status: `{pass|warn|fail|not-run}`

## Routes Under Test
- `{route}` - `{why it matters}`

## Test Files Created
- `tests/web/{feature-name}.spec.ts` - Browser workflow tests for {feature}

## Scenario Map

### Happy Path
- ✓ User can {complete main flow}

### Validation and Error States
- ✓ Validation errors are visible and actionable
- ✓ Error feedback matches the documented behavior

### Navigation and UI States
- ✓ Navigation transitions match the documented flow
- ✓ Loading, empty, success, and permission states are covered when relevant

### Out of Scope
- `{intentionally excluded scenario}`

## Selector Strategy
- Primary selectors: role, label, visible text
- Fallback selectors: test id or other stable attributes
- Last-resort selectors: CSS only when no stable semantic option exists

## Run Command
```bash
{engine-specific run command}
```

## Last Run Results
- Timestamp: `{ISO-8601 or not-run}`
- Total: `0`
- Passed: `0`
- Failed: `0`
- Duration: `0s`
- Verification Verdict: `{not-run}`

## Artifacts
- Trace: `{path or none}`
- Screenshot: `{path or none}`
- Video: `{path or none}`
- HTML Report: `{path or none}`
- Console or Network Log: `{path or none}`

## Issues Found
- None yet

## Resume Notes
- `{what to rerun or inspect next}`
