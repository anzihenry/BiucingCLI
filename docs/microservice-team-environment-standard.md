# Microservice Team Environment Standard

## Goal

This document defines a standard development environment for a mid-sized Go microservice team.

Scope:

- multi-service backend development with Go;
- local onboarding and daily service-to-service development;
- interface definition, code generation, and contract consistency;
- local dependency orchestration;
- observability, test, build, and packaging automation.

This standard intentionally starts with a compose-first local workflow instead of a Kubernetes-heavy setup, while leaving a clean path to grow into larger platform tooling later.

## Design Principles

- Prefer a small, reliable local workflow over a heavyweight platform abstraction.
- Keep each service independently understandable and runnable.
- Standardize interface and generation workflows early.
- Treat local multi-service orchestration as part of the developer experience, not an afterthought.
- Make observability available in development from day one.
- Separate service template concerns from production platform concerns.
- Promote the simplest thing that supports real collaboration across services.

## Standard Stack

### Core Service Toolchain

- `Go`: language toolchain, modules, compiler, formatter, and test runner.
- `Gin` or `net/http`: HTTP service entrypoints.
- `gRPC`: internal RPC transport when service-to-service contracts benefit from strong typing.
- `Protobuf`: interface definition and generated contract source.
- `Buf`: protobuf linting, breaking-change checks, and generation entrypoint.

### Environment and Tool Installation

- `Homebrew`: workstation tool installation on macOS.
- `mise`: pin Go, `buf`, and other project CLIs.

### Local Orchestration

- `Docker Compose`: local multi-service composition.
- `Docker Compose Watch`: optional file-sync or rebuild support for faster iteration.
- `Makefile`: stable repo command surface.

### Observability

- `OpenTelemetry`: tracing and metrics instrumentation baseline.
- `OpenTelemetry Collector`: local ingest and export entrypoint for development.

### Dependencies and Configuration

- `Go Modules`: per-service dependency declaration and checksum locking.
- `.env` or `.env.local`: local machine overrides that are not committed.
- checked-in YAML or JSON config files: local defaults that are safe to version.

Optional later:

- `Tilt` or `Skaffold`: when the local team workflow truly needs Kubernetes-native development loops.
- `Dapr`: only when service invocation, pub/sub, or state abstractions become a deliberate platform decision.

## Tool Responsibilities

### Go Toolchain

Responsible for:

- compiling and testing service code;
- module resolution;
- service-local development workflows.

Not responsible for:

- cross-service orchestration;
- protobuf contract governance;
- local dependency startup policy.

### Protobuf and Buf

Responsible for:

- defining RPC and event contracts;
- generating typed client/server code;
- enforcing lint and compatibility checks.

Not responsible for:

- runtime transport configuration;
- service business logic;
- replacing ordinary package design within a service.

### Docker Compose

Responsible for:

- starting multiple services and local dependencies together;
- wiring service discovery and environment defaults for development;
- providing one shared local integration surface.

Not responsible for:

- becoming the only way a single service can run;
- replacing CI, deployment, or production scheduling;
- hiding all infrastructure decisions behind custom scripts.

### OpenTelemetry

Responsible for:

- making traces and metrics visible in local development;
- providing a consistent baseline for future observability tooling.

Not responsible for:

- choosing the production observability vendor;
- replacing application logs or debugging discipline.

## Standard Repository Shapes

Two repo shapes are acceptable.

### Option A: Service Workspace

Use this when one repository owns multiple closely related services.

```text
.
├── services/
│   ├── gateway/
│   │   ├── cmd/server/
│   │   ├── internal/
│   │   ├── configs/
│   │   ├── go.mod
│   │   └── Dockerfile
│   └── user/
│       ├── cmd/server/
│       ├── internal/
│       ├── configs/
│       ├── go.mod
│       └── Dockerfile
├── api/
│   ├── proto/
│   ├── buf.yaml
│   ├── buf.gen.yaml
│   └── gen/
├── deploy/
│   ├── compose.yaml
│   └── otel-collector.yaml
├── scripts/
│   ├── bootstrap
│   └── doctor
├── Brewfile
├── .mise.toml
├── Makefile
└── README.md
```

### Option B: Single Service Repository

Use this when each repository contains one deployable microservice, but every repo follows the same contract and local workflow.

```text
.
├── cmd/server/
├── internal/
├── configs/
├── api/
│   ├── proto/
│   ├── buf.yaml
│   ├── buf.gen.yaml
│   └── gen/
├── deploy/
│   ├── compose.yaml
│   └── otel-collector.yaml
├── tests/
├── scripts/
│   ├── bootstrap
│   └── doctor
├── Brewfile
├── .mise.toml
├── Makefile
├── go.mod
├── go.sum
└── README.md
```

