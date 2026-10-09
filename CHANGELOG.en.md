---
title: "Changelog"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# Changelog

[中文](CHANGELOG.md) · Translation of the Chinese primary document.

Detailed historical records and publication-evidence limits are listed in the [release index](docs/releases/README.en.md).

## 0.10.0 - 2026-09-30

### CLI and packaging

- Add versioned JSON results and errors, strict option names, non-interactive input
  handling and safe escaping across generated language/configuration files.
- Introduce typed creation plans, metadata-declared file contracts and deterministic
  resource variants shared by preview, validation and project generation.
- Verify exact wheel/sdist resources, executable flags, rebuilt wheels and installed
  template output; split core and platform tests across Python 3.11–3.14.

### Frontend

- Ship CSR, SSG and SSR React Router presets with shared React/TypeScript/Tailwind
  tooling, frozen dependencies, quality gates and browser acceptance.
- Add SSG content routes, metadata, sitemap and real static 404 delivery. Add SSR
  request isolation, private configuration, bounded rendering and graceful shutdown.
- Verify installed-package projects and production Nginx/Node containers on Linux
  and macOS through the release frontend matrix.

### Native components

- Generate iOS, macOS, watchOS and tvOS shells consuming versioned static XCFrameworks,
  exact SDK locks and SafeDI constructor graphs; require Swift 6.4 or later.
- Generate Android mobile, Wear OS and TV shells with binary Maven AARs, Dagger
  graphs, JNI sessions, device-specific input and independent release identities.
- Add HarmonyOS binary HARs, constructor graphs and a Node-API bridge using the same
  canonical C++20 core as Apple and Android.
- Define session ownership, cancellation and asynchronous close across platforms;
  verify source-free SDK consumption, integrity and explicit local overrides.

### Backend

- Add Docker-first task wrappers, independent database/cache choices, validated
  file secrets, private health/admin endpoints and bounded request/shutdown behavior.
- Add PostgreSQL pools and locked migrations, Web OIDC/PostgreSQL sessions,
  Micro mTLS authorization, trusted user delegation and protocol compatibility gates.
- Add outbound HTTP/gRPC clients with identity verification, budgets and explicit
  idempotent retries, plus structured logs and OpenTelemetry traces/metrics.
- Add hardened production Compose, signed-image verification, migration/release
  guards, rollback and isolated PostgreSQL backup/restore tooling.
- Add Kubernetes/Kustomize references with replica spreading, HPA, network policies,
  connection budgets and release/evidence tools. B27 real multi-zone HA acceptance
  remains on hold; no production availability or recovery target is claimed.
- Fix backend help output, macOS DNS reconnect tests, Linux certificate fixture
  permissions and recovery timing, plus Android CI SDK initialization.

### Compatibility changes

- Rename `microservice` to `micro-service`; remove the old CLI template name.
- Remove `--dependency-store` / `dependency_store`; use independent `--database`
  and `--cache` options. Micro defaults to neither; Web requires PostgreSQL.
- Remove the Web in-memory user CRUD fixture. Application business APIs are added
  by the generated project's owner.

## 0.9.1 - 2026-09-19

- manage development and build dependencies with uv sync and a committed uv.lock;
- run CI and installed-artifact checks through uv with locked build tools;
- add verified TestPyPI/PyPI publishing through uv publish and Trusted Publishing.

## 0.9.0 - 2026-09-07

- bundle all seven templates inside wheel and source-distribution artifacts so installed CLI commands no longer depend on the source repository layout;
- normalize resolved inputs before computing platform and dependency-derived values;
- add stable user-facing failures for unknown templates, invalid metadata, target conflicts, and generation I/O errors;
- render projects through a temporary staging directory and publish them atomically;
- add cross-version CI and an installed-artifact verification gate covering all seven templates.

## 0.8.0 - 2026-08-31

- unify metadata-driven input validation and the `bootstrap`, `doctor`, `lint`, `test`, `verify`, `build`, `clean`, and `help` Make command contract across all templates.
- add Android Gradle distribution, wrapper JAR, and dependency checksum verification plus signer-certificate validation for release AABs; add HarmonyOS exact ohpm lock validation and SDK-backed HAP signer, profile, and bundle-identity verification.
- Add explicit Worker retry exhaustion, exponential backoff, scheduled-cycle continuation, cancellation, and deterministic injected-clock tests.
- Add bounded HTTP timeouts, signal-aware graceful shutdown, runtime health checks, and coordinated HTTP/gRPC draining to the Web Service and Microservice templates.
- hardened Apple archive, TestFlight, and App Store release workflows so worktree debug bundle suffixes are always discarded, with Release workspace and xcarchive identity checks before signing and upload.
- hardened Apple, Android, and HarmonyOS starter ignore rules for credentials and signing files, and added verified restoration around HarmonyOS release signing injection.
- implemented and tested the microservice starter's protobuf `Ping` gRPC contract, including real service registration and Buf generation prerequisites for runtime workflows.
- added a committed pnpm lockfile and a Playwright browser gate against the Frontend starter's production Nginx image.

