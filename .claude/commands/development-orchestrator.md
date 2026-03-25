---
name: development-orchestrator
description: Route requirement, epic, feature-plan, and plain-text requests across investigation, planning, execution, verification, and sync.
---

## Goal

Provide one Claude Code entry point for planning and implementation orchestration.

This command does not replace `/manage-epic`, `/create-plan`, or `/execute-plan`. It coordinates them.

Core responsibilities:
- route the current artifact to the right workflow
- classify work by task type and task size before coding
- investigate scope before trusting any plain-text prompt
- enforce readiness, review, and verification gates
- sync requirement, epic, and feature-plan state after each run

---

## Workflow Alignment

- Provide brief status updates (1-3 sentences) before and after important actions.
- For medium/large work, create orchestration todos for macro phases: Mode, Route, Investigate, Gate, Plan, Review, Execute, Verify, Sync.
- Keep exactly one orchestration todo `in_progress`.
- Use planning doc checkboxes for implementation task state; use command todos only for orchestration phase state.

---

## Step 0: Select Run Mode

Use `AskUserQuestion` for this step unless the user already selected the mode explicitly in the same request.

Supported modes:
- `docs-only`: generate or refresh all planning docs needed for review, then stop before implementation
- `all`: run the full workflow end to end with no more user questions after this mode selection

Required prompt:

```text
AskUserQuestion(questions=[{
  question: "Which development-orchestrator mode should I run?",
  header: "Run Mode",
  options: [
    { label: "docs-only", description: "Generate or refresh all planning docs for review, then stop before coding" },
    { label: "all", description: "Run investigation, planning, review, execution, verification, and sync in one pass" }
  ],
  multiSelect: false
}])
```

Mode rules:
- In `all`, do not ask follow-up confirmation questions. `warn` auto-continues, `fail` stops.
- In `all`, if scope is still materially ambiguous after investigation, stop and report the blocker instead of asking again.
- In `docs-only`, you may still use `AskUserQuestion` for genuinely blocking clarification, but prefer generating reviewable docs over opening extra Q&A.

---

## Step 1: Route and Classify the Request

### 1a: Detect artifact type

Read the user input and identify one of:
- requirement doc path: `docs/ai/requirements/req-{name}.md`
- epic doc path: `docs/ai/planning/epic-{name}.md`
- feature plan path: `docs/ai/planning/feature-{name}.md`
- plain-text description with no artifact path

Plain-text input is allowed for bug fixes, refactors, and other bounded work. Do not execute it yet — classify task type and task size first, then investigate before trusting it.

If the artifact type or intent is ambiguous:
- in `docs-only`, ask the user with `AskUserQuestion`
- in `all`, keep reading local context first and only stop if ambiguity remains after investigation

`docs-only` prompt:

```text
AskUserQuestion(questions=[{
  question: "Which artifact should I orchestrate?",
  header: "Artifact",
  options: [
    { label: "Requirement", description: "Start from a req doc and plan the work" },
    { label: "Epic", description: "Pick the next feature plan from an epic" },
    { label: "Feature Plan", description: "Work from one feature plan doc" }
  ],
  multiSelect: false
}])
```

### 1b: Load core context

Read:
- `docs/ai/project/CODE_CONVENTIONS.md`
- `docs/ai/project/PROJECT_STRUCTURE.md`
- `docs/ai/planning/README.md`
- the selected artifact when one exists

Then read linked docs as needed:
- requirement linked from epic or feature plan — only when the frontmatter field is non-null and the file exists on disk
- epic linked from requirement or feature plan — same guard
- selected feature plan when routing from an epic
- user-mentioned files, logs, or specs when the request is plain text

### 1c: Detect task type and task size

Classify every run on two independent axes:
- `Task Type`: `new-feature`, `bug-fix`, `refactor`, `upgrade`, or `delete`
- `Task Size`: `quick`, `standard`, or `large`

These axes are independent:
- a bug fix can be `quick` or `large`
- a refactor can be `quick` or `large`
- task size decides document depth
- task type decides minimum context required before execution

Do not treat short plain-text prompts as directly executable. Every task type must pass the investigation step and task-type gate before execution.

### 1d: Normalize routing

Rules:
- If the input is a requirement and it already links to an existing epic, route to the epic flow instead of creating a duplicate epic.
- If the input is an epic and mode is `docs-only`, iterate all tracked slices in dependency order and ensure each reviewable feature plan doc exists.
- If the input is an epic and mode is `all`, choose the next ready feature plan:
  1. first `in_progress` plan without an explicit blocker
  2. else first `open` plan whose dependencies are complete
  3. else stop and report why no plan is ready
- If the input is a feature plan, route directly to plan review.
- If the input is plain text, defer routing decision to after investigation.

---

## Step 2: Investigate

Always run this step for plain-text input before proceeding. For artifact-backed input, run this step when scope or impact is unclear.

### 2a: When to investigate locally vs. use the investigator agent

Investigate locally (read 1–2 files yourself) when:
- the artifact is a well-formed feature plan or requirement doc with clear scope
- the task is single-file and the first likely file confirms full scope

