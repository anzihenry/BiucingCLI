import { expect, test } from "playwright/test";

test("starter homepage renders key sections", async ({ page }, testInfo) => {
  await page.goto("/");

  await expect(page).toHaveTitle(/{{DISPLAY_NAME}}/);
  await expect(page.getByRole("heading", { name: "{{DISPLAY_NAME}}" })).toBeVisible();
  await expect(page.getByText("Build Queue")).toBeVisible();
  await expect(page.getByText("Project Notes")).toBeVisible();
  await expect(page.locator(".metric-card")).toHaveCount(3);

  await page.screenshot({
    path: testInfo.outputPath("browser-smoke-homepage.png"),
    fullPage: true,
  });
});
