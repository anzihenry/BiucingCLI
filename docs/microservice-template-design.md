# Microservice Template Design

## Goal

This document defines the first implementation target for a `microservice` template in BiucingCLI.

The intent is not to generate a full backend platform. The intent is to generate a contract-aware Go service starter that matches the environment standard defined in [Microservice Team Environment Standard](microservice-team-environment-standard.md).

## Position in Product Scope

The `microservice` template should come after `web-service`, not replace it.

Why:

- `web-service` is still the best simple starter for a plain HTTP backend;
- protobuf, code generation, and local orchestration add real complexity;
- the first microservice template should justify that complexity with a clearly better collaboration path.

## First Version Outcome

`biucing create microservice <project-name>` should generate:

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

Suggested `templates/microservice/template.json`:

```json
{
  "name": "microservice",
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

The `web-service` template should remain the simpler default when a project does not need:

- protobuf contracts;
- local dependency orchestration as a first-class workflow;
- a standard telemetry path;
- a stronger team-oriented environment contract.

The `microservice` template should be chosen when those needs are present on day one.

## Recommended Delivery Sequence

1. Keep `web-service` stable as the lightweight starter.
2. Introduce `microservice` as a second backend template, not as a mutation of `web-service`.
3. Implement the template with one clear path and minimal branching.
4. Validate the generated project through real `make` and `docker compose` commands before promoting it as ready.
