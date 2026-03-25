---
name: test-web-orchestrator
description: Use when the user wants one orchestration workflow to analyze specs, plans, Figma, and runtime hints, then author and verify browser-based web UI tests with multi-agent routing and bounded context.
---

# Test Web Orchestrator

Use this skill as the control plane for browser-based web UI testing.

The orchestrator is independent from `requirements-orchestrator`, `development-orchestrator`, `writing-integration-test`, and `run-test`.
It may read artifacts produced by those workflows, but it does not require them.

Core responsibilities:

- normalize flexible inputs into one bounded test context
- route multi-agent analysis with a single-writer contract
- author the final web test doc and generated test file
- run browser tests when requested and verify the outcome

## Inputs

Accept any combination of:

- web test doc path: `docs/ai/testing/web-{name}.md`
- requirement or spec doc path: `docs/ai/requirements/req-{name}.md` or other spec markdown
- feature plan path: `docs/ai/planning/feature-{name}.md`
- Figma spec doc path: `docs/ai/requirements/figma-{name}.md`
- Figma URL
- a feature name that can be resolved from the provided artifacts

Optional:

- runtime notes such as `baseURL`, auth strategy, test account, environment, or browser
- explicit engine: `playwright`, `cypress`, or `webdriverio`
- explicit run mode: `docs-only`, `author-only`, `verify-only`, or `all`
- known blockers or out-of-scope notes

## Required Context

Read these files first:

- `docs/ai/testing/web-template.md`
- `docs/ai/project/CODE_CONVENTIONS.md`
- `docs/ai/project/PROJECT_STRUCTURE.md`
- `docs/ai/testing/README.md`

Read these role files as needed:

- `.agents/roles/test-web-analyst.md`
- `.agents/roles/test-web-ui-mapper.md`
- `.agents/roles/test-web-runtime-probe.md`
- `.agents/roles/test-web-verifier.md`

When legacy behavior matters, you may also read:

- `.claude/commands/writing-integration-test.md`
- `docs/ai/testing/integration-template.md`

## Role Definitions

Worker prompts live in:

- `.agents/roles/test-web-analyst.md`
- `.agents/roles/test-web-ui-mapper.md`
- `.agents/roles/test-web-runtime-probe.md`
- `.agents/roles/test-web-verifier.md`

Load only the roles needed for the current run.

## Codex Multi-Agent Contract

This repository registers named Codex agents in `.codex/config.toml`.

Use these exact agent names when `spawn_agent` is available:

- `test_web_analyst`
- `test_web_ui_mapper`
- `test_web_runtime_probe`
- `test_web_qc`
- `test_web_verifier`

Execution policy:

- Keep the orchestrator as the only writer of `docs/ai/testing/web-{name}.md` and generated test files.
- Worker agents may write only their own artifact, except `test_web_verifier`, which is read-only.
- Prefer real sub-agents over solo simulation when available.
- Spawn only the agents selected by the routing logic below.
- If a spawned worker fails, retry once with a tighter packet, then continue solo if needed.

## Run Modes

Before routing, ask the user to choose a run mode unless it is already explicit in the prompt.

For Codex, ask directly in one concise numbered prompt:

1. `docs-only` - analyze sources and create or refresh `web-{name}.md`, but do not generate a test file or run tests
2. `author-only` - analyze sources, create or refresh `web-{name}.md`, and generate the test file, but do not run tests
3. `verify-only` - use the existing web doc and test file to run verification only
4. `all` - run analyze, map, probe, author, execute, and verify in one pass

Mode rules:

- `docs-only`:
  - may run `analyst`, `ui-mapper`, and `runtime-probe` when they improve the test doc
  - stops before test-file generation and test execution
- `author-only`:
  - may run `analyst`, `ui-mapper`, and `runtime-probe`
  - writes the test doc and test file
  - stops before execution and post-run verification
- `verify-only`:
  - requires an existing `web-{name}.md` or test file path
  - does not generate a new test file unless the user explicitly switches modes
