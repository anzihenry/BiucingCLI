# Frontend rendering variants: design and implementation plan

Status: **stage 1 models/loading and standalone resource resolver implemented;
generation integration and shipped rendering modes are not implemented**.
Recorded on 2026-09-20, against commit `070841f`. This plan is separate from the
completed kernel extraction stages 0–6. Examples below describe future behavior;
the current frontend does not accept `--set rendering=...`.

## Scope and decisions

- Keep one `frontend` template, with `rendering=csr|ssg|ssr`; default to `csr`.
- Use React Router Framework Mode and Vite for all three presets.
- Require React 19.3+ and TypeScript 7.0+; select tested stable versions and lock
  dependencies rather than permitting unbounded major upgrades.
- Use Tailwind CSS 4 and shadcn/ui, with a small checked-in component selection.
- Share pnpm/package.json/lockfile, TypeScript and quality tooling across modes.
- CSR and SSG deploy static artifacts; SSR defaults to a self-hosted Node service.
- SSR is a page-rendering/BFF layer, not an implicit database or business backend.
- No experimental RSC requirement, automatic Query layer, authentication system,
  CMS, plugin execution, or cloud-vendor dependency in this change.
- Mode selection is a generation-time preset, not a promise that changing one
  runtime environment variable converts an existing application's architecture.

## Evidence and limits of the feasibility spike

The isolated macOS spike tested Node 24.19.0, pnpm 11.21.0, React/React DOM 19.3.0,
TypeScript 7.0.2, React Router 8.4.0, Vite 8.3.0, Tailwind 4.3.3 and shadcn CLI
4.21.0. Components used the official Base UI/nova Button and Dialog. This is a
tested candidate, not an automatic mandate to keep every transitive version.

Verified: frozen installation; three production builds; route type generation
and TS 7 checking; one Vitest/Testing Library interaction test; targeted typed
lint; HTTP HTML/metadata/status assertions; fixed build-time SSG data; changing
request-time SSR data with two distinct request inputs; browser counter/dialog
interaction and deep-link refresh. Desktop 1280x800 and mobile 390x844 screenshots
showed no overflow. Initial favicon requests returned 404; no application or
hydration errors were observed.

Two integration findings must be carried forward:

1. typescript-eslint 8.70.0 rejected TypeScript 7.0 directly. The working spike
   used `@typescript/native: npm:typescript@7.0.2` for `tsc`, and
   `typescript: npm:@typescript/typescript6@6.0.2` for lint's compiler API.
   `tsc --version` remained 7.0.2; typed lint and peer checks passed. This does not
   prove that TS 6 lint understands every future TS 7 language feature. Test the
   chosen language subset and document both roles; never silently downgrade the
   project's type checker or disable rules to make CI green.
2. shadcn's temporary CLI installation hit a Zod exports error. A local
   `zod: ^3.25.76` override allowed the spike to proceed. Reproduce and narrow any
   required workaround before adopting it; a global override is not the default
   production design. Check component sources and their licenses into the
   template, preserving required notices. Generation must not fetch registries.

The spike lived under `/private/tmp/biucing-frontend-spike.tbAWKM/probe`; temporary
files may disappear and are not a durable CI dependency. Production Docker/Nginx,
Linux CI, other browsers, full lint coverage, real API/auth integration and load
testing were **not** verified. The static HTTP harness was not Nginx. These results
establish feasibility, not production certification or an updated maturity claim.

## Resource ownership

```text
frontend/
  template.json
  template/                       # common resources
    package.json
    pnpm-lock.yaml
    components.json
    tsconfig.json
    vite.config.ts
    app/root.tsx
    app/app.css
    app/components/ui/
    app/features/
    app/lib/
  variants/
    csr/template/
    ssg/template/
    ssr/template/
```

Paths inside each resource root map directly to output-relative paths. Neither
`variants/` nor `template.json` is copied to the generated project. No output path
templating is introduced.

| Common | Mode-owned |
| --- | --- |
| Dependencies and lockfile | react-router.config.ts |
| UI components, tokens, styles, pure helpers/types | routes and data-loading entry modules |
| TypeScript/Vite/lint/format baseline | SSR server entry and private environment handling |
| Component tests and shared browser interactions | SSG prerender path/data declarations |
| Common ignore files and truly identical scripts | Dockerfile, Compose, Nginx when applicable |
| Shared test helpers | README, Makefile, environment examples, rendering assertions |

Small deployment/documentation files may intentionally repeat rather than use
code-fragment substitution. Public Make command names remain consistent across
modes. Preserve existing worktree isolation, diagnostics and cleanup guarantees.
Keep `scripts/doctor` common only if its checks are genuinely identical; otherwise
make the complete file mode-owned.

