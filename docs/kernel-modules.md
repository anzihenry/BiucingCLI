# Kernel modules: stages 1–3

Stage 1 extracts foundation modules without changing generation algorithms,
template resources, serialization or CLI contracts.

| Module | Responsibility | Dependencies within the package |
| --- | --- | --- |
| `errors.py` | Existing domain exception hierarchy | None |
| `models.py` | Existing metadata and variable result dataclasses | None |
| `catalog.py` | Package resource paths and metadata loading | errors, models |
| `variables.py` | Pure variable constraint validation | models |
| `rendering.py` | Placeholder map and single-pass text rendering | escaping |
| `validation.py` | Metadata, required files, Make and placeholder checks | catalog, models, variables, rendering, escaping |
| `generation.py` | Copy/render, permissions, staging, publication and cleanup | errors, models, rendering |

`cli.py` now imports loading and errors directly from their owning modules.
`templates.py` explicitly re-exports the previous model, exception and loader
names as identical objects, preserving existing import and exception-catching
behavior. Stage 2 also re-exports moved validation, rendering and filesystem
functions/constants. Only interactive variable resolution remains implemented
there for later extraction. New modules never import CLI or the compatibility
module; CLI imports their functions directly, except the remaining resolver.

## Resource loading and test fixtures

```python
from pathlib import Path
from biucingcli.catalog import load_template, load_templates

definition = load_template("frontend")  # package-owned template_data
fixtures = load_templates(root=Path("tests/my-fixtures"))
```

The optional keyword-only `root` selects a metadata fixture root; it is not a new
CLI option or an external plugin interface. Default resource resolution remains
relative to the installed package, never the working directory. Listing preserves
sorted metadata-path order and existing unknown/invalid metadata error handling.

Tests that need to redirect the existing aggregate validator patch
`biucingcli.catalog.templates_root`, not `biucingcli.templates.templates_root`.
Import compatibility does not imply compatibility for monkeypatching internal
module globals. Filesystem failure/cancellation injection now patches
`biucingcli.generation.shutil.copytree` instead of the old templates location.

`tests/test_catalog.py` covers isolated imports, identical compatibility exports,
exception inheritance, sorted loading, working-directory independence, explicit
fixture roots and malformed metadata. Stage 0 generation snapshots remain
unchanged; installed-artifact verification also exercises the extracted modules.

## Stage 2 boundaries

The placeholder table and template-specific required-file branches are moved
without redesign. Declarative contracts and template rules belong to later
stages. `variables.py` currently owns only constraints, not interactive resolution.
`generation.py` currently owns filesystem execution, not the future typed plan.

`tests/test_generation.py` verifies independent imports and compatibility export
identity, exact binary copying, executable modes, empty directories, single-pass
insertion, source preservation, existing/late target conflicts, and cleanup on
OSError or KeyboardInterrupt during copy, text rendering and final publication.
Existing CLI error/EOF/SIGINT tests continue to verify user-facing behavior.

## Stage 3: pure template-specific derivations

`template_rules/apple.py`, `android.py` and `microservice.py` now own their
platform/module/dependency derivations. Shared type-name conversion and the
`RuleResult` dataclass live in `template_rules/common.py`. Existing CLI helper
imports are explicit aliases, not duplicated implementations.

`template_rules/registry.py` holds an immutable implementation registry and a
separate immutable template-to-rule assignment table. The CLI makes one call to
`derive_template_values` after resolving variables, without template-name
branches. Unassigned templates receive an empty result. An assigned but missing
implementation raises `InvalidTemplateError`; no dynamic imports are allowed.
Assignments remain built-in Python declarations until stage 4 introduces
declarative metadata. Unknown template requests still fail in catalog loading,
before this fallback can be reached by the CLI.

Rules accept already resolved/normalized string values and return `RuleResult`:

- `derived_values`: merged over resolved inputs, included in manifest derivations;
- `render_only_values`: merged afterwards, used for rendering but excluded from
  manifest derivations (preserves the existing Apple snippet behavior).

Apple derives platform settings and Swift module name, then builds snippets
using those settings. Android derives Kotlin module name. Microservice derives
dependency-store settings and service type name. Explicit module names and OS
versions retain their previous priority. Original resolved-variable source
records are not rewritten by derivation. Generic input validation still runs
after the merge, and unsupported platform/store choices keep existing errors.

Rules do not read terminal input, write files or run commands. The dispatcher
copies the input mapping; rule functions also avoid modifying their arguments
and return fresh results. No new validation policy, plugin lifecycle or output
schema is introduced. Template-specific required-file checks and the global
placeholder table remain unchanged for stage 4.

`tests/test_template_rules.py` directly covers each platform/store, explicit and
default names, snippet separation/escaping, invalid selections, registry fallback
and missing assignments, input/result isolation, helper aliases and independent
imports. Existing 11-case generation snapshots remain the end-to-end contract.
