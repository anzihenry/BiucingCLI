import { Link } from "react-router";
import { Welcome } from "@/features/welcome";

export default function Home() {
  return (
    <main className="mx-auto flex max-w-4xl flex-col gap-8 px-6 py-12">
      <Welcome />
      <nav aria-label="Main">
        <Link to="/about" className="underline underline-offset-4">
          About the application
        </Link>
      </nav>
    </main>
  );
}
