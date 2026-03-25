---
name: test-web-orchestrator
description: Orchestrates multi-agent web UI testing from flexible spec, plan, Figma, and runtime inputs into a web test doc, browser test file, and verification report.
---

## Goal

Provide one Claude Code entry point for multi-agent web UI testing.

This command is independent from `/requirements-orchestrator`, `/development-orchestrator`, `/writing-integration-test`, and `/run-test`.
It may read artifacts produced by those workflows, but it does not require them.

Primary outputs:
- `docs/ai/testing/web-{name}.md`
- `tests/web/{name}.spec.ts`
- worker artifacts under `docs/ai/testing/agents/`

---

## Workflow Alignment

- Provide brief status updates before and after important actions.
- For medium or large work, create orchestration todos for macro phases: Mode, Normalize, RuntimePrereqs, Gate, Analyze, QC, ScopeConfirm, Map, Probe, Author, Execute, Verify.
- Keep exactly one orchestration todo `in_progress`.
- Keep the orchestrator as the only writer of the final web doc and generated test file.

---

## Step 0: Select Run Mode

Use `AskUserQuestion` for this step unless the user already selected the mode explicitly in the same request.

Supported modes:
- `docs-only`: analyze and create or refresh `web-{name}.md`, but do not generate a test file or run tests
- `author-only`: analyze, create or refresh `web-{name}.md`, and generate a test file, but do not run tests
- `verify-only`: run verification against an existing web doc and test file without regenerating them
- `all`: run analyze, map, probe, author, execute, and verify in one pass

Required prompt:

```text
AskUserQuestion(questions=[{
  question: "Which test-web-orchestrator mode should I run?",
  header: "Run Mode",
  options: [
    { label: "docs-only", description: "Create or refresh the web test doc only" },
    { label: "author-only", description: "Create or refresh the web doc and test file, but do not run tests" },
    { label: "verify-only", description: "Run an existing web test doc and test file without regenerating them" },
    { label: "all", description: "Run analysis, authoring, execution, and verification in one pass" }
  ],
  multiSelect: false
}])
```

Mode rules:
- In `all`, do not ask follow-up confirmation questions after the mode choice.
- In `all`, treat `warn` as auto-continue and report it.
- In `all`, stop on any later ambiguity that would materially change target coverage or runtime behavior.

---

## Step 1: Normalize Inputs

Accept any combination of:
- `docs/ai/testing/web-{name}.md`
- requirement or spec docs
- `docs/ai/planning/feature-{name}.md`
- `docs/ai/requirements/figma-{name}.md`
- Figma URLs
- runtime notes such as `baseURL`, engine, auth, or test account

Normalize them into four groups:
- `Behavior Sources`
- `UI Sources`
- `Runtime Sources`
- `Constraints`

Rules:
- A single source may belong to more than one group.
- Derive a concise kebab-case feature name.
- Resolve output paths:
  - `docs/ai/testing/web-{name}.md`
  - `docs/ai/testing/agents/web-analyst-{name}.md`
  - `docs/ai/testing/agents/web-qc-{name}.md`
  - `docs/ai/testing/agents/web-ui-map-{name}.md`
  - `docs/ai/testing/agents/web-runtime-{name}.md`
  - `tests/web/{name}.spec.ts`

Read:
- `docs/ai/testing/web-template.md`
- `docs/ai/project/CODE_CONVENTIONS.md`
- `docs/ai/project/PROJECT_STRUCTURE.md`
- `docs/ai/testing/README.md`

---

## Step 1.5: Confirm Runtime Prerequisites

Use `AskUserQuestion` for this step unless the user already provided all values explicitly.

Required prompt:

