# Kernel refactor: stage 0 baseline

Baseline source: commit `8ebd568`. Stage 0 adds tests and documentation only;
production Python modules, template resources and dependency locks are unchanged.

## Generated output contract

`tests/golden/generation-baseline.json` records 11 cases: all seven templates,
four Apple platforms, and postgres/redis microservices. Free-text templates use
quotes, Unicode, XML characters, backslashes, dollar signs and placeholder-like
text. Inputs are defined in `tests/generation_baseline.py`.

Each case records the create JSON manifest and a sorted inventory of relative
paths, directory entries, exact-byte SHA-256 hashes and executable permission
bits. Binary files are not decoded. Empty directories are included. Symlinks,
if introduced, are represented separately. Read/write bits, ownership and times
are excluded because they can depend on checkout/environment policy.

Only the manifest output path and generator version are normalized. Generated
file bytes are never normalized. Schema version remains pinned. A separate test
generates each case twice in distinct temporary roots and compares the results.
The collector has no fixture-writing option: direct execution prints a candidate
to stdout. Do not regenerate expected snapshots just to make a refactor pass.
Review intentional product changes separately; hashes identify affected files
but require inspecting generated content to explain a change.

## Existing import and fault-injection boundaries

These are current repository dependencies, not a promise of a complete public
Python SDK. Preserve commonly used imports with explicit compatibility exports
during extraction; move mocks to the actual execution boundary when appropriate.

| Current boundary | Consumers / purpose |
| --- | --- |
| `biucingcli.cli:main` | console entry point, subprocess and in-process CLI tests |
| `cli.apple_platform_config`, `cli.default_kotlin_module_name` | platform derivation tests |
| `templates.TemplateVariable`, loading, validation and rendering functions | CLI and direct core tests |
| `templates.REQUIRED_COMMAND_CONTRACT` | generated Make contract tests |
| `templates.templates_root` | synthetic metadata/template fixtures |
| `templates.shutil.copytree` | I/O failure and interruption cleanup injection |
| `cli.load_template`, `cli.validate_templates` | expected-error JSON injection |
| `builtins.input`, `sys.stdin.isatty` | interactive/non-interactive behavior |

Do not maintain obsolete mock paths through hidden coupling between new modules.
`test_refactor_baseline.py` temporarily imports parser/context/resolver functions
to characterize behavior; these tests can target new interfaces after extraction.

## Current resolution order (preserve, do not redesign in this refactor)

1. Load metadata, trim positional project name, parse `--set` (last duplicate wins).
2. Reject undeclared set keys and unsupported explicit options.
3. Positional project name overrides its set value. Explicit flags override set
   values. When display name is absent from both, synthesize it from project name;
   that synthesized value currently has source `provided`.
4. Iterate variables in declaration order: trimmed nonempty provided value,
   literal default, already-resolved `default_from`, then required input handling.
   Whitespace-only provided values fall through. Literal defaults are not trimmed.
   Forward default references are not revisited; optional unresolved values omit.
5. Non-interactive missing required values are aggregated. Interactive answers
   are trimmed and recorded as `prompted`. JSON/non-TTY requests never prompt.
6. Compute template derivations from resolved values, merge derived values, then
   add Apple snippets and validate resolved input constraints.
7. Compute target path, next steps and file inventory without creating anything.
8. Preview formats the context; create executes staging/copy/render/publish first.
   Manifest `target_exists` is observed when formatting, not frozen at planning.

No forward-reference resolver, source-label correction or new precedence is part
of extraction. Any desired behavior change should be tracked independently.

## Coverage and verification

- `test_refactor_baseline.py`: inventories/manifests, repeatability, snapshot
  sensitivity, precedence, no-write context, default semantics and sources.
- `test_cli.py`: existing text goldens, metadata, normalization/derivations,
  preview/generation, conflicts and tool integrations.
- `test_json_contract.py`: schema/version and list/info JSON goldens.
- `test_cli_errors.py`: stderr/stdout, argument failures, EOF, SIGINT, exits
  (including 2/130), non-interactive behavior and staging cleanup.
- `test_escaping.py`, `test_configurations.py`: insertion contexts and parsers.
- `scripts/verify-distribution`: installed wheel/sdist and all seven templates.

Run `uv run --locked python scripts/run-tests --suite core` and static checks at
each stage. Run platform/Android suites where prerequisites are available and
artifact verification for resource/generation changes. Linux/macOS Python
3.11–3.14 CI remains the cross-platform gate; local macOS results do not replace it.
