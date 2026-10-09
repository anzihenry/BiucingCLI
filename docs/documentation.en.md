---
title: "Project documentation conventions"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# Project documentation conventions

[中文](documentation.md) · Translation of the Chinese primary document.

## Reference and scope

The structure follows HarnessBrew's `docs/documentation.md` as observed on 2026-10-09: separate durable knowledge, initiatives and version facts; create only populated domains; provide domain and initiative entrypoints. This project adopts the directory/navigation model and Chinese-primary/English-counterpart convention; release approvals are managed separately.

Scope: root README/CHANGELOG and maintained documents under docs. Markdown under `src/biucingcli/template_data/` is generated-project payload; `shared/core/README.md` is an in-place source note. Neither is relocated.

## Directory responsibilities

| Location | Content |
| --- | --- |
| Root README | Purpose, requirements, shortest example and documentation entry |
| Root CHANGELOG | Version summaries and release-index link |
| docs/README | Map and reading paths |
| product | Current positioning, users, capabilities and boundaries |
| engineering | Current architecture, modules, interfaces and constraints |
| guides | Usage, development, testing, environments, acceptance and release procedures |
| planning | Cross-initiative priorities, dependencies and delivery history |
| initiatives/feature | New capability goals, design, tasks and validation |
| initiatives/improvement | Improvements to existing capabilities |
| initiatives/refactor | Internal structure and maintainability |
| initiatives/process | Development, documentation and delivery process improvements |
| releases/version | Version notes and corresponding historical acceptance |

research, design and initiatives/research are created only when independent material exists. Durable major decisions may use a numbered engineering/decisions index; this migration does not mechanically turn each architecture table row into an ADR.

## Single maintenance locations

Current facts belong to product, engineering and guides; old initiative plans are not new usage rules. Active initiatives declare one task source. Planning links to it. The verification matrix routes checks and summarizes limits; detailed acceptance belongs to initiatives or releases. Implementation should update affected durable knowledge.

Original task/stage records retain historical context. `completed` applies only to recorded initiative scope, without inventing independent reviews, device evidence or publication. Backend tasks live in its plan; migration tasks live in the migration README.

## Metadata, states and language

Maintained documents have YAML title, status, owner and updated fields. `project-maintainers` identifies this repository's maintainers. Dates represent substantive changes or validity review.

| Type | States |
| --- | --- |
| Durable documents and navigation | draft, current, superseded |
| Initiatives and their material | proposed, active, paused, completed, cancelled |
| Release directories | recorded, planned, verified, released, cancelled, withdrawn |

`recorded` is this project's historical version state: existing notes/evidence are retained without confirming publication time, URL or immutable artifact identity. This is an explicit adaptation of HarnessBrew's standard. Promotion to verified/released requires candidate/publication evidence, not just a version number or local tag.

Root entrypoints, CHANGELOG and every maintained document under docs use a Chinese primary file and an English `.en.md` counterpart with reciprocal links. New or substantive revisions update prose, metadata, commands and examples together; indexes point to the matching language. Translated pages retain source heading anchors for stable references. Generated-project documents, raw logs and machine reports are outside translation scope and retain their original language.

## Paths and references

Directories/files use lowercase English and hyphens, with README entrypoints and README.en.md translations. Repository links are relative. No old-path redirects are provided; references, evidence paths in template metadata and corresponding CLI expectations are updated together.

assets and evidence stay near their context. Evidence identifies its commit, candidate or original environment. The migration inventory records source paths/hashes for audit only. `/tmp` paths are historical local pointers, neither guaranteed accessible today nor durable publication evidence.

## Checks and maintenance

Run `uv run --locked python scripts/check-docs`. It checks metadata, states, naming, relative links and heading anchors, all maintained-document language pairs, matching owner/status/updated fields and identical code blocks, index-state consistency and migration path coverage. The CI documentation job runs it too. Structural checks cannot establish translation semantics or actual product behavior.

Validation and author content review belong to the [migration initiative](initiatives/process/documentation-standard/README.en.md). Each delivery assesses product, engineering, guides, planning, initiatives, releases and root entries. Missing independent research/design domains are explicitly inapplicable. Maintainers should review current documents every 90 days without automatic expiration.

Remote branch protection and required GitHub status checks were not modified or confirmed. Local CI configuration does not establish remote enforcement.
