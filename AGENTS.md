# AI Agent Workflow Standards

## Core Coding Philosophy

### 1. Simplicity First (with Strategic Exceptions)
- **Default: Keep it simple**
  - Choose simplest solution that meets requirements
  - Avoid over-engineering and unnecessary abstractions
  - Don't build for hypothetical futures

- **Readability > Cleverness**
  - Prefer clear, readable code over clever one-liners
  - Code is read more often than written - optimize for understanding
  - If code needs a comment to explain what it does, consider rewriting it

- **Think ahead ONLY for:**
  - **Security**: Input validation, authentication, authorization
  - **Performance**: Scalability bottlenecks, query optimization
  - All other cases -> Choose simplicity

- **Examples:**
  - Use array methods instead of custom loops
  - Add input validation for user data (security)
  - Consider pagination for large datasets (performance)
  - Don't create abstractions for one-time operations
  - Don't write clever one-liners that require mental parsing

### 2. Deep Understanding
- If unclear about requirements, edge cases, or expected behavior -> Ask first
- Batch related questions into a single block when possible
- Never assume or guess when clarification is cheap and risk is high
- Key questions:
  - "What should happen when X occurs?"
  - "Is this the expected flow: A -> B -> C?"

### 3. Multiple Options When Appropriate
- Present 2-3 solution options with clear trade-offs when there is no obvious best choice
- Format: "Option 1: [approach] - Pros: [...] Cons: [...]"
- Let the user choose based on priorities

## Workflow Guidelines

**Tooling:**
- Prefer semantic search when available; grep/ripgrep for exact matches only
- Run independent operations in parallel when tools allow it
- Search for files matching patterns when exploring the codebase
- Search content for patterns when looking for specific code

**Communication:**
- Use Markdown minimally; backticks for `files/functions/classes`
- Mirror the user's language; code/comments in English
- Give short status updates before and after key actions

**Code Presentation:**
- Existing code: `startLine:endLine:filepath`
- New code: fenced blocks with language tag

**TODO Management:**
- Create todos for medium/large tasks (<=14 words, verb-led)
- Keep ONE `in_progress` item only
- Update immediately; mark completed when done

## Planning and Execution

### Planning First
- For non-trivial work, create or update a plan before coding
- Plans should include:
  - Goal and scope
  - Acceptance criteria
  - Risks and assumptions
  - Implementation phases or ordered tasks
  - Definition of done

### Execution Discipline
- Implement from the plan instead of improvising broad changes
- Keep edits small, reviewable, and aligned with acceptance criteria
- Update planning docs as work progresses
- Avoid speculative work outside the agreed scope

### Validation
- Run the smallest useful validation first
- Prefer project-native checks: lint, typecheck, build, focused tests
- Report failures clearly before attempting broad refactors

## Skills

Skills provide specialized guidance for recurring task types. Use them when the task clearly matches their scope.

### Skill Discovery
- Codex-native skills live in `.agents/skills/`
- Compatibility mirrors may also exist in `.claude/skills/`, `.opencode/skill/`, or `.factory/skills/`
- Prefer `.agents/skills/` as the primary source for Codex-oriented workflows

### How to Use Skills
- Use a skill when the user explicitly names it or the task strongly matches its description
- Use the minimal set of skills needed for the task
- Read only enough of each skill to perform the task correctly
- Load referenced files only when needed; avoid bulk-loading entire skill trees
- If a skill cannot be applied cleanly, state the issue briefly and continue with the best fallback

### Available Skill Triggers

| Skill | Trigger Keywords |
|-------|------------------|
| `brainstorm-partner` | brainstorm, vague idea, hard bug, unclear logic, break down problem, explore options |
| `frontend-design-fundamentals` | UI, frontend, component, styling, CSS, layout, button, form, card, page |
| `frontend-design-responsive` | responsive, mobile, tablet, breakpoints, multi-device, touch |
| `frontend-design-theme-factory` | theme, color palette, colors, fonts, brand, aesthetic |
| `frontend-design-figma-extraction` | Figma, design file, mockup, Figma URL |
| `create-plan` | create plan, planning doc, feature plan, implementation plan |
| `manage-epic` | epic, manage epic, break into feature plans, sync epic |
| `development-orchestrator` | development orchestrator, route planning, planning workflow, implementation workflow, implement this requirement, start development from req, build from req file, end-to-end planning |
| `execute-plan` | execute plan, implement plan, resume plan, phase execution |
| `prompt-leverage` | $prompt-leverage, refine prompt, normalize request, execution brief, reusable prompt |
| `react-best-practices` | React, Next.js, performance, async, Suspense, rendering, bundle |
| `quality-code-check` | lint, type check, build, validation, eslint, tsc |
| `test-web-orchestrator` | test web orchestrator, web ui test, browser test, playwright e2e, cypress e2e, ui automation, figma-driven test |
| `ux-feedback-patterns` | loading, error, form validation, async, toast, empty state |
| `ux-accessibility` | accessible, WCAG, keyboard, screen reader, ARIA, contrast |

## Repository Conventions

- `docs/ai/planning/`: epic tracking docs, feature plans, and execution checklists
- `docs/ai/requirements/`: requirement discovery docs
- `docs/ai/testing/`: unit/integration/web test plans and results
- `docs/ai/project/`: repository-wide standards and structure

When working in this repository:
- Read the relevant planning or requirement doc before implementing
- Follow `docs/ai/project/CODE_CONVENTIONS.md`
- Follow `docs/ai/project/PROJECT_STRUCTURE.md`
- Keep workflow docs updated when behavior changes
