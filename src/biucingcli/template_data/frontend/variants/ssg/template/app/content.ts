// Public, build-time content. Add a unique slug here to prerender another page.
export const articles = [
  {
    slug: "hello-static",
    title: "Hello, static content",
    description: "HTML and navigation data generated together at build time.",
    body: "This article is available in the original HTML, even without JavaScript.",
  },
  {
    slug: "extend-content",
    title: "Extend your content",
    description: "Add content, rebuild, and deploy the complete static output.",
    body: "New slugs need a new build. There is no runtime content server or automatic fallback.",
  },
] as const;

export function contentPaths() {
  const slugs = articles.map((article) => article.slug);
  if (
    new Set(slugs).size !== slugs.length ||
    slugs.some((slug) => !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug))
  ) {
    throw new Error("Content slugs must be unique, lowercase URL segments.");
  }
  return ["/", "/about", ...slugs.map((slug) => `/articles/${slug}`)];
}
