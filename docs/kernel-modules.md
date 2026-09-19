# Kernel modules: stages 1–2

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
