---
name: manage-epic
description: Use when the user wants to create, update, link, or sync an epic doc in `docs/ai/planning/epic-{name}.md` so one requirement can track multiple feature plans.
---

# Manage Epic

Use this skill to maintain the tracking layer between a requirement and its feature plans.

An epic is intentionally lightweight. It tracks:

- which feature plans belong to a requirement
- the execution order between those plans
- the current status of each plan

Do not put architecture or task-level implementation details in the epic. Those belong in feature plans.

## Inputs

- Requirement doc path: `docs/ai/requirements/req-{name}.md`
- Epic doc path: `docs/ai/planning/epic-{name}.md`
- Optional feature plan path: `docs/ai/planning/feature-{name}.md`

## Required Context

Read these files before editing:

- `docs/ai/planning/epic-template.md`
- `docs/ai/project/CODE_CONVENTIONS.md`
- `docs/ai/project/PROJECT_STRUCTURE.md`

When available, also read:

- linked requirement doc
- linked feature plan docs already listed in the epic

## Compatibility Contract

This skill must work in both orchestration-driven and standalone workflows.

- If a requirement doc does not yet have a `Related Plans` section, add or refresh it when the epic doc exists and has been written to disk.
- If the epic template includes `FR Scope` or `Depends On` columns, populate them.
- If those columns do not exist, preserve the base table shape and encode the same information in the description or dependency graph.
- Never require downstream skills to use the epic. Standalone feature plans remain valid.

## Modes

Infer the mode from the provided artifacts:

| Input | Mode | Action |
|-------|------|--------|
| Requirement doc only | `create` | Create or refresh an epic from the requirement |
| Epic doc only | `update` | Update plan rows, descriptions, or dependency graph |
| Epic doc + feature plan | `link` | Link or refresh one feature plan entry |
| Epic doc + linked feature plans | `sync` | Recompute statuses from the linked plans |

Ask the user a direct question only when the intended mode is genuinely unclear.

## Workflow

### 1. Pre-flight

Derive a concise kebab-case name from the requirement or epic path.

Expected output:

- `docs/ai/planning/epic-{name}.md`

If the epic already exists and will be materially rewritten:

- read it first
- back it up to `docs/ai/planning/archive/epic-{name}_{timestamp}.md`
- then overwrite the main file

### 2. Create mode

Read the requirement doc and extract:

- executive summary
- functional requirements
- implementation guidance
- complexity signals
- open questions that constrain decomposition

Break the requirement into 2-6 feature plans only when the requirement is too large for a single plan.

Prefer grouping by:

- feature area
- dependency order
- clear frontend/backend splits
- independently shippable slices

For each proposed feature plan, capture:

- plan name
- short description
- priority
- mapped FRs when the requirement makes that possible
- dependencies on earlier plans when needed

Ask the user for confirmation only when the breakdown would materially change scope or delivery order.

### 3. Update mode

Preserve all content that does not need to change.

Supported updates:

- add a new feature plan row
- change a plan status
- adjust description or priority
- update the dependency graph
- refresh `FR Scope` or `Depends On` values when those columns exist

### 4. Link mode

When a feature plan is created or refreshed:

1. read the epic doc
2. add or update the row for that feature plan
3. keep the feature plan frontmatter aligned with the epic and requirement paths
4. update the dependency graph only when the new plan changes actual execution order

### 5. Sync mode

Re-read each linked feature plan from disk and derive its epic status from the plan state.

Default mapping:

- has unchecked tasks and no completed tasks yet -> `open`
- has both completed and incomplete tasks -> `in_progress`
- documents an unresolved blocker -> `blocked`
- all implementation tasks complete -> `completed`

If a plan is missing, keep the epic row and mark the issue in the changelog or summary.

When all linked feature plans are `completed`, update the requirement doc to reflect that the requirement is fully planned or implemented when the surrounding workflow tracks that state.

### 6. Cross-linking rules

Only add links when the target file exists.

When creating an epic from a requirement:

- set epic frontmatter `requirement`
- add or refresh a `Related Plans` section in the requirement doc when safe to do so

When linking a feature plan:

- ensure feature plan frontmatter points to the epic and requirement when those docs exist
- keep the feature plan `Related Documents` section aligned with those frontmatter values

### 7. Final response

Report:

- created or updated epic path
- mode used
- feature plans currently tracked
- statuses changed
- any unresolved decomposition questions

## Quality Bar

- the epic stays tracking-focused
- each feature plan row is independently understandable
- dependency order is explicit
- cross-links are accurate
- the workflow still works when feature plans are created outside an epic
