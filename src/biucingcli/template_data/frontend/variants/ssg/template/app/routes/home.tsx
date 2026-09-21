import { Link } from "react-router";
import type { Route } from "./+types/home";
import { Welcome } from "@/features/welcome";
import { articles } from "@/content";
import { project } from "@/lib/project";
import { pageData } from "@/lib/content.server";
import { pageMeta } from "@/lib/metadata";

export function loader() {
  return pageData("/");
}

export function meta({ loaderData: data }: Route.MetaArgs) {
  return pageMeta(
    project.title,
    "A pre-rendered site with interactive React components.",
    data?.canonical,
  );
}

export default function Home({ loaderData }: Route.ComponentProps) {
  return (
    <main className="mx-auto flex max-w-4xl flex-col gap-8 px-6 py-12">
      <Welcome />
      <nav aria-label="Main" className="flex flex-col gap-3">
        <Link to="/about" className="underline underline-offset-4">
          About the application
        </Link>
        {articles.map((article) => (
          <Link
            key={article.slug}
            to={`/articles/${article.slug}`}
            className="underline underline-offset-4"
          >
            {article.title}
          </Link>
        ))}
      </nav>
      <p>
        Built at <time data-testid="built-at">{loaderData.builtAt}</time>
      </p>
    </main>
  );
}