```text
AskUserQuestion(questions=[
  {
    question: "What is the base URL or port for the app under test?",
    header: "Base URL",
    options: [
      { label: "http://localhost:3000", description: "Default Next.js dev port" },
      { label: "http://localhost:5173", description: "Default Vite dev port" },
      { label: "http://localhost:4200", description: "Default Angular dev port" },
      { label: "Other / not sure", description: "I'll provide it or check the config" }
    ],
    multiSelect: false
  },
  {
    question: "What auth strategy should the tests use?",
    header: "Auth Strategy",
    options: [
      { label: "storageState file", description: "Reuse a saved Playwright auth state file" },
      { label: "Test credentials", description: "Provide username and password for login" },
      { label: "No auth needed", description: "The tested flows do not require login" }
    ],
    multiSelect: false
  }
])
```

Record the confirmed values as `Runtime Config` in the Context Packet.

If the base URL cannot be resolved after this step (e.g., user selects "Other / not sure" and no config file disambiguates), fail the gate rather than guessing.

---

## Step 2: Readiness Gate

Classify the current state as `fail`, `warn`, or `pass`.

### Engine resolution order

1. explicit engine in runtime notes or the current web doc
2. `Web Tests` section in `docs/ai/project/PROJECT_STRUCTURE.md`
3. `Integration Tests` section in `docs/ai/project/PROJECT_STRUCTURE.md`
4. repo config files such as `playwright.config.*`, `cypress.config.*`, `wdio.conf.*`, or `webdriverio.*`
5. `package.json` scripts or dependencies
6. if mode is `docs-only` or `author-only`, default the authoring engine to `playwright` and record a warning
7. otherwise fail: `Cannot determine test engine`

### Fail when
- no usable behavior boundary can be derived from the provided sources
- `verify-only` is requested but no existing web doc or test file can be found
- runtime execution is required and app target, engine, or auth path is missing in a way that prevents execution
- unresolved open questions would materially change test coverage or route selection
- base URL has two or more conflicting candidates that cannot be resolved after Step 1.5

### Warn when
- authoring falls back to the default `playwright` engine
- runtime probing is unavailable because browser tooling is missing but static authoring can continue
- Figma exists without enough behavior detail to assert outcomes confidently
- constraints or out-of-scope items are implied instead of explicit

### Pass when
- the next step can proceed without guessing behavior or runtime requirements

---

## Step 3: Run Analyst First

Invoke `.claude/agents/test-web-analyst.md`.

The analyst artifact is the source of truth for:
- source normalization
- behavior map
- runtime assumptions
- routing signals

Required routing signals:
- `UI Mapping Needed`
- `Runtime Probe Feasible`
- `Authoring Ready`
- `Verification Ready`

---

## Step 3.5: QC — Codebase Analysis

Invoke `.claude/agents/test-web-qc.md`.

Pass a handoff packet that includes:
- analyst artifact path
- app source paths to read (route files, page components, form components, auth guards, API hooks) — derive from the codebase based on the feature name and analyst routing signals

Re-read `docs/ai/testing/agents/web-qc-{name}.md` from disk after the agent completes.

---

## Step 3.6: Scope Confirmation

Use `AskUserQuestion` to present the test case list from the QC artifact and ask the user to confirm or trim the scope.

Required prompt structure:

```text
AskUserQuestion(questions=[{
  question: "The QC agent found the following test cases. Which ones should be included in this run?",
  header: "Test Scope",
  options: [
    { label: "All test cases", description: "Run all {N} test cases identified by QC" },
    { label: "Exclude specific cases", description: "I'll name which to skip in the Other field" }
  ],
  multiSelect: false
}])
```

If the user excludes specific cases, record them in `Constraints` before proceeding to UI Mapper and Runtime Probe.

In `all` mode, if the user already confirmed scope and a test case list is in the QC artifact with no ambiguity, you may skip this question and auto-continue — treat it as `pass`.

---

## Step 4: Run Conditional Workers

### UI Mapper

Invoke `.claude/agents/test-web-ui-mapper.md` only when the analyst artifact says `UI Mapping Needed: yes`.

### Runtime Probe

Invoke `.claude/agents/test-web-runtime-probe.md` only when the analyst artifact says `Runtime Probe Feasible: yes`.

