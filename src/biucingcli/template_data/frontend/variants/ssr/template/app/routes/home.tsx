import { Link } from "react-router";
import type { Route } from "./+types/home";
import { Welcome } from "@/features/welcome";
import { requestSnapshot } from "@/lib/request.server";

export function loader({ request }: Route.LoaderArgs) {
  return requestSnapshot(request);
}

export default function Home({ loaderData }: Route.ComponentProps) {
  return (
    <main className="mx-auto flex max-w-4xl flex-col gap-8 px-6 py-12">
      <Welcome />
      <section aria-label="Request snapshot" className="break-words">
        <h2 className="text-xl font-semibold">Rendered for this request</h2>
        <p>
          Visitor: <span data-testid="visitor">{loaderData.visitor}</span>
        </p>
        <p>
          Request: <span data-testid="request-id">{loaderData.requestId}</span>
        </p>
        <p>
          Rendered at: <time>{loaderData.renderedAt}</time>
        </p>
      </section>
      <nav aria-label="Main">
        <Link to="/about" className="underline underline-offset-4">
          About the application
        </Link>
      </nav>
    </main>
  );
}
