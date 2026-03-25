---
name: generate-standards
description: Generates/updates code convention and project structure docs from the codebase.
---

## Goal

Generate or update `docs/ai/project/CODE_CONVENTIONS.md` and `PROJECT_STRUCTURE.md` from the current codebase with brief Q&A refinement.

## Step 1: Detect Project Context

**Tools:**
- Glob(pattern="**/package.json")
- Glob(pattern="**/pyproject.toml")
- Glob(pattern="**/*.config.{js,ts}")
- Read(file_path=...) for each config file found

Detect project languages/frameworks/libraries from repository metadata:

- Analyze `package.json`, `pyproject.toml`, lockfiles, config files
- Identify primary languages (JavaScript/TypeScript, Python, etc.)
- Identify frameworks (React, Vue, Angular, etc.)
- Identify libraries and tooling (ESLint, Prettier, testing frameworks, etc.)
- Note any build tools or bundlers in use
- **Detect test framework/library:**
  - JavaScript/TypeScript: Vitest, Jest, Mocha, Jasmine, Ava, Tape, etc.
  - Python: pytest, unittest, nose2, etc.
  - Other languages: detect from config files or dependencies
  - Check for test config files: `vitest.config.*`, `jest.config.*`, `pytest.ini`, etc.

**Error handling:**
- No config files found: Ask user for project type manually
- Invalid JSON/TOML: Skip broken file, continue with others
- Multiple conflicting configs: Prioritize root-level files

**Output**: The detected project context will be written to `CODE_CONVENTIONS.md` as the foundation for code conventions.

## Step 2: Clarify Scope (3–6 questions max)

**Tool:** AskUserQuestion(questions=[...])

Quick classification and targeted questions:

- Languages/frameworks detected: confirm correct? (a/b/other)
- Import/style tools in use: (a) ESLint/Prettier (b) Other formatter (c) None
- Test placement preference: (a) Colocated `*.spec.*` (b) `__tests__/` directory (c) Other
- Error handling strategy: (a) Exceptions/try-catch (b) Result types (c) Other
- Module organization: (a) By feature (b) By layer (c) Mixed
- Any performance/security constraints to encode? (yes/no, brief)

Keep questions short and single-purpose. Stop once sufficient info gathered.

**Error handling:**
- User skips questions: Use detected defaults from Step 1 only
- Conflicting answers: Ask follow-up clarification
- Max 2 retry attempts before proceeding with defaults

## Step 3: Auto-Discovery

**Tool:** Task(
  subagent_type='Explore',
  thoroughness='medium',
  prompt="Analyze codebase to discover:
    - Naming conventions (variables, functions, classes, constants)
    - Import patterns and ordering style
    - Folder structure organization (feature/layer/mixed)
    - Test file locations and naming patterns
    - Common architectural patterns (Repository, Factory, Strategy, etc.)
    Return concise summary with 2-3 examples for each category."
)

Analyze repository to infer:

- Dominant naming patterns:
  - Variables/functions: camelCase/PascalCase/snake_case
  - Classes/types: PascalCase
  - Constants: CONSTANT_CASE/UPPER_SNAKE_CASE
- Import patterns:
  - Import order (node/builtin, third-party, internal)
  - Grouping style
- Typical folder structure:
  - Organization under `src/` (by feature/by layer/mixed)
  - Common directories (components/, utils/, services/, etc.)
- Test file locations/naming if present:
  - Unit tests: `tests/unit/*.spec.ts` or `tests/unit/*.test.ts`
  - Integration tests: `tests/integration/*.e2e.spec.ts`
  - Web tests: `tests/web/*.spec.ts`
  - Test docs: `docs/ai/testing/unit-{name}.md`, `integration-{name}.md`, and `web-{name}.md`
- Common patterns observed:
  - Repository/Service patterns
  - Factory patterns
  - Strategy patterns
  - Other architectural patterns

**Error handling:**
- Explore agent timeout: Fallback to quick Grep-based pattern detection
- No patterns found: Generate minimal standards template
- Inconsistent patterns: Document most frequent pattern as primary

## Step 4: Draft Standards

**Tools:**
- Glob(pattern="docs/ai/project/template-convention/*.md") to find templates
- Read(file_path=...) for each matching template
- Write(file_path="docs/ai/project/CODE_CONVENTIONS.md")
- Write(file_path="docs/ai/project/PROJECT_STRUCTURE.md")