- `all`:
  - run `normalize -> gate -> analyze -> map -> probe -> author -> execute -> verify`
  - after the initial mode choice, do not ask follow-up confirmation questions
  - treat `warn` as auto-continue and report it
  - treat later ambiguity that would materially change coverage or runtime behavior as `fail`

## Context Packet

Before handing work to another worker, create a bounded packet with:

- `Mode`: `analyze`, `ui-map`, `runtime-probe`, `qc`, `author`, or `verify`
- `Run Mode`: `docs-only`, `author-only`, `verify-only`, or `all`
- `Feature Name`
- `Goal`: one concrete outcome
- `Behavior Sources`: exact doc paths or user notes that define expected behavior
- `UI Sources`: exact doc paths or URLs that define UI structure or states
- `Runtime Sources`: exact doc paths, URLs, config paths, or notes needed to run the app or tests
- `Runtime Config`: confirmed base URL/port, auth strategy (storageState path / test credentials / none), env variables
- `Constraints`: explicit non-goals, blockers, and known limitations
- `Allowed Writes`: exact file paths the worker may edit, or `none`
- `Validation`: exact commands or evidence expectations for this step
- `Stop If`: ambiguity that would materially change output correctness

When delegating to Codex agents, also include:

- `Role`: exact agent name from the Codex Multi-Agent Contract
- `Required Reads`: exact file paths the worker should load first
- `Linked Docs`: exact requirement, plan, figma, and web-doc paths relevant to this run

Do not forward the full conversation when the packet is sufficient.

## Input Normalization

Normalize every run into four input groups:

- `Behavior Sources`: requirements, specs, feature plans, acceptance criteria, bug notes
- `UI Sources`: Figma docs, Figma URLs, screenshots, existing design notes
- `Runtime Sources`: `baseURL`, auth notes, env/config files, engine choice, current web doc, existing test file
- `Constraints`: out-of-scope items, known bugs, unsupported flows, environment limits

A single source may contribute to more than one group.
For example, `feature-{name}.md` may contribute to both `Behavior Sources` and `Constraints`.

## Readiness Gate

Before authoring or executing, classify findings as `fail`, `warn`, or `pass`.

Engine resolution order:

1. explicit engine in runtime notes or the existing web doc
2. `Web Tests` section in `docs/ai/project/PROJECT_STRUCTURE.md`
3. `Integration Tests` section in `docs/ai/project/PROJECT_STRUCTURE.md`
4. repo config files such as `playwright.config.*`, `cypress.config.*`, `wdio.conf.*`, or `webdriverio.*`
5. `package.json` scripts or dependencies
6. if mode is `docs-only` or `author-only`, default authoring engine to `playwright` and record a warning
7. otherwise fail with `Cannot determine test engine`

Fail when:

- no usable behavior boundary can be derived from the provided sources
- verification is requested but no existing web doc or test file can be found
- a runtime run is required and the app target, engine, or auth path is missing in a way that prevents execution
- unresolved open questions would materially change test coverage or target route selection
- baseURL has two or more conflicting candidates that cannot be resolved from config alone

Warn when:

- the engine was defaulted for authoring instead of discovered
- runtime probing is unavailable because browser tooling is missing but static authoring can continue
- Figma exists without enough behavior detail to assert product outcomes confidently
- constraints or out-of-scope items are implied but not explicit

Pass when:

- the next step can proceed without guessing behavior or runtime requirements

## Routing Rules

### Runtime Prerequisites

Before running the analyst, confirm runtime prerequisites with the user:

- base URL or port
- auth strategy: storageState path, test credentials, or no auth needed
- env variables if any

Record confirmed values in the `Runtime Config` field of the Context Packet.

### Analyst

Run `test_web_analyst` first on every mode.

The analyst artifact is the source of truth for:

- normalized inputs
- behavior coverage strength
- runtime assumptions
- routing signals for downstream workers

### QC

Run `test_web_qc` after the analyst on every mode.

The QC agent reads the application codebase and the analyst artifact to produce formal, source-grounded test cases.
The QC artifact is the source of truth for test case scope before authoring begins.

