// @vitest-environment node
import { once } from "node:events";
import { mkdtemp, mkdir, writeFile, symlink, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { request } from "node:http";
import type { AddressInfo } from "node:net";
import { afterEach, expect, test, vi } from "vitest";
import {
  applicationListener,
  createAppServer,
  portFromEnvironment,
} from "../../server/runtime.ts";

const cleanups: (() => Promise<unknown>)[] = [];
afterEach(async () => {
  for (const cleanup of cleanups.splice(0).reverse()) await cleanup();
  vi.restoreAllMocks();
});

async function fixture() {
  const root = await mkdtemp(join(tmpdir(), "ssr-runtime-"));
  cleanups.push(() => rm(root, { recursive: true, force: true }));
  const client = join(root, "client");
  await mkdir(join(client, "assets"), { recursive: true });
  await writeFile(join(client, "assets/app.js"), "export {};");
  await writeFile(join(root, "private.txt"), "private-file-sentinel");
  await symlink(join(root, "private.txt"), join(client, "leak.txt"));
  const app = createAppServer(
    applicationListener(client, (_request, response) => {
      response.writeHead(404);
      response.end("Route not found");
    }),
  );
  cleanups.push(() => app.shutdown(100));
  app.server.listen(0, "127.0.0.1");
  await once(app.server, "listening");
  const origin = `http://127.0.0.1:${(app.server.address() as AddressInfo).port}`;
  return { ...app, origin };
}

test.each(["0", "65536", "1.5", "NaN", " 3000", "-1", ""])(
  "reject invalid PORT %s",
  (value) => {
    expect(() => portFromEnvironment(value)).toThrow();
  },
);

test("health, HEAD, static caching and missing assets", async () => {
  const { origin } = await fixture();
  expect((await fetch(`${origin}/healthz`)).status).toBe(200);
  expect((await fetch(`${origin}/healthz`, { method: "POST" })).status).toBe(
    405,
  );
  const asset = await fetch(`${origin}/assets/app.js`);
  expect(asset.headers.get("cache-control")).toContain("immutable");
  expect(asset.headers.get("content-type")).toContain("javascript");
  expect(await asset.text()).toBe("export {};");
  const head = await fetch(`${origin}/assets/app.js`, { method: "HEAD" });
  expect(head.status).toBe(200);
  expect(await head.text()).toBe("");
  expect((await fetch(`${origin}/assets/missing.js`)).status).toBe(404);
  expect((await fetch(`${origin}/missing`)).headers.get("cache-control")).toBe(
    "private, no-store",
  );
});

test.each([
  "/.env",
  "/%2e%2e/private.txt",
  "/%5cprivate.txt",
  "/%00",
  "/%ZZ",
  "/leak.txt",
])(
  "no traversal, hidden files, malformed paths or symlink escape: %s",
  async (path) => {
    const { origin } = await fixture();
    const result = await new Promise<{ status: number; body: string }>(
      (resolve, reject) => {
        const req = request(origin, { path }, (response) => {
          let body = "";
          response.setEncoding("utf8");
          response.on("data", (chunk: string) => {
            body += chunk;
          });
          response.on("end", () => {
            resolve({ status: response.statusCode ?? 0, body });
          });
        });
        req.on("error", reject);
        req.end();
      },
    );
    expect([400, 404]).toContain(result.status);
    expect(result.body).not.toContain("private-file-sentinel");
  },
);

test("unexpected handler failure returns a generic 500", async () => {
  vi.spyOn(console, "error").mockImplementation(() => undefined);
  const app = createAppServer(
    applicationListener(tmpdir(), () => {
      throw new Error("private-error-sentinel");
    }),
  );
  cleanups.push(() => app.shutdown(100));
  app.server.listen(0, "127.0.0.1");
  await once(app.server, "listening");
  const response = await fetch(
    `http://127.0.0.1:${(app.server.address() as AddressInfo).port}/missing-test-route`,
  );
  expect(response.status).toBe(500);
  expect(await response.text()).toBe("Internal server error");
  expect(console.error).toHaveBeenCalledWith("HTTP request failed");
});

test.each([true, false])(
  "shutdown drains or bounds in-flight work (complete=%s)",
  async (complete) => {
    let finish: (() => void) | undefined;
    let entered: (() => void) | undefined;
    const active = new Promise<void>((resolve) => {
      entered = resolve;
    });
    const app = createAppServer((_request, response) => {
      finish = () => response.end("finished");
      entered?.();
    });
    cleanups.push(() => app.shutdown(100));
    app.server.listen(0, "127.0.0.1");
    await once(app.server, "listening");
    const pending = fetch(
      `http://127.0.0.1:${(app.server.address() as AddressInfo).port}`,
    )
      .then((r) => r.text())
      .catch(() => "closed");
    await active;
    const stopping = app.shutdown(100);
    expect(app.shutdown(100)).toBe(stopping);
    if (complete) finish?.();
    expect(await stopping).toBe(complete);
    expect(await pending).toBe(complete ? "finished" : "closed");
  },
);
