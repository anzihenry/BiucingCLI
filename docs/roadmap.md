# Roadmap

## Phase 0: Reset

- Clear the old implementation.
- Narrow the project down to a scaffold generator.
- Rebuild the docs around a small, focused template system.

## Phase 1: Template Metadata

Build the internal template model.

Expected behavior:

- each template has a metadata file;
- metadata describes stack, variables, and next steps;
- CLI commands can read one source of truth for `list`, `info`, and `create`.

## Phase 2: `frontend` Template

Build `biucing create frontend <project-name>`.

Expected behavior:

- generate a React + TypeScript starter;
- replace a few core variables such as project and package name;
- produce a restrained folder structure and README.

## Phase 3: `web-service` Template

Build `biucing create web-service <project-name>`.

Expected behavior:

- generate a Go + Gin web service starter;
- prompt for `module_name` if missing;
- replace service name and default port;
- produce a clear backend layout with `cmd/server` and `internal` packages.

## Phase 4: CLI Experience

Build `biucing list` and `biucing info <template>`.

Expected behavior:

- show available templates clearly;
- explain what each template is for;
- describe generated structure and basic next steps.

## Phase 5: Microservice Starter

Build `biucing create microservice <project-name>`.

Expected behavior:

- generate a Go starter shaped for protobuf-based services;
- define a clean code generation path;
- keep the template smaller than a full platform starter.

## Phase 6: Apple Starter

Build `biucing create apple <project-name>`.

Expected behavior:

- generate a Tuist-based Apple app starter;
- allow choosing `ios`, `macos`, `watchos`, or `tvos`;
- include `Brewfile`, `.mise.toml`, `Makefile`, and bootstrap scripts;
- generate `Tuist.swift`, `Workspace.swift`, and `App/Project.swift`;
- wire a minimal SwiftUI app target plus unit tests;
- include at least one internal Swift package for shared code.

## Success Criteria

- A user can create a project they would realistically keep using.
- Templates reflect the maintainer's real stack instead of generic breadth.
- Generated output is small enough to understand and strong enough to build on.
