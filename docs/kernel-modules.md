# Kernel modules: stages 1–5

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

## Stage 4: template-scoped declarations

The historical stage 3 string-based rule helper remains compatible, but generation
now passes the complete `TemplateDefinition` and selects its declared `rule`.
The registry owns exact derived/render-only output sets and allowed input
overwrites; metadata must agree, and actual returned keys are checked too.

`declarations.py` validates extension metadata, names, contracts, paths, rule
outputs, escape contexts and placeholder binding collisions. `template_rules/contracts.py`
owns reusable file contracts. Base requirements always apply; built-in minimum
contract/rule assignments cannot be disabled by deleting declarations. Category
and tags no longer implicitly select technology-specific required files.

Core rendering always receives a definition and builds its bindings solely from
that template's inputs, declared contexts and rule outputs. Unknown placeholders
fail; arbitrary extra values cannot create new bindings. Source placeholder checks
run before prompting/preview and before filesystem staging. Inserted user text is
still processed once, never re-expanded. New free text is identified by validator
semantics rather than existing variable names.

`_legacy_rendering.py` freezes the previous global map exclusively for callers of
unscoped rendering helpers. It is not the template extension mechanism. Existing
JSON `to_dict` surfaces deliberately omit internal extension fields, preserving
schema version 1 and existing golden outputs.

See [template authoring](template-authoring.md) for declarations and boundaries.
`tests/test_template_declarations.py` demonstrates a new Python backend using a
new text variable through `--set`, without a new CLI option or registered rule.
It also tests negative boundaries and compares required entries against the
pre-migration contract snapshot. Existing generation snapshots remain unchanged.

## Stage 5: typed requests/plans and injected interaction

`models.CreateRequest` contains the template name, positional project name,
output directory, set values and explicit option values. These two input maps
are copied and read-only. Explicit values retain priority over set values;
the positional project name remains authoritative. CLI convenience arguments
now use one `CLI_VARIABLE_ARGUMENTS` mapping instead of duplicate dictionaries.

`generation.build_generation_plan(request, definition=None, prompt=None)` loads
or accepts a definition, checks declarations, resolves variables, computes rule
outputs, validates inputs and gathers the preview inventory. It reads template
files but creates no directories, staging areas or generated files. Definition
injection supports fixture catalogs without global patches. `prompt` is an
optional callable receiving a `TemplateVariable` and returning a string; without
it, missing required values are aggregated as non-interactive errors.

`GenerationPlan` contains typed metadata, paths, read-only resolved/derived maps,
variable-source records and preview information. It is an in-process resolved
plan, not a serialized job, filesystem snapshot or template lock: source files
and metadata must not be mutated between planning and execution. Target existence
is intentionally not frozen. `execute_generation_plan(plan)` uses the established
staging executor, which rechecks target conflicts and current template declarations.

```python
from pathlib import Path
from biucingcli.models import CreateRequest
from biucingcli.generation import build_generation_plan, execute_generation_plan

request = CreateRequest("frontend", "demo", Path("/existing/output"),
                        set_values={"display_name": "My Demo"})
plan = build_generation_plan(request)
# Inspect plan.values / plan.target_dir before choosing to execute.
execute_generation_plan(plan)
```

`variables.py` owns resolution and constraints without terminal operations.
`interaction.py` is a terminal adapter: it prints prompts to stderr and preserves
EOF/interrupt behavior. The CLI decides whether to supply that adapter based on
JSON/non-interactive flags and TTY state. Core imports do not load CLI, the terminal
adapter or the compatibility module.

The historical `templates.resolve_variables*` interactive signatures remain as
wrappers. `cli.build_create_context` and `GenerationPlan.to_context()` preserve
the previous dictionary shape for compatibility and the current formatting layer.
Active CLI preview/create paths both use `build_create_plan`; only creation calls
the executor. Formatting accepts plans and still observes current target existence.
Moving formatters out of CLI is deferred to stage 6.

`tests/test_generation_plan.py` verifies direct non-CLI planning/execution, callback
sources, missing-value aggregation, blank input, cancellation, no-write planning,
execution-time conflicts/missing parents, detached maps, CLI alias coverage and
core import boundaries. Existing EOF/PTY/JSON and output baselines remain gates.
