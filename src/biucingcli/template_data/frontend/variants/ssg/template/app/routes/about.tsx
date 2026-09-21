import { Link } from "react-router";
import type { Route } from "./+types/about";
import { project } from "@/lib/project";
import { pageData } from "@/lib/content.server";
import { pageMeta } from "@/lib/metadata";

export function loader() {
  return pageData("/about");
}
export function meta({ loaderData: data }: Route.MetaArgs) {
  return pageMeta(
    `About | ${project.title}`,
    "Static HTML, client navigation and no runtime Node server.",
    data?.canonical,
  );
}
export default function About() {
  return (
    <main className="mx-auto flex max-w-4xl flex-col gap-6 px-6 py-12">
      <h1 className="text-3xl font-semibold">About the application</h1>
      <p>This SSG preset generates HTML and navigation data at build time.</p>
      <Link to="/" className="underline underline-offset-4">
        Return home
      </Link>
    </main>
  );
}
