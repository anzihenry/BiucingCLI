import { expect, test } from "playwright/test";

export function registerSsrTests() {
  test("concurrent request HTML stays isolated, uncached and private", async ({
    request,
  }) => {
    const names = Array.from({ length: 12 }, (_, i) => `visitor-${i}-unique`);
    const responses = await Promise.all(
      names.map((visitor) => request.get(`/?visitor=${visitor}`)),
    );
    const ids = new Set<string>();
    for (const [index, response] of responses.entries()) {
      expect(response.status()).toBe(200);
      expect(response.headers()["cache-control"]).toBe("private, no-store");
      const html = await response.text();
      expect(html).toContain(names[index]);
      expect(html).toContain("Your independent frontend starts here.");
      expect(html).not.toContain("private-smoke-sentinel");
      for (const other of names.filter((n) => n !== names[index]))
        expect(html).not.toContain(other);
      const id = /data-testid="request-id">([^<]+)/.exec(html)?.[1];
      expect(id).toBeTruthy();
      ids.add(id ?? "");
    }
    expect(ids.size).toBe(names.length);
  });

  test("real 400/404, escaped special input and stable hydration", async ({
    request,
    page,
  }) => {
    expect((await request.get(`/?visitor=${"x".repeat(81)}`)).status()).toBe(
      400,
    );
    expect((await request.get("/?visitor=a&visitor=b")).status()).toBe(400);
    expect((await request.get("/missing-route")).status()).toBe(404);
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (message) => {
      if (message.type() === "error") errors.push(message.text());
    });
    const visitor = 'R&D "引号" <script>alert(1)</script> \\ $HOME';
    const response = await page.goto(
      `/?visitor=${encodeURIComponent(visitor)}`,
    );
    expect(response?.status()).toBe(200);
    await expect(page.getByTestId("visitor")).toHaveText(visitor);
    await expect(page.getByRole("button", { name: "Count: 0" })).toBeEnabled();
    const id = await page.getByTestId("request-id").textContent();
    await page.getByRole("button", { name: "Count: 0" }).click();
    await expect(page.getByRole("button", { name: "Count: 1" })).toBeVisible();
    await expect(page.getByTestId("request-id")).toHaveText(id ?? "");
    const documentStart = await page.evaluate(() => performance.timeOrigin);
    await page.getByRole("link", { name: "About the application" }).click();
    await page.getByRole("link", { name: "Return home" }).click();
    await expect(page.getByTestId("visitor")).toHaveText("Guest");
    await expect(page.getByTestId("request-id")).not.toHaveText(id ?? "");
    expect(await page.evaluate(() => performance.timeOrigin)).toBe(
      documentStart,
    );
    expect(errors).toEqual([]);
  });
}
