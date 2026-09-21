import { expect, test } from "playwright/test";
import { articles, contentPaths } from "../app/content";
import { project } from "../app/lib/project";
import { requireSiteOrigin } from "../app/lib/site";

export function registerSsgTests(production = false) {
  for (const viewport of [
    { width: 1280, height: 800 },
    { width: 390, height: 844 },
  ]) {
    test(`SSG content navigation at ${viewport.width}px`, async ({ page }) => {
      await page.setViewportSize(viewport);
      const errors: string[] = [];
      page.on("pageerror", (error) => errors.push(error.message));
      page.on("console", (message) => {
        if (message.type() === "error") errors.push(message.text());
      });
      await page.goto("/");
      await expect(
        page.getByRole("button", { name: "Count: 0" }),
      ).toBeEnabled();
      // A full document navigation would discard this marker.
      await page.evaluate(() => {
        Object.assign(window, { ssgNavigationProbe: "retained" });
      });
      for (const article of articles) {
        const dataResponse = page.waitForResponse(
          (response) =>
            response.url().includes(`/articles/${article.slug}.data`) &&
            response.status() === 200,
        );
        await page
          .getByRole("link", { name: article.title, exact: true })
          .click();
        await dataResponse;
        await expect(page).toHaveTitle(`${article.title} | ${project.title}`);
        await expect(
          page.getByRole("heading", { name: article.title }),
        ).toBeVisible();
        expect(
          await page.evaluate(
            () =>
              (window as Window & { ssgNavigationProbe?: string })
                .ssgNavigationProbe,
          ),
        ).toBe("retained");
        const timestamp = await page.getByTestId("built-at").textContent();
        expect(timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T/);
        const response = await page.reload();
        expect(response?.status()).toBe(200);
        await expect(page.getByTestId("built-at")).toHaveText(timestamp ?? "");
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= window.innerWidth,
          ),
        ).toBe(true);
        await page.getByRole("link", { name: "Return home" }).click();
        await expect(
          page.getByRole("button", { name: "Count: 0" }),
        ).toBeEnabled();
        await page.evaluate(() => {
          Object.assign(window, { ssgNavigationProbe: "retained" });
        });
      }
      expect(errors).toEqual([]);
    });
  }

  if (!production) return;

  test("SSG actions wait for hydration with delayed JavaScript", async ({
    page,
  }) => {
    let resume = () => undefined as void;
    const scriptsReady = new Promise<void>((resolve) => {
      resume = resolve;
    });
    await page.route("**/*", async (route) => {
      if (route.request().resourceType() === "script") await scriptsReady;
      await route.continue();
    });
    try {
      await page.goto("/", { waitUntil: "commit" });
      await expect(
        page.getByRole("heading", { name: project.title }),
      ).toBeVisible();
      await expect(
        page.getByRole("button", { name: "Count: 0" }),
      ).toBeDisabled();
      await expect(
        page.getByRole("button", { name: "About this starter" }),
      ).toBeDisabled();
    } finally {
      resume();
    }
    await page.getByRole("button", { name: "Count: 0" }).click();
    await expect(page.getByRole("button", { name: "Count: 1" })).toBeVisible();
  });

  test("SSG raw HTML, metadata, stable data and sitemap", async ({
    request,
    browser,
  }) => {
    const origin = requireSiteOrigin(process.env.SITE_URL);
    for (const path of contentPaths()) {
      const response = await request.get(path);
      expect(response.status()).toBe(200);
      expect(response.headers()["server"]).toContain("nginx");
      const html = await response.text();
      expect(html).not.toContain("Loading application");
      const context = await browser.newContext({ javaScriptEnabled: false });
      const page = await context.newPage();
      await page.goto(response.url());
      await expect(page.locator("title")).toHaveCount(1);
      await expect(page.locator('link[rel="canonical"]')).toHaveAttribute(
        "href",
        `${origin}${path}`,
      );
      await expect(page.locator('meta[name="description"]')).toHaveCount(1);
      await expect(page.locator('meta[property="og:url"]')).toHaveAttribute(
        "content",
        `${origin}${path}`,
      );
      await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
      const article = articles.find((entry) => path.endsWith(`/${entry.slug}`));
      if (article) {
        await expect(
          page.getByText(article.body, { exact: true }),
        ).toBeVisible();
        expect(await (await request.get(`${path}?visitor=other`)).text()).toBe(
          html,
        );
        const data = await request.get(`${path}.data`);
        expect(data.status()).toBe(200);
        expect(await data.text()).toContain(article.title);
        expect(
          await (await request.get(`${path}.data?visitor=other`)).text(),
        ).toBe(await data.text());
      }
      await context.close();
    }
    const sitemap = await request.get("/sitemap.xml");
    expect(sitemap.status()).toBe(200);
    expect(sitemap.headers()["content-type"]).toContain("xml");
    const xml = await sitemap.text();
    for (const path of contentPaths())
      expect(xml).toContain(`<loc>${origin}${path}</loc>`);
    expect(xml.match(/<loc>/g)).toHaveLength(contentPaths().length);
    expect(xml).not.toContain("localhost");
    expect(await (await request.get("/robots.txt")).text()).toContain(
      `Sitemap: ${origin}/sitemap.xml`,
    );
    expect((await request.get("/favicon.svg")).status()).toBe(200);
  });

  test("SSG returns real 404s without SPA fallback", async ({
    request,
    page,
  }) => {
    for (const path of [
      "/missing-route",
      "/articles/not-built",
      "/articles/not-built.data",
      "/assets/missing.js",
      "/__spa-fallback.html",
    ]) {
      expect((await request.get(path)).status(), path).toBe(404);
    }
    expect((await page.goto("/articles/not-built"))?.status()).toBe(404);
    await expect(
      page.getByRole("heading", { name: "Page not found" }),
    ).toBeVisible();
    await expect(page.locator('meta[name="robots"]')).toHaveAttribute(
      "content",
      "noindex",
    );
    await page.getByRole("link", { name: "Return home" }).click();
    await expect(
      page.getByRole("heading", { name: project.title }),
    ).toBeVisible();
  });
}
