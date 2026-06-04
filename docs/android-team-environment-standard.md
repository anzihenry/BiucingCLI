# Android Team Environment Standard

## Goal

This document defines a standard development environment for a mid-sized Android team.

Scope:

- Android app development with Kotlin;
- local onboarding and daily development;
- SDK, emulator, and dependency consistency;
- build, test, lint, and release automation.

This standard intentionally centers on the Android-native toolchain and uses `Gradle` as the build and project automation layer.

## Design Principles

- Keep the build path Android-native: `Android Studio`, `Gradle`, Android SDK, Emulator.
- Use one command entrypoint for onboarding and one for daily automation.
- Prefer `Kotlin` as the default language for app and module code.
- Treat `Gradle Wrapper` as the only supported project Gradle entrypoint.
- Pin tool versions in the repo.
- Separate local developer concerns from CI concerns.
- Keep machine-specific SDK paths out of committed project files.

## Standard Stack

### Core Android Toolchain

- `Android Studio`: the primary IDE and SDK management surface.
- `Gradle Wrapper`: the canonical CLI build, test, and automation entrypoint.
- `Android SDK`: platforms, build-tools, platform-tools, and emulator packages.
- `adb`: device, emulator, install, logcat, and debug bridge tooling.
- `Emulator`: local app and UI test execution.

### Environment and Tool Installation

- `Homebrew`: install workstation-level tools on macOS.
- `mise`: pin and activate project runtime versions such as `java`.
- `cmdline-tools`: provide `sdkmanager` and `avdmanager` for SDK and AVD management.

Rule:

- keep `cmdline-tools/latest` as a real directory under the Android SDK root, not only as an external symlink into another tool-managed tree.

### Project Structure and Build Logic

- `Gradle`: build graph, dependency resolution, module composition, and task automation.
- `Android Gradle Plugin`: Android-specific build integration.

### Dependencies

- `Maven Central`: default dependency source.
- `Google Maven`: Android and Jetpack dependency source.
- `Version Catalog`: centralize dependency coordinates and versions.

### Automation

- `Makefile`: stable command surface for developers and CI.
- `fastlane`: beta, internal distribution, Play Store delivery, and metadata automation.

## Tool Responsibilities

### Android Studio

Responsible for:

- SDK installation and updates;
- emulator and device debugging;
- layout inspection, profiling, and local development workflows.

Not responsible for:

- being the only way to build or test the app;
- being the source of truth for versions or build logic.

### Gradle Wrapper

Responsible for:

- all supported build, test, lint, and packaging commands;
- dependency resolution and lockstep plugin execution;
- module composition and shared build conventions.

Not responsible for:

- installing the Android SDK itself;
- hiding environment problems that should be surfaced by `doctor` checks.

### Android SDK and cmdline-tools

Responsible for:

- platform packages, build-tools, platform-tools, emulator images, and licenses;
- command-line management through `sdkmanager`, `avdmanager`, and `adb`.

Not responsible for:

- pinning Java or Gradle versions;
- defining project build logic.

### Homebrew

Responsible for:

- workstation tool installation from `Brewfile`.

Not responsible for:

- pinning per-project runtime versions.

### mise

Responsible for:

- project-level runtime pinning for tools such as `java`;
- activating the expected tool versions in a reproducible way.

### fastlane

Responsible for:

- lanes for internal, beta, and release distribution;
- Play Store metadata, screenshots, and deployment automation;
- packaging release logic so CI and local release flows use the same commands.

### Makefile

Responsible for:

- exposing the small, stable command set the team actually uses every day.

## Standard Repository Layout

```text
.
├── app/
│   ├── build.gradle.kts
│   ├── src/
│   │   ├── main/
│   │   │   ├── AndroidManifest.xml
│   │   │   ├── java/
│   │   │   └── res/
│   │   ├── test/
│   │   └── androidTest/
├── core/
│   ├── designsystem/
│   ├── model/
│   ├── network/
│   └── testing/
├── feature/
│   ├── home/
│   ├── profile/
│   └── settings/
├── gradle/
│   ├── libs.versions.toml
│   └── wrapper/
├── build-logic/
│   └── convention/
├── fastlane/
│   ├── Fastfile
│   └── Appfile
├── scripts/
│   ├── bootstrap
│   ├── doctor
│   ├── setup-android-sdk
│   └── ci/
├── .mise.toml
├── Brewfile
├── Makefile
├── settings.gradle.kts
├── build.gradle.kts
├── gradle.properties
└── README.md
```

## Directory Rules

### `app/`

Contains the installable Android application module.

