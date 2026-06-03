# Product Design

## Purpose

BiucingCLI helps an independent developer start a new project quickly with a scaffold that already matches a familiar technical stack.

It is not trying to design the whole project on the developer's behalf. Its job is narrower and more useful: create a clean starting structure that the developer would actually keep using.

## Primary User

The primary user is an independent developer who frequently uses a stable personal stack and wants to avoid repeating setup work across projects.

The current stack focus is:

- `Frontend`: React + TypeScript
- `Backend Web Service`: Go + Gin
- `Apple`: Swift + Tuist + SwiftPM
- `Serialization`: Protobuf
- `Mobile`: Kotlin, later

## Problem

Starting a new project often means choosing between two bad options:

- rebuild the same structure by hand every time;
- copy an old repository that contains too much irrelevant baggage.

Generic scaffold tools reduce some setup pain, but they often optimize for breadth instead of fit. They support many combinations, but few of them feel like a good default for a specific developer's real workflow.

BiucingCLI should solve that by generating a small set of high-quality starters that reflect a consistent engineering style.

## Product Principles

1. Prefer a few strong templates over many shallow ones.
2. Generate structures that are useful on day one and readable on day thirty.
3. Keep setup choices minimal and provide sane defaults.
4. Let templates reflect real project habits, not abstract completeness.
5. Grow the template set only after the existing ones feel stable.

## Core Workflow

```text
choose template -> fill a few variables -> generate project -> start coding
```

## First Version Commands

### 1. `biucing list`

Show available templates with a short description.

### 2. `biucing info <template>`

Explain what a template generates, what stack it uses, and when to choose it.

### 3. `biucing create <template> <project-name>`

Generate a new project from an internal template, replacing a small set of variables such as project name, module name, and service port.

## First Version Templates

### `frontend`

Default stack:

- React
- TypeScript

Expected output:

- app entry files that run out of the box;
- restrained folder structure for components, pages, hooks, services, and shared types;
- minimal configuration files;
- a useful README.

### `web`

Default stack:

- Go
- Gin

Expected output:

- `cmd/server` entrypoint;
- `internal` packages for handler, service, repository, router, model, and config;
- base config file;
- Docker build files;
- minimal README and HTTP test coverage.

### `apple`

Default stack:

- Swift
- Tuist
- Swift Package Manager
- fastlane

Supported platforms:

- iOS
- macOS
- watchOS
- tvOS

Expected output:

- a repo-level `Tuist.swift` and `Workspace.swift`;
- an `App/Project.swift` manifest with app and test targets;
- bootstrap files such as `Brewfile`, `.mise.toml`, `Makefile`, and `scripts/bootstrap`;
- at least one internal package under `Packages/`;
- a README that explains the local environment workflow.

### `microservice`

Planned later:

- Go
- Protobuf

This template should come after `frontend` and `web` feel solid, because protobuf generation and service conventions add complexity quickly.

## What BiucingCLI Is Not

- Not a giant template marketplace.
- Not a one-command full application generator.
- Not a replacement for architecture judgment.
- Not a remote template distribution platform for the first version.

## First Version Scope

The first usable version should support a local-only workflow:

- internal templates stored in the repository;
- a small metadata file per template;
- variable replacement for a few high-value fields;
- concise post-generation next steps.

## Future Direction

Later versions can add:

- optional template profiles such as `gin` or `protobuf`;
- a microservice starter with code generation flow;
- Android starters based on Kotlin;
- richer initialization flags once the core templates are proven.
