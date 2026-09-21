// Pure validation shared by the build configuration and server-only loaders.
export function parseSiteOrigin(raw: string | undefined): string | undefined {
  if (!raw) return undefined;
  let url: URL;
  try {
    url = new URL(raw);
  } catch {
    throw new Error("SITE_URL must be an absolute HTTPS origin.");
  }
  if (
    raw !== raw.trim() ||
    url.protocol !== "https:" ||
    url.username ||
    url.password ||
    url.search ||
    url.hash ||
    url.pathname !== "/" ||
    url.port ||
    url.hostname.length > 253 ||
    !/^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(
      url.hostname,
    ) ||
    url.hostname.endsWith(".localhost") ||
    url.hostname.endsWith(".local") ||
    url.hostname.endsWith(".") ||
    /^[\d.]+$/.test(url.hostname) ||
    url.hostname.includes(":")
  ) {
    throw new Error(
      "SITE_URL must be a public HTTPS origin without credentials, path, port, query or fragment.",
    );
  }
  return url.origin;
}

export function requireSiteOrigin(raw: string | undefined): string {
  const origin = parseSiteOrigin(raw);
  if (!origin)
    throw new Error(
      "Set SITE_URL to your public HTTPS origin before building SSG.",
    );
  return origin;
}
