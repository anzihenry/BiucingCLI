# BiucingCLI

BiucingCLI is a scaffold generator for independent developers who want practical, reusable project starters built around a stable personal stack.

The project is being restarted from a clean slate with a narrower goal: generate useful project skeletons, not an all-purpose agent workflow.

## Version

The current repository release target is `0.9.1`.

```bash
biucing --version
```

See [CHANGELOG.md](CHANGELOG.md) for the latest release summary.

## Installation

Install the PyPI release as an isolated command with `uv`:

```bash
uv tool install biucingcli==0.9.1
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
uv run --locked python -m unittest discover -s tests
uv run --locked ruff check --select E4,E7,E9,F src tests scripts
uv run --locked biucing validate
uv run --locked python scripts/verify-distribution
```

Manage dependencies with `uv add`, `uv add --dev`, and `uv remove`; commit
`pyproject.toml` and `uv.lock` together. For deliberate upgrades use
`uv lock --upgrade-package PACKAGE`, followed by `uv sync --locked` and tests.
The `build` group locks setuptools and wheel. Build from that synced environment
with `uv build --no-sources --no-build-isolation`; plain isolated `uv build`
does not use the build dependency versions from `uv.lock`.

See [the uv development and publishing guide](docs/uv-workflow.md) for local
builds, TestPyPI rehearsal, and automated PyPI publishing with `uv publish`.

## Errors and Automation

For scripts, use `--json`; it disables interactive prompts. Successful JSON
results go to stdout. Failures leave stdout empty and write one JSON error
object to stderr with `schema_version`, `ok: false`, and `error.code/message`.
See [the CLI error contract](docs/cli-errors.md) for exit codes and examples.

## Product Direction


BiucingCLI focuses on a small set of templates that match the maintainer's real development habits:

- `frontend`: React + TypeScript starter with Docker-first local development, Vitest, and Playwright smoke checks
- `web-service`: Go + Gin web service starter with Docker development/runtime workflows
- `microservice`: Go + Protobuf + Buf + Compose starter with gRPC, OpenTelemetry, and local dependency orchestration
- `worker`: Go background worker starter with scheduled and oneshot execution modes
- `apple`: SwiftUI + Tuist + SwiftPM Apple app starter for `ios`, `macos`, `watchos`, and `tvos`
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
biucing info microservice
biucing info worker
biucing info apple
biucing info android
biucing info harmonyos
biucing create frontend my-app --dry-run
biucing create web-service user-service --plan --json
biucing create frontend my-app
biucing create web-service user-service
biucing create microservice user-service
biucing create worker email-worker
biucing create apple my-apple-app
biucing create android my-android-app
biucing create harmonyos my-harmony-app
```

## Project Status

This repository contains a small internal template system with practical starters for seven flows:

- `frontend`
- `web-service`
- `microservice`
- `worker`
- `apple`
- `android`
- `harmonyos`

The current maturity split is:

- `frontend`, `web-service`, and `microservice` are fully Dockerized for development, verification, and runtime packaging.
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

## Design Docs

- Android template note: the current Android starter now includes a committed `gradle-wrapper.jar`; if the team refreshes Gradle later, commit the regenerated wrapper files back into the repo.
- [0.3.0 Plan](docs/0.3.0-plan.md)
- [0.4.0 Plan](docs/0.4.0-plan.md)
- [0.6.0 Plan](docs/0.6.0-plan.md)
- [0.6.0 Worktree Task Breakdown](docs/0.6.0-worktree-tasks.md)
- [Worktree Isolation Contract](docs/worktree-isolation-contract.md)
- [0.6.0 Worktree Collision Audit](docs/0.6.0-worktree-collision-audit.md)
- [0.6.0 Release Prep](docs/0.6.0-release-prep.md)
- [0.6.1 Plan](docs/0.6.1-plan.md)
- [0.6.1 Worktree Hardening Task Breakdown](docs/0.6.1-worktree-hardening-tasks.md)
- [0.6.1 Release Prep](docs/0.6.1-release-prep.md)
- [0.7.0 Release Notes](docs/0.7.0-release-notes.md)
- [0.7.0 Release Prep](docs/0.7.0-release-prep.md)
- [0.8.0 Release Notes](docs/0.8.0-release-notes.md)
- [0.8.0 Release Prep](docs/0.8.0-release-prep.md)
- [0.9.0 Plan](docs/0.9.0-plan.md)
- [0.9.0 Release Notes](docs/0.9.0-release-notes.md)
- [0.9.0 Release Prep](docs/0.9.0-release-prep.md)
- [0.4.0 Release Prep](docs/0.4.0-release-prep.md)
- [0.3.0 Release Prep](docs/0.3.0-release-prep.md)
- [Release Checklist](docs/release-checklist.md)
- [Verification Matrix](docs/verification-matrix.md)
- [Product Design](docs/product-design.md)
- [Roadmap](docs/roadmap.md)
- [Template System](docs/template-system.md)
- [Web Service Team Environment Standard](docs/web-service-team-environment-standard.md)
- [Microservice Team Environment Standard](docs/microservice-team-environment-standard.md)
- [Apple Team Environment Standard](docs/apple-team-environment-standard.md)
- [Android Team Environment Standard](docs/android-team-environment-standard.md)
- [HarmonyOS Team Environment Standard](docs/harmonyos-team-environment-standard.md)
- [Android Template Design](docs/android-template-design.md)
- [Microservice Template Design](docs/microservice-template-design.md)
