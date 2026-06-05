# BiucingCLI

BiucingCLI is a scaffold generator for independent developers who want practical, reusable project starters built around a stable personal stack.

The project is being restarted from a clean slate with a narrower goal: generate useful project skeletons, not an all-purpose agent workflow.

## Product Direction

BiucingCLI focuses on a small set of templates that match the maintainer's real development habits:

- `frontend`: React + TypeScript
- `web-service`: Go + Gin
- `microservice`: Go + Protobuf + Buf + Compose

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
biucing create frontend my-app
biucing create web-service user-service
biucing create microservice user-service
```

## Project Status

This repository contains a small internal template system with practical starters for frontend, web-service, apple, android, and microservice flows.

Local Android validation status:

- the Android starter now includes a committed Gradle wrapper;
- the generated Android project has passed a real `./gradlew assembleDebug` smoke build;
- the maintainer workstation has one validated emulator target retained as `Biucing_API_35`.

## Design Docs

- Android template note: the current Android starter now includes a committed `gradle-wrapper.jar`; if the team refreshes Gradle later, commit the regenerated wrapper files back into the repo.
- [Product Design](docs/product-design.md)
- [Roadmap](docs/roadmap.md)
- [Template System](docs/template-system.md)
- [Web Service Team Environment Standard](docs/web-service-team-environment-standard.md)
- [Microservice Team Environment Standard](docs/microservice-team-environment-standard.md)
- [Apple Team Environment Standard](docs/apple-team-environment-standard.md)
- [Android Team Environment Standard](docs/android-team-environment-standard.md)
- [Android Template Design](docs/android-template-design.md)
- [Microservice Template Design](docs/microservice-template-design.md)