One package.json and lockfile are the initial policy: no JSON deep merge, no
per-generation dependency resolution. Static production images copy only client
artifacts, not node_modules; SSR retains required production dependencies. Some
SSR-related packages in a CSR development install are an accepted tradeoff.
Installation scripts and native package support need verification on CI targets.

## Metadata contract (internal, proposed)

`variants` is optional. Omission means the existing single-directory template;
explicit null, wrong types, empty options and unknown keys inside this new object
are errors. This change does not globally tighten old metadata parsing.

Valid extension excerpt (existing required descriptive metadata omitted):

```json
{
  "variables": [
    {"name": "rendering", "required": true, "validator": "text",
     "choices": ["csr", "ssg", "ssr"], "default": "csr"}
  ],
  "variants": {
    "selector": "rendering",
    "options": {
      "csr": {
        "source": "variants/csr/template",
        "required_entries": ["nginx.conf"],
        "forbidden_entries": ["app/entry.server.tsx"],
        "overrides": []
      },
      "ssg": {
        "source": "variants/ssg/template",
        "required_entries": ["nginx.conf"],
        "forbidden_entries": ["app/entry.server.tsx"],
        "overrides": []
      },
      "ssr": {
        "source": "variants/ssr/template",
        "required_entries": ["app/entry.server.tsx"],
        "forbidden_entries": ["nginx.conf"],
        "overrides": [],
        "next_steps": ["make bootstrap", "make build"]
      }
    }
  }
}
```

- Exactly one selector is supported. It references a declared input variable
  with nonempty choices and a literal default contained in those choices.
  Option keys must match choices exactly, using `[a-z][a-z0-9_]*` identifiers.
- Default ownership is the variable declaration only. No separate variant default,
  `default_from`, rule-derived selection, or rule overwrite of the selector.
- `source` is required; it is a normalized POSIX path relative to the directory
  containing template.json, strictly beneath `variants/`. When that mode's
  resources are inspected it must exist as a directory. Sources cannot alias/nest
  another option's root or overlap the common root.
- `required_entries`, `forbidden_entries`, `overrides` are optional string lists,
  defaulting to empty, with no duplicate paths. Required paths add to, never
  replace, existing base/built-in/template contracts. Requirements apply to the
  effective output, not to the common directory alone.
- Forbidden paths reject both that entry and its descendants. Required/forbidden
  contradictions are metadata errors. No glob patterns or condition expressions.
- Optional `next_steps` replaces the common list; omission inherits it and an
  explicit empty list means no steps. Existing scoped rendering rules still apply.
- Mode-specific variables, contracts, commands, maturity overrides and arbitrary
  metadata inheritance are out of scope. Commands stay common by name; generated
  Makefiles implement their different behavior. Aggregate maturity must not imply
  that every mode has passed checks that only one mode has passed.

Invalid examples (mutations of the valid excerpt):

| Invalid input | Expected classification |
| --- | --- |
| selector `missing_variable` | invalid template: undeclared selector |
| default `auto`, or missing `ssr` option | invalid template: default/choices/options mismatch |
| source `../other/template` or an absolute path | invalid template: unsafe source |
| overrides `["Dockerfile"]` without both files | invalid template: stale override |
| common and mode both provide Dockerfile without an override | invalid template: resource collision |
| output file `assets` alongside `assets/logo.svg` | invalid template: file/directory collision |
| `--set rendering=auto` | invalid input: unsupported choice, no writes |

## Deterministic composition and safety

1. Enumerate common resources, then the selected option, preserving empty
   directories and existing file permission/binary behavior.
2. Same-path directories merge. Same-path regular files are errors unless their
   exact output path is listed in `overrides`; that replaces the whole file.
   Each override must be consumed exactly once. Directory replacement is forbidden.
3. Reject absolute paths, `.`/`..` segments, backslashes, empty segments, NULs,
   paths outside their resource root, special files, and symlinks (including in
   root ancestors beneath the template directory) for variant-enabled templates.
4. Reject distinct output paths that collide under Unicode NFC normalization and
   case folding, including parent-directory segments. Do not rename paths to fix
   them. This is a cross-platform collision rule, not a claim of Windows support.
5. Sort output paths deterministically. Each entry retains its source layer for
   diagnostics. Do not silently ignore dotfiles, binaries or empty directories.
6. No file deletion directives, content deep merge, multiple selectors, arbitrary
   Python imports, commands or user-provided external resource roots.

Legacy templates retain existing path/symlink semantics and golden outputs. Do not
use this feature as an excuse to change unrelated template behavior.

## Kernel integration

- `models.py`: add typed variant declarations, resource entries and resolved
  resources; extend GenerationPlan with an immutable resource selection.
- `catalog.py` / `declarations.py`: load/check the new optional schema and selector.
- New `resources.py`: enumerate, compose, detect conflicts and return the plan's
  effective resource set. No CLI imports, text rendering or target writes.
