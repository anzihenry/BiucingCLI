---
title: "Using BiucingCLI"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# Using BiucingCLI

[中文](using.md) · Translation of the Chinese primary document.

BiucingCLI is a scaffold generator for independent developers who want practical, reusable project starters built around a stable personal stack.

BiucingCLI generates project skeletons from seven built-in templates. See [product scope](../product/overview.en.md) for the current boundaries.

Apple generates four thin shells for iOS, macOS, watchOS and tvOS, using static component SDKs, exact dependency locks, SafeDI 2.0.0 and the shared C++20 core. `--platform` selects the default operational platform. See the [architecture and implementation record](../engineering/native/apple.en.md).

## Version

The current repository release target is `0.10.0`. See the [release notes](../releases/0.10.0/notes.en.md) for changes and migration notes.

```bash
biucing --version
```

See [CHANGELOG.md](../../CHANGELOG.en.md) for the latest release summary.

## Installation

Install the PyPI release as an isolated command with `uv`:

```bash
uv tool install biucingcli==0.10.0
biucing --version
```

Upgrade with `uv tool upgrade biucingcli`, or run temporarily with
`uvx --from biucingcli biucing --help`.

To install the current checkout instead:

```bash
git clone https://github.com/anzihenry/BiucingCLI.git
cd BiucingCLI
uv tool install .
biucing --version
```

For contributor work, use uv 0.12.16 (the version pinned in CI). Python defaults
to 3.11 via `.python-version`; CI tests 3.11–3.14. uv installs the project and
locked development/build dependencies into `.venv`:

```bash
uv sync --locked
uv run --locked biucing list
uv run --locked python scripts/run-tests --suite core
uv run --locked ruff check --select E4,E7,E9,F src tests scripts
uv run --locked biucing validate
uv run --locked python scripts/verify-distribution
```

Core checks run on Linux and macOS without native SDKs. See [testing](testing.en.md)
for macOS tool integrations and optional Android resource compilation.
See [kernel modules](../engineering/kernel-modules.en.md) for ownership and compatibility
boundaries, and [template authoring](template-authoring.en.md) to add templates.
The [frontend rendering plan](../initiatives/feature/frontend-rendering/plan.en.md) tracks CSR/SSG/SSR
variants. The shipped frontend now defaults to CSR (explicitly select it with
`--set rendering=csr`); `--set rendering=ssg` generates a static content site.
SSG production builds require an explicit public HTTPS `SITE_URL` for canonical
URLs and sitemap. `--set rendering=ssr` generates request-time HTML with a
self-hosted Node runtime, private server configuration and graceful shutdown.
See [frontend artifact acceptance](frontend-acceptance.en.md) to run
all three modes from an installed wheel and understand the separate CI/release gates.

Manage dependencies with `uv add`, `uv add --dev`, and `uv remove`; commit
`pyproject.toml` and `uv.lock` together. For deliberate upgrades use
`uv lock --upgrade-package PACKAGE`, followed by `uv sync --locked` and tests.
The `build` group locks setuptools and wheel. Build from that synced environment
with `uv build --no-sources --no-build-isolation`; plain isolated `uv build`
does not use the build dependency versions from `uv.lock`.

See [the uv development and publishing guide](development.en.md) for local
builds, TestPyPI rehearsal, and automated PyPI publishing with `uv publish`.

## Errors and Automation

For scripts, use `--json`; it disables interactive prompts. Successful JSON
results go to stdout. Failures leave stdout empty and write one JSON error
object to stderr with `schema_version`, `ok: false`, and `error.code/message`.
See [the CLI error contract](../engineering/cli-errors.en.md) for exit codes and examples.
All JSON results include `schema_version` and `generator_version`; list/info
also expose each variable's validator, choices, and effective numeric bounds.
See [the JSON contract](../engineering/json-contract.en.md) for compatibility and field semantics.

## Product Direction


BiucingCLI focuses on a small set of templates that match the maintainer's real development habits:

- `frontend`: React Router Framework Mode CSR/SSG/SSR, React 19.3, TypeScript 7, Tailwind 4 and shadcn/ui; shared pnpm lockfile, Vitest and Playwright checks
- `web-service`: Go + Gin web service starter with Docker development/runtime workflows
- `micro-service`: Go + Protobuf + Buf + Compose starter with gRPC, OpenTelemetry, and local dependency orchestration
- `worker`: Go background worker starter with scheduled and oneshot execution modes
- `apple`: Swift 6.4 + SwiftUI + Tuist + SafeDI starter generating four thin Apple shells, versioned static XCFramework components, exact locks and a portable C++20 core; Android/HarmonyOS adapters remain future integrations
- `android`: Kotlin + Gradle + Jetpack Compose Android app starter with fastlane and a committed Gradle wrapper
- `harmonyos`: ArkTS + ArkUI HarmonyOS app starter for DevEco Studio projects