- `build.gradle.kts`: app module build configuration.
- `src/main/AndroidManifest.xml`: app manifest.
- `src/main/java/`: app shell, navigation, and composition root.
- `src/main/res/`: resources.
- `src/test/`: local JVM tests.
- `src/androidTest/`: instrumentation and UI tests.

Rule:

- if code exists only because the app must launch, compose screens, or declare Android components, it belongs in `app/`.

### `feature/`

Contains user-facing feature modules.

Use for:

- screen flows;
- presentation logic;
- feature-specific state and UI.

Rule:

- user-facing functionality should not accumulate directly in `app/` once the codebase grows beyond a small starter.

### `core/`

Contains reusable shared modules.

Use for:

- design system components;
- domain models;
- networking;
- persistence;
- shared test support.

Rule:

- if a module can be shared by multiple features without depending on app shell concerns, prefer putting it under `core/`.

### `build-logic/`

Contains shared Gradle convention plugins and build configuration code.

Rule:

- keep repeated Gradle logic here instead of copying the same plugin and Android config blocks across modules.

### `gradle/`

Contains Gradle wrapper files and the version catalog.

Rule:

- commit the wrapper and version catalog;
- do not rely on globally installed `gradle`.

### `fastlane/`

Contains delivery automation only.

Rule:

- local build orchestration belongs in `Makefile` and `scripts/`;
- release and Play Store orchestration belongs in `fastlane/`.

### `scripts/`

Contains bootstrap, environment checks, and CI wrappers.

Rule:

- scripts may call `brew`, `mise`, `sdkmanager`, `adb`, and `./gradlew`;
- scripts should not duplicate business logic already defined in `Fastfile`, `Makefile`, or Gradle tasks.

## Source of Truth

The team should treat these files as the canonical sources of truth:

- `Brewfile`: workstation tools.
- `.mise.toml`: runtime versions.
- `settings.gradle.kts`: module graph and plugin repository setup.
- `build.gradle.kts`: root build conventions.
- `gradle/libs.versions.toml`: dependency and plugin versions.
- `gradle.properties`: shared Gradle and Android build settings.
- `Makefile`: supported developer commands.
- `fastlane/Fastfile`: supported delivery lanes.

The team should not treat local SDK paths, IDE caches, or generated artifacts as source of truth.

## Required Root Files

### `Brewfile`

Should include tools such as:

- `mise`
- `android-platform-tools`
- `openjdk@17`
- `fastlane`

Optional:

- `gh`
- `jq`

### `.mise.toml`

Should pin versions for at least:

- `java`

Add others only when the repo actually depends on them.

### `gradle/libs.versions.toml`

Should centralize:

- Android Gradle Plugin version;
- Kotlin version;
- Jetpack library versions;
- test and lint library versions.

### `Makefile`

Should define the standard developer surface:

- `bootstrap`
- `doctor`
- `clean`
- `build`
- `test`
- `test-ui`
- `lint`
- `format`
- `install-debug`
- `beta`
- `release`

### `scripts/bootstrap`

Should:

1. confirm `java` is available and matches the pinned version;
2. install `Homebrew` dependencies from `Brewfile`;
3. install pinned runtimes with `mise`;
4. verify `ANDROID_HOME` or `ANDROID_SDK_ROOT`;
5. verify `cmdline-tools`, `platform-tools`, and required SDK packages;
6. accept required SDK licenses if the workflow allows it;
7. run a basic `doctor` check;
8. warm the Gradle wrapper and dependency resolution path.

## Local Repair Notes

The following issues were observed and repaired on the maintainer machine while validating the Android starter:

- `sdkmanager` and `avdmanager` were installed and callable, but `~/Library/Android/sdk/cmdline-tools` initially pointed outside the SDK root through a symlink.
- in that layout, `avdmanager create avd` failed with `Package path is not valid. Valid system image paths are: null` even though the system image files were present on disk.
- copying `cmdline-tools/latest` into the SDK root as a real directory restored normal package registry behavior for `avdmanager`.
- `gradle` was installed and usable, but in constrained environments it may need `GRADLE_USER_HOME` pointed at a writable directory.
- a healthy final AVD was validated as `Biucing_API_35`.

Recommended workstation checks:

- `sdkmanager --licenses`
- `avdmanager list avd`
- `emulator -list-avds`
- `./gradlew help`

Recommended workstation target state:

- `ANDROID_HOME` or `ANDROID_SDK_ROOT` points to the active SDK root;
- `cmdline-tools/latest/bin/sdkmanager` and `cmdline-tools/latest/bin/avdmanager` exist inside that SDK root;
- at least one healthy AVD exists and can be started;
- the project builds through the committed Gradle wrapper, not a globally installed Gradle binary.

## Standard Initialization Commands

