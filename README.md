# BiucingCLI

BiucingCLI is a scaffold generator for independent developers who want practical, reusable project starters built around a stable personal stack.

The project is being restarted from a clean slate with a narrower goal: generate useful project skeletons, not an all-purpose agent workflow.

## Version

The current repository release target is `0.1.0`.

```bash
biucing --version
```

See [CHANGELOG.md](CHANGELOG.md) for the initial release summary.

## Product Direction

BiucingCLI focuses on a small set of templates that match the maintainer's real development habits:

- `frontend`: React + TypeScript starter with Docker-first local development, Vitest, and Playwright smoke checks
- `web-service`: Go + Gin web service starter with Docker development/runtime workflows
- `microservice`: Go + Protobuf + Buf + Compose starter with gRPC, OpenTelemetry, and local dependency orchestration
- `apple`: SwiftUI + Tuist + SwiftPM Apple app starter for `ios`, `macos`, `watchos`, and `tvos`
- `android`: Kotlin + Gradle + Jetpack Compose Android app starter with fastlane and a committed Gradle wrapper

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
biucing info apple
biucing info android
biucing create frontend my-app
biucing create web-service user-service
biucing create microservice user-service
biucing create apple my-apple-app
biucing create android my-android-app
```

## Project Status

This repository contains a small internal template system with practical starters for five flows:

- `frontend`
- `web-service`
- `microservice`
- `apple`
- `android`

The current maturity split is:

- `frontend`, `web-service`, and `microservice` are the most operationally complete templates today; they now support Docker-first development and runtime packaging.
- `apple` and `android` are strong platform starters with real project structure, automation scaffolding, and validation coverage, but they intentionally follow native platform workflows instead of Docker-first local development.

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