### Scope Confirmation

After QC, present the test case list from the QC artifact to the user.
Ask the user to approve the scope or exclude specific test cases before proceeding to ui-mapper, probe, or authoring.
Record any excluded test cases in `Constraints`.

### UI Mapper

Run `test_web_ui_mapper` only when the analyst artifact says `UI Mapping Needed: yes`.

Prefer this worker when:

- a Figma source exists
- the flow is UI-heavy or state-heavy
- selector strategy would otherwise be guesswork

### Runtime Probe

Run `test_web_runtime_probe` only when the analyst artifact says `Runtime Probe Feasible: yes`.

If browser tooling is unavailable but the rest of the flow is still authorable:

- skip `runtime-probe`
- keep the gate at `warn`
- continue with static analysis

If the selected mode requires an actual run and runtime prerequisites are materially broken:

- fail the gate
- stop before execution

Tooling for this step follows the Browser Tooling Strategy — Phase 1.
The probe artifact must include a confirmed selector map and a reachability report.

### Verifier

Run `test_web_verifier` after test execution in `all` mode.

Run it in `verify-only` after the test run completes, even when the run failed.
The verifier must classify the result as:

- implementation bug
- selector drift
- runtime/environment blocker
- flaky or incomplete test coverage

## Browser Tooling Strategy

Use two distinct tools across two distinct phases. Never mix them in the same step.

### Phase 1 — Exploration (runtime-probe)

Use a lightweight browser CLI, not the full test framework:

- **Claude Code**: use active MCP Playwright tools (`browser_snapshot`, `browser_navigate`,
  `browser_click`, etc.)
- **Codex / shell-only**: use `playwright-cli` commands (`goto`, `snapshot`, `click`, `route`)

Goals of this phase:
- confirm the app is reachable and auth succeeds
- capture actual selectors from live DOM snapshots
- validate that expected routes and UI states exist before authoring

Output this phase must produce:
- a confirmed selector map: element description → observed selector
- a reachability report: which routes are live, which return error or redirect
- auth state if the flow requires login

Do not write assertions in this phase. The probe only observes and records.

### Phase 2 — Authoring (test file generation)

Use `@playwright/test` to generate `tests/web/{name}.spec.ts`.

Rules:
- every selector must be grounded in probe output or UI mapper output — never guessed
- if probe did not run, use `getByRole`, `getByLabel`, or `getByText` only; never invent
  `data-testid` values, CSS class names, or nth-child paths
- every test must assert a visible outcome, not only perform actions
- each test covers exactly one user journey from entry point to observable result
- declare API strategy explicitly at the top of the test file:
  - `mock` — use `page.route()` to intercept; do not call real backend
  - `real` — requires stable data seed; document the seed command in the web doc
  - never mix mock and real calls within the same test suite

### Selector Grounding Decision

| Probe ran | UI mapper ran | Selector to use | Confidence |
|-----------|---------------|-----------------|------------|
| yes       | any           | confirmed selector from probe artifact | high |
| no        | yes           | selector from UI mapper artifact        | medium |
| no        | no            | `getByRole` / `getByLabel` / `getByText` only | low |

Record the confidence level in the web doc `Selector Strategy` section.

## Workflow

### 0. Choose mode

Ask for the run mode unless it was already made explicit.

### 1. Normalize input

- derive a concise kebab-case feature name
- classify sources into `Behavior Sources`, `UI Sources`, `Runtime Sources`, and `Constraints`
- resolve the output paths:
  - `docs/ai/testing/web-{name}.md`
  - `docs/ai/testing/agents/web-analyst-{name}.md`
  - `docs/ai/testing/agents/web-qc-{name}.md`
  - `docs/ai/testing/agents/web-ui-map-{name}.md`
  - `docs/ai/testing/agents/web-runtime-{name}.md`
  - `tests/web/{name}.spec.ts`

### 1.5. Confirm runtime prerequisites

Ask the user:

- base URL or port for the app under test
- auth strategy: storageState path, test credentials (username/password), or no auth needed
- any required env variables

