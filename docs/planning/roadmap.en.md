---
title: "Current roadmap"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# Current roadmap

[中文](roadmap.md) · Translation of the Chinese primary document.

## Existing delivery baseline

The source version is 0.10.0; see [CHANGELOG](../../CHANGELOG.en.md) and [historical candidate records](../releases/README.en.md). Version numbers and local tags alone do not establish publication.

- Seven templates, packaged resources and JSON/error contracts are established.
- Frontend CSR/SSG/SSR implementation and verification live in the [initiative](../initiatives/feature/frontend-rendering/README.en.md).
- Native binary components and shared session contracts live in the [initiative](../initiatives/feature/native-components/README.en.md); device coverage remains bounded by platform evidence.
- Backend B01–B24 have delivered their documented scope; B25/B26 deliver Kubernetes references. Task state is maintained only in the [backend plan](../initiatives/feature/backend-services/plan.en.md).
- Unified generation recorded final acceptance on 2026-10-06; see the [initiative](../initiatives/refactor/unified-generation/README.en.md).

## Current coordination and dependencies

- B27 real multi-zone HA exercises remain on hold. Resumption requires a target cluster, multi-zone ingress, managed PostgreSQL, backups and authorization; see the [backend initiative](../initiatives/feature/backend-services/README.en.md). No new version or schedule is assigned.
- Documentation restructuring is tracked in the [initiative](../initiatives/process/documentation-standard/README.en.md). Full prose translation is outside this migration.
- Other backend extensions remain demand-driven, rather than automatically becoming mandatory work from an old plan.

## Deferred boundaries

Remote template marketplaces, automatic worktree management and general workflow orchestration remain outside product scope. See [delivery history](delivery-history.en.md) for older planning context.
