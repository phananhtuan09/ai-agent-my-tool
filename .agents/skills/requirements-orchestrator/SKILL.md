---
name: requirements-orchestrator
description: Use when the user wants to clarify a feature request into requirement docs, coordinate BA/SA/Researcher/UI/UX sub-work, and produce `docs/ai/requirements/req-{name}.md` plus agent artifacts.
---

# Requirements Orchestrator

Use this skill to turn a vague or partial feature request into a structured requirement package in `docs/ai/requirements/`.

Operate as a requirement team lead. Your job is to decide which specialist roles to invoke, pass each one only the context it needs, collect their outputs, resolve conflicts, and publish one consolidated requirement doc.

## Inputs

- A feature request, bug scope, or product idea
- Optional existing requirement doc: `docs/ai/requirements/req-{name}.md`
- Optional design notes, screenshots, or external references
- Optional tech constraints: existing stack, performance budget, timeline, or deployment limits
- Optional related artifacts: Figma frame paths, epic path, API documentation links

## Required Context

Read these files before drafting or delegating work:

- `docs/ai/requirements/req-template.md`
- `docs/ai/project/CODE_CONVENTIONS.md`
- `docs/ai/project/PROJECT_STRUCTURE.md`

Read these templates when producing or validating role outputs:

- `docs/ai/requirements/templates/ba-template.md`
- `docs/ai/requirements/templates/sa-template.md`
- `docs/ai/requirements/templates/research-template.md`
- `docs/ai/requirements/templates/uiux-template.md`

## Role Definitions

Role prompts live in:

- `.agents/roles/requirement-ba.md`
- `.agents/roles/requirement-sa.md`
- `.agents/roles/requirement-researcher.md`
- `.agents/roles/requirement-uiux.md`

Load only the roles needed for the current request.

## Team Lead Contract

The orchestrator is responsible for:

- selecting the minimal role set from the user prompt
- creating a small handoff package for each role instead of forwarding full working memory
- choosing parallel versus sequential execution from the dependency graph below
- collecting role outputs from files, not from transient chat summaries
- resolving contradictions before writing the final requirement doc

Treat each role as a worker with its own bounded context. If Codex multi-agent is available, spawn real sub-agents. If it is not available, simulate the same worker boundary yourself by following the role file and restricting yourself to that role's declared inputs and outputs while producing its artifact.

## Codex Multi-Agent Contract

This repository registers named Codex agents in `.codex/config.toml`.

Use these exact agent names when `spawn_agent` is available:

- `requirement_ba`
- `requirement_sa`
- `requirement_researcher`
- `requirement_uiux`

Delegation rules:

- Prefer real sub-agents over solo simulation when `spawn_agent` is available.
- Spawn only the agents selected by the routing logic in this skill.
- Keep the orchestrator as the only writer of the final consolidated requirement doc.
- Worker agents may write only their own role artifact.
- Wait for spawned workers to finish before consolidating.
- If a spawn fails, retry once with a tighter packet. If it still fails, continue solo and preserve the same handoff boundaries.

## Codex Tool Mapping

- Claude `Read/Edit/Write` -> inspect with shell tools and edit with `apply_patch`
- Claude `AskUserQuestion` -> ask the user directly only when a wrong assumption would materially change scope
- Claude `Task(...)` -> use Codex multi-agent or role-based parallel work when available; otherwise execute the role workflows yourself in sequence
- Claude background tasks -> use `multi_tool_use.parallel` only for independent reads, not for file edits

## Workflow

### 1. Pre-flight

Derive a concise kebab-case feature name from the prompt.

Expected outputs:

- `docs/ai/requirements/agents/ba-{name}.md`
- `docs/ai/requirements/agents/sa-{name}.md`
- `docs/ai/requirements/agents/research-{name}.md`
- `docs/ai/requirements/agents/uiux-{name}.md`
- `docs/ai/requirements/req-{name}.md`

If `docs/ai/requirements/req-{name}.md` already exists:

- read it first
- decide whether to refresh, extend, or review in place
- back it up to `docs/ai/requirements/archive/req-{name}_{timestamp}.md` before overwriting

### 2. Analyze the request

Classify the request on four axes:

- Feature type: `UI`, `API`, `Data`, or `Full-stack`
- Complexity: `Simple`, `Medium`, or `Complex`
- Domain research needed: yes or no
- UI/UX design needed: yes or no

Choose the role set with this routing matrix:

| Prompt Signal | Required Roles |
|---------------|----------------|
| Any feature request | BA + SA |
| Domain jargon, compliance, standards, or unfamiliar external service | BA + SA + Researcher |
| Screens, forms, dashboards, flows, navigation, states, or user-facing interactions | BA + SA + UI/UX |
| Both research and UI concerns | BA + SA + Researcher + UI/UX |

Do not ask the user which roles to run unless the prompt is ambiguous enough that the product boundary itself is unclear.

### 3. Run BA first

Load `.agents/roles/requirement-ba.md`.

Produce `docs/ai/requirements/agents/ba-{name}.md`.

The BA output is the source of truth for:

- problem statement
- users and user stories
- functional requirements
- business rules
- out-of-scope items
- open questions

Ask the user concise follow-up questions only when a wrong assumption would change scope, user flow, or acceptance criteria.

Cap at two clarification rounds. After two rounds, mark remaining unknowns as `[ASSUMPTION]` and continue.

### 4. Re-evaluate role selection after BA

After reading `docs/ai/requirements/agents/ba-{name}.md`, re-check whether downstream roles are needed.

