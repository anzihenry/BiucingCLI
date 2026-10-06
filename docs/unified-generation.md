# Unified generation kernel

## Scope and contract

Keep the existing CLI/module boundaries and CreateRequest → GenerationPlan →
execute_generation_plan flow. Template payloads, platform architectures, dependency
versions, commands and public JSON shapes are unchanged. This work does not add a
plugin framework, template upgrades or shared backend payloads.

Every template will select resource layers (common only, or common plus a variant),
validate their effective output, and use one staged publisher. All generated plans
will contain resource inventories and source fingerprints. Ordinary templates must
continue to omit variant fields from public output.

Deliberate behavior changes for ordinary templates:

- Reject source symlinks, special files, unsafe paths and case/Unicode collisions.
- Check full metadata, required entries, Make targets and placeholders on creation.
- Reject source/metadata drift after planning instead of silently using new input.
- Report dangling target symlinks as target conflicts.
- Render read-only text and restore modes; clean read-only staging directories on failure.
- Determine executable scripts from project-relative paths, never output ancestors.

Fingerprints detect consistency changes; they are not filesystem snapshots or locks.
Publication retains the existing check-then-rename boundary, without promising atomic
no-replace behavior against arbitrary concurrent target creation.

## Delivery stages

1. Record contracts and establish shared single/multi-layer output tests.
2. Unify resource layers, strict enumeration, fingerprinting and effective validation.
3. Route plans and compatibility entrypoints through one publisher; remove copytree generation.
4. Run core/platform/distribution gates, retain output goldens and document final behavior.

Each stage is committed separately. Normal output snapshots must remain unchanged;
intentional behavior changes are covered by explicit boundary tests rather than
blanket golden regeneration. Full native/device/deployment checks are only needed
if their template output changes.

## Baseline

Before implementation: 213 core tests pass; template validation passes. The focused
resource/generation suite has 51 passing tests. Existing ordinary-template resource
inventories allow symlinks and generation uses copytree; variant plans alone have
fingerprints and strict effective-resource validation. Shared contract tests start
with behavior already supported by both paths, then expand as the paths converge.

## Stage 2 result

Resource enumeration and fingerprinting now share layer selection and enforce the
same strict policy for ordinary and variant resources. Full `validate` checks all
ordinary/selected inventories through the effective-resource validator. Missing
entries retain the aggregated diagnostic used by ordinary templates. Generation
still uses its previous two execution paths until stage 3.

Validation: 42 focused resource/variant/shared/template-validation tests, Ruff and
`biucing validate` passed. No payload or golden output was changed.

## Stage 3 result

All plans now require resource inventories/fingerprints and use one staged publisher.
`render_template` keeps its resolved-value signature and adapts to that same resource
preparation/publisher without repeating defaults, prompts or derivations. The old
copytree generation branch is removed. Ordinary public results still omit variant
fields; incomplete manually assembled plans fail instead of silently rebuilding.

Shared tests now cover source/render-time drift, effective validation, symlink
rejection, read-only permissions/cleanup, output ancestor independence, conflicts,
cancellation, binary/empty-directory output and direct-entrypoint equivalence.
CLI preflight metadata validation is intentionally retained before --set parsing to
preserve error priority; the independent core entrypoint also validates metadata.
The repeated preflight is now metadata-only, not a repeated ordinary resource scan.

Validation: 223 core tests and Ruff passed, including unchanged generation goldens.
