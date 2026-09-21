# {{PROJECT_NAME}} — SSG

React Router Framework Mode, React 19.3, TypeScript 7, Tailwind 4 and checked-in
shadcn/ui components. HTML **and** client-navigation `.data` files are generated
at build time. Deploy the entire `build/client/` directory; no runtime Node server
or business backend is required. This is not SSR or a CSR fallback for unknown URLs.

## Start and verify

```bash
make bootstrap
make install
make dev
```

Development can run without an origin; canonical URLs are then omitted. To build,
set your actual public HTTPS origin (not localhost, a URL path or credentials):

```bash
export SITE_URL=https://www.example.com
make verify
make browser-smoke
make browser-smoke-production
```

`SITE_URL` is public build-time configuration. It is intentionally required rather
than silently emitting localhost metadata. Rebuild after changing it. Compose
also reads `.env`, but export the value for `make docker-build` and local pnpm.
The production image only receives it as a builder argument, not runtime config.

Without Docker, use Node 24.19.x and pnpm 11.21.0:

```bash
pnpm install --frozen-lockfile
pnpm peers check
export SITE_URL=https://www.example.com
pnpm verify
pnpm browser:install
pnpm browser:smoke
pnpm browser:smoke:build
```

Vite preview validates interactions, not Nginx status/rewrites. Run
`make browser-smoke-production` for real static HTML, per-page metadata, no-JS
content, stable build data, sitemap/robots, navigation payloads and actual 404s.
The shared tests cover counter/dialog keyboard focus, desktop/mobile and refresh.
`PLAYWRIGHT_CHANNEL=chrome` can select local Chrome explicitly for pnpm tests.

## Content and deployment contract

- Add public entries to `app/content.ts`; each unique lowercase slug becomes an
  `/articles/<slug>` prerender path. `contentPaths()` is the source for both the
  build and sitemap. New route families must be added to `app/routes.ts` and the
  path list. No automatic arbitrary dynamic-route generation is provided.
- Loaders run at build time. Only public fields should be returned: serialized
  loader data is downloadable. `builtAt` demonstrates a build snapshot, not a
  request timestamp. Never put secrets into content, loader output or `VITE_*`.
- Metadata uses the configured origin, never the incoming request host/query.
  Each page gets one title, a description, canonical and Open Graph metadata.
- Deploy HTML, assets, `.data`, sitemap, robots and `404.html` as one release.
  Do not rewrite missing paths or `.data` requests to the home page. Nginx serves
  known `/path` and `/path/` from `/path/index.html`, with HTTP 404 for unknown
  paths/assets and a plain noindex error page. Other hosts must mirror this policy.
- The build removes the framework SPA fallback. Runtime images copy only static
  client artifacts; the intermediate build/server output is not a deployment.
- No CMS, request-time API, forms/actions, authentication or incremental rebuild
  service is installed. Add those only with an explicit architecture decision.

## Worktree isolation

```bash
make worktree-info
make worktree-doctor
make worktree-compose-config
make dev DEV_HOST_PORT=15173
make browser-smoke-production HOST_PORT=18080
make clean-worktree
```

Compose names, image tags and caches are scoped to the checkout. `clean-worktree`
removes only this project's containers/network/volumes; it retains source files
and built images. `make bootstrap-full` optionally preinstalls browsers in the dev
image. Normal `make browser-install` uses the isolated browser-cache volume.

The shared toolchain checks formatting, typed ESLint (including a negative
no-floating-promises control), TS 7, route types, Vitest and the production build.
TS 6 exists only as a compiler-API compatibility alias for typescript-eslint;
typecheck explicitly invokes TS 7. Dependencies and lockfile are shared with CSR.
See `THIRD_PARTY_NOTICES.md` for the shadcn MIT notice.
