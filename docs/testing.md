# Test suites and configuration validation

For kernel extraction contracts and generated-output snapshots, see
[the stage 0 baseline](kernel-refactor-baseline.md).
Current foundation boundaries and fixture-root APIs are documented in
[kernel modules](kernel-modules.md).

The planned frontend rendering extension has a separate
[stage 0 specification and baseline record](frontend-rendering-plan.md).
Generated-project acceptance is recorded per stage. Stage 6 adds a separate
[installed-wheel three-mode runner and CI matrix](frontend-artifact-acceptance.md),
not coverage claimed by Python core. Hosted workflow results require a CI run.
Stage 1 adds 21 Python-only resource declaration/selection tests in
`test_resources.py`. Stage 2 adds 17 integration tests in
`test_variant_generation.py`. Stage 3 adds four shipped-CSR tests in
`test_frontend_variants.py`. Stage 4 adds two SSG contract tests and a separate
`frontend-ssg` golden case (159 core, 11 platform, one Android in total).
Fixture tests remain separate from frontend builds. Only frontend entries in
generation/list/required-file goldens are intentionally migrated; all other
template baselines remain unchanged.

Install the locked development/build environment with `uv sync --locked`.

## Frontend CSR/SSG/SSR toolchain (separate from Python core)

Generate a new frontend project, then inside it run:

For SSG (`--set rendering=ssg`), export `SITE_URL=https://your-public-domain.example`
before `verify`, `build` or production browser checks. Development alone may omit
it; no canonical origin is then emitted. The origin is validated at build time,
not added as a generator variable or silently defaulted to localhost.

```bash
pnpm install --frozen-lockfile
pnpm peers check
pnpm verify
pnpm browser:install
pnpm browser:smoke
pnpm browser:smoke:build
make browser-smoke-production
```

Use Node 24.19.x and pnpm 11.21.0. `verify` includes format, typed lint, a TS 7
version assertion, a deliberately invalid typed-lint negative control, component
tests, route type generation and production build. `browser:smoke:build` uses Vite
preview for static artifacts; the production Make target tests real Nginx through
Docker and requires its daemon. Local checks can explicitly select installed
Chrome using `PLAYWRIGHT_CHANNEL=chrome`; that is not a bundled-Chromium CI result.
Browser tests share interactions in `tests/interactions.ts`, test desktop/mobile,
and check navigation, refresh, counter, dialog Escape/focus, overflow and errors.
Nginx-only assertions additionally cover shell HTML, favicon, missing assets and
the expected CSR HTTP-200/client-not-found behavior for unknown routes.

The stage-3 local run passed frozen install and quality gates plus both development
and built-artifact browser checks using installed Chrome.
Production-build checks also passed with Playwright Chromium selected explicitly
using `PLAYWRIGHT_CHANNEL=chromium` (two more viewport cases). The separate
Headless Shell download was cancelled at cleanup; no default-channel result is
claimed for that macOS run. The Docker follow-up passed the normal development
image, frozen install, strict peers, `make verify`, production image and Nginx
health/static-runtime checks on Linux arm64. Three actual-Nginx browser tests
also passed using macOS Chrome. An IPv4/IPv6 mismatch during SPA prerender was
fixed with explicit `preview.host: "127.0.0.1"` and a Python regression assertion;
macOS and Docker production builds both passed afterward. Optional full dev image,
amd64/native Linux and remote CI are not claimed. Full installed-wheel three-mode
Node/container CI is stage 6, not part of the Python matrix today.

Docker Linux arm64 browser follow-up passed three actual-Nginx tests using explicit
Playwright Chromium, then the unmodified Make workflow passed three production and
two development tests using its default bundled Headless Shell. This is actual
container browser coverage, separate from macOS Chrome and Vite-preview evidence.

## Stage 4 SSG acceptance

