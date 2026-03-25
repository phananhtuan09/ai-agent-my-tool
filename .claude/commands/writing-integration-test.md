---
name: writing-integration-test
description: Generates Playwright E2E test files for UI/integration testing that can be run repeatedly.
---

Use `docs/ai/testing/integration-{name}.md` as the source of truth.

- **Load template:** Read `docs/ai/testing/integration-template.md` to understand required structure.

## Workflow Alignment

- Provide brief status updates (1–3 sentences) before/after important actions.
- For medium/large tasks, create todos (≤14 words, verb-led). Keep only one `in_progress` item.
- Update todos immediately after progress; mark completed upon finish.
- Default to parallel execution for independent operations; use sequential steps only when dependencies exist.

## Step 1: Gather Context (minimal)

- Ask for feature name if not provided (must be kebab-case).
- **Load planning doc:** Read `docs/ai/planning/feature-{name}.md` for:
  - User flows and interactions to test
  - UI components and pages involved
  - Acceptance criteria (test alignment)
- **Verify Playwright MCP:** Confirm `playwright` MCP server is available via `/mcp` command.
- **Check Playwright setup:** Verify `@playwright/test` is installed in `package.json`.
  - If not installed, run: `npm install -D @playwright/test && npx playwright install`
- **Check for playwright.config:** If missing, create basic config file.
- **Load standards:**
  - `docs/ai/project/PROJECT_STRUCTURE.md` for test file placement rules
  - `docs/ai/project/CODE_CONVENTIONS.md` for coding standards

**Source of truth:** Planning doc acceptance criteria + actual UI behavior.

## Step 2: Ask Testing Approach

**Tool:** AskUserQuestion

Ask user which approach to use for test exploration and writing:

```
Question: Which approach do you want to use for integration testing?
Options:
  1. Playwright MCP (Recommended) - Interactive browser exploration to discover selectors
  2. @playwright/test package only - Write tests directly without browser exploration
```

**If user chooses "Playwright MCP":**
- Use Playwright MCP tools for UI exploration (Step 3)
- Then generate test files based on discovered selectors

**If user chooses "@playwright/test package only":**
- Skip Step 3 (Explore UI)
- Generate test files directly based on planning doc and code analysis
- Use best-practice selectors (getByRole, getByLabel, getByText)

## Step 3: Scope (UI/Integration tests only)

- **Focus on:**
  - User journey flows: complete user interactions from start to finish
  - Page navigation: routing, redirects, deep links
  - Form interactions: input, validation, submission, error states
  - UI state changes: loading states, error states, success feedback
  - Visual verification: element visibility, text content, layout
  - Cross-browser testing: Chrome, Firefox, WebKit (if configured)
  - Responsive behavior: different viewport sizes (if applicable)
  - Accessibility: keyboard navigation, ARIA labels (basic checks)

- **DO NOT write:**
  - Unit tests for pure functions (use `/writing-test` instead)
  - API-only tests without UI interaction
  - Performance/load testing
  - Complex data seeding requiring database manipulation

- **Test isolation:**
  - Each test should be independent and repeatable
  - Use `page.goto()` to start from known state
  - Clean up any created data after test (if applicable)

## Step 4: Explore UI with Playwright MCP (if user chose MCP)

**Pre-requisite: Ensure local server is running**
- Before exploring, verify the application server is running
- If server is not running, prompt user: "Please start your local server (e.g., `npm run dev`) before proceeding"
- Check server availability by attempting to navigate to the base URL

Use Playwright MCP to explore the actual UI and understand element selectors:

**Available Playwright MCP tools for exploration:**
- `browser_navigate` - Navigate to URL to see actual page
- `browser_snapshot` - Get accessibility tree (best for finding selectors)
- `browser_click` - Test clicking elements
- `browser_type` - Test typing into inputs
- `browser_screenshot` - Capture current state

**Exploration workflow:**
1. Navigate to the page: `browser_navigate url="{BASE_URL}/page"` (read BASE_URL from .env or config)
2. Get element tree: `browser_snapshot` → use this to find accurate selectors
3. Test interactions to verify selectors work
4. Use discovered selectors in generated test files

## Step 5: Generate Playwright Test Files

**Test file location:** `tests/integration/` directory

**File naming:** `{feature-name}.e2e.spec.ts`

**Test file template:**
```typescript
import { test, expect } from '@playwright/test';

test.describe('{Feature Name}', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to starting page
    await page.goto('/page-url');
  });

  test('should [happy path scenario]', async ({ page }) => {
    // Arrange - initial state verified
    await expect(page.getByRole('heading', { name: 'Title' })).toBeVisible();

    // Act - user interactions
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Submit' }).click();

    // Assert - expected outcome
    await expect(page.getByText('Success')).toBeVisible();
    await expect(page).toHaveURL('/dashboard');
  });

  test('should show error for invalid input', async ({ page }) => {
    // Act - trigger error
    await page.getByRole('button', { name: 'Submit' }).click();

    // Assert - error displayed
    await expect(page.getByText('Email is required')).toBeVisible();
  });

  test('should handle edge case: [description]', async ({ page }) => {
    // Edge case test
  });
});
```

