# BiucingCLI

BiucingCLI is a scaffold generator for independent developers who want practical, reusable project starters built around a stable personal stack.

The project is being restarted from a clean slate with a narrower goal: generate useful project skeletons, not an all-purpose agent workflow.

## Version

The current repository release target is `0.4.0`.

```bash
biucing --version
```

See [CHANGELOG.md](CHANGELOG.md) for the latest release summary.

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
- non-interactive create failures now report all missing required values together.

Template consistency status:

- template metadata now exposes verification tier, operating assumptions, and workflow labels;
- `biucing validate` now checks the stronger metadata contract plus family-level required starter entries;
- `biucing info <template>` now surfaces those consistency fields directly.

Local Android validation status:

- the Android starter now includes a committed Gradle wrapper;
- the generated Android project has passed real `./gradlew assembleDebug` and `./gradlew assembleRelease` verification;
- the maintainer workstation has one validated emulator target retained as `Biucing_API_35`.

Local Apple validation status:

- the generated Apple starter has passed real `make generate` verification for both `iOS` and `macOS`;
- `iOS` output now renders a mobile-specific starter structure and has passed real `make build`;
- `macOS` output now renders a desktop-specific starter structure and has passed real `make test`.

## Design Docs

- Android template note: the current Android starter now includes a committed `gradle-wrapper.jar`; if the team refreshes Gradle later, commit the regenerated wrapper files back into the repo.
- [0.3.0 Plan](docs/0.3.0-plan.md)
- [0.4.0 Plan](docs/0.4.0-plan.md)
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
