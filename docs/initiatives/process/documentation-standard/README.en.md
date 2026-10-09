---
title: "Documentation structure migration"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

# Documentation structure migration

[中文](README.md) · Translation of the Chinese primary document.

## Goal and scope

Adopt HarnessBrew's current domain/initiative/release structure, removing old flat paths without compatibility files. Owner: project-maintainers. This entry owns migration task state.

Scope: root entrypoints, 66 repository documents, navigation, metadata, references, automated structure checks and CI. Generated-project documentation remains in place; repository-evidence paths in template metadata are updated.

## Completion conditions and tasks

- Each original document has a disposition in the [inventory](evidence/migration-inventory.json).
- The current roadmap and backend summary agree with existing stage evidence.
- Root entrypoints, CHANGELOG and all maintained docs now have bilingual prose, matching-language navigation and automated checks.
- Local documentation checks, core regression, template validation and author content review pass; independent review is not claimed.

## Materials and limits

[Project documentation conventions](../../../documentation.en.md), [Documentation map](../../../README.en.md), [Documentation migration validation](validation.en.md). This includes structural migration and bilingual maintained prose; generated-project documents and raw evidence are not translated. Historical evidence only gains local-reference/context updates; old acceptance is not presented as a new run.

## Delivery result

Structural migration is complete. Documentation checks, core regression, template and distribution validation passed; see [Documentation migration validation](validation.en.md). Bilingual maintained prose is complete; independent review has not been performed.
