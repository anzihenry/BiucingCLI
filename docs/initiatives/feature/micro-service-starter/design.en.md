---
title: "Microservice Template Design"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

# Microservice Template Design

[中文](design.md) · Translation of the Chinese primary document.

> Initiative material: historical background, design or acceptance for the recorded stage. See the [documentation map](../../../README.en.md) for current usage.

> Historical starter design. Production architecture after 2026-09-26 follows [backend architecture](../../../engineering/backend/architecture.en.md) and [Micro Service architecture](../../../engineering/backend/micro-service.en.md). Early scope limits below do not define the new target.

## Goal

This document defines the first implementation target for a `micro-service` template in BiucingCLI.

The intent is not to generate a full backend platform. The intent is to generate a contract-aware Go service starter that matches the environment standard defined in [Microservice Team Environment Standard](../../../guides/environments/micro-service.en.md).

## Position in Product Scope

The `micro-service` template serves internal service-to-service calls and
machine-to-machine contracts. `web-service` serves customer-facing HTTP APIs.
They have different identity and authorization boundaries.

Why:

- `web-service` remains the customer-facing entrypoint;
- protobuf, code generation, and local orchestration add real complexity;
- the first microservice template should justify that complexity with a clearly better collaboration path.

## First Version Outcome

`biucing create micro-service <project-name>` should generate:

- a Go service starter with protobuf contract scaffolding;
- `Buf` configuration and a reproducible generation path;
- a stable `Makefile` and `scripts/bootstrap` / `scripts/doctor` surface;
- a local `Docker Compose` flow for the service and one supporting dependency;
- local OpenTelemetry Collector wiring;
- a README that explains both single-service and composed workflows.

It should not try to generate:

- a fleet of many services;
- Kubernetes manifests;
- a service mesh;
- a large internal platform framework;
- every transport style at once.

## Recommended Stack

The default stack should be:

- Go
- Gin
- Protobuf
- Buf
- Docker Compose
- OpenTelemetry

This keeps the first version practical and aligned with a contract-first service workflow.

## Template Metadata Proposal

Suggested `templates/micro-service/template.json`:

```json
{
  "name": "micro-service",
  "description": "Go microservice starter with Protobuf, Buf, Compose, and OpenTelemetry",
  "stack": ["Go", "Gin", "Protobuf", "Buf", "Docker Compose", "OpenTelemetry"],
  "variables": [
    { "name": "project_name", "required": true },
    { "name": "module_name", "required": true, "prompt": "Go module name: " },
    { "name": "service_name", "required": false, "default_from": "project_name" },
    { "name": "proto_package", "required": true, "prompt": "Proto package: " },
    { "name": "http_port", "required": false, "default": "8080" },
    { "name": "grpc_port", "required": false, "default": "9090" },
    { "name": "dependency_store", "required": false, "default": "postgres" },
    { "name": "otel_exporter_endpoint", "required": false, "default": "http://otel-collector:4318" }
  ],
  "next_steps": [
    "make bootstrap",
    "make doctor",
    "make proto",
    "make test",
    "make run",
    "make up"
  ]
}
```

## Variable Design

### Core Variables

- `project_name`: target directory name.
- `module_name`: Go module path.
- `service_name`: deployable service name and default compose service key.
- `proto_package`: protobuf package namespace, such as `user.v1`.

### Runtime Variables

- `http_port`: HTTP health, admin, or gateway-facing port.
- `grpc_port`: internal RPC port.
- `dependency_store`: initial local dependency, such as `postgres` or `redis`.
- `otel_exporter_endpoint`: local telemetry export destination.

## Placeholder Proposal

The current renderer does simple text replacement. The first microservice template should stay within that constraint.

Suggested placeholders:

- `{{PROJECT_NAME}}`
- `{{MODULE_NAME}}`
- `{{SERVICE_NAME}}`
- `{{PROTO_PACKAGE}}`
- `{{HTTP_PORT}}`
- `{{GRPC_PORT}}`
- `{{DEPENDENCY_STORE}}`
- `{{OTEL_EXPORTER_ENDPOINT}}`

## Directory Shape

Suggested generated output:

```text
my-microservice/
  README.md
  Brewfile
  .mise.toml
  Makefile
  Dockerfile
  cmd/
    server/
      main.go
  internal/
    config/
    handler/
    service/
    repository/
    router/
    transport/
    telemetry/
  api/
    proto/
      {{SERVICE_NAME}}/v1/
        service.proto
    buf.yaml
    buf.gen.yaml
    gen/
  configs/
    config.yaml
  deploy/
    compose.yaml
    otel-collector.yaml
  scripts/
    bootstrap
    doctor
  tests/
```

