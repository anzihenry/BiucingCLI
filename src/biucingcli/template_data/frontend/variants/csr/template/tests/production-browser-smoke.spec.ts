import { expect, test } from "playwright/test";
import { registerInteractionTests } from "./interactions";

registerInteractionTests();

test("static production shell and missing assets", async ({
  request,
  page,
}) => {
  const response = await request.get("/");
  expect(response.headers()["server"]).toContain("nginx");
  const html = await response.text();
  expect(html).toContain("Loading application");
  expect(html).not.toContain("Your independent frontend starts here.");
  expect((await request.get("/assets/missing.js")).status()).toBe(404);
  expect((await request.get("/favicon.svg")).status()).toBe(200);
  const missing = await page.goto("/missing-route");
  expect(missing?.status()).toBe(200);
  await expect(
    page.getByRole("heading", { name: "Page not found" }),
  ).toBeVisible();
});
