# {{DISPLAY_NAME}}

CSR frontend: React Router Framework Mode, React 19.3, TypeScript 7, Tailwind 4
and checked-in shadcn/ui Base UI/nova Button and Dialog.

## Package Manager

Use Node 24.19.x and pnpm 11.21.0 with the committed `pnpm-lock.yaml`.
No registry access is performed by the generator. Install dependencies afterwards:

```sh
pnpm install --frozen-lockfile
pnpm dev
pnpm verify
pnpm build
pnpm preview --host 127.0.0.1
```

`typecheck` runs React Router type generation and the TS 7.0.2 compiler explicitly.
`typescript` is an alias to Microsoft's TS 6 compiler API for typescript-eslint
8.70 compatibility; it is **not** the project type checker. `@typescript/native`
aliases TS 7.0.2. Do not use bare `tsc` as the quality gate. Keep both roles
tested when upgrading; lint's TS 6 parser does not promise support for future TS 7 syntax.
Use `pnpm install --no-frozen-lockfile` or `make lockfile-update` only when deliberately
updating dependencies, and commit the resulting lockfile.

## Structure

- `app/root.tsx`: shared document, loading shell and safe error boundary.
- `app/features/`, `app/components/ui/`, `app/lib/`: shared UI and pure code.
- `app/routes.ts`, `app/routes/`, `react-router.config.ts`: CSR routing preset.
- `vitest.config.ts`: isolated component tests; no framework build plugin in tests.
- `components.json`: shadcn configuration. Component sources and license are
  checked in. Generation does not invoke the shadcn CLI.
- `build/client/`: static deployment output, not `dist/`.

The starter deliberately has no mock API, auth, database, or query layer. Add a
typed API client when an actual backend contract exists. Shared code must not
read `window` at module scope: even CSR builds render a loading shell at build time.

## Quality Checks

`pnpm verify` checks formatting, typed lint, component tests, route types and
production build. `pnpm browser:smoke` tests navigation, refresh, dialog keyboard
interaction and narrow/desktop layouts against a development server.
`pnpm browser:smoke:build` builds and tests static production artifacts using Vite
preview; this is a local check, not a production server recommendation. Install
bundled Chromium with `pnpm browser:install`, or explicitly select an installed
Chrome with `PLAYWRIGHT_CHANNEL=chrome` for local checks.
`make browser-smoke-production` tests the actual production Nginx image, including
missing assets. Raw CSR HTML contains a loading shell, not route content; this is
not an SEO/SSG/SSR preset. Unknown navigation paths receive HTTP 200 from the SPA
fallback and then render a client-side not-found page. Missing assets return 404.

## Docker Workflow

```sh
make bootstrap
make dev
make verify
make docker-build
make docker-run
make browser-smoke-production
```

The default development image stays relatively light: browser binaries install
via `make browser-install`. `make bootstrap-full` preloads them;
`DEV_DOCKERFILE=Dockerfile.dev.full make dev` selects that image.
Static production copies only `build/client/`; no Node runtime or node_modules.

## Available Commands

Common commands remain `bootstrap`, `doctor`, `lint`, `test`, `verify`, `build`,
`clean` and `help`. Additional commands: `install`, `dev`, `dev-shell`, `typecheck`,
`preview`, `format`, `format-check`, `browser-install`, `browser-smoke`,
`browser-smoke-production`, `docker-build`, `docker-run`, `lockfile-update`.

## Worktree isolation

Compose names, images, node_modules, pnpm/browser caches and cleanup are scoped to
the worktree. Override `DEV_HOST_PORT` and `HOST_PORT` when running worktrees together.
`make worktree-info` explains names/paths; `make worktree-doctor` checks ports and
prints suggested overrides; `make worktree-compose-config` renders Compose config.
`make clean-worktree` removes only the current Compose project's volumes and smoke
container. Source files are not removed. Local pnpm commands use `.pnpm-store/`.

## Runtime Configuration

This static preset has no private runtime environment. Any `VITE_*` variable
referenced by application code is public and embedded at build time. Never put
secrets there. Changing a container environment does not rewrite bundled assets.
Changing the rendering architecture requires a deliberate migration, not an env flag.

## Docker Files

`Dockerfile` builds static resources and serves them with Nginx.
`Dockerfile.dev` / `Dockerfile.dev.full` provide Node tooling.
`compose.dev.yaml` owns worktree-scoped mounts and ports.
`nginx.conf` supplies SPA fallback and non-fallback asset 404s.
