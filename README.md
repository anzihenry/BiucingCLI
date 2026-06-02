# BiucingCLI

BiucingCLI is a scaffold generator for independent developers who want practical, reusable project starters built around a stable personal stack.

The project is being restarted from a clean slate with a narrower goal: generate useful project skeletons, not an all-purpose agent workflow.

## Product Direction

BiucingCLI focuses on a small set of templates that match the maintainer's real development habits:

- `frontend`: React + TypeScript
- `web`: Go + Gin
- `microservice`: planned later, with Go + Protobuf

The value is not broad ecosystem coverage. The value is generating starters that are restrained, readable, and worth using as a real base.

## Intended Users

- Independent developers who frequently start new projects.
- Builders who prefer a consistent personal stack over endless framework choices.
- Developers who want fewer setup decisions at project start.

## First Commands

```bash
biucing list
biucing info frontend
biucing info web
biucing create frontend my-app
biucing create web user-service
```

## Project Status

This repository currently contains the new product definition and a minimal CLI shell. The first implementation target is `biucing create`, backed by a small internal template system.

## Design Docs

- [Product Design](docs/product-design.md)
- [Roadmap](docs/roadmap.md)
- [Template System](docs/template-system.md)
