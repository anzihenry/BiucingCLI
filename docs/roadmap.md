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

## Next

The next release scope is not locked yet.
Use [docs/roadmap.md](roadmap.md) together with a future version plan once `0.5.0` priorities are chosen.

## Deferred

These remain intentionally out of scope unless the roadmap changes:

- several unrelated new templates in one release;
- a heavy external templating engine;
- remote registries, plugin systems, or online template marketplaces;
- turning BiucingCLI into a generalized platform or workflow orchestrator.
