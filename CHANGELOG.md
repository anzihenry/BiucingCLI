# Changelog

## Unreleased

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
