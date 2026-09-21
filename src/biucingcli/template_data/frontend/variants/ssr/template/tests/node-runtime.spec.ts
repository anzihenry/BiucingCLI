import { spawn } from "node:child_process";
import { once } from "node:events";
import { readFile, readdir } from "node:fs/promises";
import { expect, test } from "playwright/test";

test("private configuration failures produce sanitized HTML/data 500 and clean SIGTERM", async ({
  request,
}) => {
  const sentinel = "private-failure-sentinel";
  const child = spawn(process.execPath, ["server/index.ts"], {
    env: {
      ...process.env,
      PORT: "4190",
      HOST: "127.0.0.1",
      NODE_ENV: "production",
      SSR_PRIVATE_TOKEN: sentinel.repeat(300),
    },
    stdio: ["ignore", "pipe", "pipe"],
  });
  let logs = "";
  child.stdout.on("data", (chunk: Buffer) => {
    logs += chunk.toString();
  });
  child.stderr.on("data", (chunk: Buffer) => {
    logs += chunk.toString();
  });
  const exited = once(child, "exit");
  try {
    await expect
      .poll(async () => {
        try {
          return (await request.get("http://127.0.0.1:4190/healthz")).status();
        } catch {
          return 0;
        }
      })
      .toBe(200);
    for (const path of ["/", "/_.data"]) {
      const response = await request.get(`http://127.0.0.1:4190${path}`);
      expect(response.status()).toBe(500);
      expect(response.headers()["cache-control"]).toBe("private, no-store");
      const body = await response.text();
      expect(body).not.toContain(sentinel);
      expect(body).not.toContain("Invalid private configuration");
      expect(body).not.toContain("request.server");
    }
    expect(logs).not.toContain(sentinel);
    expect(logs).not.toContain("Invalid private configuration");
    child.kill("SIGTERM");
    const watchdog = setTimeout(() => child.kill("SIGKILL"), 12_000);
    try {
      expect(await exited).toEqual([0, null]);
    } finally {
      clearTimeout(watchdog);
    }
  } finally {
    if (child.exitCode === null && child.signalCode === null)
      child.kill("SIGKILL");
    await exited;
  }
});

test("client artifacts contain no private server module or environment names", async () => {
  for (const name of await readdir("build/client/assets")) {
    const contents = await readFile(`build/client/assets/${name}`, "utf8");
    expect(contents).not.toContain("SSR_PRIVATE_TOKEN");
    expect(contents).not.toContain("privateConfiguration");
    expect(contents).not.toContain("private-smoke-sentinel");
  }
});
