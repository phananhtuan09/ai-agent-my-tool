import fs from "node:fs";
import path from "node:path";

import { expect, test } from "@playwright/test";

const BASE_URL = "http://127.0.0.1:8000";
const SCREENSHOT_DIR = path.join(
  process.cwd(),
  "test-results",
  "midnight-ai-theme-rollout"
);

function ensureScreenshotDir(): void {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function capture(page: import("@playwright/test").Page, name: string): Promise<void> {
  ensureScreenshotDir();
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, name),
    fullPage: true,
  });
}

test.use({ baseURL: BASE_URL, viewport: { width: 1440, height: 1200 } });

test("dashboard desktop shell follows Midnight AI layout", async ({ page }) => {
  await page.goto("/");
  await page.locator(".page-hero.accent-blue").waitFor();
  await page.waitForTimeout(1500);
  await capture(page, "dashboard-desktop.png");

  await expect(page.locator(".dashboard-card")).toHaveCount(2);
  await expect(page.locator(".nav-toggle")).toBeHidden();
  await expect(page.locator(".sidebar-close")).toBeHidden();
  await expect(page.locator(".hero-badge")).toContainText("Midnight AI");
});

test("config desktop keeps themed hero and form cluster", async ({ page }) => {
  await page.goto("/config");
  await page.locator("#openai-config-form").waitFor();
  await page.waitForTimeout(1000);
  await capture(page, "config-desktop.png");

  await expect(page.locator(".page-hero")).toContainText("OpenAI config");
  await expect(page.locator('input[name="base_url"]')).toBeVisible();
  await expect(page.locator('button[data-loading-text="Saving..."]')).toBeVisible();
  await expect(page.locator(".topbar .nav-toggle")).toBeHidden();
});

test("config HTMX save returns success feedback without leaving the themed layout", async ({
  page,
}) => {
  await page.goto("/config");
  await page.locator("#openai-config-form").waitFor();

  const saveRequest = page.waitForResponse((response) => {
    return response.url().includes("/config/openai") && response.request().method() === "POST";
  });

  await page.locator("#openai-config-form button[type='submit']").click();
  await saveRequest;

  await expect(page.locator("#config-feedback .feedback")).toBeVisible();
  await expect(page.locator("#config-feedback")).toContainText("OpenAI settings saved.");
  await expect(page.locator("#openai-config-form")).toBeVisible();
  await expect(page.locator("#openai-config-form select[name='default_model']")).toBeVisible();
  await capture(page, "config-save-feedback.png");
});

test("config HTMX API actions render inline model-field errors for unreachable endpoints", async ({
  page,
}) => {
  await page.goto("/config");
  await page.locator("#openai-config-form").waitFor();

  await page.locator("#openai-config-form input[name='base_url']").fill("http://127.0.0.1:9/v1");

  const testRequest = page.waitForResponse((response) => {
    return (
      response.url().includes("/config/openai/test") &&
      response.request().method() === "POST"
    );
  });

  await page.getByRole("button", { name: "Test API" }).click();
  await testRequest;

  await expect(page.locator("#openai-model-field .feedback.feedback-error")).toBeVisible();
  await expect(page.locator("#openai-model-field")).toContainText("Model fetch failed");
  await expect(page.locator("#openai-model-field select[name='default_model']")).toHaveCount(1);

  const fetchRequest = page.waitForResponse((response) => {
    return (
      response.url().includes("/config/openai/fetch-models") &&
      response.request().method() === "POST"
    );
  });

  await page.getByRole("button", { name: "Fetch models" }).click();
  await fetchRequest;

  await expect(page.locator("#openai-model-field .feedback.feedback-error")).toBeVisible();
  await expect(page.locator("#openai-model-field")).toContainText("Model fetch failed");
  await expect(page.locator("#openai-model-field select[name='default_model']")).toHaveCount(1);
  await capture(page, "config-model-field-error.png");
});

test("daily scheduler desktop renders hero, chat, timeline, and controls", async ({
  page,
}) => {
  await page.goto("/agents/daily_scheduler");
  await page.locator("#daily-schedule-chat-panel").waitFor();
  await page.waitForTimeout(2000);
  await capture(page, "daily-scheduler-desktop.png");

  await expect(page.locator("#connection-status")).toBeVisible();
  await expect(page.locator("#daily-schedule-chat-panel textarea[name='message']")).toBeVisible();
  await expect(page.locator("#daily-schedule-timeline")).toBeVisible();
  await expect(page.locator("#daily-schedule-controls")).toBeVisible();
  await expect(page.locator(".topbar .nav-toggle")).toBeHidden();
});

test("crypto airdrop desktop keeps controls inline instead of mobile toggle", async ({
  page,
}) => {
  await page.goto("/agents/crypto_airdrop");
  await page.locator("#airdrop-results-panel").waitFor();
  await page.waitForTimeout(2000);
  await capture(page, "crypto-airdrop-desktop.png");

  await expect(page.locator("#airdrop-sidebar")).toBeVisible();
  await expect(page.locator(".filter-toggle")).toBeHidden();
  await expect(page.locator("#crypto-airdrop-controls")).toBeVisible();
  await expect(page.locator("#crypto-airdrop-chat-panel")).toBeVisible();
});

