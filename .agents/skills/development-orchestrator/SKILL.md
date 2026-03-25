---
name: development-orchestrator
description: Use when the user wants one orchestration workflow to route requirement, epic, and feature-plan artifacts across planning and implementation with readiness gates, investigation, verification, and status sync.
---

# Development Orchestrator

Use this skill as the control plane for planning and implementation.

The orchestrator does not replace `manage-epic`, `create-plan`, or `execute-plan`. It sits above them and does five things:

- route the current artifact to the right workflow
- classify the work by task type and task size before execution
- investigate scope when the prompt is too thin to trust
- enforce readiness and verification gates
- sync status across requirement, epic, and feature-plan docs

## Inputs

Accept one of:

- requirement doc path: `docs/ai/requirements/req-{name}.md`
- epic doc path: `docs/ai/planning/epic-{name}.md`
- feature plan path: `docs/ai/planning/feature-{name}.md`
- a feature name that can be resolved to one of the above
- plain-text description with no artifact path

Optional:

- direct user scope notes
- blocker notes
- explicit orchestrator run mode: `docs-only` or `all`
- explicit instruction to plan only, execute only, or sync only
- spec paths, bug reports, screenshots, or hinted files

## Required Context

Read these files first:

- `docs/ai/project/CODE_CONVENTIONS.md`
- `docs/ai/project/PROJECT_STRUCTURE.md`
- `docs/ai/planning/README.md`

Read these workflow skills as needed:

- `.agents/skills/manage-epic/SKILL.md`
- `.agents/skills/create-plan/SKILL.md`
- `.agents/skills/execute-plan/SKILL.md`
- `.agents/skills/quality-code-check/SKILL.md` when validation becomes the main task

If `manage-epic` is unavailable, fall back to `.claude/commands/manage-epic.md`.

## Role Definitions

Optional worker prompts live in:

- `.agents/roles/task-investigator.md`
- `.agents/roles/dev-plan-reviewer.md`
- `.agents/roles/dev-verifier.md`

Use them when the work is large enough or ambiguous enough to benefit from explicit worker boundaries. Otherwise simulate the same boundary yourself.

## Codex Multi-Agent Contract

This repository registers named Codex agents in `.codex/config.toml`.

Use these exact agent names when `spawn_agent` is available:

- `task_investigator`
- `dev_plan_reviewer`
- `dev_verifier`

Execution policy:

- Keep one primary writer for requirement, epic, feature-plan, and implementation edits.
- Use sub-agents for read-heavy investigation, review, and verification when safe.
- Do not run more than one write-heavy implementation worker at a time.
- If a spawned investigation, review, or verification agent fails, retry once with a tighter packet, then continue solo if needed.

## Compatibility Contract

This skill must work with and without optional orchestrator-specific template changes.

- Do not assume `req-template` already contains `Related Plans`.
- Do not assume `epic-template` already contains `FR Scope` or `Depends On`.
- Do not assume `execute-plan` auto-syncs epic status.
- If any of those integrations exist, use them.
- If they do not exist, keep the workflow moving by updating docs explicitly and only when safe.

Standalone `create-plan` and `execute-plan` flows must remain valid.

## Run Modes

Before routing, ask the user to choose the orchestrator run mode unless the prompt already selected one explicitly.

For Codex, ask directly in one concise numbered prompt:

1. `docs-only` - generate or refresh the planning docs needed for review, then stop before implementation
2. `all` - run the full workflow end to end with no further confirmation prompts

Mode rules:

- `docs-only`:
  - requirement input -> create or refresh the epic when needed, then generate every feature plan doc needed for review
  - epic input -> create or refresh all missing or stale feature plans tracked by the epic, not just the next ready slice
  - feature-plan input -> review and fix the selected plan doc only
  - plain-text input -> generate the minimum planning artifact needed for the detected task size, then stop before implementation
  - stop before `execute`, implementation `verify`, and post-implementation `sync`
