import { Link } from "react-router";

export default function About() {
  return (
    <main className="mx-auto flex max-w-4xl flex-col gap-6 px-6 py-12">
      <h1 className="text-3xl font-semibold">About the application</h1>
      <p>
        This SSR preset renders HTML on Node for each request. It does not
        include a business backend or authentication.
      </p>
      <Link to="/" className="underline underline-offset-4">
        Return home
      </Link>
    </main>
  );
}