The SSG preset shares the lockfile and quality gate with CSR. The generated
`app/lib/site.test.ts` covers origin validation and content lookup; the shared
component test additionally checks disabled actions in server HTML. Four SSG
unit/component cases pass. The default Linux Headless Shell production workflow
passes seven cases: desktop/mobile interactions and data navigation, delayed JS
hydration, raw HTML/metadata/sitemap/fixed data, and real static 404s. Four Linux
development cases pass from both a cold cache and a repeated launch. macOS Chrome
passes four development and four static-preview cases; default CSR's two
development/two preview cases and complete quality gate also pass.

Build-time SITE_URL negative checks reject missing or invalid origins. Preview is
mode-owned: SSG maps known paths to pre-rendered documents, CSR keeps SPA fallback.
Use the production Make target for Nginx status/header behavior; Vite preview is
not evidence of deployment correctness. Python checks now include an SSG golden,
all-mode config parsing, wheel/sdist SSG resources and installed-wheel generation.
Node/browser execution from the installed wheel, amd64 and remote CI are not yet
covered. See the stage 4 record in the rendering plan for scope and cold-start fixes.

The stage-specific statements above record their original evidence. Stage 6 adds
installed-wheel execution without modifying generated outputs; see the current
[artifact acceptance guide](frontend-artifact-acceptance.md) and stage 6 record
for the macOS/Linux results and the still-pending hosted CI gate.

## Stage 5 SSR acceptance

Generate with `--set rendering=ssr`; the dependency lockfile and quality commands
are shared with CSR/SSG. `pnpm browser:smoke:build` starts the production Node
entry directly and runs seven checks, including an isolated misconfigured-server
probe for sanitized HTML/data 500s and a client-bundle private-module scan.
`pnpm preview` also renders requests but uses Vite's host; it is not the production
process. `make browser-smoke-production` targets the actual non-root image,
injects a harmless private sentinel, checks health and runs five browser/HTTP
checks before asserting a clean SIGTERM exit. Do not use real secrets as fixtures.
The macOS Chrome and Docker Linux arm64 default Headless Shell runs passed;
Linux development passed on both a cold cache and a repeated launch. The latter
used exact-version Linux browser artifacts pre-fetched through the host network
because container downloads were slow; no browser assertions were skipped.
Linux `pnpm browser:install --only-shell` also passed with normal dependency
validation. The redundant full Chromium download was cancelled after Headless
Shell acceptance; that full download is not a claimed successful check.

The 31 generated unit/component cases cover request snapshots, invalid input,
private configuration errors, SSR HEAD/status/deadline/cancellation, static path
and symlink boundaries, cache headers and graceful versus forced connection drain.
The four development checks cover desktop/mobile interactions, twelve concurrent
request-specific HTML responses, status codes and special-input hydration.
The new Python SSR ownership/determinism cases and exact-output golden bring
coverage to 161 core + 11 platform + one Android = 173 tests. Installed wheel/sdist
verification includes SSR resources and independently generated SSR configs.
The installed-wheel runner and six-job Node/browser CI matrix are implemented in
stage 6; actual hosted CI execution still needs a push. Eleven artifact/runner/CI
regressions brought totals to 172 core + 11 platform + one Android = 184.
The subsequent cache-contamination guard brings current totals to 173 core +
11 platform + one Android = 185. It checks shared and mode-specific frontend
resource layers for local dependency/build artifacts, including empty directories
that Git does not track. Do not run package-manager commands inside template
source directories; generate a project outside the checkout for frontend checks.
The three frontend goldens had mistakenly included local `.pnpm-store/v3` empty
directories; only those directory records were removed. The corrected 173-test
core suite also passes in a fresh Git archive with the repair patch applied,
without copying ignored/untracked workspace files.

See the stage 5 record in the rendering plan for actual platform results and
limits. Keep these generated-project checks separate from Python-only core CI.

## Core: Linux and macOS

```bash
uv run --locked python scripts/run-tests --suite core
uv run --locked python scripts/verify-distribution
```

