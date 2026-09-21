// @vitest-environment node
import type { EntryContext } from "react-router";
import { renderToPipeableStream } from "react-dom/server";
import type { RenderToPipeableStreamOptions } from "react-dom/server";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import handleRequest from "./entry.server";

vi.mock("react-dom/server", () => ({ renderToPipeableStream: vi.fn() }));

let callbacks: RenderToPipeableStreamOptions;
const abort = vi.fn();
beforeEach(() => {
  vi.useFakeTimers();
  vi.mocked(renderToPipeableStream).mockImplementation((_node, options) => {
    callbacks = options ?? {};
    return {
      abort,
      pipe: (body) => {
        body.end("<html>safe</html>");
        return body;
      },
    };
  });
});
afterEach(() => {
  vi.useRealTimers();
  vi.clearAllMocks();
});

function render(signal?: AbortSignal) {
  return handleRequest(
    new Request("http://localhost/", { signal }),
    200,
    new Headers(),
    {} as EntryContext,
  );
}

test("HEAD preserves status without rendering", async () => {
  const response = await handleRequest(
    new Request("http://localhost/", { method: "HEAD" }),
    404,
    new Headers(),
    {} as EntryContext,
  );
  expect(response.status).toBe(404);
  expect(await response.text()).toBe("");
  expect(renderToPipeableStream).not.toHaveBeenCalled();
});

test("render errors retain 500 and private cache headers", async () => {
  const pending = render();
  callbacks.onError?.(new Error("private-error"), { componentStack: "" });
  callbacks.onAllReady?.();
  const response = await pending;
  expect(response.status).toBe(500);
  expect(response.headers.get("cache-control")).toBe("private, no-store");
  expect(await response.text()).toBe("<html>safe</html>");
  expect(vi.getTimerCount()).toBe(0);
});

test("shell failures clear the deadline and redact the error", async () => {
  const result = expect(render()).rejects.toThrow("Rendering failed");
  callbacks.onShellError?.(new Error("private-error"));
  await result;
  expect(vi.getTimerCount()).toBe(0);
});

test.each([true, false])(
  "client cancellation before/after render starts: %s",
  async (before) => {
    const controller = new AbortController();
    if (before) controller.abort();
    const result = expect(render(controller.signal)).rejects.toThrow(
      "Rendering cancelled",
    );
    if (!before) controller.abort();
    await result;
    expect(abort).toHaveBeenCalled();
    expect(vi.getTimerCount()).toBe(0);
  },
);

test("render deadline aborts work and rejects", async () => {
  const result = expect(render()).rejects.toThrow("Rendering cancelled");
  await vi.advanceTimersByTimeAsync(6000);
  await result;
  expect(abort).toHaveBeenCalled();
  expect(vi.getTimerCount()).toBe(0);
});