## 0.7.0 - 2026-08-01

- completed release-delivery workflows for the Apple and Android starters, including signed archive/upload lanes for App Store Connect and Google Play tracks when local credentials are configured;
- added Android release-signing verification and App Bundle artifact checks, including a reliable `BundleConfig.pb` integrity check;
- completed HarmonyOS local pre-distribution automation with signing preflight and signed HAP build support;
- recorded fresh native real-build evidence: Apple iOS/macOS generation, build, test, and simulator verification; Android lint, unit, APK, AAB, and emulator UI verification; HarmonyOS verify, test, and HAP verification;
- clarified the remaining external boundary: no real store upload is claimed without the respective Apple, Google Play, or AppGallery credentials and application records.

## 0.6.1 - 2026-07-20

- unified worktree identity across all seven starters with `WORKTREE_LABEL`, hash-based `WORKTREE_ID`, and `WORKTREE_SLUG`.
- added Docker-first port conflict advice and generated `make worktree-compose-config` diagnostics.
- strengthened native worktree verification docs with explicit `static`, `doctor`, and `real-build` evidence tiers.
- clarified HarmonyOS debug identity behavior with a read-only diagnostic target and deferred bundle rewriting boundary.
- added 0.6.1 release-prep evidence covering all seven generated templates.

## 0.6.0 - 2026-07-19

- added a shared worktree isolation contract and release evidence path across all seven starters.
- exposed template worktree support through `biucing list`, `biucing info`, JSON output, and `biucing validate`.
- made Docker-first starters worktree-ready with isolated Compose project names, Docker volumes, image tags, host ports, dependency stores, caches, diagnostics, and cleanup.
- made native starters worktree-ready with isolated build/tool caches, local signing/config visibility, generated-output cleanup, and debug identity suffix hooks.

## 0.5.0 - 2026-06-28

- added an experimental `harmonyos` template for ArkTS + ArkUI DevEco Studio projects with CLI flags, doctor/bootstrap scripts, metadata validation, and render tests.
- strengthened the `harmonyos` template with real `hvigorw` build alignment, a team environment standard, lint configuration guards, deeper doctor checks, and release-signing guidance.
- expanded the `harmonyos` starter with shared app config, design-system tokens, a settings/config page, deeper generated-project guards, and local signing material driven `make release` automation.

## 0.4.0 - 2026-06-26

- added `create --dry-run`, `create --plan`, and JSON create manifests so generation can be previewed and audited more easily;
- strengthened template metadata and `validate` rules with verification tiers, operating assumptions, workflow labels, and family-level required-file checks;
- added a new `worker` starter for scheduled and oneshot background execution workloads;
- refreshed release-prep and verification docs to match the expanded six-template product surface.

## 0.3.0 - 2026-06-19

Product-hardening release for BiucingCLI itself.

- expanded `template.json` so templates now expose category, tags, platforms, maturity, and validation metadata;
- added machine-readable `--json` output for `biucing list` and `biucing info`;
- improved `biucing create` scripting with `--set key=value` overrides and explicit non-interactive failure behavior;
- added repo-level validation for template metadata completeness and placeholder consistency;
- added golden coverage for `list/info` output and standardized release-checklist, verification-matrix, and `0.3.0` release-prep documentation.

## 0.2.0 - 2026-06-17

Template-system expansion release for BiucingCLI.

- fully Dockerized the `frontend`, `web-service`, and `microservice` templates for development, build, and runtime workflows;
- strengthened the Apple starter with default lint/format config, better doctor coverage, platform-specific `iOS` and `macOS` output, release documentation, and a new `Packages/AppServices` shared package;
- strengthened the Android starter with real formatting, richer doctor checks, UI smoke coverage, release-signing placeholders, modular infrastructure expansion, and a more intentional design-system layer;
- completed the Apple/Android roadmap and validated the resulting templates with repeated real generated-project build and test runs.

## 0.1.0 - 2026-06-06

Initial public project baseline for BiucingCLI.

- shipped the focused scaffold-generator rewrite with `list`, `info`, and `create` flows;
- included practical starters for `frontend`, `apple`, `android`, `web-service`, and `microservice`;
- aligned repository docs around the template system and team-environment standards;
- added real validation coverage for generated projects and template rendering behavior.