Spawn the investigator agent when any of these are true:
- the input is plain text (always)
- task type is still ambiguous after reading core docs
- the prompt names a symptom but not the owning module
- scope is still unclear after reading one or two likely files
- multi-file or cross-layer impact is likely, especially for `refactor`, `upgrade`, or `delete`
- the user provided spec files, logs, or hint paths that need bounded triage

### 2b: Agent invocation

```text
Agent(
  subagent_type="task-investigator",
  description="Classify task type, inspect likely scope, and surface blocking gaps",
  prompt="Input Artifact: {requirement | epic | feature-plan | plain-text}
Task Type Hint: {detected type or ambiguous}
Task Size Hint: {quick | standard | large}
Goal: {one concrete outcome expected from this run}
Prompt Summary: {concise user request}
Hint Files: {list or none}
Linked Docs: {paths or none}
Known Facts: {facts already confirmed from core context reading}
Blocking Gaps: {items still unclear before investigation}
Stop If: {ambiguity that would materially change implementation}

Return the structured investigation report only."
)
```

Required output shape:

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

### 2c: Interpret the investigation report

Read the report once and act on it immediately:

- `Recommended Next Step: proceed` and `Unclear` is empty → continue to Step 3
- `Recommended Next Step: ask-user` or blocking gaps remain → use the investigator's `Questions for User` to call `AskUserQuestion` once; treat the answer as the final context before proceeding
- `Recommended Next Step: escalate-to-spec` → stop; report the missing spec as a blocker; ask the user to provide a requirement doc path or confirm a new requirement doc should be created before this run can continue — do not proceed to execution
- `Confidence: low` with non-empty `Unclear` → treat as `ask-user` regardless of the recommended step

---

## Step 3: Task Type Gate

Before planning or executing, confirm the minimum required information for the detected task type.

| Type | Minimum required before execute |
| --- | --- |
| `new-feature` | integration point, one existing pattern file or module to follow, and an explicit out-of-scope boundary |
| `bug-fix` | symptom or error description, expected versus actual behavior, and a reproduction path |
| `refactor` | explicit behavior-preserved contract, validation or test coverage plan, and a scope boundary |
| `upgrade` | target dependency or API change, behavior to preserve, and a caller or dependent list |
| `delete` | remove versus disable decision, dependency trace, and the intended safety or rollback boundary |

How to apply the gate:
- use the investigation report as the primary source for these minimums
- if a minimum is still missing after investigation, ask the user once for the remaining blocking gaps
- do not infer or assume missing minimums without investigation evidence

If the task-type gate fails:
- stop
- report the exact missing minimum input

If the task-type gate warns:
- in `all`, continue automatically and include the warning in the final report
- in `docs-only`, continue unless the warning changes which docs should be generated

---

## Step 4: Readiness Gate

Classify the current state as `fail`, `warn`, or `pass` after the task-type gate is satisfied.

### Proportionality

Match required spec depth to task size before applying the gate:
- **Quick task**: single concern, clear outcome, no cross-cutting dependency chain, and a minimal inline plan is sufficient
- **Standard task**: multiple behaviors or files but no epic needed, so a feature plan doc is sufficient
- **Large task**: multi-deliverable, cross-layer, or dependency-ordered slices, so full spec plus epic is required

Apply `fail` / `warn` / `pass` relative to the expected depth for that task size, not against the full spec bar.

### Fail when
- the target artifact cannot be found
- the core behavior or feature boundary is missing
- task-type minimum information is still missing after investigation and user clarification
- no acceptance criteria or behavior contract exist for non-trivial work
- unresolved open questions would materially change implementation

### Warn when
- out-of-scope is missing but the implementation boundary is still clear
- dependency order is implied but not explicit
- risks exist without concrete mitigation yet
- validation is thin but still sufficient for the current scope

### Pass when
- the next workflow can proceed without guessing behavior

If the gate fails:
- stop
- report the exact missing input or ambiguity

If the gate warns:
- in `all`, continue automatically and include the warning in the final report
- in `docs-only`, ask the user only when the warning would change what docs should be generated

---

## Step 5: Planning Route

### 5a: Requirement input

If the requirement already links to an epic on disk:
- switch to epic flow

Otherwise decide size:
- **Large / multi-slice / dependency-heavy** -> Use `Skill(manage-epic)`
- **Small / self-contained** -> Use `Skill(create-plan)`

Use this heuristic for `manage-epic`:
- more than one independently shippable deliverable
- work spans multiple major layers or domains
- likely implementation exceeds three phases
- requirement clearly decomposes into dependent slices

If epic breakdown approval is needed:
1. In `docs-only`, enter plan mode, run `Skill(manage-epic)` to propose and confirm the breakdown, then exit plan mode after approval and write the epic to disk
2. In `all`, stop and report the unresolved breakdown instead of asking another question

Mode-specific behavior:
- In `docs-only`, if the work routes to `manage-epic`, create or refresh the epic and then generate or refresh every feature plan listed in that epic before stopping.
- In `docs-only`, if the work routes directly to `create-plan`, generate or refresh the single feature plan and stop after plan review.
- In `all`, continue past planning into review, execution, verification, and sync.

