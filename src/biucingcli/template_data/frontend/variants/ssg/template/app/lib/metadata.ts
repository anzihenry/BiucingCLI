import type { MetaDescriptor } from "react-router";

export function pageMeta(
  title: string,
  description: string,
  canonical?: string,
): MetaDescriptor[] {
  return [
    { title },
    { name: "description", content: description },
    { property: "og:title", content: title },
    { property: "og:description", content: description },
    { property: "og:type", content: "website" },
    ...(canonical
      ? [
          {
            tagName: "link",
            rel: "canonical",
            href: canonical,
          } as MetaDescriptor,
          { property: "og:url", content: canonical },
        ]
      : []),
  ];
}