test("mobile drawer opens and closes correctly", async ({ browser }) => {
  const context = await browser.newContext({
    baseURL: BASE_URL,
    viewport: { width: 390, height: 844 },
  });
  const page = await context.newPage();

  await page.goto("/");
  await page.locator(".nav-toggle").waitFor();
  await expect(page.locator(".nav-toggle")).toBeVisible();
  await page.locator(".nav-toggle").click();
  await expect(page.locator("body")).toHaveClass(/sidebar-open/);
  await expect(page.locator(".shell-overlay")).toBeVisible();
  await capture(page, "dashboard-mobile-drawer-open.png");

  await page.locator(".shell-overlay").click();
  await expect(page.locator("body")).not.toHaveClass(/sidebar-open/);
  await context.close();
});

test("agent config modal opens from the shell and saves the selected model", async ({ page }) => {
  await page.goto("/agents/daily_scheduler");
  await page.locator("#daily-schedule-chat-panel").waitFor();

  const modalRequest = page.waitForResponse((response) => {
    return (
      response.url().includes("/agents/daily_scheduler/config") &&
      response.request().method() === "GET"
    );
  });

  await page.getByRole("button", { name: "Change model" }).click();
  await modalRequest;

  await expect(page.locator("#modal-root .modal-card")).toBeVisible();
  await expect(page.locator("#modal-root")).toContainText("Model configuration");
  await expect(page.locator("#modal-root select[name='model']")).toBeVisible();

  const saveModalRequest = page.waitForResponse((response) => {
    return (
      response.url().includes("/agents/daily_scheduler/config") &&
      response.request().method() === "POST"
    );
  });

  await page.locator("#modal-root select[name='model']").selectOption("gpt-5-mini");
  await page.locator("#modal-root button[type='submit']").click();
  await saveModalRequest;

  await expect(page.locator("#modal-root #config-feedback .feedback")).toBeVisible();
  await expect(page.locator("#modal-root #config-feedback")).toContainText(
    "Model selection saved."
  );
  await capture(page, "daily-scheduler-change-model-modal.png");
});

test("daily scheduler HTMX planning refresh keeps themed transcript and timeline", async ({
  page,
}) => {
  const marker = `PW${Date.now()}`;
  const plannerMessage = `Playwright review ${marker} 15m, Verify HTMX flow ${marker} 20m`;

  await page.goto("/agents/daily_scheduler");
  await page.locator("#daily-schedule-chat-panel textarea[name='message']").waitFor();
  await page
    .locator("#daily-schedule-chat-panel textarea[name='message']")
    .fill(plannerMessage);

  const schedulerRequest = page.waitForResponse((response) => {
    return (
      response.url().includes("/agents/daily_scheduler/chat") &&
      response.request().method() === "POST"
    );
  });

  await page.locator("#daily-schedule-chat-panel button[type='submit']").click();
  await schedulerRequest;

  await expect(page.locator("#daily-schedule-chat-list")).toContainText(marker);
  await expect(page.locator("#daily-schedule-timeline")).toHaveCount(1);
  await expect(page.locator("#daily-schedule-timeline table#schedule-table")).toBeVisible();
  await expect(page.locator("#daily-schedule-timeline .summary-strip")).toBeVisible();
  await expect(page.locator("#daily-schedule-timeline")).toContainText("Playwright review");
  await expect(page.locator("#daily-schedule-chat-panel .btn.is-loading")).toHaveCount(0);
  await capture(page, "daily-scheduler-htmx-refresh.png");
});

test("crypto airdrop HTMX crawl and filter preserve themed results", async ({ page }) => {
  const filterMessage = "show ethereum";

  await page.goto("/agents/crypto_airdrop");
  await page.locator("#crypto-airdrop-controls [data-run-airdrop]").waitFor();

  const crawlRequest = page.waitForResponse((response) => {
    return (
      response.url().includes("/agents/crypto_airdrop/run") &&
      response.request().method() === "POST"
    );
  });

  await page.locator("#crypto-airdrop-controls [data-run-airdrop]").click();
  await crawlRequest;

  await expect(page.locator("#crypto-airdrop-run-feedback .feedback")).toBeVisible();
  await expect(page.locator("#airdrop-results-panel")).toContainText("Ranked");

  const chatRequest = page.waitForResponse((response) => {
    return (
      response.url().includes("/agents/crypto_airdrop/chat") &&
      response.request().method() === "POST"
    );
  });

  await page.locator("#crypto-airdrop-chat-panel textarea[name='message']").fill(filterMessage);
  await page.locator("#crypto-airdrop-chat-panel button[type='submit']").click();
  await chatRequest;

  await expect(page.locator("#crypto-airdrop-chat-list")).toContainText(filterMessage);
  await expect(page.locator("#crypto-airdrop-chat-list")).toContainText("Showing");
  await expect(page.locator("#airdrop-results-panel")).toHaveCount(1);
  await expect(page.locator("#airdrop-results-panel table#airdrop-table")).toBeVisible();
  await expect(page.locator("#airdrop-results-panel")).toContainText("Ethereum");
  await expect(page.locator("#crypto-airdrop-chat-panel .btn.is-loading")).toHaveCount(0);
  await capture(page, "crypto-airdrop-htmx-refresh.png");
});
