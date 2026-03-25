---
phase: planning
title: Planning Documentation
description: Feature planning docs and workflow guidelines
---

# Planning Documentation

## Purpose
This directory contains planning documents for both epics and individual features.

- `epic-{name}.md`: tracking doc that links one requirement to multiple feature plans
- `feature-{name}.md`: implementation-focused plan with phases, tasks, and pseudo-code

## Feature Planning Workflow

### Starting from a Requirement
- Small or self-contained requirement: use `create-plan`
- Large requirement with multiple slices or dependencies: use `manage-epic` first, then create feature plans under that epic
- If you want one entry point that routes planning and execution for you, use `development-orchestrator`
- `development-orchestrator` now starts by selecting a run mode:
  - `docs-only`: generate or refresh the planning docs needed for review, then stop before implementation
  - `all`: run planning, review, implementation, verification, and sync in one pass
  - Before execution, it also detects both task type (`new-feature`, `bug-fix`, `refactor`, `upgrade`, `delete`) and task size (`quick`, `standard`, `large`)
  - Plain-text requests are no longer executed purely because they look small; they must first pass the task-type gate
  - Ambiguous or likely multi-file work can trigger a bounded investigation step before planning or coding

### Creating a Feature Plan
Use the `create-plan` command to generate a new feature plan:
- Command: Available in `.cursor/commands/`, `.claude/commands/`, or `.github/prompts/`
- Output: `docs/ai/planning/feature-{name}.md`
- Template: `docs/ai/planning/feature-template.md`

### Creating an Epic
Use the `manage-epic` workflow when a requirement needs multiple feature plans:
- Output: `docs/ai/planning/epic-{name}.md`
- Template: `docs/ai/planning/epic-template.md`
- Purpose: track plan breakdown, dependencies, and execution status

### Feature Plan Structure
Each feature plan follows the template structure with 5 sections:

1. **Goal & Acceptance Criteria**: Objectives, scope, and Given-When-Then format
2. **Risks & Assumptions**: Key risks and assumptions to be aware of
3. **Definition of Done**: Completion criteria (build/test/review/docs)
4. **Implementation Plan**:
   - Summary of solution approach
   - Phases with detailed tasks and pseudo-code
5. **Follow-ups**: TODOs or deferred work

### What Makes a Good Plan?
A good plan helps both humans and AI agents understand:
- **For humans**: What problem we're solving, why, and how
- **For AI agents**: Exactly what files to change, what logic to implement, and in what order

The plan should be:
- Clear enough for a different AI agent to execute independently
- Detailed enough with pseudo-code to guide implementation
- Concise enough to avoid information overload

### From Plan to Execution
- After the plan is written, use the `execute-plan` command to begin implementation
- The AI agent will read the plan and implement tasks phase by phase
- Tasks are tracked with checkboxes `[ ]` → `[x]` as they complete
- Do not start coding until the plan is reviewed and agreed upon
- If an epic exists, keep epic status in sync with feature-plan progress

### Feature Plan Naming Convention
- Format: `feature-{name}.md` (kebab-case)
- Example: `feature-user-authentication.md`
- If duplicate name exists, append suffix: `feature-{name}-2.md`

## Template Reference
See `epic-template.md` and `feature-template.md` for the exact structure required for planning docs.

## Related Documentation
- Test plans: `../testing/`
- Project standards: `../project/`

---

**Note**: For project-level planning (milestones, phases, timelines), use a separate project planning document outside this directory structure.
