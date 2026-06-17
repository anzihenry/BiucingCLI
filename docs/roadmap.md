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

## Next

### 0.3.0 - Productize The Generator

Primary direction:

- keep the current five-template strategy stable;
- improve BiucingCLI itself as a product, not just the generated templates;
- make the generator easier to inspect, script, validate, and trust in repeated use.

Planned workstreams:

- CLI experience hardening:
  add better inspection and machine-readable output around template discovery and creation.
- Template metadata evolution:
  extend metadata so the CLI can explain maturity, platform support, validation status, and operating assumptions.
- Verification productization:
  standardize how the repo proves template quality across Python tests and generated-project smoke checks.
- Release readiness:
  make version planning, changelog preparation, and release evidence easier to maintain from the repo.

### Candidate 0.3.0 Outcomes

- `biucing list` and `biucing info` can serve both humans and scripts cleanly.
- `biucing create` is more predictable in unattended and repeatable workflows.
- each template exposes clearer maturity signals and supported workflows.
- the repo has a cleaner release plan and verification matrix for future versions.

## Deferred

These are intentionally not the center of `0.3.0` unless the roadmap changes:

- broad new template categories;
- a heavy external templating engine;
- turning BiucingCLI into a generalized platform or workflow orchestrator.
