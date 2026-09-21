import { PassThrough } from "node:stream";
import { createReadableStreamFromReadable } from "@react-router/node";
import { ServerRouter } from "react-router";
import type { EntryContext } from "react-router";
import { renderToPipeableStream } from "react-dom/server";

export const streamTimeout = 5000;

export default function handleRequest(
  request: Request,
  status: number,
  headers: Headers,
  context: EntryContext,
) {
  headers.set("Cache-Control", "private, no-store");
  headers.set("Content-Type", "text/html; charset=utf-8");
  if (request.method === "HEAD") return new Response(null, { status, headers });
  return new Promise<Response>((resolve, reject) => {
    const body = new PassThrough();
    let cancelled = false;
    const cleanup = () => {
      clearTimeout(timer);
      request.signal.removeEventListener("abort", cancel);
    };
    const cancel = () => {
      cancelled = true;
      cleanup();
      reject(new Error("Rendering cancelled"));
      stream.abort();
      body.destroy();
    };
    body.on("close", () => {
      cleanup();
      stream.abort();
    });
    body.on("error", cleanup);
    const stream = renderToPipeableStream(
      <ServerRouter context={context} url={request.url} />,
      {
        // Wait for all content so render failures retain an accurate HTTP status.
        // Streaming Suspense latency tuning is deliberately outside this starter.
        onAllReady() {
          if (cancelled) return;
          clearTimeout(timer);
          resolve(
            new Response(createReadableStreamFromReadable(body), {
              status,
              headers,
            }),
          );
          stream.pipe(body);
        },
        onShellError() {
          cleanup();
          reject(new Error("Rendering failed"));
        },
        onError() {
          status = 500;
        },
      },
    );
    const timer = setTimeout(cancel, streamTimeout + 1000);
    request.signal.addEventListener("abort", cancel, { once: true });
    if (request.signal.aborted) cancel();
  });
}

export function handleDataRequest(response: Response) {
  response.headers.set("Cache-Control", "private, no-store");
  return response;
}

export function handleError(
  _error: unknown,
  { request }: { request: Request },
) {
  if (!request.signal.aborted) console.error("SSR request failed");
}
