---
name: writing-test
description: Generates comprehensive unit test files with edge cases, parameter variations, and coverage analysis.
---

Use `docs/ai/testing/unit-{name}.md` as the source of truth.

## Workflow Alignment

- Provide brief status updates (1–3 sentences) before/after important actions.
- For medium/large tasks, create todos (≤14 words, verb-led). Keep only one `in_progress` item.
- Update todos immediately after progress; mark completed upon finish.
- Default to parallel execution for independent operations; use sequential steps only when dependencies exist.

## Step 1: Gather Context (minimal)

- Ask for feature name if not provided (must be kebab-case).
- **Load template:** Read `docs/ai/testing/unit-template.md` to understand required structure.
- **Load planning doc:** Read `docs/ai/planning/feature-{name}.md` for:
  - Acceptance criteria (test alignment)
  - Implementation plan (files to test)
  - Functions/components that need coverage
- **Load test configuration from PROJECT_STRUCTURE.md:**
  - Read `docs/ai/project/PROJECT_STRUCTURE.md`
  - Look for "Test Configuration" section → "Unit Tests" subsection
  - Extract: Framework, Run command, Config file, Test location, File pattern
  - **If Test Configuration not found:**
    1. Check `package.json` for test dependencies (vitest, jest, mocha, etc.)
    2. Check for config files: `vitest.config.*`, `jest.config.*`, `pytest.ini`
    3. If still not found, ask user using AskUserQuestion:
       ```
       Question: Which unit test framework do you want to use?
       Options:
         1. Vitest (Recommended for Vite/modern projects)
         2. Jest (Popular, works with most projects)
         3. Mocha (Flexible, requires setup)
         4. pytest (Python projects)
       ```
    4. After user selection, suggest running `/generate-standards` to persist the choice
- **Load standards:**
  - `docs/ai/project/CODE_CONVENTIONS.md` for coding standards

**Source of truth:** PROJECT_STRUCTURE.md test configuration → planning doc acceptance criteria → source code.

## Step 2: Scope (logic and component tests only)

- **Focus on:**
  - Pure function logic: test with various input parameters (happy path, edge cases, invalid inputs)
  - Component logic: test component behavior with different props/parameters (without complex rendering)
  - Utility functions: test return values, error handling, boundary conditions
  - Parameter variations: systematically test different combinations of parameters
  - Edge cases: null, undefined, empty values, boundary values
  - Error handling: invalid inputs, exceptions, error messages
  - Type safety: type mismatches, missing properties, contract violations
  - Property-based testing: mathematical properties (commutativity, associativity, idempotency)
- **DO NOT write:**
  - Integration tests between multiple modules/services (requires heavy setup)
  - Complex UI rendering tests requiring heavy DOM setup
  - E2E flows or end-to-end user journey tests
  - Tests requiring external API calls, database connections, or network mocking
  - Performance/load testing
- **Dependency isolation (mocking):**
  - **Prefer `vi.spyOn`/`jest.spyOn`** over complete function overwrites for better type safety
  - Use spyOn to mock specific methods while preserving original implementation
  - Mock external dependencies (API clients, database connections, file system)
  - Mock imported utilities/hooks if they have side effects
  - Keep internal logic unmocked (test actual implementation)
  - Use test framework's mocking utilities (vi.mock, jest.mock, unittest.mock) only when spyOn is insufficient
- Keep tests simple, fast, and deterministic.

## Step 3: Analyze Code & Generate Tests (automatic)

**Analyze implementation:**
- Read files referenced in `docs/ai/planning/feature-{name}.md`; if the plan does not name files clearly, scan source
- Identify functions/components: signatures, parameters, return types, exceptions
- Map: input types → expected outputs → edge cases → error cases

**Generate test files:**
- Create test file in `tests/unit/` directory
- File naming: `{feature-name}.spec.ts` or `{component-name}.spec.ts`
- Follow naming conventions from `CODE_CONVENTIONS.md`

**Test coverage strategy:**
- **Happy path**: normal parameters → expected output
- **Edge cases**: null, undefined, empty, boundaries (min/max, 0, -1)
- **Parameter combinations**: systematically test input variations
- **Error handling**: invalid inputs, exceptions, error messages
- **Type safety**: wrong types, missing properties
- **Property-based** (if applicable): commutativity, associativity, idempotency

