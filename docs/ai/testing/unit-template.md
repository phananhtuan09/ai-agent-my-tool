# Unit Test Plan: {Feature Name}

Note: All content in this document must be written in English.

## Test Files Created
- `tests/unit/test-file.spec.ts` - Tests for [component/function]
- `tests/unit/another-test.spec.ts` - Tests for [component/function]

## Unit Tests

### Function/Component Name
- ✓ Happy path: normal parameters → expected output
- ✓ Edge case: empty/null input → handled correctly  
- ✓ Edge case: boundary values (min/max, 0, -1) → handled correctly
- ✓ Parameter variation: [param1]=X, [param2]=Y → output Z
- ✓ Error case: invalid input → throws/returns error
- ✓ Type safety: wrong type input → handled correctly
- ✓ Property-based: [property] maintained → verified

### Another Function/Component
- [Similar test cases...]

## Run Command
```bash
npm test
# or
npx vitest run
# or language-specific command
```

## Last Run Results
- Total: 15 tests
- Passed: 14
- Failed: 1
- Skipped: 0
- Coverage:
  - Lines: 82% (123/150)
  - Branches: 75% (30/40)
  - Functions: 90% (18/20)

## Coverage Targets
- Target: 80% (lines), 70% (branches)
- Current: 82% (lines), 75% (branches)
- Status: ✓ Targets met

## Notes
- All tests run automatically via command line
- Test results logged to terminal with detailed output
- Focus on logic testing, edge cases, and parameter variations
- No complex integration or UI rendering tests

## Quality Checks
- Linter: pass on changed files
- Type checks: pass
- Build: green

## Process
- After each batch of implementation edits, run linter/type/build on changed files.
- Auto-fix linter issues (up to 3 attempts) before requesting review.
