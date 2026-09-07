import { expect, test } from "playwright/test";

test("production image serves the starter through nginx", async ({
  page,
}, testInfo) => {
  const response = await page.goto("/");

  expect(response?.ok()).toBe(true);
  expect(response?.headers()["server"]).toContain("nginx");
  await expect(page).toHaveTitle(/{{DISPLAY_NAME}}/);
  await expect(
    page.getByRole("heading", { name: "{{DISPLAY_NAME}}" }),
  ).toBeVisible();
  await expect(page.getByText("Build Queue")).toBeVisible();
  await expect(page.getByText("Project Notes")).toBeVisible();
  await expect(page.locator(".metric-card")).toHaveCount(3);

  await page.screenshot({
    path: testInfo.outputPath("production-image-homepage.png"),
    fullPage: true,
  });
});
