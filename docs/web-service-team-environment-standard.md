# Web Service Team Environment Standard

## Goal

This document defines a standard development environment for a mid-sized Go web service team.

Scope:

- HTTP API and internal web service development with Go;
- local onboarding and daily development;
- dependency, runtime, and configuration consistency;
- test, build, containerization, and delivery automation.

This standard intentionally centers on the Go-native toolchain and uses a small repo-level command surface instead of a heavy framework layer.

## Design Principles

- Keep the build path Go-native: `go`, standard packages, and plain repo structure.
- Use one command entrypoint for onboarding and one for daily automation.
- Prefer the standard library first; add framework code only where it clearly improves developer speed.
- Pin the Go version in the repo.
- Separate local developer concerns from CI and deployment concerns.
- Keep environment configuration explicit and file-based by default.
- Start from a small starter, but leave a clear path to grow into a fuller team environment.

## Standard Stack

### Core Service Toolchain

- `Go`: language toolchain, module system, compiler, test runner, formatter.
- `Gin`: lightweight HTTP routing and middleware layer for service entrypoints.
- `net/http/httptest`: default HTTP-level testing surface.

### Environment and Tool Installation

- `Homebrew`: install workstation-level tools on macOS.
- `mise`: pin and activate the Go version and any supporting CLIs.

### Dependencies

- `Go Modules`: canonical dependency management and version locking.
- `go.sum`: resolved dependency checksum lockfile that must be committed.

### Configuration

- YAML config files for checked-in local defaults.
- Environment variables for deployment-specific overrides when needed.

### Automation

- `Makefile`: stable command surface for developers and CI.
- `Docker`: reproducible local packaging and deployment parity.

Optional later:

- `golangci-lint`: aggregate lint runner.
- `air` or `reflex`: local hot-reload for service development.
- `buf`: only when the repo grows into protobuf-backed services.

## Tool Responsibilities

### Go Toolchain

Responsible for:

- module resolution;
- formatting, compilation, and test execution;
- native build and run workflows.

Not responsible for:

- environment bootstrapping across the whole workstation;
- container packaging policy;
- release orchestration beyond compiling binaries.

### Gin

Responsible for:

- HTTP routing;
- middleware composition;
- request and response handling at the transport layer.

Not responsible for:

- business logic ownership;
- repository or domain modeling conventions;
- configuration management.

### Go Modules

Responsible for:

- dependency declaration in `go.mod`;
- resolved checksum tracking in `go.sum`.

Rule:

- generated projects should be considered incomplete until `go.sum` exists and is committed.

### Homebrew

Responsible for:

- workstation tool installation from `Brewfile`.

Not responsible for:

- pinning per-project runtime versions.

### mise

Responsible for:

- project-level runtime pinning for tools such as `go`.

### Makefile

Responsible for:

- exposing the small, stable command set the team actually uses every day.

### Docker

Responsible for:

- building a runnable production-like image;
- verifying that the service can start from repo-managed configuration.

Not responsible for:

- replacing the local `go test` and `go run` loop for everyday development.

## Standard Repository Layout

```text
.
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── config/
│   ├── handler/
│   ├── model/
│   ├── repository/
│   ├── router/
│   └── service/
├── configs/
│   └── config.yaml
├── tests/
├── scripts/
│   ├── bootstrap
│   ├── doctor
│   └── ci/
├── .mise.toml
├── Brewfile
├── Makefile
├── go.mod
├── go.sum
├── Dockerfile
└── README.md
```

## Directory Rules

### `cmd/`

Contains service entrypoints only.

Rule:

- keep application startup and dependency wiring here;
- do not let business logic accumulate in `cmd/`.

### `internal/`

Contains non-exported service code.

Use for:

- transport handlers;
- business logic services;
- repositories and data access adapters;
- response or domain models;
- router wiring;
- config parsing.

Rule:

- if code is specific to this service and should not be imported by other modules, it belongs under `internal/`.

### `configs/`

Contains checked-in local and development defaults.

Rule:

- keep one local default config file under version control;
- allow environment variables to override deploy-specific values when necessary.