Generate two documents:

### CODE_CONVENTIONS.md

**Content order** (see Notes for template matching details):
1. Project context from Step 1
2. User preferences from Step 2
3. Auto-discovered rules from Step 3
4. Matching templates (merged and applied on top)

**Sections to include:**
- Naming conventions (variables, functions, classes, constants)
- Import order and grouping
- Formatting tools (ESLint/Prettier/etc.) if detected
- Function size and complexity guidelines
- Error handling strategy (exceptions/result types)
- Test rules (unit first, integration when needed)
- Comments policy (only for complex logic)
- Async/await patterns if applicable

### PROJECT_STRUCTURE.md

**Sections to include:**
- Folder layout summary (`src/`, `docs/ai/**`, etc.)
- Module boundaries and dependency direction
- Design patterns actually observed in codebase
- Test placement and naming conventions
- Config/secrets handling summary
- **Test Configuration section** (critical for `/writing-test`, `/writing-integration-test`, `/test-web-orchestrator`, and `/run-test` commands):
  ```markdown
  ## Test Configuration

  ### Unit Tests
  - Framework: [Vitest/Jest/Mocha/pytest/etc.]
  - Run command: `[npm test / npx vitest run / pytest / etc.]`
  - Config file: [vitest.config.ts / jest.config.js / pytest.ini / etc.]
  - Test location: `tests/unit/`
  - File pattern: `*.spec.ts` or `*.test.ts`

  ### Integration Tests
  - Framework: [Playwright / Cypress / etc.]
  - Run command: `npx playwright test`
  - Config file: `playwright.config.ts`
  - Test location: `tests/integration/`
  - File pattern: `*.e2e.spec.ts`

  ### Web Tests
  - Framework: [Playwright / Cypress / WebdriverIO / etc.]
  - Run command: `npx playwright test tests/web/*.spec.ts`
  - Config file: `playwright.config.ts` or equivalent
  - Test location: `tests/web/`
  - File pattern: `*.spec.ts`
  ```

**Error handling:**
- Template directory not found: Use hardcoded minimal template
- Template parse error: Skip broken template, log warning
- No matching templates: Generate standards from Step 3 discovery only

## Step 5: Persist (Update-in-place, Non-destructive)

**Tools:**
- Read(file_path=...) to check existing content
- Edit(file_path=..., old_string=..., new_string=...) for updates within managed blocks
- Write(file_path=...) if file doesn't exist

**Target files:**
- `docs/ai/project/CODE_CONVENTIONS.md`
- `docs/ai/project/PROJECT_STRUCTURE.md`

**Update strategy:**
- Use managed block markers to wrap generated content (see Notes for marker format)
- If file exists with markers: Update content between START/END markers only
- If file exists without markers: Append managed block to end
- If file doesn't exist: Create with header note and managed block
- Never modify content outside managed blocks

**Error handling:**
- File write permission denied: Notify user, suggest manual save
- File locked by another process: Retry once, then notify user
- Invalid marker format in existing file: Append new managed block instead of updating

## Step 6: Next Actions

- Suggest running `code-review` to validate new standards are being followed
- Inform user they can manually edit these files anytime

## Notes

### General Guidelines

- Focus on patterns actually present in codebase, not ideal patterns
- Keep generated docs concise and actionable
- User can refine standards manually after generation

### Template Matching Details (Step 4)

**Template loading logic:**
1. Glob all files in `docs/ai/project/template-convention/`
2. Match templates by filename:
   - `common.md` → Always include if present
   - `javascript.md`, `typescript.md`, `python.md` → Match by language
   - `react.md`, `vue.md`, `angular.md` → Match by framework
   - Other files → Match by detected tooling
3. Merge order: `common.md` → language → framework → tooling
4. Templates appear at top of generated doc, followed by auto-discovered rules

### Managed Block Markers (Step 5)

**Marker format for CODE_CONVENTIONS.md:**
```
<!-- GENERATED: CODE_CONVENTIONS:START -->
... generated content ...
<!-- GENERATED: CODE_CONVENTIONS:END -->
```

**Marker format for PROJECT_STRUCTURE.md:**
```
<!-- GENERATED: PROJECT_STRUCTURE:START -->
... generated content ...
<!-- GENERATED: PROJECT_STRUCTURE:END -->
```

**Header note template:**
```
This document is auto-generated from codebase analysis + brief Q&A.
Edit manually as needed.
```
