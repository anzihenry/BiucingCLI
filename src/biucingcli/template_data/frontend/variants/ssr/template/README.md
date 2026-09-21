# {{PROJECT_NAME}}

React Router Framework SSR, React 19.3, TypeScript 7, Tailwind 4 and checked-in
shadcn/ui components. This preset serves request-time HTML with a self-hosted
Node 24 server. It is not a database, authentication system or business backend.

## Docker-first workflow

```bash
make bootstrap
make install
make dev
make verify
make build
make preview
make browser-smoke
make browser-smoke-production
make docker-run
```

The shared lockfile is authoritative: use frozen installs. `make lockfile-update`
is an intentional dependency maintenance action. Type checking runs TypeScript
7.0.2 through `@typescript/native`; ESLint uses the separate TypeScript 6 API
compatibility dependency. Do not replace the type checker with the lint API.

Without Docker, use Node 24.19.0 and pnpm 11.21.0: `pnpm install --frozen-lockfile`,
`pnpm verify`, `pnpm dev`. After building, `pnpm preview` serves actual SSR via
Vite's preview host; `node server/index.ts` runs the production Node service.
`pnpm browser:smoke:build` tests that Node service, not Vite preview. Install the
browser first with `pnpm browser:install`. Production smoke also checks clean
SIGTERM exit. Runtime unit tests cover draining and forcibly closing requests.

## Request and environment boundaries

The home loader accepts one optional `visitor` query (at most 80 UTF-16 code
units, no controls), then creates a new request ID and timestamp on every call.
These public fields are serialized by React Router, not hand-built HTML/JSON.
React escapes displayed input. Client navigation invokes loaders again; request
snapshots are never stored in shared module state. Query input is not identity.

Server-only code lives in `app/lib/*.server.ts`. `SSR_PRIVATE_TOKEN` demonstrates
a private integration setting; it is not returned by the loader. Never return
the entire environment or backend payload. `VITE_*` is public, build-time client
configuration, never a place for credentials. Runtime Node does not auto-load
`.env`; inject variables using your deployment's secret manager or explicit
`docker run --env-file /path/to/private.env ...`. Private files are excluded from
the Docker build context. No secret is needed to build.

Compose forwards `SSR_PRIVATE_TOKEN` from the shell or its local `.env`;
`make docker-run` forwards the shell variable without embedding its value in
the command. `CONTAINER_PORT` also sets the runtime's `PORT` when using Make.

HTML and React Router data responses use `private, no-store`. Only fingerprinted
`/assets/` files use long-lived immutable caching; public files revalidate. Do not
enable shared HTML/data caching without a deliberate per-user/cache-key design.

## Deployment and limits

Production defaults: `HOST=0.0.0.0`, `PORT=3000`; bind host accepts explicit IPv4/
IPv6 addresses listed in `server/index.ts`. The image runs as non-root `node` and
contains production dependencies, compiled client/server output and the small
Node runtime. It does not contain application source or development dependencies.
Node 24 runs the runtime's erasable TypeScript directly; `pnpm typecheck` checks it.

`GET /healthz` is process readiness, not an upstream dependency check. SIGTERM and
SIGINT stop acceptance, drain requests for up to 10 seconds, then close remaining
connections (exit 1 if forced). Allow at least 15 seconds termination grace at the
orchestrator. Request/header timeouts bound slow input; rendering waits for all
content with a six-second abort deadline to preserve render error statuses.

Deploy behind a TLS reverse proxy with an explicit allowed-host policy. The
server does not trust forwarded host/protocol headers automatically. Configure
origin/secure-cookie/proxy trust deliberately before adding login or absolute
redirects. Generic error pages avoid private details; add your own redacted
observability, dependency readiness, rate limits and CSRF/auth before business
mutations. Streaming latency tuning, multi-instance sessions, load tests and
other browser engines are not included.

Use `make worktree-info` and `make worktree-doctor`; set separate `DEV_HOST_PORT`
and `HOST_PORT` for parallel worktrees. `make clean-worktree` removes only this
worktree's Compose resources and production smoke container, including caches.

To add a page, register it in `app/routes.ts`, add its loader and route component,
then test direct HTML, HTTP status, client navigation and refresh. Changes to
shared UI must still pass the CSR and SSG gates. See `THIRD_PARTY_NOTICES.md` for
checked-in component attribution.
