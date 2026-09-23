# Apple Team Environment Standard

## Goal

This document defines a standard development environment for a mid-sized Apple platform team.

Scope:

- iOS, iPadOS, macOS, watchOS, and tvOS app development;
- local onboarding and daily development;
- project generation and dependency consistency;
- test, build, signing, and delivery automation.

This standard intentionally centers on the Apple-native toolchain and uses `Tuist` as the project-generation layer.

## Design Principles

- Keep the build path Apple-native: `Xcode`, `xcodebuild`, Simulator, Instruments.
- Use one command entrypoint for onboarding and one for daily automation.
- Prefer `Swift Package Manager` for dependencies.
- Generate project files; do not hand-edit `.xcodeproj`.
- Pin tool versions in the repo.
- Separate local developer concerns from CI concerns.
- Keep code signing out of ad hoc local setup as much as possible.

## Standard Stack

### Core Apple Toolchain

- `Xcode`: the full IDE and Apple SDK distribution.
- `Swift 6.4+`: minimum compiler/SwiftPM toolchain for generated packages; Xcode 27
  is the verified baseline. Xcode `SWIFT_VERSION=6.0` selects Swift 6 language mode.
- `C++20`: shared portable core; SwiftPM/CMake for source development, static XCFramework for app integration.
- `xcodebuild`: CLI build and test entrypoint.
- `xcrun`: access to Apple command-line tools such as `simctl`.
- `Simulator`: local app and UI test execution.
- `Instruments`: profiling and diagnostics.

### Environment and Tool Installation

- `Homebrew`: install workstation-level tools.
- `mise`: pin and activate project runtime versions.
- `xcodes`: install and switch between Xcode versions when the team needs parallel support.

### Project Generation and Modularization

- `Tuist`: generate workspaces/projects, manage project structure, and standardize modules.

### Dependencies

- `Swift Package Manager`: default dependency manager.
- `CocoaPods`: allowed only for legacy vendor SDKs that are not available through SwiftPM.

### Automation

- `Makefile`: stable command surface for developers and CI.
- `fastlane`: release, signing, screenshots, TestFlight/App Store automation.

## Tool Responsibilities

### Xcode

Responsible for:

- SDKs, signing integration, local debugging, profiling, interface editing;
- local simulator/device development;
- archive verification when needed.

Not responsible for:

- being the source of truth for project structure;
- being the only way to build or test the app.

### Tuist

Responsible for:

- workspace and project generation;
- module boundaries and target graph definition;
- shared project conventions;
- template and scaffold generation for new modules/features.

Not responsible for:

- package publishing;
- code signing policy;
- replacing `xcodebuild` as the real build executor.

### Swift Package Manager

Responsible for:

- first-party and third-party dependency declaration;
- package version locking through `Package.resolved`;
- reusable internal libraries when package boundaries make sense.

### Homebrew

Responsible for:

- workstation tool installation from `Brewfile`.

Not responsible for:

- pinning per-project runtime versions.

### mise

Responsible for:

- project-level runtime pinning for tools such as `ruby`, `node`, and `tuist`;
- activating the expected tool versions in a reproducible way.

### fastlane

Responsible for:

- lanes for test, beta, release, signing sync, and store upload;
- packaging release logic so CI and local release flows use the same commands.

### Makefile

Responsible for:

- exposing the small, stable command set the team actually uses every day.

## Standard Repository Layout

```text
Apps/{ios,macos,watchos,tvos}/   Tuist manifests, thin app shells and tests
Composition/                   Platform implementations, public factories, SafeDI graph
Dependencies/                  Exact declarations, committed binary lock
Components/                    One source-development package with multiple targets
Shared/Core/                   C++20, C ABI, Apple facade, CMake/SwiftPM tests
fastlane/                      Per-platform archive and delivery
scripts/components             Build, publish, resolve, override and verify SDKs
Tuist.swift / Workspace.swift  Shared project configuration
```

All four shells are generated together. `--platform` selects the default command
platform; `make build PLATFORM=macos` changes it for a command. Each app has its own
platform-suffixed bundle identifier and lifecycle.

## Directory and Dependency Rules

- `Apps/` owns lifecycle, root navigation and platform application configuration.
- `Composition/` binds public component factories to platform implementations.
- `Components/` is for independent component source development and testing.
  Shells do not reference its source package: they consume static XCFrameworks.
- `Shared/Core/` owns portable domain rules/state and the C ABI. Native platform
  dependencies must remain in adapters outside it.
- `Dependencies/components.json` declares exact SDK versions;
  `components.lock.json` locks the full dependency closure and artifact manifests.
- `.artifacts/` is the default local immutable registry. Teams may supply an
  explicitly configured registry using `COMPONENT_REGISTRY`.
- `Dependencies/overrides.local.json` is ignored local state. CI/Release rejects
  overrides; ordinary builds fail if a locked binary is missing or modified.
- Generated `.xcodeproj`, `.xcworkspace`, DI constructors and resolved binaries
  are outputs, not sources of truth.

