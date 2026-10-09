---
title: "Documentation migration validation"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

# Documentation migration validation

[中文](validation.md) · Translation of the Chinese primary document.

## Content identity and scope

Baseline commit: `9ee0efb1bdd20969808f8bffbea42bef72e9a142`. The reviewed object is this uncommitted workspace's repository documents, evidence-path metadata, expected JSON, documentation checker and CI. Source paths and original hashes live in the [inventory](evidence/migration-inventory.json).

## Impact assessment

| Domain | Treatment |
| --- | --- |
| research / design | Inapplicable: no independent research or interaction/visual material; old product-design is an initiative's initial product background |
| product | Updated: bilingual current positioning and boundaries |
| engineering | Updated: durable architecture/contracts with explicit initiative history |
| guides | Updated: detailed README becomes using; development/testing/environment/release procedures grouped |
| planning | Updated: current roadmap separated from history; version/backend summaries corrected |
| initiatives | Updated: stable topic paths, entries, scope, task sources and evidence links |
| releases | Updated: version directories; recorded does not infer publication |
| Root / CHANGELOG | Updated: concise bilingual README and changelog release-index link; historical entries now have Chinese and English counterparts |
| Template resources / implementation | Only repository evidence-path metadata and corresponding expected JSON change; generated Markdown and source are not relocated |
| Checks / CI | Structure checker and documentation job added; remote enforcement settings untouched |

## Checks and review

Author content review is complete; no independent review was performed. Directory and bilingual conventions are adopted without claiming the full HarnessBrew review/release process. The user-requested follow-up now provides bilingual maintained prose; generated-project documents and raw evidence remain outside translation scope. Structural checks do not validate historical local SDK/container/cluster logs; historical acceptance was not rerun.

## Structural migration checks (2026-10-09, Asia/Shanghai)

- Documentation structure: 148 Markdown files and 66 migration paths passed; all original file hashes match the baseline commit.
- Documentation failure cases: final 6 tests passed, covering missing files/anchors, invalid metadata, language pairs, index drift, stale paths and isolated navigation.
- Core regression: 228 tests passed in 27.071 seconds. The later isolated-navigation test is included in the final 6 focused checks above.
- Ruff E4/E7/E9/F, template validate and git diff --check passed.
- wheel/sdist: exact bytes/executable flags for 637 resources, sdist-to-wheel rebuild, installed generation/configuration parsing for seven templates and frontend SSG/SSR passed. The default uv cache was sandbox-restricted; the successful run used writable `UV_CACHE_DIR=/tmp/biucing-doc-uv-cache` without permission escalation.

Raw logs: [core](evidence/core.log), [distribution](evidence/distribution.log). Pre-translation hashes and review scope are in the [structural snapshot](evidence/structural-workspace-checks.json); final file identity is in the [workspace checks record](evidence/workspace-checks.json). This record is neither an independent review nor immutable release-artifact evidence.

## Content review and remaining boundaries

Corrected the old 0.9.0 Current roadmap, contradictory backend P4/P5 summary and obsolete copytree generation description. Old template-tree examples and extraction stages now live in historical initiatives. Old paths are removed; metadata and CLI JSON expectations change together. No implementation, dependency-lock, generated-project Markdown or generated-content golden changes occurred.

Device/native-SDK, production-container, cluster-failure and publication gates were not rerun; their historical limits remain. The bilingual follow-up below completes maintained prose; independent review remains unperformed.

Final conclusion: structural migration, bilingual maintained prose and local automated checks passed. Owner: project-maintainers. Workspace identity is the baseline commit plus hashes in the check record.

## Bilingual follow-up checks (2026-10-09, Asia/Shanghai)

- Added a counterpart for 70 previously single-language documents. Final scope: 218 Markdown files, 109 Chinese-primary/English pairs, covering root README, CHANGELOG and every maintained document under docs.
- Language switches, matching-language navigation, index titles, heading anchors and metadata checks pass. All 152 code blocks match between languages. Native/backend/historical-plan evidence boundaries and outstanding work are retained.
- The gate now requires all prose counterparts, matching owner/status/updated fields and identical code blocks. Eight failure-case tests pass.
- Core: 231 passed in 30.179 seconds. Ruff E4/E7/E9/F, template validation and git diff --check pass.
- Distribution passes: 637 resources preserve bytes/executable flags across wheel, sdist and rebuilt wheel; installed generation/configuration parsing covers seven templates plus frontend SSG/SSR.

Fresh logs: [core](evidence/bilingual-core.log), [distribution](evidence/bilingual-distribution.log). The [translation inventory](evidence/translation-inventory.json) records source snapshots, language directions and pair scope. The [structural snapshot](evidence/structural-workspace-checks.json) preserves pre-translation hashes; the [final workspace record](evidence/workspace-checks.json) identifies final files. Structural checks do not replace semantic translation review. This is author review, without independent review or remote CI execution.