For BiucingCLI, the first `microservice` template should target Option B. It keeps the generated project understandable while still standardizing the contract, observability, and orchestration surfaces that distinguish a microservice from a plain web service.

## Directory Rules

### `api/`

Contains protobuf definitions and generated code configuration.

Rule:

- treat `.proto` files and `buf` config as source of truth;
- generated code may be committed or regenerated consistently, but the repo must define one clear policy.

### `deploy/`

Contains local orchestration files only.

Rule:

- keep `compose.yaml` development-oriented;
- do not mix local compose conventions with production deployment manifests.

### `internal/`

Contains service-local implementation details.

Rule:

- transport adapters, business logic, repositories, config parsing, and orchestration code belong here;
- generated protobuf code should not be hand-edited under `internal/`.

### `scripts/`

Contains bootstrap and health-check flows.

Rule:

- scripts may call `brew`, `mise`, `buf`, `go`, `docker`, and repo `make` targets;
- scripts should not become a hidden second build system.

## Source of Truth

The team should treat these files as canonical:

- `Brewfile`: workstation tool installation.
- `.mise.toml`: pinned project runtime and CLI versions.
- `api/proto/*.proto`: contract source.
- `api/buf.yaml` and `api/buf.gen.yaml`: protobuf lint and generation policy.
- `go.mod` and `go.sum`: service dependency graph and lock state.
- `deploy/compose.yaml`: supported local multi-service orchestration path.
- `deploy/otel-collector.yaml`: supported local telemetry pipeline.
- `Makefile`: supported developer commands.

The team should not treat personal shell aliases, ad hoc local containers, or copied generated code as the real source of truth.

## Required Root Files

### `Brewfile`

Should include tools such as:

- `mise`
- `go`
- `buf`
- `docker`
- `jq`

Optional:

- `grpcurl`
- `gh`

### `.mise.toml`

Should pin versions for at least:

- `go`
- `buf`

Add other tools only when the repo truly depends on them.

### `Makefile`

Should define the standard developer surface:

- `make bootstrap`
- `make doctor`
- `make proto`
- `make lint`
- `make test`
- `make verify`
- `make run`
- `make up`
- `make down`
- `make logs`
- `make docker-build`

### `deploy/compose.yaml`

Should start at least:

- the service itself;
- one local dependency when the service needs one, such as `postgres` or `redis`;
- an OpenTelemetry Collector when observability is part of the standard.

The first version should optimize for clarity over completeness.

## Standard Local Workflow

### First-Time Onboarding

Expected flow:

1. Install workstation tools from `Brewfile`.
2. Activate pinned runtimes with `mise`.
3. Run `make bootstrap`.
4. Run `make doctor`.
5. Run `make proto`.
6. Run `make test`.
7. Run `make up`.

### Daily Development

Expected flow:

1. Update protobuf contracts intentionally.
2. Regenerate code through `make proto`.
3. Run `make test`.
4. Run `make run` when iterating on one service.
5. Run `make up` when validating service-to-service or dependency integration.
6. Run `make verify` before pushing changes.

## Contract and Code Generation Rules

- Use `Buf` as the single entrypoint for protobuf lint and generation.
- Generated code should be reproducible from checked-in config only.
- Breaking-change detection should be part of CI when the service has published contracts.
- A repo should not require developers to remember raw `protoc` invocations.

## Observability Rules

- Every service should emit structured logs.
- Every service should expose health endpoints for local checks.
- Traces should be visible in local development through a standard collector path.
- Metrics can start small, but the instrumentation path should exist from day one.

## Current Product Positioning

The existing `web-service` template should remain the lightweight single-service starter for straightforward HTTP backends.

The future `microservice` template should be positioned differently:

- stronger contract-first workflow;
- local multi-service orchestration by default;
- baseline observability included;
- environment standard designed for team collaboration rather than only personal scaffolding.

## Recommendation

For BiucingCLI, the default microservice environment standard should be:

- `Go + Protobuf + Buf` for service and contract development;
- `Docker Compose` for local orchestration;
- `OpenTelemetry` for local observability;
- `Homebrew + mise + Makefile` for repeatable local setup.

Not recommended for version one:

- defaulting immediately to Kubernetes-native development loops;
- baking in Dapr or a service mesh before the template contract is proven;
- generating a large platform mono-repo with many empty services.

Recommended rollout:

1. Add a microservice environment standard document.
2. Add a matching `microservice` template design doc.
3. Implement a single-service microservice starter with protobuf, buf, compose, and telemetry scaffolding.
4. Validate that generated output supports both `make run` and `make up`.
