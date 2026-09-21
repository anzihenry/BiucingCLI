import type { Config } from "@react-router/dev/config";
import { rm } from "node:fs/promises";
import { join } from "node:path";
import { contentPaths } from "./app/content";
import { requireSiteOrigin } from "./app/lib/site";

export default {
  ssr: false,
  prerender() {
    requireSiteOrigin(process.env.SITE_URL);
    return [...contentPaths(), "/sitemap.xml", "/robots.txt"];
  },
  async buildEnd({ reactRouterConfig }) {
    // This preset has real static 404s, never an arbitrary-path SPA fallback.
    await rm(
      join(reactRouterConfig.buildDirectory, "client", "__spa-fallback.html"),
      { force: true },
    );
  },
} satisfies Config;
