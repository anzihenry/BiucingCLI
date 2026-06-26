# Changelog

## Unreleased

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
