import { env } from "../../config/env";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function buildUrl(path: string): string {
  if (!env.apiBaseUrl) {
    throw new Error("VITE_API_BASE_URL is not configured");
  }

  return new URL(path, `${env.apiBaseUrl.replace(/\/+$/, "")}/`).toString();
}

export async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(buildUrl(path), {
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new ApiError(`Request failed for ${path}`, response.status);
  }

  return (await response.json()) as T;
}