Escalate to `Researcher` if BA reveals:

- unfamiliar domain terminology
- compliance, legal, policy, or standards-sensitive language
- external APIs, services, or libraries that need source verification
- feasibility questions caused by incomplete domain knowledge

Escalate to `UI/UX` if BA reveals:

- screens, pages, dashboards, forms, or tables
- step-by-step flows or navigation concerns
- error, empty, loading, success, or validation states needing definition
- role-specific user journeys

The post-BA decision overrides the initial prompt-only routing matrix.

### 5. Build role handoff packages

Before invoking any worker, prepare a minimal input package.

Every packet must include:

- `Role`: exact Codex agent name
- `Feature Name`: kebab-case feature identifier
- `Goal`: one concrete outcome
- `Allowed Writes`: exact artifact path for that worker
- `Required Reads`: exact file paths the worker should load first
- `Inputs`: only the facts, paths, and answers needed for this role
- `Non-Goals`: explicit out-of-scope items
- `Stop If`: ambiguity that would materially change scope or output correctness

#### BA handoff

- `Role`: `requirement_ba`
- original user prompt
- existing requirement doc if present
- any direct user answers gathered during clarification

#### SA handoff

- `Role`: `requirement_sa`
- BA output path
- project standards paths
- short note listing areas that need feasibility focus

#### Researcher handoff

- `Role`: `requirement_researcher`
- BA output path when available
- exact terms, standards, libraries, or APIs to research
- short note explaining why research is needed

#### UI/UX handoff

- `Role`: `requirement_uiux`
- BA output path
- SA output path when available
- any design notes or screenshots
- short note listing the flows or screens that need definition

Each worker should receive only its handoff package plus its role definition.

### 6. Execute the dependency graph

Use this DAG:

1. BA runs first.
2. After BA completes, SA always runs.
3. Researcher may run in parallel with SA because both depend only on BA output.
4. UI/UX runs after SA when technical constraints matter. If the UI request is trivial and SA adds no relevant constraint, UI/UX may run after BA, but prefer BA -> SA -> UI/UX.
5. Consolidation runs only after all selected worker outputs are complete.

Execution strategy:

- if `spawn_agent` is available, use the named agents from the Codex Multi-Agent Contract
- spawn `requirement_ba` first and wait for its artifact before deciding downstream work
- after BA, spawn `requirement_sa`
- when research is selected, spawn `requirement_researcher` in parallel with `requirement_sa`
- when UI/UX is selected, prefer spawning `requirement_uiux` after SA completes unless the BA artifact is sufficient and SA adds no relevant constraint
- if `spawn_agent` is not available, execute the same DAG serially while preserving the same handoff boundaries
- do not invent extra worker roles unless the user explicitly asks for them

Produce only the files that apply. Do not create placeholder docs for skipped roles.

### 7. Collect worker results

The orchestrator must read worker artifacts from disk and build a consolidation summary with:

- roles executed
- outputs created
- key decisions per role
- blockers per role
- open questions per role
- follow-on role signals discovered by BA
- contradictions across roles

Do not rely on memory of intermediate reasoning. Use the files as the source of truth.

### 8. Resolve conflicts

Compare role outputs before consolidation.

Look for:

- BA requirement marked must-have but SA says not feasible
- Research guidance that changes BA language or SA approach
- UI proposals that conflict with technical constraints
- missing acceptance criteria, missing edge cases, or contradictory assumptions

When the conflict materially changes scope or implementation, ask the user a direct question. Otherwise, resolve it in favor of the most concrete project constraint and record the assumption.

### 9. Consolidate final requirement

Create `docs/ai/requirements/req-{name}.md` using `docs/ai/requirements/req-template.md`.

The final requirement must:

- be written in English
- include the `Quick Links` table with all four agent rows from the template
- mark each row as `✅ Complete` or `⏭️ Skipped`
- link produced role documents and keep skipped ones visibly marked instead of deleting rows
- synthesize instead of copying sections blindly
- convert unresolved gaps into explicit open questions
- derive acceptance criteria in testable language
- include technical risks and edge cases when known

Use the following fan-in mapping:

| Final Section | Source of Truth |
|---------------|-----------------|
| Problem Statement, Users, User Stories, Functional Requirements, Business Rules, Out of Scope | BA |
| Technical Assessment, Risks, Edge Cases, Suggested Phases | SA |
| Glossary, Compliance, Standards, External References | Researcher |
| Screen Inventory, Flows, Wireframes, Interaction Patterns | UI/UX |

If two workers disagree, document the chosen direction and the reason in `Open Questions` or the relevant section.

### 10. Final response

Report:

- created or updated file paths
- which roles were executed versus skipped
- major assumptions
- unresolved questions or blockers

## Output Rules

- Keep agent docs focused on their own role; avoid repeating full content from another role
- Every worker artifact must end with a short `Handoff Summary` section covering decisions, blockers, and open questions
- Prefer concrete tables and checklists over vague prose
- Keep naming consistent across BA, SA, Researcher, UI/UX, and final requirement docs
- When browsing is needed for domain research, cite sources in the research artifact

## Quality Bar

- The selected roles clearly match the prompt
- Worker execution order follows the dependency graph
- Each worker used only bounded context from its handoff package
- Requirement scope is clear enough to plan implementation
- Functional requirements are testable
- Technical feasibility is addressed
- Open questions are explicit rather than hidden in prose
- Output files follow the templates closely without leaving template placeholders behind
