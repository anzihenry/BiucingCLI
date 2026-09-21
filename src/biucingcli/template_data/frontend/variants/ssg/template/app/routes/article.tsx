import { Link } from "react-router";
import type { Route } from "./+types/article";
import { findArticle, pageData } from "@/lib/content.server";
import { pageMeta } from "@/lib/metadata";
import { project } from "@/lib/project";

export function loader({ params }: Route.LoaderArgs) {
  const article = findArticle(params.slug);
  return { article, ...pageData(`/articles/${article.slug}`) };
}
export function meta({ loaderData: data }: Route.MetaArgs) {
  return data
    ? pageMeta(
        `${data.article.title} | ${project.title}`,
        data.article.description,
        data.canonical,
      )
    : [{ title: "Page not found" }, { name: "robots", content: "noindex" }];
}
export default function Article({ loaderData }: Route.ComponentProps) {
  return (
    <main className="mx-auto flex max-w-4xl flex-col gap-6 px-6 py-12">
      <h1 className="text-3xl font-semibold">{loaderData.article.title}</h1>
      <p>{loaderData.article.body}</p>
      <p>
        Built at <time data-testid="built-at">{loaderData.builtAt}</time>
      </p>
      <Link to="/" className="underline underline-offset-4">
        Return home
      </Link>
    </main>
  );
}