**Selector priority (most stable to least):**
1. `getByRole()` - accessibility roles (button, heading, textbox)
2. `getByLabel()` - form labels
3. `getByText()` - visible text content
4. `getByTestId()` - data-testid attributes
5. `getByPlaceholder()` - placeholder text
6. CSS selectors - last resort

**Generate tests for:**
- Happy path: normal user flow → expected success
- Validation errors: missing/invalid input → error messages
- Edge cases: empty states, boundary values, special characters
- Navigation: page transitions, back button, deep links
- Loading states: verify loading indicators appear/disappear

## Step 6: Create Playwright Config (if missing)

**File:** `playwright.config.ts`

**Dynamic Base URL:** Read port from `.env`, `package.json` scripts, or existing config. Do NOT hardcode `localhost:3000`.

```typescript
import { defineConfig, devices } from '@playwright/test';

// Read from environment or default to 3000
const PORT = process.env.PORT || 3000;
const BASE_URL = process.env.BASE_URL || `http://localhost:${PORT}`;

export default defineConfig({
  testDir: './tests/integration',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: BASE_URL,
    reuseExistingServer: !process.env.CI,
  },
});
```

## Step 7: Ask User for Next Action

**Tool:** AskUserQuestion

After test files are created, ask user:

```
Question: Test files have been created. What would you like to do next?
Options:
  1. Run tests now (Recommended) - Execute tests and see results
  2. Skip to next command - Continue without running tests
```

**If user chooses "Run tests now":** Proceed to Step 8 (Run Tests).
**If user chooses "Skip":** Jump to Step 9 (Update Integration Testing Doc) with placeholder results.

## Step 8: Run Tests & Verify (if user requested)

**Run commands:**
```bash
# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test tests/integration/{feature-name}.e2e.spec.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Run with UI mode (interactive)
npx playwright test --ui

# Show HTML report
npx playwright show-report
```

**If tests fail:**
- Analyze failure: selector issue vs actual bug
- Use `browser_snapshot` via MCP to verify current DOM structure (if MCP approach was chosen)
- Fix selectors if elements changed
- **Report UI bug** if behavior doesn't match acceptance criteria
- Re-run tests after fixing

## Step 9: Update Integration Testing Doc

Create/update `docs/ai/testing/integration-{name}.md` with:

```markdown
# Integration Test Plan: {Feature Name}

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
npx playwright test tests/integration/{feature-name}.e2e.spec.ts
```

## Last Run Results
- Total: X tests
- Passed: Y
- Failed: Z
- Duration: Xs

## Notes
- Tests are repeatable and independent
- Run `npx playwright test --ui` for interactive debugging
```

## Step 10: Add npm Script (optional)

Add to `package.json`:
```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:headed": "playwright test --headed"
  }
}
```

## Notes

- **Playwright MCP is for exploration** - use it to discover selectors and test interactions
- **Test files are the output** - actual `*.e2e.spec.ts` files that run repeatedly
- Keep tests focused on user-visible behavior, not implementation details
- Use stable selectors (roles, labels) over fragile ones (CSS classes)
- Tests should be deterministic - avoid time-dependent assertions

**Authentication handling:**
- If feature requires authentication, tests will get stuck on login screen
- Solutions:
  1. **Use `storageState`**: Save authenticated state to file and reuse across tests
     ```typescript
     // Save auth state after login
     await page.context().storageState({ path: 'playwright/.auth/user.json' });

     // Reuse in playwright.config.ts
     use: { storageState: 'playwright/.auth/user.json' }
     ```
  2. **Login in `beforeEach`**: Add login steps before each test
     ```typescript
     test.beforeEach(async ({ page }) => {
       await page.goto('/login');
       await page.getByLabel('Email').fill('test@example.com');
       await page.getByLabel('Password').fill('password');
       await page.getByRole('button', { name: 'Login' }).click();
       await page.waitForURL('/dashboard');
     });
     ```
  3. **API login**: Use API to get auth token, then set cookies/localStorage

**Scope boundaries:**
- **Creates:** Playwright test files (`*.e2e.spec.ts`), config, npm scripts
- **Creates:** Integration test documentation (`docs/ai/testing/integration-{name}.md`)
- **Uses:** Playwright MCP for UI exploration and selector discovery
- **Does NOT edit:** Application source code
- **If UI bug found:** Report to user with details
- Idempotent: safe to re-run; updates/extends test files

**Comparison with `/writing-test`:**
| Aspect | `/writing-test` | `/writing-integration-test` |
|--------|-----------------|-------------------|
| Focus | Unit/logic tests | UI/integration tests |
| Framework | Vitest/Jest | Playwright |
| Speed | Fast (ms) | Slower (seconds) |
| Scope | Functions, components | User flows, pages |
| Output | `tests/unit/*.spec.ts` | `tests/integration/*.e2e.spec.ts` |
| Run command | `npm test` | `npx playwright test` |

**When to use `/test-web-orchestrator` instead:**
- The workflow must read mixed inputs such as spec docs, feature plans, Figma, and runtime notes
- You want multi-agent analysis before generating browser tests
- You want a dedicated `docs/ai/testing/web-{name}.md` rerun artifact and post-run verification flow
