---
title: "Product positioning and scope"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# Product positioning and scope

[中文](overview.md) · Translation of the Chinese primary document.

## Positioning and users

BiucingCLI generates project skeletons for independent developers who frequently start projects with a stable personal stack. It prioritizes a small set of verifiable, maintainable templates.

## Current capabilities

The source version is 0.10.0, with seven built-in templates: frontend, web-service, micro-service, worker, apple, android and harmonyos. The CLI supports discovery, inspection, input validation, previews, JSON output and generation; see [usage](../guides/using.en.md).

Generation uses packaged resources and a unified planning/publication pipeline; see [engineering](../engineering/README.en.md). Native devices, signing, store delivery and backend production availability are bounded by the evidence referenced in the [verification matrix](../guides/verification-matrix.en.md).

## Boundaries

The tool does not migrate existing generated projects, manage Git worktrees, provide a remote template marketplace or implement a general Agent workflow. Generated-project owners implement application business logic.

## Current focus

Keep template delivery, CLI contracts and installed resources consistent. Kubernetes is a reference delivery; B27 real multi-zone HA acceptance is on hold. HarmonyOS device/signing limits and other platform boundaries remain governed by initiative evidence. See the [roadmap](../planning/roadmap.en.md).

The initial positioning is historical material in the [scaffold baseline initiative](../initiatives/feature/scaffold-baseline/README.en.md).
