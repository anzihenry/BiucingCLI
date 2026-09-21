// @vitest-environment node
import { afterEach, expect, test, vi } from "vitest";
import { requestSnapshot } from "./request.server";

afterEach(() => {
  vi.unstubAllEnvs();
});

test("request snapshots are independent and expose only public fields", () => {
  vi.stubEnv("SSR_PRIVATE_TOKEN", "private-unit-sentinel");
  const first = requestSnapshot(new Request("http://localhost/?visitor=Alice"));
  const second = requestSnapshot(new Request("http://localhost/?visitor=Bob"));
  expect(first.visitor).toBe("Alice");
  expect(second.visitor).toBe("Bob");
  expect(first.requestId).not.toBe(second.requestId);
  expect(Object.keys(first).sort()).toEqual([
    "renderedAt",
    "requestId",
    "visitor",
  ]);
  expect(JSON.stringify(first)).not.toContain("private-unit-sentinel");
});

test.each([
  "visitor=a&visitor=b",
  `visitor=${"x".repeat(81)}`,
  "visitor=%00",
  "visitor=%0A",
])("invalid input fails closed: %s", (query) => {
  expect(() =>
    requestSnapshot(new Request(`http://localhost/?${query}`)),
  ).toThrow();
});

test("invalid private configuration throws without including its contents", () => {
  vi.stubEnv("SSR_PRIVATE_TOKEN", "private-unit-sentinel".repeat(300));
  expect(() => requestSnapshot(new Request("http://localhost/"))).toThrow(
    "Invalid private configuration",
  );
});