- `validation.py`: inspect the effective set for required files, Make contracts
  and placeholders, reporting source and output paths. `validate` enumerates all
  options, not only the default. It must not resolve/prompt for unrelated inputs.
- `generation.py`: resolve inputs, derive values (selector immutable), validate
  inputs, select resources and build the plan. Preview counts and execution use
  that same selection. Stage-copy and render once; preserve cleanup/publication.
- `presentation.py`: optional variant summaries and selected-variant fields;
  no source filesystem paths in public JSON.
- CLI remains a thin adapter; use existing `--set` with no frontend-name branches.

Check all variant declaration shapes before resolving inputs. On create/preview,
resource content checks inspect the selected effective set; an unselected mode's
missing source/content is reported by full `validate`, not silently considered
tested by a successful create. Selected roots must exist and be safe.

For new variant plans, record source inventory/type/mode/content fingerprints
and metadata selection at planning. Recheck before staging; do not silently
re-resolve a changed option or accept missing/changed resources. A changed source
is GenerationError and requires a new plan. This is a consistency check, not a
persistent snapshot, cross-process lock or defense against arbitrary concurrent
source mutation. Rendering still uses existing context escaping and single-pass
replacement. No claim of atomic no-replace publication is added.

## CLI and JSON contract

Planned commands:

```bash
biucing info frontend
biucing create frontend demo --set rendering=ssg --plan --json
biucing create frontend demo --set rendering=ssr --non-interactive
biucing validate --json
```

- No-flag frontend creation chooses CSR through the normal default mechanism.
- `info` text adds modes/default for variant templates. `list` text remains one
  frontend entry; it does not list variants as separate templates.
- List/info template objects gain optional `variants` with only
  `selector`, `default`, `choices`. Example:
  `{"selector":"rendering","default":"csr","choices":["csr","ssg","ssr"]}`.
  Default is computed from the input declaration, never separately stored.
- Create/plan/dry-run JSON gains optional `selected_variant`:
  `{"selector":"rendering","value":"ssg"}`. Existing resolved-variable source
  records also include rendering; existing counts refer to effective output.
- Both additions are omitted for legacy templates, preserving their shape.
  They are additive under schema version 1 per [JSON contract](json-contract.md).
  Internal paths/override policies are not exposed. No existing fields change
  type, location or semantics; any future breaking change needs a schema bump.
- Validation retains `ok/error_count/errors`; errors include mode context, e.g.
  `frontend[ssg]: missing required entry: nginx.conf`. No new per-mode JSON result
  envelope or CLI exit code is introduced.
- Bad user choices retain the invalid-input path; malformed resources/declarations
  use InvalidTemplateError; target conflicts retain GenerationConflictError.
  See [existing error contract](cli-errors.md). JSON failures remain JSON on stderr.

## Phases and gates

| Stage | Deliverable | Gate |
| --- | --- | --- |
| 0 | This specification, spike findings and current baseline record | Documentation-only diff; old tests/goldens unchanged |
| 1 | Models, loader and standalone resource resolver with fixtures | Determinism, empty dirs/binaries, override/path/collision negatives; no target writes |
| 2 | Plan/validation/execution/presentation integration | Preview/output agreement, all-option validation, source-change and cleanup tests; all seven old output baselines unchanged |
| 3 | Shared frontend toolchain and CSR migration | Frozen install, lint/format/types/tests, production browser checks; intentional frontend-only golden update |
| 4 | SSG configuration, routes, content/metadata and deployment | Raw HTML, build-time data, navigation data, deep links, real 404; no runtime Node requirement |
| 5 | SSR entry, request data, env separation and deployment | Request-specific HTML, no data leakage, hydration, errors/404, health and shutdown |
| 6 | Installed-artifact, deployment and CI coverage; docs | All three modes from wheel pass; Linux/macOS core and deployment jobs pass |

Stage 1–2 use fixture templates only; do not change official frontend resources.
Stage 3 may initially declare only CSR: do not advertise SSG/SSR until each is
implemented. Frontend output changes are intentional migration changes, not
byte-for-byte compatibility. Other templates retain their golden output.
No phase authorizes an automatic commit, push, version bump or publication.

## Final acceptance matrix

- Core: schema types, default/explicit selector resolution, no rule overwrite,
  source containment, dotfiles, Unicode/case collisions, stale/undeclared
  overrides, forbidden entries, unknown tokens, invalid unselected modes detected
  by validate, accurate counts, source drift, target conflict and cleanup.
- Compatibility: legacy imports/call paths, error/EOF/cancellation/JSON envelopes,
  input precedence, existing goldens. Never refresh goldens simply to pass tests.
