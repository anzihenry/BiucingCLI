# Roadmap

## Shipped

### 0.1.0 - Scaffold Generator Baseline

- established the metadata-driven template system;
- shipped `biucing list`, `biucing info`, `biucing create`, and `biucing --version`;
- shipped five starters: `frontend`, `web-service`, `microservice`, `apple`, and `android`;
- aligned the repo around a focused scaffold-generator product direction.

### 0.2.0 - Template Maturity Expansion

- fully Dockerized the `frontend`, `web-service`, and `microservice` starters for local development and runtime packaging;
- expanded the Apple starter into a stronger Tuist + SwiftPM baseline with platform-aware output and better doctor/lint/release guidance;
- expanded the Android starter into a more complete Kotlin + Compose baseline with a committed Gradle wrapper, stronger doctor checks, UI smoke coverage, and release-signing placeholders;
- validated generated starters repeatedly with real build and test workflows.

### 0.3.0 - Productize The Generator

- expanded the CLI surface beyond create-time generation by shipping `validate` plus JSON output for `list`, `info`, and `validate`;
- made `create` more scriptable with `--set KEY=VALUE`, `--non-interactive`, and clearer variable resolution behavior;
- enriched template metadata so the CLI can expose category, tags, platform support, maturity, validation status, variables, and next steps;
- added repo-level validation and golden coverage so the generator surface is easier to trust and maintain;
- prepared versioned release-planning and verification docs to make future releases easier to repeat.

### 0.4.0 - Sharpen The Product, Normalize The Portfolio, Add One New Surface
- improved generation UX with dry-run, plan-style inspection, and machine-readable create manifests;
- tightened the shared metadata, validation, docs, and workflow contract across the template family;
- added the new `worker` starter as a sixth template surface;
- `biucing create` can preview what it will generate before files are written.
- scripts can rely on a stable, machine-readable generation summary after create succeeds.
- the current template family follows a clearer shared product contract.
- the portfolio grows through a new `worker` starter without lowering validation quality.

### 0.5.0 - HarmonyOS Starter

- added an experimental `harmonyos` template for ArkTS + ArkUI DevEco Studio projects;
- wired HarmonyOS bootstrap, doctor, lint, build, and release-signing guidance;
- expanded the template portfolio to seven shipped starters;
- kept HarmonyOS generated-project validation separate from workstation-specific SDK availability.

### 0.6.0 - Worktree-First Starters

`0.6.0` makes BiucingCLI's generated starters safe for parallel Git worktree development.

The release is centered on:

- a shared worktree isolation contract across all seven templates;
- Docker-first isolation for Compose project names, volumes, ports, runtime image tags, dependency stores, and caches;
- native-template isolation for build caches, local signing files, IDE output, and debug app identities;
- generated `make worktree-info`, `make worktree-doctor`, and `make clean-worktree` workflows where appropriate;
- validation, docs, and release evidence that prove parallel-worktree behavior instead of only claiming it.

Implementation status:

- Phase A through Phase D are complete;
- all seven templates declare `worktree-ready` metadata;
- Phase E release-hardening docs and verification evidence are complete.

Planning anchors:

- [0.6.0 Plan](0.6.0-plan.md)
- [0.6.0 Worktree Task Breakdown](0.6.0-worktree-tasks.md)
- [0.6.0 Release Prep](0.6.0-release-prep.md)

### 0.6.1 - Worktree Isolation Hardening

`0.6.1` hardened the worktree-first behavior shipped in `0.6.0`.

The release is focused on:

- unifying the worktree identity model across Docker-first and native templates;
- adding actionable port-conflict advice for Docker-first templates;
- exposing non-invasive Compose config diagnostics as generated-project commands;
- making native worktree evidence more precise;
- deciding the safe boundary for HarmonyOS debug identity behavior.

Planning anchors:

- [0.6.1 Plan](0.6.1-plan.md)
- [0.6.1 Worktree Hardening Task Breakdown](0.6.1-worktree-hardening-tasks.md)
- [0.6.1 Release Prep](0.6.1-release-prep.md)

Implementation status:

- all seven templates use one worktree identity model;
- Docker-first templates expose port conflict advice and Compose config diagnostics;
- native evidence is split into `static`, `doctor`, and `real-build` tiers;
- HarmonyOS debug bundle rewriting is explicitly deferred behind a read-only diagnostic boundary.

## Current

### 0.7.0 - Native Release Readiness

`0.7.0` completes the native templates' local verification and pre-distribution workflows.

The release is focused on:

- Apple Fastlane archive, TestFlight, and App Store Connect delivery lanes;
- Android signing validation, release AAB validation, and Google Play internal/production delivery lanes;
- HarmonyOS signing preflight and local release HAP generation;
- fresh real-build evidence across Apple, Android, and HarmonyOS.

Release anchors:

- [0.7.0 Release Notes](0.7.0-release-notes.md)
- [0.7.0 Release Prep](0.7.0-release-prep.md)

External account credentials and actual store submissions remain intentionally outside the committed template configuration.

## Deferred

These remain intentionally out of scope unless the roadmap changes:

- several unrelated new templates in one release;
- a heavy external templating engine;
- remote registries, plugin systems, or online template marketplaces;
- turning BiucingCLI into a generalized platform or workflow orchestrator.
- automatically managing Git worktrees inside BiucingCLI.
