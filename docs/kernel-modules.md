# Kernel modules: stage 1

Stage 1 extracts foundation modules without changing generation algorithms,
template resources, serialization or CLI contracts.

| Module | Responsibility | Dependencies within the package |
| --- | --- | --- |
| `errors.py` | Existing domain exception hierarchy | None |
| `models.py` | Existing metadata and variable result dataclasses | None |
| `catalog.py` | Package resource paths and metadata loading | errors, models |

`cli.py` now imports loading and errors directly from their owning modules.
`templates.py` explicitly re-exports the previous model, exception and loader
names as identical objects, preserving existing import and exception-catching
behavior. Validation, variable resolution and rendering remain there for later
stages. The foundation modules never import CLI or the compatibility module.

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
module globals. Other fault-injection seams remain unchanged at this stage.

`tests/test_catalog.py` covers isolated imports, identical compatibility exports,
exception inheritance, sorted loading, working-directory independence, explicit
fixture roots and malformed metadata. Stage 0 generation snapshots remain
unchanged; installed-artifact verification also exercises the extracted modules.