## Module and Directory Responsibilities

### `cmd/server`

Responsibilities:

- application startup;
- dependency wiring;
- HTTP and gRPC server bootstrapping.

### `internal/transport`

Responsibilities:

- transport-specific adapters;
- request or response translation;
- gRPC server registration helpers when needed.

### `internal/telemetry`

Responsibilities:

- OpenTelemetry setup;
- tracer and meter initialization;
- shared observability glue.

### `api/proto`

Responsibilities:

- service contract definitions;
- request and response schemas;
- versioned API namespace.

## Build and Generation Strategy

The first version should define these flows clearly:

- `make proto`: run `buf generate`;
- `make lint`: run Go lint plus `buf lint`;
- `make test`: run Go tests;
- `make verify`: run doctor, proto validation, lint, and tests;
- `make run`: run the service directly on the host;
- `make up`: run the service plus dependencies with Compose.

Avoid in version one:

- raw `protoc` commands in README instructions;
- many custom generation scripts;
- multiple language outputs;
- dynamic template branching based on many flags.

## Compose Expectations

The generated `deploy/compose.yaml` should include:

- the service container;
- one dependency service;
- an OpenTelemetry Collector container.

The first version should keep the compose file small and readable. It should show the development topology without pretending to model production perfectly.

## README Expectations

The generated README should explain:

- required tools;
- how `make bootstrap` works;
- how protobuf generation works through `Buf`;
- the difference between `make run` and `make up`;
- where contracts, generated code, and telemetry config live;
- what files are source of truth.

The README should not promise Kubernetes or production deployment workflows by default.

## First Version Validation Plan

The template should be considered healthy when a generated sample can:

1. run `make bootstrap`;
2. run `make doctor`;
3. run `make proto`;
4. run `make test`;
5. start with `make run`;
6. start with `docker compose -f deploy/compose.yaml up --build`.

## Relationship to `web-service`

Choose by ownership and caller, not by which starter is simpler. `web-service`
owns the customer-facing HTTP/API and user-login boundary. `micro-service`
owns an internal capability, its protobuf/gRPC contract, and its own data.
A customer-facing operation may call a microservice: the generated web project
then needs a versioned gRPC client adapter, while the microservice remains the
contract owner and server. Neither template should reach into the other's
`internal/` packages or database tables.

The production integration target is described in [Web Service architecture](../../../engineering/backend/web-service.en.md):
workload identity and mTLS authenticate the calling service; an explicitly
authorized web caller can pass a terminal user's trusted `(issuer, subject)`
context for user-scoped RPCs. The receiving microservice must authorize both
the calling service/method and the user's operation on its own resource.
Client deadlines, bounded retries, trace propagation, contract compatibility,
independent release, and downstream failure behavior are part of this boundary.
The current template only serves a `Ping` RPC and does not yet implement this
production authentication or a real database-backed business operation.

### Cross-template integration acceptance

An integration fixture should generate one project from each template and prove:

1. The web project consumes a fixed, published version of the microservice's
   protobuf contract and calls it through a generated gRPC client adapter.
2. The microservice accepts only the expected workload identity over mTLS;
   missing, untrusted, or wrong-client certificates fail before business logic.
3. A user-scoped RPC carries an explicit `(issuer, subject)` asserted by an
   authorized web caller. The microservice applies its own object-level rule;
   a different user receives no data even when the caller is otherwise allowed.
4. Deadline and cancellation reach the server; an unavailable dependency maps
   to a stable external error without leaking internal addresses or details.
5. Read retries are bounded; writes require an idempotency design before any
   retry. Trace IDs connect the external request and internal RPC.
6. A compatible protobuf change can roll out independently, while a breaking
   change fails the contract check before release.

Local Compose may generate ephemeral test CA and workload certificates for this
fixture. Production certificate issuance, rotation, network policy, and the
service trust domain are supplied by the deployment environment and documented
as configuration requirements. Do not commit a production private key or use
plaintext gRPC as a production default.

## Recommended Delivery Sequence

1. Keep `web-service` and `micro-service` distinct by caller and business ownership.
2. Introduce `micro-service` as a second backend template, not as a mutation of `web-service`.
3. Implement the template with one clear path and minimal branching.
4. Validate the generated project through real `make` and `docker compose` commands before promoting it as ready.