- `all`:
  - run `route -> classify -> investigate -> gate -> plan -> plan-review -> execute -> verify -> sync` in one pass
  - after the initial mode choice, do not ask follow-up confirmation questions
  - treat `warn` as auto-continue and report it
  - treat any later ambiguity that would materially change behavior as `fail` and stop

## Classification Model

Classify every run on two independent axes before planning or executing:

- `Task Type`: `new-feature`, `bug-fix`, `refactor`, `upgrade`, or `delete`
- `Task Size`: `quick`, `standard`, or `large`

These axes are independent:

- a bug fix can be `quick` or `large`
- a refactor can be `quick` or `large`
- task size decides document depth
- task type decides minimum context needed before execution

Do not auto-execute a plain-text prompt only because it looks short. A `quick` task still has to pass the type-specific gate.

## Task Type Gate

Before planning or executing, confirm the minimum required information for the detected task type:

| Type | Minimum required before execute |
| --- | --- |
| `new-feature` | integration point, one existing pattern file or module to follow, and an explicit out-of-scope boundary |
| `bug-fix` | symptom or error description, expected versus actual behavior, and a reproduction path |
| `refactor` | explicit behavior-preserved contract, validation or test coverage plan, and a scope boundary |
| `upgrade` | target dependency or API change, behavior to preserve, and a caller or dependent list |
| `delete` | remove versus disable decision, dependency trace, and the intended safety or rollback boundary |

If these minimums are missing:

- use the investigation report as the primary source to fill them
- if a minimum is still missing after investigation, ask the user once for the remaining blocking gaps
- do not assume or infer minimums without investigation evidence

## Investigation Policy

Always run investigation for plain-text input before proceeding to the task-type gate or planning. The investigation result is the primary source for fulfilling task-type minimums — do not infer or assume minimums without it.

Investigate locally (read 1–2 files yourself) when:
- the artifact is a well-formed feature plan or requirement doc with clear scope
- the task is unambiguously single-file and the first likely file confirms full scope

Spawn `task_investigator` when any of these are true:

- the input is plain text (always)
- task type is ambiguous after reading the prompt and core docs
- the prompt names a symptom but not the owning module or integration point
- the scope is still unclear after reading one or two likely files
- multi-file or cross-layer impact is likely, especially for `refactor`, `upgrade`, or `delete`
- the user supplied spec files, logs, or hints that need bounded triage before planning

The investigator is read-only and must return this fixed structure:

```markdown
## Investigation Report

**Task Type:** bug-fix | refactor | new-feature | upgrade | delete
**Confidence:** high | medium | low
**Scope:** single-file | multi-file | cross-layer

### Files Read
- `path/to/file.ts` - why it was read

### Known (from codebase)
- fact 1

### Unclear (blocking)
- gap 1

### Questions for User
1. question only when a blocking gap remains

### Recommended Next Step
proceed | ask-user | escalate-to-spec
```

Use the report to decide whether to continue, ask the user, or escalate from plain prompt to planning docs.

## Context Packet

Before handing work to another skill or worker, create a bounded packet with:

- `Mode`: `route`, `investigate`, `plan`, `plan-review`, `execute`, `verify`, or `sync`
- `Run Mode`: `docs-only` or `all`
- `Input Artifact`: `requirement`, `epic`, `feature-plan`, or `plain-text`
- `Task Type`: detected type plus confidence
- `Task Size`: `quick`, `standard`, or `large`
- `Goal`: one concrete outcome
- `Source of Truth`: exact doc paths, files, specs, or prompt snippets
- `Known Facts`: only the facts relevant to this step
- `Blocking Gaps`: unresolved items that still matter
- `Allowed Files`: files the worker may edit
- `Non-Goals`: explicit out-of-scope items
- `Validation`: exact commands or validation expectations
- `Stop If`: ambiguity that would materially change behavior

Do not forward full conversation history when the packet is sufficient.

When delegating to Codex agents, also include:

- `Role`: exact agent name from the Codex Multi-Agent Contract
- `Allowed Writes`: exact file paths the worker may edit, or `none` for read-only investigation and verification
- `Linked Docs`: exact requirement, epic, and feature-plan paths relevant to this step

