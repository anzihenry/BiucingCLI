# HarmonyOS Team Environment Standard

## Goal

This document defines a standard development environment for a mid-sized HarmonyOS team.

Scope:

- HarmonyOS app development with ArkTS and ArkUI;
- local onboarding and daily development;
- DevEco Studio, SDK, and hvigor consistency;
- build, lint configuration, signing, and release handoff.

This standard intentionally centers on the HarmonyOS-native toolchain and uses `hvigorw` as the command-line build entrypoint.

## Design Principles

- Keep the build path HarmonyOS-native: `DevEco Studio`, HarmonyOS SDK, `ohpm`, and `hvigorw`.
- Use one command entrypoint for onboarding and one for daily automation.
- Prefer ArkTS and ArkUI for app code.
- Keep SDK paths and signing material out of committed project files.
- Treat unsigned local HAP builds as the default generated-project validation target.
- Add CLI test and release commands only after their DevEco/hvigor behavior is stable on a real workstation.

## Standard Stack

### Core HarmonyOS Toolchain

- `DevEco Studio`: the primary IDE, SDK management surface, signing UI, previewer, and device workflow.
- `HarmonyOS SDK`: application SDK, ArkTS build tools, toolchains, resources, and previewer support.
- `ohpm`: HarmonyOS package manager and dependency installer.
- `hvigorw`: the canonical CLI build entrypoint.
- `ArkTS`: default app language.
- `ArkUI`: default declarative UI layer.

### Environment and Tool Installation

- `zsh` startup environment: exports the DevEco tools and SDK paths for local CLI builds.
- `mise`: pins Node.js for command-line build consistency.
- `Makefile`: exposes the small supported command surface.

Recommended macOS environment:

```bash
export PATH="/Applications/DevEco-Studio.app/Contents/tools/ohpm/bin:/Applications/DevEco-Studio.app/Contents/tools/hvigor/bin:$PATH"
export DEVECO_SDK_HOME="/Applications/DevEco-Studio.app/Contents/sdk"
export HOS_SDK_HOME="/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony"
```

## Tool Responsibilities

### DevEco Studio

Responsible for:

- SDK installation and updates;
- signing material setup;
- device and emulator workflows;
- previewer, profiler, and IDE lint feedback.

Not responsible for:

- being the only way to build a generated starter;
- hiding missing SDK environment from command-line validation.

### hvigorw

Responsible for:

- local command-line HAP packaging;
- running the same project build graph that DevEco Studio uses;
- surfacing project structure and SDK compatibility errors.

Not responsible for:

- installing DevEco Studio or SDKs;
- managing signing secrets.

### ohpm

Responsible for:

- installing HarmonyOS package dependencies;
- keeping generated project dependencies reproducible.

### Makefile

Responsible for:

- exposing supported developer commands;
- keeping CLI validation short and repeatable.

## Standard Repository Layout

```text
.
├── AppScope/
│   ├── app.json5
│   └── resources/
├── entry/
│   ├── build-profile.json5
│   ├── hvigorfile.ts
│   ├── oh-package.json5
│   └── src/
│       └── main/
│           ├── ets/
│           │   ├── core/
│           │   │   ├── config/
│           │   │   └── designsystem/
│           │   ├── entryability/
│           │   └── pages/
│           ├── module.json5
│           └── resources/
├── docs/
│   └── release-signing.local.properties.example
├── hvigor/
│   └── hvigor-config.json5
├── scripts/
│   ├── bootstrap
│   ├── doctor
│   ├── lint
│   └── release-build
├── .mise.toml
├── Makefile
├── build-profile.json5
├── code-linter.json5
├── hvigorfile.ts
├── oh-package-lock.json5
├── oh-package.json5
└── README.md
```

## Source of Truth

- `build-profile.json5`: product, module, SDK, build mode, and signing shape.
- `AppScope/app.json5`: application identity, bundle name, label, icon, and version.
- `entry/src/main/module.json5`: entry module, ability, device types, and routes.
- `entry/src/main/ets/core/config/AppConfig.ets`: generated bundle, module, ability, version, and channel constants.
- `entry/src/main/ets/core/designsystem/Tokens.ets`: shared ArkUI tokens for starter pages.
- `entry/src/main/ets/pages/`: routeable ArkUI pages, including settings/config surfaces.
- `oh-package.json5` and `oh-package-lock.json5`: HarmonyOS package metadata and lock state.
- `hvigor/hvigor-config.json5`: hvigor execution settings.
- `code-linter.json5`: DevEco Studio lint configuration source.
- `Makefile`: supported CLI commands.
- `scripts/doctor`: local environment readiness checks.

## Supported Commands

```bash
make bootstrap
make doctor
make lint
make build
make package
make release
make signing-info
make open
```

`make build` must produce an unsigned HAP on a configured workstation. `make release` may be used only when local signing material has been supplied through git-ignored `local.properties`.

## Lint Policy

The template commits `code-linter.json5` and exposes `make lint` as a static configuration guard.

Current CLI lint scope:

- verify lint config is valid JSON;
- verify source/config files contain no unrendered template placeholders;
- verify required HarmonyOS config, page, design system, and release script files exist.

DevEco Studio remains the primary full ArkTS lint surface until a stable command-line linter entrypoint is verified. In the current DevEco Studio CLI install, `hvigorw tasks` does not expose lint, `hvigorw lint` is not a working public HAP task, and `hvigorw arkLinter` reports that the task is not present for the generated entry module.

## Testing Policy

Do not expose `make test` until a generated project can run ArkTS/Hypium tests reliably through the CLI on a clean workstation.

Current verification found that `hvigorw test --mode module -p module=entry` enters the UnitTest pipeline, but fails unless `entry/src/test/List.test.ets` exists and then still fails because `@ohos/hypium` cannot be resolved. Declaring `@ohos/hypium@1.0.0` in `oh-package.json5` follows DevEco template shape, but the configured OpenHarmony ohpm registry did not provide that package during verification. Keep this blocked until dependency resolution is repeatable.

The current release bar is:

- generate a project;
- run `make bootstrap`;
- run `make doctor`;
- run `make lint`;
- run `make build`;
- verify an unsigned HAP is produced.

## Signing And Release Policy

Generated projects should not commit signing secrets.

Local signing setup may use:

- DevEco Studio project signing settings;
- local-only `local.properties`;
- CI-specific secret injection.

`make release` reads local-only signing keys from `local.properties`, checks that certificate, profile, and store files exist, temporarily injects a `HarmonyOS` release signing config into `build-profile.json5`, runs hvigor with `buildMode=release`, and restores the original build profile afterward.
