# Changelog

## Unreleased

- fix frontend generation baselines contaminated by local empty pnpm cache
  directories; guard shared and mode-specific resource layers against build artifacts.

- add installed-wheel CSR/SSG/SSR acceptance with native frontend quality/browser
  checks, real production-container checks, scoped cleanup and retained diagnostics;
  share a six-job Linux/macOS frontend matrix between CI and release gates.
- verify every template resource in wheel/sdist and in a wheel rebuilt from sdist,
  including hidden files, binaries and executable flags; add artifact/runner/CI
  regressions without changing generated projects or existing golden outputs.

- add the frontend SSR preset with request-isolated loaders, private server
  configuration, uncached HTML/data responses, bounded rendering and a non-root
  Node production image; cover input/error handling, client artifact boundaries,
  HTTP/static file safety and graceful/forced shutdown. Preserve one shared
  frontend dependency lockfile and add SSR generation/distribution regressions.

- add the frontend SSG preset with explicitly enumerated content routes, build-time
  HTML/navigation data, validated SITE_URL, per-page metadata, sitemap/robots and
  static Nginx real-404 deployment; share dependencies/components with CSR and
  separate preview routing so deep-link refresh does not fall back to the homepage.

- migrate frontend to a CSR-only React Router Framework preset with shared React
  19.3 / TypeScript 7 / Tailwind 4 / shadcn UI resources and a pnpm 11 lockfile;
  preserve worktree-scoped Docker/Make workflows, add typed-lint negative checks,
  browser interaction coverage and frontend-only golden updates. SSG/SSR are not
  advertised yet. Revalidate development/production Docker images on Linux arm64
  and browser behavior against actual Nginx; fix the IPv4/IPv6 preview mismatch
  in container SPA prerender and protect the configuration with a regression check.

- integrate optional resource variants with generation plans, effective file/Make/
  placeholder validation, all-mode validation and staged execution; detect source
  drift and add optional schema-1 variant summaries without changing legacy output;
- add 17 fixture-based integration tests for variants, JSON contracts, source
  changes, conflicts and cleanup; shipped frontend resources remain unchanged.

- add immutable resource-variant models, strict optional metadata loading and a
  standalone deterministic resource resolver with 21 fixture-based core tests;
  generation/preview integration and shipped frontend modes remain future work.

- document the stage-0 frontend CSR/SSG/SSR design, resource composition contract,
  compatibility decisions and phased acceptance gates; no runtime changes yet.

- move text/JSON presentation and output versioning out of CLI, retaining formatter
  adapters and existing output contracts;
- organize CLI, generated-output, platform and module tests without dropping
  existing cases, and document template contribution and compatibility boundaries.

- introduce typed creation requests and generation plans shared by preview and
  execution, and inject input callbacks instead of reading terminals in the core;
- consolidate CLI variable aliases while retaining legacy resolver/context adapters.

- declare template file contracts, rule outputs and escape contexts in metadata;
- scope generation placeholders per template and validate extension declarations;
- verify declaration-only onboarding with a Python backend fixture, preserving
  existing output and required-file baselines.

- extract Apple, Android and microservice derivations into pure built-in rules
  selected by a static registry, preserving generated output and JSON metadata.

- separate variable constraints, template validation, text rendering and filesystem
  generation, preserving legacy exports and adding multi-stage cleanup regressions.

- extract template models, domain errors and resource loading into independent
  modules, retaining legacy imports and adding explicit fixture-root loading.

- parse generated JSON, JSON5, YAML, TOML, XML and plist configurations in
  regression tests and installed-wheel verification;
- split Python-only Linux/macOS core CI from macOS tool integration release gates;
- add explicit suite selection and prevent dedicated suites from silently skipping tests.

- expose variable validators, choices, and effective numeric bounds in list/info JSON;
- add schema_version and generator_version to every JSON result and error envelope.

- handle terminal EOF and Ctrl+C without tracebacks, with exit codes 2 and 130;
- disable prompts for JSON mode and non-terminal stdin, and send prompts to stderr;
- emit versioned JSON errors on stderr, including argument parsing and validation failures;
- require complete long option names so JSON error-mode detection is unambiguous.

- escape free-text template inputs for their XML, Android resource, JSON,
  JavaScript, Kotlin, Swift, YAML, and Dockerfile contexts;
- preserve placeholder-like user text with single-pass rendering and add
  special-character generation regression coverage.

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
