---
title: "Documentation map"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# Documentation map

[中文](README.md) · Translation of the Chinese primary document.

## Reading paths

- Use the project: [BiucingCLI](../README.en.md) → [Guides](guides/README.en.md).
- Understand capabilities: [Product documentation](product/README.en.md) → [Engineering documentation](engineering/README.en.md).
- Develop and verify: [Development, builds, and publishing with uv](guides/development.en.md) → [Test suites and configuration validation](guides/testing.en.md) → [BiucingCLI Verification Matrix](guides/verification-matrix.en.md).
- Track work: [Project planning](planning/README.en.md) → [Initiative index](initiatives/README.en.md).
- Inspect versions: [Changelog](../CHANGELOG.en.md) → [Release record index](releases/README.en.md).
- Maintain documentation: [Project documentation conventions](documentation.en.md) → [Documentation structure migration](initiatives/process/documentation-standard/README.en.md).

## Boundaries

Durable knowledge, repeatable procedures, initiatives and version facts have separate homes. The directory model follows HarnessBrew. Only populated domains are created; no standalone research or interaction/visual design material exists yet.

Root entrypoints, CHANGELOG and maintained docs have Chinese primary files and English `.en.md` counterparts with language switches and language-specific indexes. Generated-project documents, raw logs and machine reports retain their original language.

Documents under `src/biucingcli/template_data/` are generated-project resources; `shared/core/README.md` is an in-place source note. Both retain their locations. Old repository documentation paths are removed without redirects.
