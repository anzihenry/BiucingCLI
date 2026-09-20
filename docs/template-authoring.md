# Adding a built-in template

This document describes shipped generation behavior. For the optional resource
variant extension (models and standalone resolution only; not yet connected to
generation), see the
[frontend rendering plan](frontend-rendering-plan.md).

Place `template.json` and a `template/` resource tree under
`src/biucingcli/template_data/<name>/`. Keep the metadata name equal to the directory.
Existing descriptive metadata (stack, maturity, validation, worktree, commands,
etc.) remains required; the excerpt below shows only the extension-related fields.

```json
{
  "name": "python-api",
  "category": "backend",
  "contracts": [],
  "required_entries": ["pyproject.toml"],
  "rule": null,
  "derived_outputs": [],
  "render_outputs": [],
  "variables": [
    {"name": "project_name", "required": true, "validator": "project-name"},
    {"name": "greeting", "required": true, "validator": "text", "contexts": ["JSON"]}
  ]
}
```

Use `{{GREETING_JSON}}` inside a double-quoted JSON string and `{{GREETING}}` in
Markdown. Supply new variables with `--set greeting=...`; no CLI option or rule
registration is needed for templates that only resolve inputs/defaults.

## File contracts

All templates require `README.md`, `Makefile`, `.gitignore` and `scripts/doctor`.
The existing common Make command contract also remains mandatory. Opt into:

- `docker-compose`: `.dockerignore`, `compose.dev.yaml`;
- `go-backend`: `go.mod`, `go.sum`, `cmd`, `internal`, `configs`, `scripts`;
- `native-tools`: `.mise.toml`, `scripts`.

`required_entries` adds template-specific files/directories. Paths must be
normalized relative POSIX paths, without traversal. Category and tags are display
metadata, not implicit Go/native contracts. Built-ins have project-owned minimum
contract assignments; removing declarations is an error and does not remove the
underlying file checks. The required-entry golden pins all pre-migration checks.

## Variables, contexts and bindings

Variable/output names use lowercase snake-style identifiers matching
`[a-z][a-z0-9_]*`; tokens use uppercase. Contexts must be declared explicitly and
can be JSON, XML, SWIFT, KOTLIN, JS_SINGLE, ANDROID or DOCKER. They reuse existing
escaping implementations and do not add surrounding quotes, except Android's
resource-specific quoting. Choose the context appropriate to the insertion site.

Text, display-name and URL variables are considered free text. Choice variables
are also free text unless every choice uses only letters, digits, dots, underscores
and hyphens. Raw free-text tokens are rejected outside Markdown source files.
Names are not a safety exemption: a newly introduced `greeting` is protected just
like an existing `display_name`. Declaring a context does not verify that the
author used it in the right language; generated configuration parsing and target
language tests remain necessary. Human-readable next steps retain their existing
formatting behavior and are not shell-executed by the generator.

Bindings cannot collide: `title` with JSON context conflicts with a variable named
`title_json`. A template cannot use another template's inputs or outputs. Optional
declared variables without values still render as empty strings. Unknown tokens
fail before generation; literal token-looking user values are not reprocessed.

## Complex built-in rules

Only templates needing computation require a pure Python rule module. Register
it explicitly in `template_rules/registry.py`, including its output sets and
permitted input overwrites, and declare its `rule`, `derived_outputs` and
`render_outputs` in metadata. Rules may not be imported by arbitrary module path.
Outputs require a registered rule; metadata and actual result keys must match its
contract. Render-only outputs are trusted code fragments produced by built-in
code, not an escape hatch for declaring arbitrary user input safe.

## Verification

Run locked core tests and `biucing validate`, then installed-distribution checks.
Add source/variant/configuration tests and register new release smoke scenarios
in `scripts/verify-distribution` (its expected template set is deliberately
explicit). A fixture demonstrating complete loading, validation, preview and
generation is in `tests/test_template_declarations.py`; it is not a shipped
eighth template. Add platform tests if the new template needs language/SDK proof.

Internal extension metadata is not yet exposed by list/info JSON: this change
preserves the current public schema. Neither third-party plugin execution nor a
new CLI option for external template directories is introduced.

## Contribution checklist

1. Add metadata and template resources; declare only the contracts, variables,
   escape contexts and required entries the template needs. Keep `project_name`
   constrained by the existing project-name validator.
2. For a pure declaration template, use `--set` and the generic generation flow;
   do not add template-name branches to CLI or the generator.
3. For computed values, add a pure rule module and explicitly register its callable,
   output sets and allowed overwrites. Add direct rule tests; retain separation
   between manifest-visible derivations and render-only snippets.
4. For a new shared contract, add it to `template_rules/contracts.py` with tests.
   Built-in minimum policy and the required-entry golden should be updated only
   as a reviewed product change, not to silence missing-file errors.
5. Add core output/configuration tests and representative generation baselines.
   Native compiler/shell tests must be marked as platform or Android tests rather
   than silently adding tool requirements to core. See [test organization](testing.md).
6. Extend installed-wheel smoke cases and expected template inventory. Verify
   `uv run --locked biucing validate`, locked core tests and distribution checks;
   run relevant platform tests and require Linux/macOS CI before release.

Use `catalog`, `models`, `variables`, `generation` and `presentation` for direct
Python integration. Terminal decisions belong to the CLI adapter; renderers and
rules must not prompt, print diagnostics or terminate the process. The retained
legacy imports exist for compatibility, not as the recommended extension surface.