### 5b: Epic input

If mode is `docs-only`:
- create or refresh every missing or stale feature plan tracked by the epic
- stop after plan review summarizes the generated docs

If mode is `all`:
- if the selected feature plan file does not exist yet, use `Skill(create-plan)` with the epic path so the new plan links back to the epic and requirement
- if the selected feature plan already exists, proceed to plan review

### 5c: Feature plan input

Skip directly to plan review.

Mode-specific behavior:
- `docs-only` -> stop after plan review and any safe plan-doc fixes
- `all` -> continue to execution when review is pass or warn

### 5d: Plain-text input

Investigation must complete (Step 2) before proceeding here.

If task size is `quick` and both gates passed:
- create a minimal inline plan with goal, expected outcome, likely files, validation, and explicit non-goals
- skip durable planning docs
- continue directly to execution in `all`
- stop after presenting the inline plan in `docs-only`

If task size is `standard`:
- create or refresh a feature plan doc before execution

If task size is `large`:
- create or refresh the requirement, epic, and feature-plan docs before execution

Escalate a plain-text request when:
- the investigator recommends `escalate-to-spec`
- the task is `large`
- the task is `new-feature` with unclear boundaries
- the task is `refactor`, `upgrade`, or `delete` with multi-file impact and no explicit contract

Escalation action: stop execution; surface the missing spec as a blocker in the final report; ask the user to provide a requirement doc path or confirm that a new requirement doc should be created — do not proceed to planning or execution.

---

## Step 6: Plan Review

Skip this step for inline `quick` tasks that intentionally do not create a durable feature plan doc.

Use an isolated sub-agent:

```text
Agent(
  subagent_type="dev-plan-reviewer",
  description="Review feature plan readiness",
  prompt="Feature plan: {feature plan path}
Requirement: {req path or none}
Epic: {epic path or none}
Task Type: {detected type}
Task Size: {detected size}
Orchestrator note: {specific concern if any}

Return the concise review summary only."
)
```

Interpret results:
- `fail` -> stop until the plan doc is fixed
- `warn` in `docs-only` -> keep the docs for human review and report the warnings
- `warn` in `all` -> continue automatically
- `pass` in `docs-only` -> stop after the review summary
- `pass` in `all` -> continue to execution

---

## Step 7: Execute

Skip this step entirely in `docs-only`.

Run:

```text
Skill(execute-plan)
```

Pass only bounded execution context:
- selected feature plan path when one exists
- linked requirement path when relevant
- linked epic path when relevant
- relevant acceptance criteria or behavior-preserved contract
- investigation facts that still matter

Rules:
- do not execute more than one feature plan at a time
- keep execution scoped to the selected feature plan or inline quick-task plan

---

## Step 8: Verify

Skip this step entirely in `docs-only`.

Use an isolated sub-agent:

```text
Agent(
  subagent_type="dev-verifier",
  description="Verify execution results",
  prompt="Feature plan: {feature plan path or inline quick-task summary}
Requirement: {req path or none}
Epic: {epic path or none}
Task Type: {detected type}
Changed files: {list from execute phase}
Validation summary: {quality-check output or summary}

Return the concise verification summary only."
)
```

Interpret results:
- `fail` -> stop and report the resume point
- `warn` in `all` -> continue automatically to sync
- `pass` -> continue to sync

---

## Step 9: Sync

In `docs-only`, do not run post-implementation sync. Only keep cross-links accurate while generating planning docs.

When the feature plan frontmatter contains a non-null `epic_plan`:

```text
Skill(manage-epic)
```

Use sync mode and update:
- epic row status
- dependency graph when execution order changed
- requirement `Related Plans` section when useful

Status mapping:
- untouched plan -> `open`
- partial completion -> `in_progress`
- explicit blocker -> `blocked`
- all tasks complete -> `completed`

Skip this step entirely for standalone feature plans with no epic link.

---

## Step 10: Final Response

Report:
- run mode used
- input artifact and route chosen
- detected task type and task size
- whether investigation was used and what it found
- gate result
- files created or updated
- skipped steps
- current feature plan status or review status
- epic sync result when applicable
- next resume point or next command

Recommended next actions:
- `docs-only` result -> review the generated docs, then run `/development-orchestrator` again in `all` mode
- `all` result -> `/development-orchestrator` again to continue the next ready slice
- `/execute-plan` directly only when the user intentionally wants to bypass orchestration

---

## Notes

- Keep user interaction in the command layer. For Claude Code, mode selection and blocking clarification must use `AskUserQuestion`. Do not ask the user questions inside worker agents.
- Worker agents must read `.claude/agents/*`, which in turn read shared `.agents/roles/*` files.
- Do not silently skip from one feature plan to another after a failure.
- The planning doc remains the source of truth for implementation task state.
- **Clarification limit:** Do not ask the user more than two clarification rounds. If the input is still ambiguous after two rounds, stop and report the exact missing information as a blocker.
