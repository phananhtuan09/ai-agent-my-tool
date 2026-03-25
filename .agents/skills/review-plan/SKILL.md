---
name: review-plan
description: Use when the user asks to review a feature planning doc before implementation for clarity, completeness, logic, project alignment, and AI executability.
---

# Review Plan

Use this skill to review a planning doc before implementation starts.
The goal is to catch ambiguity, missing scope, broken logic, or project misalignment before an AI agent writes code.

## Inputs

- A planning doc path, usually `docs/ai/planning/feature-{name}.md`
- Optional related docs referenced by the plan

## Codex Tool Mapping

- Claude `Read/Glob/Grep` -> inspect files with `rg`, `rg --files`, `find`, and `sed`
- Claude review-only agent behavior -> do not edit implementation code unless the user explicitly asks
- Independent file reads -> use `multi_tool_use.parallel` only for parallel reads

## Workflow

### 1. Load the plan and required context

Read these files first:

- the target planning doc
- `docs/ai/project/CODE_CONVENTIONS.md`
- `docs/ai/project/PROJECT_STRUCTURE.md`

If the plan links to a requirement doc, epic doc, or design source that materially affects the review, read only the specific linked files needed to judge correctness.

### 2. Review with an implementation mindset

Assume the next AI agent will implement the plan literally.
Focus on whether the plan is executable, not whether it is nicely formatted.

Check whether:

- the intended behavior is unambiguous
- edge cases and failure states are defined
- file targets and architecture choices fit the repository
- task order and dependencies are technically sound
- the plan is specific enough that an AI agent will not guess

### 3. Evaluate the five critical criteria

#### 1. Clarity

Ask:

- Can I tell exactly what needs to be built?
- Are any terms vague, overloaded, or open to interpretation?
- Would two implementers build the same thing from this plan?
- Are user flows, states, and edge cases explicit?

Red flags:

- "Handle errors appropriately"
- "Similar to existing feature" without naming the source
- "Support various formats" without listing them
- missing details on state transitions, validations, or UX behavior

#### 2. Completeness

Ask:

- Does the plan cover happy path and unhappy paths?
- Are validation rules, dependencies, and failure modes included?
- Is any requirement implied but not described?
- Are there missing pieces that would block implementation?

Red flags:

- only the happy path is described
- no error handling strategy
- missing validation rules
- unclear edge-case behavior
- unstated dependencies or prerequisites

#### 3. Project Context Alignment

Compare against:

- `docs/ai/project/CODE_CONVENTIONS.md`
- `docs/ai/project/PROJECT_STRUCTURE.md`

Ask:

- Does the plan reuse existing patterns before inventing new ones?
- Are file paths and ownership boundaries consistent with the repo?
- Does naming match existing conventions?
- Does it avoid duplicating utilities or components that likely already exist?

Red flags:

- introducing new patterns with no justification
- file placement that conflicts with project structure
- ignoring reusable existing modules
- inconsistent naming or architecture boundaries

#### 4. Logic Soundness

Ask:

- Does the technical flow make sense end to end?
- Are task dependencies ordered correctly?
- Are there race conditions, missing state transitions, or security gaps?
- Do data flow, error handling, and persistence behavior hold together?

Red flags:

- a step depends on code or data not created yet
- missing state-management considerations
- external calls without failure handling
- unsafe validation, auth, or sanitization assumptions
- architecture that does not fit the expected scale or lifecycle

#### 5. AI Executability

Ask:

- Are instructions concrete enough for an AI agent to implement without guessing?
- Are pseudo-code blocks specific on inputs, outputs, and logic flow?
- Does each task have clear success criteria?
- Would any task require human judgment that the plan never resolves?

Red flags:

- "Implement similar to X" without stating which behavior matters
- abstract pseudo-code with key branches omitted
- missing input or output contracts
- vague acceptance criteria
- steps that depend on unstated product decisions

### 4. Produce an actionable verdict

Prefer concrete findings over general commentary.
If the plan is weak, identify the exact section or task causing risk and suggest how to fix it.
If the plan is strong, still call out any residual risks or assumptions.

## Output Format

Use this structure:

```markdown
## Plan Review: {feature-name}

### Verdict
**Status**: Ready to Execute | Needs Clarification | Not Ready
**Confidence**: High | Medium | Low

### 1. Clarity Assessment
**Score**: Clear | Some Ambiguity | Too Vague
[Specific findings]

### 2. Completeness Assessment
**Score**: Complete | Gaps Found | Major Missing Pieces
[Specific findings]

### 3. Project Context Alignment
**Score**: Aligned | Minor Deviations | Misaligned
[Specific findings]

### 4. Logic Soundness
**Score**: Sound | Minor Issues | Flawed Logic
[Specific findings]

### 5. AI Executability
**Score**: Executable | Risky Areas | Likely Misimplementation
[Specific findings]

### Critical Issues (Must Fix)
1. [Issue] -> [Suggested fix]

### Warnings (Should Fix)
1. [Issue] -> [Suggested fix]

### Suggestions (Nice to Have)
1. [Improvement idea]

### Recommendation
[Proceed / revise specific sections / major rework needed]
```

If a section has no findings, state that explicitly instead of leaving it empty.
If there are no critical issues, say `None`.

## Quality Bar

- Review behavior and implementation readiness, not markdown formatting
- Be specific enough that the author can revise the plan directly
- Treat ambiguity as implementation risk
- Prefer file or section references when available
- Do not invent missing requirements; flag them as gaps
