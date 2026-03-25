---
phase: testing
title: Testing Documentation
description: Feature test plans and testing guidelines
---

# Testing Documentation

## Purpose
This directory contains test plans for individual features across unit, integration, and browser-driven web testing workflows.

## Testing Workflow

### Unit Test Plans
Use the `writing-test` command for logic-focused coverage:
- Output: `docs/ai/testing/unit-{name}.md`
- Template: `docs/ai/testing/unit-template.md`

### Integration Test Plans
Use the `writing-integration-test` command for lightweight Playwright-driven UI flows:
- Output: `docs/ai/testing/integration-{name}.md`
- Template: `docs/ai/testing/integration-template.md`

### Web UI Test Plans
Use the `test-web-orchestrator` workflow for multi-agent browser testing driven by flexible inputs such as requirements, feature plans, Figma, and runtime notes:
- Output: `docs/ai/testing/web-{name}.md`
- Template: `docs/ai/testing/web-template.md`
- Worker artifacts: `docs/ai/testing/agents/web-*.md`

### Testing Philosophy
- **Unit tests** focus on pure logic, edge cases, and deterministic parameter coverage.
- **Integration tests** focus on lightweight Playwright-based UI flows when a single-command workflow is enough.
- **Web UI tests** focus on browser-driven user journeys, selectors, runtime probing, and verification against flexible source artifacts.
- **Automation** should keep test intent explicit, rerunnable, and grounded in acceptance criteria.

### Test Doc Types
- `unit-{name}.md`: logic and isolated component test plans
- `integration-{name}.md`: lightweight Playwright UI flow plans
- `web-{name}.md`: multi-agent browser UI test plans with runtime assumptions and rerun notes

### Browser Testing Guidance
- Use `writing-integration-test` when you already know the UI flow and only need a focused Playwright test file quickly.
- Use `test-web-orchestrator` when the workflow must read mixed inputs, route multi-agent analysis, probe runtime, and verify the outcome.
- Keep browser tests focused on user-visible behavior, not implementation details.
- Prefer stable selectors: roles, labels, visible text, then test ids.

## Template Reference
- `unit-template.md`
- `integration-template.md`
- `web-template.md`

## Related Documentation
- Planning docs: `../planning/`
- Project standards: `../project/`

## Validation Requirements
- After each batch of implementation edits, run:
  - Linter on changed files (must pass; auto-fix up to 3 attempts)
  - Type checks (must pass)
  - Build (must be green)
- Map test cases to the feature's Acceptance Criteria.

---

**Note**: The lightweight and orchestrated browser workflows can coexist. `writing-integration-test` remains the quick path; `test-web-orchestrator` is the multi-agent path.