For a fresh machine, the supported path should be:

```bash
brew bundle
mise install
make bootstrap
```

For daily development:

```bash
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
- `make doctor`: verify Java version, SDK path, `adb`, emulator availability, and tool versions.
- `make clean`: run `./gradlew clean`.
- `make build`: build the main app through `./gradlew assembleDebug` or the team-standard aggregate task.
- `make test`: run local unit tests through `./gradlew test`.
- `make test-ui`: run instrumentation or UI tests through `./gradlew connectedDebugAndroidTest`.
- `make lint`: run Android lint and static analysis through `./gradlew lint`.
- `make format`: run the team-standard formatter, such as `ktlintFormat` or `spotlessApply`.
- `make install-debug`: install a debug build to the active device or emulator.
- `make beta`: call the `fastlane beta` lane.
- `make release`: call the `fastlane release` lane.

## Android Studio Version Policy

The team should pin one primary Android Studio and Android Gradle Plugin combination per active branch line.

Rules:

- local machines and CI must use a compatible Java and AGP combination;
- Android Studio upgrades require a repo PR that updates docs and CI config together;
- Gradle wrapper and AGP upgrades should be reviewed as build-system changes, not casual dependency bumps.

## SDK Version Policy

The team should pin:

- one `compileSdk`;
- one `minSdk` policy per app line;
- one `targetSdk` value that tracks current platform requirements on a planned schedule.

Rules:

- SDK version changes should be deliberate and documented;
- emulator images used in CI and local UI testing should match repo expectations;
- machine-local SDK installs may vary in extra packages, but the required project packages must be documented and checked by `doctor`.

## Dependency Policy

Default rule:

- add new dependencies through the version catalog.

Additional rules:

- prefer Jetpack and well-maintained Kotlin-first libraries;
- review dependency additions like code;
- keep app modules thin and push reusable logic into shared modules;
- avoid mixing multiple overlapping frameworks without a clear reason.

## Module Boundary Policy

Use this split:

- app shell: application class, navigation root, dependency wiring, manifests;
- feature modules: user-facing flows and screens;
- core modules: shared design system, domain, data, and utilities;
- test support modules: fixtures, fake implementations, and instrumentation helpers.

Do not put everything in one app module.

Recommended evolution path:

1. start with `app` plus a small number of `feature` and `core` modules;
2. extract repeated logic into shared modules;
3. introduce stricter build logic conventions when module count justifies it.

## Testing Standard

The team should maintain three test layers:

- local JVM tests for business logic and view models;
- instrumentation tests for Android framework integration;
- UI tests for critical user journeys only.

Rules:

- default to fast local tests first;
- keep UI tests focused and stable;
- standard commands must run the same way locally and in CI.

## CI Standard

CI should execute the same repo entrypoints as local development:

```bash
make doctor
make build
make test
```

Release CI should use:

```bash
make beta
make release
```

Rules:

- CI must not call hidden one-off scripts instead of repo-standard commands;
- CI must provision the required Java and Android SDK packages explicitly;
- CI should rely on the committed Gradle wrapper, not a global Gradle install.

## Signing and Release Standard

Recommended default for a mid-sized Android team:

- local development uses debug signing only;
- release keystores and Play credentials are managed centrally in CI or a secure secret store;
- release lanes own bundle generation, signing, and distribution behavior.

Avoid:

- undocumented manual keystore sharing as a normal onboarding step;
- release-critical signing logic living only in one engineer's machine state.

## Recommended Adoption Path

1. Pin Java and Android tool expectations in `Brewfile`, `.mise.toml`, and `Makefile`.
2. Standardize `./gradlew` as the only supported Gradle entrypoint.
3. Add `scripts/bootstrap` and `scripts/doctor` for repeatable onboarding.
4. Centralize versions in `gradle/libs.versions.toml`.
5. Add `fastlane` for beta and release lanes.
6. Split code into `app`, `feature`, `core`, and `build-logic` as the codebase grows.

## Non-Goals

- not a cross-platform Flutter or React Native standard;
- not a global monorepo standard for every client platform;
- not a process for very large organizations with custom Android build farms;
- not a requirement to over-modularize a small starter from day one.

## Default Decision

For a mid-sized Android team starting now, the default environment standard should be:

- `Android Studio` as the required Android IDE;
- `Homebrew` for workstation packages on macOS;
- `mise` for runtime pinning;
- `Gradle Wrapper` as the human-facing and CI-facing build entrypoint;
- `Android SDK` plus `cmdline-tools` for SDK and emulator management;
- `Version Catalog` for dependency version control;
- `Makefile` as the stable command surface;
- `fastlane` for beta and release automation.