Runtime probe policy:
- if browser tooling is unavailable but the selected mode does not require execution, skip with warning
- if execution is required and runtime prerequisites are materially broken, stop with `fail`
- before executing any interaction that could create, modify, or delete app data, use `AskUserQuestion` to confirm the user consents before proceeding

Tooling:
- Claude Code: use MCP Playwright tools (`browser_snapshot`, `browser_navigate`, `browser_click`, etc.)
- Codex / shell-only: use `playwright-cli` commands (`goto`, `snapshot`, `click`, `route`)

Do not write assertions in this step. The probe only observes and records.

Required probe output:
- confirmed selector map: element description → observed selector
- reachability report: which routes are live, which return error or redirect
- auth state snapshot if the flow requires login

Execution order:
1. Analyst always runs first.
2. QC runs after Analyst to produce formal test cases.
3. Scope confirmation happens after QC.
4. UI Mapper and Runtime Probe may run in parallel after scope is confirmed.
5. Authoring waits for all selected worker outputs.

---

## Step 5: Consolidate the Final Web Doc

Read worker artifacts from disk and create or refresh `docs/ai/testing/web-{name}.md` using `docs/ai/testing/web-template.md`.

The final web doc must include:
- normalized input sources
- runtime assumptions
- routes under test
- scenario map
- selector strategy with confidence level (probe-grounded / ui-mapper / static-inferred)
- run command
- artifacts
- issues found
- resume notes

Idempotency rules:
- refresh the web doc in place when scope is unchanged
- overwrite `Last Run Results`, `Artifacts`, `Issues Found`, and `Resume Notes`
- preserve still-valid source inventory and scope sections
- archive the old web doc only when the scope changes materially

If worker outputs conflict on behavior scope or runtime target, resolve the contradiction before writing the web doc. Document the chosen direction and the reason in `Resume Notes`.

---

## Step 6: Generate the Test File

Skip this step in `docs-only` and `verify-only`.

Create or refresh `tests/web/{name}.spec.ts`.

Authoring rules:
- use `@playwright/test` conventions
- selectors must be grounded in probe or UI mapper output — never guessed:
  - probe ran → use confirmed selector from probe artifact
  - only UI mapper ran → use selector from UI mapper artifact
  - neither ran → use `getByRole`, `getByLabel`, or `getByText` only; never invent `data-testid` values or CSS class names
- every test must assert a visible outcome, not only perform actions
- each test covers exactly one user journey from entry point to observable result
- declare API strategy explicitly as a comment at the top of the test file:
  - `mock` — use `page.route()` to intercept; do not call real backend
  - `real` — requires stable data seed; document the seed command in the web doc
  - never mix mock and real calls within the same test suite
- use the resolved engine

---

## Step 7: Execute Tests

Skip this step in `docs-only` and `author-only`.

Rules:
- run the smallest useful scope first, usually `tests/web/{name}.spec.ts`
- prefer the command recorded in the web doc when it exists
- capture stdout/stderr, duration, and artifact paths
- do not silently switch engines or test targets mid-run

If the run fails:
- keep the failure output
- proceed to verification

---

## Step 8: Verify

Skip this step in `docs-only` and `author-only`.

Invoke `.claude/agents/test-web-verifier.md` after execution, even if the run failed.

The verifier must return:
- `Verification Verdict`: `pass`, `warn`, or `fail`
- `Issue Type`
- `Coverage Gaps`
- `Runtime Gaps`
- `Retry Advice`

Write the verifier result into:
- `Last Run Results`
- `Issues Found`
- `Resume Notes`

Do not create a separate verifier artifact file.

---

## Step 9: Failure Handling

- If runtime probing is unavailable because tooling is missing: warn and continue only when the selected mode does not require execution.
- If test generation fails: stop and report the blocker.
- If test execution fails: still run verification to classify the failure.
- Do not silently fall back to another engine, another feature, or another test file.

---

## Final Response

Report:
- run mode used
- normalized inputs
- gate verdict
- agents executed
- files created or updated
- engine chosen and how it was resolved
- whether runtime probing ran or was skipped
- verification verdict when execution happened
- blockers and resume point