- Distribution: wheel and sdist contain every resource layer, including hidden
  files. Generate all modes from installed wheel outside checkout; also verify
  the sdist can reproduce a wheel containing the same needed resources.
- Generated engineering: frozen pnpm install, TS7 checker version assertion,
  route types, typed lint (including a negative rule fixture), format, unit and
  component tests, production build. Lockfile/versions consistent across modes.
- Runtime: actual CSR/SSG static server/container and SSR production container;
  navigation/refresh, missing assets, HTML metadata, proper 404, SSG fixed data,
  SSR request isolation, no private config in browser assets/serialized data,
  error handling, keyboard dialog/focus and desktop/mobile browser smoke.
- SSG site origin: add and validate an explicit site URL before emitting canonical
  URLs/sitemaps. Do not use localhost as production metadata. Dynamic content
  paths must be enumerated; SSG is not automatic arbitrary-route generation.
- CI: keep Python-only Linux/macOS tests separate from frontend Node/browser and
  container jobs. Run three rendering scenarios without multiplying every frontend
  build across every Python version. Verify platform-native dependency installation.
- Preserve worktree names, ports, caches, outputs, diagnostics and scoped cleanup.
  Reassess maturity from real evidence; spike success is not release verification.

## Stage 0 baseline record

Executed on macOS on 2026-09-20 against `070841f`, with documentation-only local
changes and uv 0.12.17. All commands below completed successfully:

| Command | Result |
| --- | --- |
| `uv run --locked python scripts/run-tests --suite core` | 115 passed |
| `uv run --locked python scripts/run-tests --suite platform` | 11 passed |
| `AAPT2=/Users/xiejinheng/Library/Android/sdk/build-tools/35.0.1/aapt2 uv run --locked python scripts/run-tests --suite android` | 1 passed |
| `uv run --locked biucing validate` | Passed |
| `uv run --locked python scripts/verify-distribution` | Wheel, sdist and all seven templates passed |

The core run includes generated-project baseline comparison and repeated
generation in different temporary roots. No goldens were regenerated. SHA-256:

```text
7cc9696fb264be2e60674b5688d01abd915e35b62a5ecf95ec2bc04e6c05847c  tests/golden/generation-baseline.json
41dd067d7a2cbab73a9add55ab558125a8af9882f6f7adc111380badb8728d5f  tests/golden/required-entries.json
```

These are local baseline results, not a new remote CI run, Linux execution or
three-mode production certification. The distribution command did not use
`--check-make`; existing Make integrations ran in the platform suite. Stage 0
changes only documentation: no runtime changes, new template variables, public
JSON fields, package version changes or golden refreshes.

## Stage 1 implementation boundary

`models.py` now defines `TemplateVariant`, `TemplateVariants`, `ResourceEntry`
and `ResolvedResources`. New collection fields defensively copy inputs to tuples
or a read-only mapping. `TemplateDefinition.variants` defaults to None and is
deliberately absent from `to_dict()` in this phase.

`variant_declarations.py` parses the optional strict schema and checks selector,
paths, source overlap and required/forbidden contradictions without filesystem
I/O. Catalog invokes it only for variant declarations; old metadata parsing and
the shipped template set remain unchanged. Root existence/content is inspected
only for the selected mode by the standalone resolver.

```python
from biucingcli.catalog import load_template
from biucingcli.resources import resolve_resources
from biucingcli.variables import resolve_variables_detailed

# fixture_root contains an experimental template, not a new CLI plugin source.
definition = load_template("fixture", root=fixture_root)
resolved = resolve_variables_detailed(
    definition, {"project_name": "demo", "rendering": "ssg"}
)
resources = resolve_resources(definition, resolved.values)
```

The resolver expects resolved inputs; missing/unknown selections raise ValueError.
It performs no prompting, derivation, text replacement, copying or target writes.
Its deterministic entries record source/output path, common/option layer, kind
and permission bits. Equal directories merge with common permissions winning;
whole-file overrides require exact explicit declarations, with stale overrides
rejected. Variant-enabled trees reject symlinks, special files, unsafe paths and
case/Unicode collisions. Output constraints and unrendered next steps are returned
for stage 2 to consume; actual required/forbidden file enforcement, Make checks
and placeholder validation are not performed by this resolver.

For legacy inventory only, symlinks are represented as symlink entries and are not
traversed. This inventory is not a replacement implementation of copytree: legacy
generation continues to use its existing path unchanged. Do not connect a legacy
inventory to an executor that assumes all entries are files/directories.

`tests/test_resources.py` provides 21 core tests, using temporary metadata/resource
fixtures and no new shipped template. Stages 2 onward must still integrate the
resolver with GenerationPlan, execute/preview, full validate and presentation.
Source fingerprints/rechecks also remain stage 2 work. A fixture successfully
loading is **not** evidence that the current CLI can generate variant resources.