**For complex test suites (>15 test cases):**
- Use Task tool with `subagent_type='general-purpose'`
- Task prompt: "Generate comprehensive test cases for [function] covering happy path, edge cases, error handling, and parameter combinations"

## Step 4: Ask User for Next Action

**Tool:** AskUserQuestion

After test files are created, ask user:

```
Question: Test files have been created. What would you like to do next?
Options:
  1. Run tests now (Recommended) - Execute tests and see results
  2. Skip to next command - Continue without running tests
```

**If user chooses "Run tests now":** Proceed to Step 5 (Run Tests).
**If user chooses "Skip":** Jump to Step 7 (Update Testing Doc) with placeholder results.

## Step 5: Run Tests with Logging (if user requested)

**Execute test command from PROJECT_STRUCTURE.md configuration:**
- Use the "Run command" from Test Configuration section
- If not configured, use framework defaults:
  - Vitest: `npx vitest run --passWithNoTests`
  - Jest: `npx jest --ci --passWithNoTests`
  - Mocha: `npx mocha --reporter spec`
  - pytest: `pytest -v --tb=short`

**Display output:**
- Test execution progress and results (pass/fail, timing)
- Test summary (total/passed/failed/skipped)
- Error messages and stack traces for failures
- Coverage report (lines, branches, functions %)

**If tests fail:**
- Analyze failure reason (test logic vs implementation bug)
- **Fix test logic** if test expectations are incorrect
- **Report implementation bug** if source code violates acceptance criteria (do NOT auto-fix source code)
- Re-run tests after fixing test logic
- Update testing doc with results

## Step 6: Coverage Gap Analysis (if tests were run)

**Analyze coverage report:**
- Identify untested branches/lines/functions

**Generate additional tests (max 3 iterations):**
- Create test cases for uncovered branches/lines/functions
- Re-run tests with coverage
- Verify targets met (default: 80% lines, 70% branches)
- **Loop limit:** Maximum 3 retry attempts to prevent infinite loops
- If targets not met after 3 attempts:
  - Report current coverage status to user
  - List remaining uncovered areas
  - Stop and let user decide next steps

## Step 7: Update Testing Doc

Use structure from `docs/ai/testing/unit-template.md` to populate `docs/ai/testing/unit-{name}.md`.

Fill with:

- **Test Files Created**: List all test files generated with paths
- **Test Cases Summary**: Brief summary of what was tested (function/component + key scenarios)
  - Happy path scenarios
  - Edge cases covered
  - Parameter variations tested
  - Error scenarios handled
  - Property-based tests (if any)
- **Run Command**: Command to execute tests
- **Last Run Results**: Summary of test execution
  - Total/passed/failed count
  - Coverage percentages (lines, branches, functions)
  - Any notable findings or issues
- **Coverage Targets**: Coverage goals and current status

Ensure all required sections from template are present. Keep the document brief and actionable.

## Step 8: Verify Tests Pass (if tests were run)

- Ensure all generated tests pass successfully
- Ensure coverage targets are met (default: 80% lines, 70% branches)
- If any test fails:
  - Debug test logic and fix test expectations
  - **OR** report implementation bug to user (if source code violates acceptance criteria)
- Re-run tests after fixing test logic

## Notes

- Tests should be simple enough to run quickly and verify logic correctness
- Focus on catching logic errors and edge cases through systematic parameter variation
- Avoid complex test setup or mocking unless necessary for logic isolation
- All tests must be automatically runnable via command line
- Test execution must show clear, detailed logging in terminal
- AI excels at: edge case generation, parameter combinations, property-based testing, coverage analysis
- Keep tests deterministic (avoid external dependencies, random values without seeds, time-dependent logic)

**Scope boundaries:**
- **Creates:** Test files only (*.spec.*, *.test.*)
- **Modifies:** Test files only when fixing test logic
- **Does NOT edit:** Non-test source files (implementation code)
- **If implementation bug found:** Report to user; do NOT auto-fix source code
- Idempotent: safe to re-run; updates test doc deterministically