Core tests need only Python and the locked dependencies; no Go, Node, Java,
zsh, Xcode or Android SDK is needed. CI and publishing run this suite and
installed-distribution validation on Ubuntu and macOS with Python 3.11–3.14.

Generated JSON, JSON5, YAML, TOML, XML, plist and entitlements files are parsed,
including hidden configuration directories. JSON/JSON5/YAML duplicate keys are
rejected; YAML uses a safe loader with merge support. Failures name the relative
file path. Tests cover all seven templates, Apple platform variants, microservice
dependency variants, special text inputs, malformed files and unsafe YAML tags.
The distribution verifier also parses files generated by the installed wheel
outside the checkout. Parsers are development dependencies, not CLI dependencies.

These are syntax checks, not schema validation or proof of a successful native
build. `biucing validate` retains its template-metadata validation behavior.

## Platform integrations: macOS

```bash
uv run --locked python scripts/run-tests --suite platform
uv run --locked python scripts/verify-distribution --check-make
```

Requires Go (matching generated projects), Node, Swift, Git, Make, zsh, JDK
(`keytool` and `jarsigner`) and `/usr/libexec/PlistBuddy`. CI uses Go 1.26.x,
Node 24, the macOS runner's Swift/JDK tools and Python 3.11. This separate job
checks generated shell/Make contracts, Go tests, Java signing fixtures,
Apple identity scripts and JavaScript/Swift escaping. It is a release gate.

## Optional Android SDK integration

```bash
AAPT2=/absolute/path/to/sdk/build-tools/VERSION/aapt2 \
  uv run --locked python scripts/run-tests --suite android
```

This compiles generated Android resources using a real SDK tool. It is not part
of the SDK-free core matrix. A requested suite fails on missing prerequisites
or skipped tests, so missing tools cannot silently satisfy its coverage.

Use `--list` with any suite to inspect membership without running it. Unmarked
tests belong to core; `platform_test` and `android_test` in `tests/suite_support.py`
opt tests into tool-dependent groups. `--suite all` and standard unittest
discovery retain full-suite execution (optional tools may be skipped there).

## Test organization after kernel extraction

| Area | Test modules |
| --- | --- |
| CLI commands, precedence and interaction | `test_cli.py`, `test_cli_errors.py` |
| Public output contracts | `test_json_contract.py`, `test_presentation.py` |
| Models, catalog and resource loading | `test_catalog.py` |
| Template declarations and structural validation | `test_template_declarations.py`, `test_template_validation.py` |
| Pure rendering and rule helpers | `test_rendering.py`, `test_rule_helpers.py`, `test_template_rules.py` |
| Planning and filesystem execution | `test_generation_plan.py`, `test_generation.py` |
| Resource variants and effective generation | `test_resources.py`, `test_variant_generation.py` |
| Generated template contents | `test_native_outputs.py`, `test_service_outputs.py` |
| External tool integration | `test_platform_integration.py` plus marked escaping tests |
| Escaping and configuration parsers | `test_escaping.py`, `test_configurations.py` |
| Stable generated output | `test_refactor_baseline.py`, `generation_baseline.py`, `golden/` |

`cli_support.py` contains shared fixture helpers, no discovered tests. Native
output assertions belong to core when they only inspect generated files; test
location alone does not determine the suite. Tool-dependent methods retain their
explicit markers. Stage 6 retained all 122 existing test method names exactly
once and added five presentation tests (115 core, 11 platform, one Android).

New unit tests should import the owning module. Keep old import checks in explicit
compatibility tests. Moving a mock requires targeting the module where the symbol
is actually used, not preserving hidden cross-module coupling. Do not refresh
goldens merely to accommodate a refactor; inspect intentional output changes.

Stage 6 activated a direct assertion against `info-web-service.txt`, which had
previously become stale and was no longer used by the partial CLI assertions.
Its maturity-summary line was reconciled against the pre-stage-6 committed CLI
output, not inferred from the new implementation. Generated-project and JSON
goldens were unchanged.
