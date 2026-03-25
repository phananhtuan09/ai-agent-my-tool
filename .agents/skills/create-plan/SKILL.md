---
name: create-plan
description: Use when the user asks to create, refresh, or update a feature planning doc in `docs/ai/planning/feature-{name}.md`, including goal, acceptance criteria, risks, phased tasks, and implementation details.
---

# Create Plan

Use this skill to produce a complete planning doc that fits this repository's workflow.

## Inputs

- A feature request, bug scope, or implementation brief
- Optional requirement doc: `docs/ai/requirements/req-{name}.md`
- Optional epic doc: `docs/ai/planning/epic-{name}.md`
- Optional design source: Figma URL, screenshot, mockup, or written design notes

## Codex Tool Mapping

- Claude `Read/Edit/Write` -> inspect files with shell tools and edit with `apply_patch`
- Claude `AskUserQuestion` -> ask the user directly only when a wrong assumption would materially change scope
- Claude `Task(Explore)` -> explore the repo directly with `rg`, `rg --files`, `find`, `sed`, and parallel shell reads
- Background task patterns -> use `multi_tool_use.parallel` only for independent reads

## Workflow

### 1. Load required context

Read these files first:

- `docs/ai/planning/feature-template.md`
- `docs/ai/project/CODE_CONVENTIONS.md`
- `docs/ai/project/PROJECT_STRUCTURE.md`

If the user supplied a requirement doc, read it.

If the user supplied an epic doc:

- read the epic doc first
- read its linked requirement doc if present
- capture any tracked row metadata such as `FR Scope` and `Depends On`
- plan to set feature-plan frontmatter `epic_plan` and `requirement`

### 2. Normalize scope

Infer as much as possible from the prompt and repository context.

Ask the user a concise question only if one of these is still unclear and risky:

- the core feature boundary
- the primary user flow
- a required external dependency or API
- the source of truth when multiple design sources conflict

When a requirement doc exists, map it into the plan instead of re-asking:

- Problem Statement and User Stories -> Goal
- Business Rules and Functional Requirements -> Implementation Plan
- Non-Functional Requirements and Edge Cases -> Risks and Assumptions
- Acceptance Criteria -> Acceptance Criteria
- Out of Scope -> Follow-ups

### 3. Research the codebase

Explore existing patterns before drafting the plan.

Look for:

- similar features
- reusable components, hooks, services, or utilities
- naming and file placement patterns
- validation, error handling, and testing conventions

Keep only actionable findings. If nothing useful exists, omit the `Codebase Context` section.

### 4. Resolve design input

If the user supplied a Figma URL, treat design extraction as a separate phase.

Derive the expected file:

- `docs/ai/requirements/figma-{name}.md`

Then:

- if the file exists and `status: complete`, read it and use it for `2a. Design Specifications`
- if the file exists and `status: partial`, warn that specs are incomplete and proceed only with available data
- if the file does not exist, tell the user to run `/extract-figma {url} {name}` first instead of guessing design values

If the user already supplied screenshots or detailed design notes, use those directly and skip theme generation.

If the task is UI-heavy and no design source exists, use the minimal relevant design skills:

- `frontend-design-fundamentals`
- `frontend-design-theme-factory`
- `frontend-design-responsive`

Only include one design section in the plan:

- `2a. Design Specifications`
- `2b. Theme Specification`

Never include both.

### 5. Derive the feature name and output path

Create a concise kebab-case feature name from the prompt and loaded context.

Output path:

- `docs/ai/planning/feature-{name}.md`

If the file already exists:

- create `docs/ai/planning/archive/` if needed
- back up the existing file to `docs/ai/planning/archive/feature-{name}_{timestamp}.md`
- then overwrite the main file

### 6. Draft the plan

Follow `docs/ai/planning/feature-template.md` closely.
The plan must be written in English.

Include:

1. `Related Documents` only when a requirement or epic exists
2. `Codebase Context` only when research found something concrete
3. `Design Specifications` or `Theme Specification` when applicable
4. `Goal & Acceptance Criteria`
5. `Risks & Assumptions`
6. `Definition of Done`
7. `Implementation Plan`
8. `Follow-ups`

Related-doc and frontmatter rules:

- if standalone, set `requirement: null` and `epic_plan: null`, then omit `Related Documents`
- if only a requirement exists, link it and leave `epic_plan: null`
- if epic context exists, link both docs and align the plan with the epic row metadata when that table tracks `FR Scope` and `Depends On`

Implementation Plan rules:

- use one phase for small work with 5 tasks or fewer
- use 2-3 phases for medium work with 6-12 tasks
- use 3-5 phases for larger work
- each task must use checkbox format: `[ ] [ACTION] path/to/file - Summary`
- `ACTION` must be one of `ADDED`, `MODIFIED`, `DELETED`, `RENAMED`
- add structured pseudo-code under each task when it changes behavior

Pseudo-code should cover:

- function or endpoint signature
- input validation with concrete constraints
- logic flow
- return shape for success and failure
- edge cases
- dependencies

### 7. Update linked docs when needed

If an epic doc is linked and it clearly tracks feature plans, add or update the new plan entry there.

When the epic uses the newer table shape, also refresh:

- status -> `open`
- `FR Scope`
- `Depends On`

Preserve the existing table shape when the epic still uses the older schema.
Do not modify unrelated docs.

### 8. Final response

Report:

- the created or updated plan path
- the feature name
- phase count and phase names
- any assumptions that materially shaped the plan
- any archive path created when an existing plan was replaced

## Quality Bar

- Keep the plan implementation-focused, not a restatement of requirements
- Prefer concrete file targets over vague work items
- Keep phases dependency-ordered
- Avoid speculative future work outside current scope
- Match existing repository patterns whenever they exist
- Use pre-extracted Figma docs instead of ad-hoc design guessing
