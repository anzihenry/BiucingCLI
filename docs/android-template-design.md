# Android Template Design

## Goal

This document defines the first implementation target for an `android` template in BiucingCLI.

The intent is not to generate every possible Android architecture. The intent is to generate a Kotlin-first starter that matches the environment standard already defined in [Android Team Environment Standard](android-team-environment-standard.md).

## Position in Product Scope

The `android` template should be treated as a later-stage template, after the current `frontend`, `web-service`, and `apple` template system feels stable.

Why:

- Android introduces more environment surface than `frontend` or `web-service`;
- the template needs to coordinate `Gradle`, Android SDK expectations, emulator guidance, and signing boundaries;
- the CLI currently supports simple placeholder replacement only, so the first Android template should stay intentionally small.

## First Version Outcome

`biucing create android <project-name>` should generate:

- a Kotlin Android app starter;
- a stable multi-module layout with `app`, `feature`, and `core`;
- `Gradle Wrapper`-based commands;
- a small `Makefile` and `scripts/bootstrap` / `scripts/doctor` surface;
- a README that explains local setup and the first build commands.

It should not try to generate:

- multiple app flavors on day one;
- Play Store publishing credentials;
- complex code generation pipelines;
- a large modular architecture with dozens of modules.

## Recommended Stack

The default stack should be:

- Kotlin
- Android Gradle Plugin
- Gradle Wrapper
- Jetpack Compose
- AndroidX / Jetpack
- fastlane

This keeps the template current and aligned with a Kotlin-first modern Android workflow.

## Template Metadata Proposal

Suggested `templates/android/template.json`:

```json
{
  "name": "android",
  "description": "Kotlin Android app starter for mid-sized teams",
  "stack": ["Kotlin", "Android", "Gradle", "Jetpack Compose", "fastlane"],
  "variables": [
    { "name": "project_name", "required": true },
    { "name": "display_name", "required": false, "default_from": "project_name" },
    { "name": "package_name", "required": true, "prompt": "Android package name: " },
    { "name": "application_id", "required": false, "default_from": "package_name" },
    { "name": "organization_name", "required": false, "default": "Example Team" },
    { "name": "compile_sdk", "required": false, "default": "35" },
    { "name": "min_sdk", "required": false, "default": "26" },
    { "name": "target_sdk", "required": false, "default": "35" },
    { "name": "version_code", "required": false, "default": "1" },
    { "name": "version_name", "required": false, "default": "1.0.0" },
    { "name": "java_version", "required": false, "default": "17" },
    { "name": "android_namespace", "required": false, "default_from": "package_name" },
    { "name": "kotlin_module_name", "required": false }
  ],
  "next_steps": [
    "make bootstrap",
    "make build",
    "make test",
    "open -a \"Android Studio\" ."
  ]
}
```

## Variable Design

### Core Variables

- `project_name`: target directory name.
- `display_name`: human-facing app name shown in generated docs and default resources.
- `package_name`: base Java/Kotlin package path, such as `com.example.app`.
- `application_id`: Android application ID. Defaulting to `package_name` keeps the first version simple.

### SDK and Version Variables

- `compile_sdk`: repo-standard compile SDK.
- `min_sdk`: minimum supported Android version.
- `target_sdk`: target SDK for behavior and policy compatibility.
- `version_code`: initial Android version code.
- `version_name`: initial user-facing version string.
- `java_version`: Java toolchain version for Gradle and Android builds.

### Naming Variables

- `android_namespace`: module namespace for AGP. Default to `package_name`.
- `kotlin_module_name`: fallback for places where a PascalCase module identifier is useful in docs or sample code.
- `organization_name`: used in README and ownership placeholders only.

## Placeholder Proposal

The current renderer does simple text replacement. The Android template should stay within that constraint.

Suggested new placeholders:

- `{{APPLICATION_ID}}`
- `{{ANDROID_NAMESPACE}}`
- `{{COMPILE_SDK}}`
- `{{MIN_SDK}}`
- `{{TARGET_SDK}}`
- `{{VERSION_CODE}}`
- `{{VERSION_NAME}}`
- `{{JAVA_VERSION}}`
- `{{KOTLIN_MODULE_NAME}}`

The existing placeholders remain useful:

- `{{PROJECT_NAME}}`
- `{{DISPLAY_NAME}}`
- `{{PACKAGE_NAME}}`
- `{{ORGANIZATION_NAME}}`

## Directory Shape

Suggested generated output:

```text
my-android-app/
  README.md
  Brewfile
  .mise.toml
  Makefile
  settings.gradle.kts
  build.gradle.kts
  gradle.properties
  app/
    build.gradle.kts
    src/
      main/
        AndroidManifest.xml
        java/
        res/
      test/
      androidTest/
  core/
    designsystem/
      build.gradle.kts
      src/
    model/
      build.gradle.kts
      src/
  feature/
    home/
      build.gradle.kts
      src/
  fastlane/
    Fastfile
    Appfile
  gradle/
    libs.versions.toml
    wrapper/
  scripts/
    bootstrap
    doctor
    setup-android-sdk
```