## Readiness Gate

After task-type minimums are satisfied, classify findings as `fail`, `warn`, or `pass`.

### Proportionality

Match required spec depth to task size before applying the gate:

- **Quick task**: single concern, clear outcome, no cross-cutting dependency chain, and a minimal inline plan is sufficient
- **Standard task**: multiple behaviors or files but no epic needed, so a feature plan doc is sufficient
- **Large task**: multi-deliverable, cross-layer, or dependency-ordered slices, so full spec plus epic is required

Apply `fail` / `warn` / `pass` relative to the expected depth for that task size, not against the full spec bar.

Fail when:

- the core behavior or feature boundary is missing
- task-type minimum information is still missing
- no acceptance criteria or behavior contract exist for non-trivial work
- unresolved open questions would materially change implementation
- the target artifact cannot be found

Warn when:

- out-of-scope is missing but the implementation boundary is still clear
- dependency order is implied but not explicit
- risks exist without concrete mitigation yet
- validation is thin but still sufficient for the current scope

Pass when:

- the next workflow can proceed without guessing behavior

## Routing Rules

### Requirement input

Choose `manage-epic` when one or more of these are true:

- more than one independently shippable deliverable exists
- the work spans multiple major layers or domains
- the likely implementation will exceed three phases
- the requirement clearly decomposes into dependent slices

Otherwise choose `create-plan` directly.

If the run mode is `docs-only` and the requirement routes to `manage-epic`:

- create or refresh the epic first
- then generate or refresh all feature plans required by that epic
- stop after plan docs are ready for review
- if decomposition still needs user approval, stop and ask before creating downstream plans

If the run mode is `docs-only` and the requirement routes directly to `create-plan`:

- create or refresh the single feature plan
- stop after plan review

### Epic input

If the run mode is `docs-only`:

- iterate the epic's tracked slices in dependency order
- create or refresh every missing or stale feature plan doc needed for review
- stop after the plan docs are ready for review

If the run mode is `all`, choose the next plan in this order:

1. first `in_progress` plan without a blocking issue
2. first `open` plan whose dependencies are complete
3. if no plan is ready, stop and report why

If the run mode is `all` and the selected feature plan does not exist yet, run `create-plan` for that slice before execution.

### Feature plan input

Run `plan-review` first.

If the run mode is `docs-only`, stop after plan review and any deterministic plan fixes.

If the run mode is `all` and the review passes, run `execute-plan`.

After `all` mode execution, always run `verify` and then `sync` when an epic link exists.

### Plain-text input

Investigation must complete before using plain text as the source of truth.

- `quick` + investigation complete + gate `pass` -> create a minimal inline plan and proceed directly to `execute`
- `standard` -> create or refresh a feature plan doc before execution
- `large` -> create or refresh the requirement, epic, and feature-plan docs before execution

Escalate a plain-text request when:

- the investigator recommends `escalate-to-spec`
- the task is `large`
- the task is `new-feature` with unclear boundaries
- the task is `refactor`, `upgrade`, or `delete` with multi-file impact and no explicit contract

Escalation action: stop execution; surface the missing spec as a blocker; ask the user to provide a requirement doc path or confirm that a new requirement doc should be created — do not proceed to planning or execution.

## Workflow

### 0. Choose mode

Ask the user to choose `docs-only` or `all` unless the mode is already explicit in the prompt.

### 1. Route and classify

Identify the artifact type and linked documents:

- requirement linked to epic
- epic linked to requirement and feature plans
- feature plan linked to requirement or epic via frontmatter — only when the frontmatter field is non-null and the file exists on disk
- plain-text prompt with optional hints, specs, or file paths

Re-read files from disk instead of relying on chat memory.

Then:

- detect `Task Type`
- estimate `Task Size`
- load the first one or two likely code files when that helps confirm scope
- for plain-text input, always defer routing decision to after investigation

### 2. Investigate gaps

For plain-text input, always run investigation before proceeding. For artifact-backed input, run when scope or impact is unclear.

