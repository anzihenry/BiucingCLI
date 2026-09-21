import { articles } from "../content";
import { parseSiteOrigin, requireSiteOrigin } from "./site";

// Evaluated by the build server, serialized into HTML and .data artifacts.
// Static requests never evaluate this again; changes require a fresh deployment.
const builtAt = new Date().toISOString();

export function pageData(path: string) {
  const origin =
    process.env.NODE_ENV === "production"
      ? requireSiteOrigin(process.env.SITE_URL)
      : parseSiteOrigin(process.env.SITE_URL);
  return { builtAt, canonical: origin ? `${origin}${path}` : undefined };
}

export function findArticle(slug: string | undefined) {
  const article = articles.find((entry) => entry.slug === slug);
  if (!article) {
    // React Router handles thrown HTTP responses as route errors.
    // eslint-disable-next-line @typescript-eslint/only-throw-error
    throw new Response("Not found", { status: 404 });
  }
  return article;
}