### `tests/`

Contains HTTP-level and integration-style tests.

Rule:

- prefer fast request/response tests with `httptest` before adding heavier external-environment tests.

### `scripts/`

Contains bootstrap, environment checks, and CI wrappers.

Rule:

- scripts may call `brew`, `mise`, `go`, `docker`, and repo `make` targets;
- scripts should not duplicate stable logic already defined in `Makefile`.

## Source of Truth

The team should treat these files as the canonical sources of truth:

- `Brewfile`: workstation tools.
- `.mise.toml`: pinned runtime versions.
- `go.mod`: declared dependency graph.
- `go.sum`: resolved dependency lock state.
- `configs/*.yaml`: checked-in local defaults.
- `Makefile`: supported developer commands.
- `Dockerfile`: supported container packaging path.

The team should not treat personal shell setup, global Go installs, or ad hoc local scripts as source of truth.

## Required Root Files

### `Brewfile`

Should include tools such as:

- `mise`
- `go`
- `docker`
- `golangci-lint`
- `jq`

Optional:

- `air`
- `gh`

### `.mise.toml`

Should pin versions for at least:

- `go`

Add other tools only when the repo actually depends on them.

### `Makefile`

Should provide a stable interface such as:

- `make bootstrap`
- `make doctor`
- `make tidy`
- `make test`
- `make run`
- `make build`
- `make docker-build`

### `scripts/bootstrap`

Should:

- install Brew dependencies if needed;
- activate the pinned runtime through `mise`;
- run `go mod tidy` when the repo is first created or dependencies change.

### `scripts/doctor`

Should verify:

- Go is installed and matches the repo expectation;
- Docker is available when container workflows are required;
- `go.sum` exists;
- the service can load local config successfully.

## Standard Local Workflow

### First-Time Onboarding

Expected flow:

1. Install workstation tools from `Brewfile`.
2. Activate pinned runtimes with `mise`.
3. Run `make bootstrap`.
4. Run `make test`.
5. Run `make run`.

### Daily Development

Expected flow:

1. Update dependencies intentionally with `go get` or direct module edits.
2. Regenerate `go.sum` through `go mod tidy`.
3. Run `make test`.
4. Run `make run` for local iteration.
5. Use `make docker-build` when validating packaging changes.

## Current `web-service` Template Assessment

The current `web-service` template already provides a solid starter-level backend shape:

- `Go + Gin` stack selection;
- `cmd/server` entrypoint;
- `internal/config`, `handler`, `service`, `repository`, `model`, and `router` packages;
- local YAML config;
- `Makefile`;
- `Dockerfile`;
- HTTP-level tests using `httptest`.

This is enough for a useful personal starter and it matches the current product direction.

However, it is not yet at the same maturity level as the `apple` and `android` templates because it is still missing environment-standard pieces:

- no `Brewfile`;
- no `.mise.toml`;
- no `scripts/bootstrap`;
- no `scripts/doctor`;
- no committed `go.sum` in the generated project;
- no explicit lint or CI-oriented command surface.

## Recommendation

The repo should keep `web-service` as a lighter starter for now, but it is worth promoting it toward a full team-environment template in a second step.

Reasoning:

- the current backend starter is already functional and validated on the main path;
- adding environment standard files now would improve reproducibility without forcing a large framework decision;
- unlike Apple and Android, a Go web service does not need heavy platform tooling before it becomes useful;
- the highest-value gap is environment consistency, not application architecture.

Recommended next phase:

1. Add `Brewfile`, `.mise.toml`, `scripts/bootstrap`, and `scripts/doctor` to `web-service`.
2. Update the generated README to prefer `make bootstrap` and `make doctor` over raw first-run commands.
3. Ensure generation plus `make test` works on a clean machine with only the standard tools installed.
4. Add lint only after the bootstrap path is stable.

Not recommended yet:

- introducing protobuf or microservice-specific code generation into `web-service`;
- adding a heavyweight framework or service platform layer;
- overfitting the starter to deployment infrastructure before the local environment contract is stable.