Record confirmed answers as `Runtime Config` in the Context Packet. Fail the gate if baseURL remains ambiguous after this step.

### 2. Gate

- resolve the engine
- assess whether authoring or execution can proceed
- classify the result as `fail`, `warn`, or `pass`

### 3. Analyze

- run `test_web_analyst`
- re-read the analyst artifact from disk
- use its `Routing Signals` section to decide whether to spawn `ui-mapper` and `runtime-probe`

### 3.5. QC — codebase analysis

- run `test_web_qc`
- re-read the QC artifact from disk

### 3.6. Scope confirmation

- present the test case list from the QC artifact to the user
- ask the user to approve all cases or exclude specific ones
- record excluded cases in `Constraints` before proceeding

### 4. Run downstream workers

Use this DAG:

1. `analyst` runs first
2. after `analyst`, run `qc` to read codebase and produce test cases
3. after `qc` and scope confirmation, `ui-mapper` and `runtime-probe` may run in parallel because both depend on the analyst artifact
4. authoring waits for all selected worker outputs
5. execution waits for authoring
6. verification waits for execution

If `spawn_agent` is unavailable, preserve the same boundaries and execute serially.

### 5. Consolidate

The orchestrator must read worker artifacts from disk and build a bounded summary with:

- inputs used
- agent outputs created
- behavior coverage quality
- selector strategy confidence
- runtime blockers
- contradictions across sources or workers

Resolve contradictions before authoring the final web doc.

### 6. Author outputs

In `docs-only`, create or refresh only `docs/ai/testing/web-{name}.md`.

In `author-only` and `all`:

- create or refresh `docs/ai/testing/web-{name}.md`
- create or refresh `tests/web/{name}.spec.ts`

Authoring constraints:
- follow the Browser Tooling Strategy — Phase 2 selector grounding rules
- if probe output is available, read `docs/ai/testing/agents/web-runtime-{name}.md` before
  writing any selector
- record which selectors are probe-grounded vs statically inferred in the web doc

Idempotency rules:

- refresh the web doc in place when the scope is unchanged
- overwrite `Last Run Results`, `Artifacts`, `Issues Found`, and `Resume Notes` with current data
- preserve manually useful sections such as source inventory and out-of-scope notes when still valid
- archive the old web doc only when the scope or target flow changes materially

### 7. Execute

Skip this step in `docs-only` and `author-only`.

For `verify-only` and `all`:

- run the smallest useful scope first, usually the generated or referenced test file
- prefer the command recorded in the web doc when it exists
- capture stdout or stderr, duration, and artifact locations

### 8. Verify

Skip this step in `docs-only` and `author-only`.

Always run `test_web_verifier` after execution, even when the run failed.

The verifier should return:

- `Verification Verdict`: `pass`, `warn`, or `fail`
- `Issue Type`
- `Coverage Gaps`
- `Runtime Gaps`
- `Retry Advice`

Write the verifier result into the final web doc instead of creating a separate verifier artifact.

## Failure Handling

If `runtime-probe` cannot run because tooling is unavailable:

- warn and continue when the selected mode does not require execution
- fail when execution is required and no equivalent runtime path exists

If test generation fails:

- stop and report the blocker
- do not silently fall back to another engine or file location

If the test run fails:

- still run the verifier
- record whether the failure looks like a product bug, selector drift, runtime blocker, or flaky setup

Do not silently switch to another source set or another engine mid-run.

## Final Response

Report:

- run mode used
- inputs consumed and how they were normalized
- gate result
- agents executed
- files created or updated
- engine chosen and how it was resolved
- whether runtime probing ran or was skipped
- verification verdict when execution happened
- blockers and resume point

## Quality Bar

- the workflow is independent from existing planning or test workflows
- worker context stays bounded
- routing decisions are grounded in the analyst artifact
- authoring and execution do not guess missing runtime requirements
- the final web doc is useful as a rerun source of truth
- selectors in the generated test file are grounded in probe or UI mapper output, not guessed
- API strategy (mock or real) is declared explicitly and consistent across the test suite
