# Integration Test Plan: {Feature Name}

Note: All content in this document must be written in English.

## Test Files Created
- `tests/integration/{feature-name}.e2e.spec.ts` - E2E tests for {feature}

## Test Scenarios

### Happy Path
- ✓ User can [complete main flow]
- ✓ Form submits successfully with valid data
- ✓ Navigation works correctly

### Error Handling
- ✓ Validation errors display for invalid input
- ✓ Error messages are clear and helpful

### Edge Cases
- ✓ Empty state displays correctly
- ✓ Special characters handled properly

## Run Command
```bash
# Run specific feature tests
npx playwright test tests/integration/{feature-name}.e2e.spec.ts

# Run all integration tests
npx playwright test

# Run in headed mode (see browser)
npx playwright test --headed

# Run with UI mode (interactive debugging)
npx playwright test --ui
```

## Last Run Results
- Total: 0 tests
- Passed: 0
- Failed: 0
- Duration: 0s

## Coverage
- Happy path scenarios: [count]
- Error scenarios: [count]
- Edge case scenarios: [count]

## Issues Found
- None yet

## Notes
- Tests are repeatable and independent
- Run `npx playwright test --ui` for interactive debugging
- Screenshots captured on failure in `test-results/` directory
- HTML report available via `npx playwright show-report`
