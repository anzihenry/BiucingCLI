import { requireSiteOrigin } from "@/lib/site";

export function loader() {
  const origin = requireSiteOrigin(process.env.SITE_URL);
  return new Response(
    `User-agent: *\nAllow: /\nSitemap: ${origin}/sitemap.xml\n`,
    {
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    },
  );
}
