import { contentPaths } from "@/content";
import { requireSiteOrigin } from "@/lib/site";

export function loader() {
  const origin = requireSiteOrigin(process.env.SITE_URL);
  const entries = contentPaths()
    .map((path) => `<url><loc>${origin}${path}</loc></url>`)
    .join("");
  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${entries}</urlset>`,
    {
      headers: { "Content-Type": "application/xml; charset=utf-8" },
    },
  );
}