SafeDI 2.0.0 CLI validates component-internal and shell-public construction graphs.
Graph descriptions stay outside compiled SDK APIs; generated constructors are
compiled against real types. No global service locator or source scan across the
binary boundary is used. See [the architecture decisions](apple-shell-component-architecture.md).

## Required Root Files

### `Brewfile`

Should include tools such as:

- `mise`
- `xcodes`
- `swiftlint`
- `swiftformat`
- `fastlane`

Optional:

- `gh`
- `jq`
- `xcbeautify`

### `.mise.toml`

Should pin versions for at least:

- `ruby`
- `node`
- `tuist`

Add others only when the repo actually depends on them.

### `Makefile`

Should define the standard developer surface:

- `bootstrap`
- `doctor`
- `generate`
- `clean`
- `build`
- `test`
- `test-ui`
- `lint`
- `format`
- `beta`
- `release`

### `scripts/bootstrap`

Should:

1. check that full `Xcode` is installed;
2. confirm the active developer directory;
3. install `Homebrew` dependencies from `Brewfile`;
4. install pinned runtimes with `mise`;
5. install or activate `Tuist`;
6. resolve Swift packages;
7. generate the workspace with `Tuist`;
8. run a basic `doctor` check.

## Standard Initialization Commands

For a fresh machine, the supported path should be:

```bash
xcode-select -p
brew bundle
mise install
make bootstrap
```

For daily development:

```bash
make generate
make build
make test
```

For environment validation:

```bash
make doctor
```

For release automation:

```bash
make beta
make release
```

## Standard Make Targets

Recommended definitions:

- `make bootstrap`: one-time or recovery setup.
- `make doctor`: verify Xcode selection, simulator availability, tool versions, signing prerequisites.
- `make generate`: run `tuist install` if needed, then `tuist generate`.
- `make build`: build the main app scheme through `xcodebuild`.
- `make test`: run unit and integration tests through `xcodebuild test`.
- `make test-ui`: run UI tests on a fixed simulator destination.
- `make lint`: run `swiftlint`.
- `make format`: run `swiftformat`.
- `make beta`: call the `fastlane beta` lane.
- `make release`: call the `fastlane release` lane.

## Xcode Version Policy

The team should pin one primary Xcode version per active branch line.

Rules:

- local machines and CI must use the same Xcode version;
- version changes require a repo PR that updates docs and CI config together;
- `xcode-select` should point to the team-approved Xcode app;
- if multiple Xcode versions are needed, switch them explicitly with `xcodes` or `xcode-select`.

## Dependency Policy

Default rule:

- manage component development dependencies through `SwiftPM`; product shells use the exact binary SDK lock.

Exceptions:

- use `CocoaPods` only when a required SDK does not work correctly with SwiftPM;
- every `CocoaPods` exception must have a short documented reason in the repo.

Additional rules:

- commit `Package.resolved`;
- review dependency additions like code;
- keep app targets thin and push reusable logic into internal modules.

## Module Boundary Policy

Use this split:

- app shell: navigation, lifecycle, composition root, entitlements, environment wiring;
- feature modules: user-facing flows and screens;
- shared packages: reusable logic and infrastructure;
- test support modules: fixtures, mocks, preview helpers.

Do not put everything in one app target.

Recommended evolution path:

1. start with a small number of feature modules;
2. maintain source components in `Components/` and publish their stable SDK boundaries;
3. add stricter boundaries only when module count and build times justify it.

## CI Standard

CI should execute the same repo entrypoints as local development:

```bash
make doctor
make generate
make test
```

Release CI should use:

```bash
make beta
make release
```

Rules:

- CI must not call hidden one-off scripts instead of repo-standard commands;
- CI must declare the Xcode version explicitly;
- generated projects may be regenerated in CI, but generation inputs must come from the repo only.

## Code Signing Standard

Recommended default for a mid-sized team:

- local development uses Xcode automatic signing where possible;
- distribution credentials are managed centrally through `fastlane match` or Apple-managed cloud certificates;
- release lanes own archive and upload behavior.

Avoid:

- undocumented manual certificate export/import as a normal onboarding step;
- release-critical signing logic living only in one engineer's machine state.

## Recommended Adoption Path

1. Pin the Xcode version and commit `Brewfile`, `.mise.toml`, and `Makefile`.
2. Introduce `Tuist` and move project structure into manifests.
3. Standardize `make bootstrap`, `make generate`, and `make test`.
4. Migrate dependencies toward `SwiftPM`.
5. Add `fastlane` for beta and release lanes.
6. Split modules into `Apps/` and `Components/` as the codebase grows.

## Non-Goals

- not a Bazel-based monorepo standard;
- not an all-manual Xcode project workflow;
- not a multi-platform backend/frontend umbrella standard;
- not a process for very large organizations with custom build farms.

## Default Decision

For a mid-sized Apple team starting now, the default environment standard should be:

- full `Xcode` as the required Apple toolchain;
- `Homebrew` for workstation packages;
- `mise` for runtime and CLI pinning;
- `Tuist` for project generation and project conventions;
- `SwiftPM` for component development and exact binary SDK manifests for shell integration;
- `Makefile` as the human-facing command surface;
- `fastlane` for signing, beta, and release automation.
