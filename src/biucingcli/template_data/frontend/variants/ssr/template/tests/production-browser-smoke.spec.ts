import { expect, test } from "playwright/test";
import { registerInteractionTests } from "./interactions";
import { registerSsrTests } from "./ssr";

registerInteractionTests("SSR production");
registerSsrTests();

test("Node health, assets and data responses", async ({ request }) => {
  expect((await request.get("/healthz")).status()).toBe(200);
  expect((await request.head("/about")).status()).toBe(200);
  expect((await request.get("/assets/missing.js")).status()).toBe(404);
  expect((await request.get("/favicon.svg")).status()).toBe(200);
  const data = await request.get("/_.data?visitor=public-data-marker");
  expect(data.status()).toBe(200);
  expect(data.headers()["cache-control"]).toBe("private, no-store");
  expect(await data.text()).not.toContain("private-smoke-sentinel");
  expect(await data.text()).toContain("public-data-marker");
  expect((await request.get("/_.data?visitor=a&visitor=b")).status()).toBe(400);
});
