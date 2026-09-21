import { defineConfig } from "playwright/test";

export default defineConfig({
  testDir: "./tests",
  testMatch: ["production-browser-smoke.spec.ts", "node-runtime.spec.ts"],
  workers: 1,
  fullyParallel: false,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:4189",
    channel: process.env.PLAYWRIGHT_CHANNEL,
    headless: true,
    screenshot: "only-on-failure",
  },
  webServer: {
    command: "node server/index.ts",
    env: {
      PORT: "4189",
      HOST: "127.0.0.1",
      NODE_ENV: "production",
      SSR_PRIVATE_TOKEN: "private-smoke-sentinel",
    },
    url: "http://127.0.0.1:4189/healthz",
    reuseExistingServer: false,
    timeout: 30_000,
    gracefulShutdown: { signal: "SIGTERM", timeout: 15_000 },
  },
});