## Module Plan

### `app`

Responsibilities:

- application manifest;
- app entrypoint;
- navigation root;
- dependency wiring;
- top-level Compose shell.

### `feature/home`

Responsibilities:

- one sample user-facing feature;
- a screen and minimal presentation logic;
- a concrete demonstration of how future features should be added.

This is enough to prove the module pattern without generating empty folders for many speculative features.

### `core/model`

Responsibilities:

- shared domain models and app-wide types.

### `core/designsystem`

Responsibilities:

- theme setup;
- reusable Compose primitives;
- typography and color tokens.

This gives the starter one meaningful shared module path without making the graph too complex.

## Build File Strategy

The first version should use:

- `settings.gradle.kts` for module includes and repository configuration;
- root `build.gradle.kts` for shared plugin declarations only;
- `gradle/libs.versions.toml` for plugin and dependency versions;
- per-module `build.gradle.kts` files for Android and Kotlin configuration.

Avoid in version one:

- heavy custom Gradle plugins;
- large `buildSrc` logic;
- complex flavor matrices;
- KSP or kapt unless the starter truly needs them.

## README Expectations

The generated README should explain:

- required local tools;
- how `make bootstrap` works;
- how `make wrapper` is used when the team intentionally refreshes the committed wrapper files;
- how to run `make build`, `make test`, and `make install-debug`;
- where feature and shared modules live;
- what files are source of truth.

The README should not pretend release signing is locally configured by default.
The README should also state that `gradle/wrapper/gradle-wrapper.jar` is committed in the starter and should remain versioned after refreshes.

## Scripts and Makefile Expectations

### `Makefile`

Recommended first targets:

- `bootstrap`
- `doctor`
- `clean`
- `build`
- `test`
- `test-ui`
- `lint`
- `format`
- `install-debug`

### `scripts/bootstrap`

Should:

1. verify `java`;
2. install `brew` dependencies if available;
3. run `mise install`;
4. check `ANDROID_HOME` or `ANDROID_SDK_ROOT`;
5. check `adb`, `sdkmanager`, and required SDK packages;
6. run the environment `doctor` check.

### `scripts/doctor`

Should verify:

- Java version;
- Android SDK path;
- `adb`;
- `sdkmanager`;
- at least one emulator or connected device;
- Gradle wrapper availability.

The doctor output should make the wrapper strategy explicit:

- the starter should ship with committed wrapper files and use `./gradlew` by default;
- if the wrapper files are missing or intentionally refreshed, regenerate them with local `gradle` and recommit the results.

## Testing Shape

The generated starter should include:

- one local JVM test in a shared module;
- one app-level instrumentation or UI smoke test only if it can stay stable;
- one minimal lint path.

The template should avoid generating a large, mostly empty test tree.

## CLI Impact

To support an Android template cleanly, the CLI likely needs:

1. new `create` flags for Android variables;
2. new placeholder mappings in `src/biucingcli/templates.py`;
3. one small helper for deriving a default `kotlin_module_name`, similar to the existing Swift helper;
4. tests that validate Android placeholder rendering and next-step output.

This is still a low-risk extension because it follows the same metadata-driven pattern already used by existing templates.

## Recommended Implementation Order

### Phase 1: Metadata and Placeholder Support

- extend placeholder mapping for Android values;
- add CLI flags and defaults;
- add test coverage for resolved variables and rendered output.

### Phase 2: Template Skeleton

- add `templates/android/template.json`;
- add root Gradle files, version catalog, `Makefile`, and scripts;
- add `app`, `feature/home`, `core/model`, and `core/designsystem`.

### Phase 3: Verification Net

- add tests that `biucing create android` produces the expected files;
- verify rendered values in `settings.gradle.kts`, `gradle.properties`, and app manifest;
- verify next-step output is readable and consistent.

### Phase 4: Docs Alignment

- update `README.md`;
- update `docs/template-system.md`;
- align the generated Android README and design docs on the `gradle-wrapper.jar` commit policy;
- update `docs/product-design.md` and `docs/roadmap.md` only if Android moves from later to planned implementation.

## Default Decision

For the first BiucingCLI Android template, the default should be:

- Kotlin only;
- Jetpack Compose as the UI path;
- Gradle Kotlin DSL;
- `Gradle Wrapper` as the only supported build entrypoint;
- one app module plus a very small set of shared and feature modules;
- environment bootstrap through `Brewfile`, `.mise.toml`, `Makefile`, and `scripts/`.