The value is not broad ecosystem coverage. The value is generating starters that are restrained, readable, and worth using as a real base.

## Intended Users

- Independent developers who frequently start new projects.
- Builders who prefer a consistent personal stack over endless framework choices.
- Developers who want fewer setup decisions at project start.

## First Commands

```bash
biucing list
biucing info frontend
biucing info web-service
biucing info micro-service
biucing info worker
biucing info apple
biucing info android
biucing info harmonyos
biucing create frontend my-app --dry-run
biucing create web-service user-service --plan --json
biucing create frontend my-app
biucing create web-service user-service
biucing create micro-service user-service
biucing create worker email-worker
biucing create apple my-apple-app
biucing create android my-android-app
biucing create harmonyos my-harmony-app
```

## Project Status

This repository contains a small internal template system with practical starters for seven flows:

- `frontend`
- `web-service`
- `micro-service`
- `worker`
- `apple`
- `android`
- `harmonyos`

The current maturity split is:

- `frontend`, `web-service`, and `micro-service` include Docker development, verification, and runtime workflows. The migrated frontend's current verification limits are recorded in the [rendering plan](../initiatives/feature/frontend-rendering/plan.en.md).
- `worker` is a backend-adjacent starter for scheduled and oneshot background execution, with generated-project `go test ./...` validation and Docker packaging.
- `apple` and `android` are now first-class native platform starters with stronger doctor flows, release guidance, richer starter architecture, and repeated real generated-project validation.
- `harmonyos` is an experimental native starter for ArkTS/ArkUI projects that open in DevEco Studio and expose bootstrap, doctor, lint, build, and signing guidance workflows.

Generator UX status:

- `biucing create ... --dry-run` previews resolved variables, target location, template file count, and next steps without writing files;
- `biucing create ... --plan --json` returns a machine-readable preview payload for scripts and automation;
- `biucing create ... --json` returns a machine-readable manifest after a real generation run;
- non-interactive create failures now report all missing required values together;
- all resolved inputs are normalized and validated before a target directory is created, including names, package identities, ports, versions, URLs, numeric bounds, and enumerated choices.

Template consistency status:

- template metadata now exposes verification tier, operating assumptions, and workflow labels;
- every template implements `make bootstrap`, `doctor`, `lint`, `test`, `verify`, `build`, `clean`, and `help` as a shared command contract;
- `biucing validate` checks the stronger metadata contract, input validator definitions, matching `.PHONY` Make targets, and family-level required starter entries;
- `biucing info <template>` now surfaces those consistency fields directly.

Worktree-first status:

- all seven templates now declare `worktree-ready` support metadata;
- generated projects expose `make worktree-info`, `make worktree-doctor`, and `make clean-worktree`;
- Docker-first starters isolate Compose project names, volumes, image tags, published host ports, dependency stores, and caches;
- Docker-first starters now expose port conflict advice and `make worktree-compose-config` for non-invasive Compose diagnostics;
- native starters isolate build caches, local signing/config files, generated output, and debug install identity hooks where the platform supports them;
- native release evidence is now labeled as `static`, `doctor`, or `real-build` so worktree claims do not overstate SDK-backed coverage.

Local Android validation status:

- the Android starter now includes a committed Gradle wrapper;
- the generated Android project has passed real lint, JVM unit tests, debug APK and release AAB builds, plus AAB integrity checks;
- the maintainer workstation has validated the Compose UI smoke test on `Biucing_API_35`.

Local Apple validation status:

- the generated Apple starter has passed real `make generate` verification for both `iOS` and `macOS`;
- `iOS` output now renders a mobile-specific starter structure and has passed real `make build`;
- `macOS` output now renders a desktop-specific starter structure and has passed real `make test`.

Local HarmonyOS validation status:

- the generated HarmonyOS starter has passed real `make bootstrap` and `make verify` verification with a local DevEco Studio/HarmonyOS SDK install;
- `make verify` now covers `doctor`, `lint`, ArkTS/Hypium `test`, unsigned HAP `build`, and package artifact fingerprinting;
- `make release-preflight` and `make release` are wired to local-only signing material and fail fast when `local.properties` is missing or incomplete.

## Documentation

See the [documentation map](../README.en.md) for architecture, contributor guides, initiatives and version records.
