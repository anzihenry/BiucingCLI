---
title: "Kernel modules and unified generation"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# Kernel modules and unified generation

[中文](kernel-modules.md) · Translation of the Chinese primary document.

The current CLI owns parsing, terminal policy, command dispatch and error-to-exit
mapping. `presentation.py` owns text/JSON results and schema/generator versions;
`generation.py` owns planning/execution; supporting modules own models, catalog,
variable resolution, declarations, rendering and built-in template rules. The [extraction history](../initiatives/refactor/generation-kernel/plan.en.md) records the original stages and compatibility decisions.

## Current generation boundary

All templates now use one resource-plan/publisher pipeline. `resources.py` selects
common-only or common-plus-variant layers, applies strict path/type checks and
fingerprints the selected sources. `validation.py` checks effective required files,
Make targets and placeholders. `generation.py` creates typed plans and executes
one staging/render/permission-restoration/publication/cleanup implementation.
`render_template` remains an adapter for already resolved values, without repeating
input resolution or derivation. No CLI/module dependency direction has changed.

Every normal GenerationPlan includes resources and a fingerprint. Ordinary plans
still omit variant fields from public JSON. Metadata is checked before prompting;
effective source contents are checked after inputs select the resources. Source
changes after planning cause GenerationError and require a new plan. Fingerprints
are consistency checks, not snapshots, locks or atomic no-replace publication.

Ordinary templates now reject source symlinks and special/unsafe/colliding paths,
validate the full effective contract on creation, and share read-only-file and
failure-cleanup behavior with variants. Fault injection targets `shutil.copy2`,
`render_text` and `os.replace` in generation, not the removed copytree branch.
See [unified generation](../initiatives/refactor/unified-generation/validation.en.md) for migration decisions and evidence.

## Historical implementation

The extraction stages and their original compatibility decisions are maintained in the [generation-kernel initiative](../initiatives/refactor/generation-kernel/plan.en.md). The current boundary above is authoritative.
