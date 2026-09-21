import { createServer } from "node:http";
import type { RequestListener, ServerResponse } from "node:http";
import { createReadStream } from "node:fs";
import { realpath, stat } from "node:fs/promises";
import { extname, resolve, sep } from "node:path";
import { pipeline } from "node:stream/promises";
import { pathToFileURL } from "node:url";
import { createRequestListener } from "@react-router/node";
import type { ServerBuild } from "react-router";

const mime: Record<string, string> = {
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".jpg": "image/jpeg",
  ".webp": "image/webp",
  ".woff2": "font/woff2",
  ".txt": "text/plain; charset=utf-8",
  ".json": "application/json",
};

export function portFromEnvironment(value = "3000") {
  if (!/^[0-9]+$/.test(value) || Number(value) < 1 || Number(value) > 65535) {
    throw new Error("PORT must be an integer between 1 and 65535");
  }
  return Number(value);
}

function reply(response: ServerResponse, status: number, message: string) {
  response.writeHead(status, { "Content-Type": "text/plain; charset=utf-8" });
  response.end(message);
}

export async function loadApplication(root = process.cwd()) {
  const build = (await import(
    pathToFileURL(resolve(root, "build/server/index.js")).href
  )) as ServerBuild;
  return createRequestListener({ build, mode: "production" });
}

export function applicationListener(
  clientRoot: string,
  application: RequestListener,
): RequestListener {
  return (request, response) => {
    response.setHeader("Cache-Control", "private, no-store");
    response.setHeader("X-Content-Type-Options", "nosniff");
    const serve = async () => {
      // No implicit X-Forwarded-* trust. Configure TLS/origin policy at your proxy.
      delete request.headers["x-forwarded-host"];
      delete request.headers["x-forwarded-proto"];
      let pathname: string;
      try {
        pathname = decodeURIComponent((request.url ?? "/").split("?")[0]);
      } catch {
        reply(response, 400, "Bad request");
        return;
      }
      if (
        !pathname.startsWith("/") ||
        /[\\\u0000-\u001f\u007f]/u.test(pathname) ||
        pathname.split("/").some((part) => part.startsWith("."))
      ) {
        reply(response, 400, "Bad request");
        return;
      }
      if (pathname === "/healthz") {
        if (request.method !== "GET" && request.method !== "HEAD") {
          response.setHeader("Allow", "GET, HEAD");
          reply(response, 405, "Method not allowed");
          return;
        }
        reply(response, 200, "ok\n");
        return;
      }
      const root = await realpath(clientRoot);
      const candidate = resolve(root, `.${pathname}`);
      if (candidate.startsWith(root + sep)) {
        try {
          const canonical = await realpath(candidate);
          if (!canonical.startsWith(root + sep)) {
            reply(response, 404, "Not found");
            return;
          }
          const file = await stat(canonical);
          if (file.isFile()) {
            if (request.method !== "GET" && request.method !== "HEAD") {
              response.setHeader("Allow", "GET, HEAD");
              reply(response, 405, "Method not allowed");
              return;
            }
            response.setHeader(
              "Content-Type",
              mime[extname(canonical)] ?? "application/octet-stream",
            );
            response.setHeader("Content-Length", file.size);
            response.setHeader(
              "Cache-Control",
              pathname.startsWith("/assets/")
                ? "public, max-age=31536000, immutable"
                : "public, max-age=0, must-revalidate",
            );
            if (request.method === "HEAD") {
              response.end();
              return;
            }
            await pipeline(createReadStream(canonical), response);
            return;
          }
        } catch (error) {
          if (response.destroyed) return;
          const code = (error as NodeJS.ErrnoException).code;
          if (code !== "ENOENT" && code !== "ENOTDIR") throw error;
        }
      }
      if (pathname.startsWith("/assets/")) {
        reply(response, 404, "Not found");
        return;
      }
      await Promise.resolve(application(request, response));
    };
    void serve().catch(() => {
      console.error("HTTP request failed");
      if (response.headersSent) response.destroy();
      else reply(response, 500, "Internal server error");
    });
  };
}

export function createAppServer(listener: RequestListener) {
  let stopping = false;
  const server = createServer(
    { requestTimeout: 30_000, headersTimeout: 10_000, keepAliveTimeout: 5000 },
    (request, response) => {
      const socket = request.socket;
      response.on("finish", () => {
        if (stopping) socket.end();
      });
      if (stopping) {
        response.setHeader("Connection", "close");
        reply(response, 503, "Shutting down");
      } else {
        void listener(request, response);
      }
    },
  );
  let pending: Promise<boolean> | undefined;
  function shutdown(timeout = 10_000) {
    pending ??= new Promise<boolean>((resolveShutdown) => {
      stopping = true;
      const timer = setTimeout(() => {
        server.closeAllConnections();
        resolveShutdown(false);
      }, timeout);
      server.close(() => {
        clearTimeout(timer);
        resolveShutdown(true);
      });
    });
    return pending;
  }
  return { server, shutdown };
}
