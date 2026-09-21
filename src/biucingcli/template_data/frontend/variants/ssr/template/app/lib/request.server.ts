import { randomUUID } from "node:crypto";
import { data } from "react-router";

// Never return process.env, credentials, or a backend response wholesale.
// A real backend client can use this private value; it is not public loader data.
function privateConfiguration() {
  const token = process.env.SSR_PRIVATE_TOKEN ?? "";
  if (token.length > 4096) throw new Error("Invalid private configuration");
  return { token };
}

export function requestSnapshot(request: Request) {
  privateConfiguration();
  const values = new URL(request.url).searchParams.getAll("visitor");
  const visitor = values[0] ?? "Guest";
  if (
    values.length > 1 ||
    visitor.length > 80 ||
    /[\u0000-\u001f\u007f]/u.test(visitor)
  ) {
    // React Router intentionally accepts thrown data responses.
    // eslint-disable-next-line @typescript-eslint/only-throw-error
    throw data("Invalid visitor", { status: 400 });
  }
  return {
    visitor,
    requestId: randomUUID(),
    renderedAt: new Date().toISOString(),
  };
}
