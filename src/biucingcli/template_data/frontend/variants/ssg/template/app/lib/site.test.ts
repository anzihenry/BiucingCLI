import { describe, expect, it } from "vitest";
import { parseSiteOrigin, requireSiteOrigin } from "./site";
import { contentPaths } from "../content";
import { findArticle } from "./content.server";

describe("SSG build contract", () => {
  it("requires an explicit public HTTPS origin for production", () => {
    expect(parseSiteOrigin(undefined)).toBeUndefined();
    expect(requireSiteOrigin("https://example.com/")).toBe(
      "https://example.com",
    );
    expect(() => requireSiteOrigin(undefined)).toThrow("Set SITE_URL");
    for (const value of [
      "",
      "localhost",
      "https://a&b.example.com",
      "https://-bad.example.com",
      "http://example.com",
      "https://localhost",
      "https://a.localhost",
      "https://127.0.0.1",
      "https://[::1]",
      "https://user:pass@example.com",
      "https://example.com/path",
      "https://example.com?x=1",
      "https://example.com#x",
      "https://example.com:8443",
      " https://example.com",
    ]) {
      expect(() => requireSiteOrigin(value), value).toThrow();
    }
  });
  it("enumerates every content slug and rejects missing content", () => {
    expect(contentPaths()).toEqual([
      "/",
      "/about",
      "/articles/hello-static",
      "/articles/extend-content",
    ]);
    expect(findArticle("hello-static").title).toBe("Hello, static content");
    try {
      findArticle("missing");
      expect.unreachable();
    } catch (error) {
      expect(error).toBeInstanceOf(Response);
      expect((error as Response).status).toBe(404);
    }
  });
});
