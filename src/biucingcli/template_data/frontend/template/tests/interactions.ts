import { expect, test } from "playwright/test";
import { project } from "../app/lib/project";

export function registerInteractionTests(mode = "CSR") {
  for (const viewport of [
    { width: 1280, height: 800 },
    { width: 390, height: 844 },
  ]) {
    test(`${mode} interactions at ${viewport.width}px`, async ({
      page,
    }, testInfo) => {
      await page.setViewportSize(viewport);
      const errors: string[] = [];
      page.on("pageerror", (error) => errors.push(error.message));
      page.on("console", (message) => {
        if (message.type() === "error") errors.push(message.text());
      });
      const response = await page.goto("/");
      expect(response?.ok()).toBe(true);
      await expect(page).toHaveTitle(project.title);
      await expect(
        page.getByRole("heading", { name: project.title }),
      ).toBeVisible();
      await page.getByRole("button", { name: "Count: 0" }).click();
      await expect(
        page.getByRole("button", { name: "Count: 1" }),
      ).toBeVisible();
      const trigger = page.getByRole("button", { name: "About this starter" });
      await trigger.click();
      await expect(
        page.getByRole("dialog", { name: "Ready to build" }),
      ).toBeVisible();
      await page.keyboard.press("Escape");
      await expect(page.getByRole("dialog")).toBeHidden();
      await expect(trigger).toBeFocused();
      await page.getByRole("link", { name: "About the application" }).click();
      await expect(page).toHaveURL(/\/about$/);
      await page.reload();
      await expect(
        page.getByRole("heading", { name: "About the application" }),
      ).toBeVisible();
      await page.getByRole("link", { name: "Return home" }).click();
      await expect(
        page.getByRole("button", { name: "Count: 0" }),
      ).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
      ).toBe(true);
      expect(errors).toEqual([]);
      await page.screenshot({
        path: testInfo.outputPath("homepage.png"),
        fullPage: true,
      });
    });
  }
}
