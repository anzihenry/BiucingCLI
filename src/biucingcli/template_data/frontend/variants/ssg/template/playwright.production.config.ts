import { defineConfig } from "playwright/test";

const baseURL = process.env.PLAYWRIGHT_BASE_URL;

if (!baseURL) {
  throw new Error(
    "PLAYWRIGHT_BASE_URL is required for production image browser tests.",
  );
}

export default defineConfig({
  testDir: "./tests",
  testMatch: "production-browser-smoke.spec.ts",
  fullyParallel: false,
  reporter: "list",
  use: {
    channel: process.env.PLAYWRIGHT_CHANNEL,
    baseURL,
    headless: true,
    screenshot: "only-on-failure",
  },
});