- run `task_investigator` with a read-only packet
- read the report once
- `Recommended Next Step: proceed` and `Unclear` is empty → continue to gate
- `Recommended Next Step: ask-user` or blocking gaps remain → use the investigator's `Questions for User` to ask the user once; treat the answer as final context
- `Recommended Next Step: escalate-to-spec` → stop; report the missing spec as a blocker; ask the user to provide a requirement doc path or confirm a new requirement doc should be created — do not proceed to execution
- `Confidence: low` with non-empty `Unclear` → treat as `ask-user` regardless of the recommended step

### 3. Apply gates

Run the `Task Type Gate` first, then the proportional `Readiness Gate`.

- `fail` -> stop and report the exact missing input
- `warn` in `all` -> continue automatically and report the warning
- `warn` in `docs-only` -> continue unless the warning changes which docs should be generated

### 4. Plan

For requirement-driven work:

- choose `manage-epic` or `create-plan`
- pass only the requirement and direct constraints

For epic-driven work:

- in `docs-only`, generate or refresh all feature plan docs needed for review
- in `all`, select the next ready slice and create or refresh that feature plan when needed

For plain-text work:

- keep `quick` tasks inline
- create the smallest durable artifact that makes the task execution-safe

### 5. Plan review

Skip this step for inline `quick` tasks that intentionally do not create a durable feature plan doc.

Validate that the selected feature plan has:

- a clear goal
- testable acceptance criteria or explicit behavior-preserved contract
- dependency-ordered phases
- concrete file targets
- validation expectations

If the plan fails review, fix the plan before execution or stop with the missing information.

In `docs-only`:

- run plan review on each generated or selected feature plan
- apply deterministic plan-doc fixes when safe
- stop after reporting any remaining warnings for human review

When `spawn_agent` is available, delegate this step to `dev_plan_reviewer` with a read-only packet unless the worker is explicitly allowed to patch the plan.

### 6. Execute

Skip this step entirely in `docs-only`.

Pass only the selected feature plan, linked requirement and epic paths, the relevant acceptance criteria or behavior contract, and the investigator facts that still matter.

Do not execute more than one feature plan at a time.

Keep execution in the primary orchestrator thread unless you later add a dedicated execution agent with a strict single-writer contract.

### 7. Verify

Skip this step entirely in `docs-only`.

Check:

- touched code matches the current plan tasks
- acceptance criteria or preserved behavior are still covered
- validation ran at the smallest useful scope first
- blockers are recorded explicitly when work could not finish

Use `quality-code-check` when lint, type, build, or test work becomes the main task.

When `spawn_agent` is available, delegate the verification summary to `dev_verifier` after execution and validation complete.

### 8. Sync

Skip this step in `docs-only` unless a plan-generation step must update safe cross-links while writing docs.

When `epic_plan` exists:

- update the feature plan status in the epic
- keep the dependency graph accurate when execution order changed
- update the requirement's `Related Plans` section when safe and useful

Status mapping:

- untouched plan -> `open`
- partial completion -> `in_progress`
- explicit blocker -> `blocked`
- all tasks complete -> `completed`

### 9. Failure handling

If execution or verification fails mid-phase:

- keep the feature plan as the source of truth
- mark the next task as blocked with a concise reason
- sync the epic status to `blocked` only when the plan is actually blocked, not merely incomplete
- stop and report the concrete resume point

Do not silently skip to another feature plan.

## Final response

Report:

- run mode used
- input artifact and route chosen
- detected task type and task size
- whether investigation was used
- gates passed, warned, or failed
- files created or updated
- skipped steps
- next resume point
- blockers or assumptions

## Quality Bar

- routing decisions are explainable from repository artifacts
- task type and task size are both explicit before execution
- quick plain-text tasks do not bypass type-specific minimum context
- investigation stays bounded and read-only
- worker context stays bounded
- no implementation begins from an unready plan
- epic and feature-plan status stay aligned when an epic is in play
- standalone planning or execution still works without this orchestrator
- **Clarification limit:** do not ask the user more than two clarification rounds; if the input is still ambiguous after two rounds, stop and report the exact missing information as a blocker
