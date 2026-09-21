# Frontend rendering variants: design and implementation plan

Status: **stage 6 implementation and local installed-artifact acceptance complete.
Hosted CI/release-gate execution remains pending a push; no remote success claimed.**
Initially recorded on 2026-09-20, against commit `070841f`. This plan is separate from the
completed kernel extraction stages 0–6. Examples below describe future behavior;
the current frontend accepts `--set rendering=csr|ssg|ssr` (default: `csr`).

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

## Metadata contract (internal)

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

Target commands after all modes ship (today `csr` and `ssg` are accepted;
`ssr` fails as an invalid choice without creating files):

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

## Stage 1 implementation boundary (historical)

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

## Stage 2 implementation boundary

Variant-enabled definitions now select resources during `build_generation_plan`.
The plan retains `ResolvedResources` and a fingerprint. Counts, top-level entries,
effective next steps and `selected_variant` come from the same selection used by
execution. The legacy direct `render_template` entry point also supports variants
through the same preparation/publication helpers; it does not silently copy only
the common layer. Legacy definitions keep the original copytree execution path.

Variant generation validates metadata before prompting, then checks the selected
effective resource set after resolving inputs. Required/forbidden paths, Make
targets, free-text contexts and next-step placeholders are checked. Shadowed
common files and unselected mode content do not participate in these checks.
`validate` checks every declared option without prompting for required inputs;
errors from resource resolution/content checks are collected with mode context.
Malformed declarations remain catalog/domain errors under the existing envelope.

The fingerprint captures definition state, on-disk metadata, and inventory,
permission bits and content of both selected source layers, including shadowed
common files and directory roots. It is checked after preparation, before staging
and before publication. Execution compares current selection with the saved one;
changes raise GenerationError rather than silently rebuilding a different plan.
This is not a persisted snapshot or a concurrent filesystem lock.

Variant publication copies only listed entries, renders text once, preserves
binary bytes and file modes, and applies directory modes after writing children.
Cleanup restores owner traversal/write permissions inside unpublished staging
directories when needed. Existing and late target conflicts (including dangling
target symlinks), OSError and cancellation preserve the user target and clean
staging. Final publication still does not promise atomic no-replace semantics
against arbitrary concurrent target creation.

Public schema-1 JSON adds optional `variants` for list/info and `selected_variant`
for create/plan/dry-run. Legacy outputs omit both. See
[JSON contract](json-contract.md#resource-variants). No source path or fingerprint
is exposed. Info text lists selector/choices/default; existing resolved-variable
lines also identify the selected mode in preview/create text.

`test_variant_generation.py` adds 17 core tests covering these integrations and
failure paths. All official template resources and existing goldens remain
unchanged. Stage 3 begins the intentional frontend resource migration; installed
three-mode frontend/container/browser coverage remains stages 3–6, not a claim
made by the current seven-template distribution verifier.

## Stage 3 implementation boundary

The shipped frontend is now variant-enabled, with **only CSR** declared and
defaulted. Both `biucing create frontend demo` and explicit `--set rendering=csr`
generate the same file inventory. `ssg`, `ssr` and unknown values are rejected
before writes. There are no new generator branches or CLI flags in this stage.

Common resources own package.json/lockfile, pnpm workspace settings, Vite/TS/lint/
format/Vitest, document/error/loading shell, theme, checked-in shadcn Button/Dialog
and MIT notice, the welcome feature, project constants, and shared browser tests.
The CSR layer owns route declaration/modules, React Router configuration,
Make/Docker/Compose/Nginx/doctor, env guidance, README and browser launch presets.
No overrides or JSON merges are needed. The old `src/` tree and source index.html
are intentionally removed; application output is `build/client/`. Existing API
mock/dashboard code is replaced with a small counter/dialog/routes example;
there is no invented backend API contract in the new preset.

Pinned central versions: Node 24.19.x, pnpm 11.21.0, React 19.3.0, React Router
8.4.0, TypeScript 7.0.2, Vite 8.3.0, Tailwind 4.3.3, Vitest 5.0.1 and Playwright
1.63.0. TS 6.0.2 remains a specifically named compatibility alias for lint's API;
the typecheck command invokes TS 7 by its explicit path. The lint command checks
the compiler version and a no-floating-promises negative control. React Hooks
7.1.1 is used because 7.0.1 did not declare ESLint 10 support. Strict peer checks
pass without overrides or suppressed peer ranges. The shadcn CLI/Zod workaround
is not a dependency or override of generated applications.

pnpm 11 ignores store configuration in the old `.npmrc`; it is now declared as
`storeDir: ${PNPM_STORE_DIR:-.pnpm-store}` in pnpm-workspace.yaml and verified both
locally and with an explicit environment override. Docker uses its scoped store
volume. Existing Make command names, scoped Compose/image/cache names, explicit
ports, diagnostics and cleanup remain. Frozen install runs on dev startup rather
than trusting the existence of a potentially stale node_modules directory.

Generated formatting is independent of display-name substitution in browser
tests: they import the shared project constant instead of duplicating user text.
The user-text declaration is locally prettier-ignored so its escaping/length
cannot force a post-generation manual format step. JSX renders the string as text.

Local verification on macOS (2026-09-21): clean frozen install, strict peers,
format/lint (including negative control), TS 7/route types, component test and
production build passed. Desktop 1280x800 and mobile 390x844 browser checks passed
against both development and production-build Vite preview using installed Chrome.
Production-build desktop/mobile tests also passed with the downloaded Playwright
Chromium via `PLAYWRIGHT_CHANNEL=chromium`. The optional separate Headless Shell
download was stopped during cleanup; the default no-channel launch was not tested.
An additional interactive browser check confirmed Escape focus restoration,
deep-link refresh, no overflow and no console errors.

Docker follow-up on 2026-09-21 (Docker Desktop 29.8.0, Linux arm64): a freshly
generated project with quotes, Chinese text, angle brackets, backslash, dollar
sign and placeholder-like display text passed the normal development image build,
frozen install, strict peers and complete `make verify`. The multi-stage production
image built successfully; Nginx configuration/health checks passed, and the runtime
contains static output without Node, node_modules or a server bundle. Three
Playwright tests using macOS Chrome against actual containerized Nginx passed,
covering desktop/mobile interactions and static-response behavior. Compose scoped
names, ports, store path, diagnostics and container-to-host connectivity passed.
Linux arm64 Playwright Chromium passed the same three actual-Nginx tests. After
the bundled Headless Shell download completed, the default-channel Make workflow
also passed all three actual-Nginx production tests and both development tests.
The scoped test containers/network/volumes are removed with `make clean-worktree`;
built images and generated temporary projects are retained for reproduction.

This run found a container-only SPA prerender failure: Vite preview listened on
`::1` while the React Router request connected to `127.0.0.1`. Common Vite config
now explicitly sets `preview.host` to `127.0.0.1`; a generated-config regression
assertion protects it. Both Docker and macOS builds pass with the fix.
This evidence does not cover the optional `Dockerfile.dev.full` image, Linux amd64,
native Linux hosts, remote CI, SSG or SSR.

Python coverage: 157 core + 11 macOS platform + one Android test; four new shipped
CSR tests check default/explicit equivalence, ownership, choices and toolchain
roles. Resource-aware assertions replace tests assuming Make/README live in the
common directory. Generation/list/required-file goldens change only for frontend;
other templates preserve their entries. The wheel/sdist verifier generates the
new CSR output and parses seven frontend configs. It does not yet run Node or
three-mode browser/container checks from installed artifacts (stage 6).

## Stage 4 implementation and verification (2026-09-21)

`rendering=ssg` is now available alongside default CSR; SSR remains rejected.
The SSG resource layer owns complete routes, public content, server-only loaders,
site-origin validation, page metadata, prerender configuration, static deployment,
preview routing and acceptance tests. It requires no generator-core branches,
per-mode variable schema, dependency changes or JSON merges. Node/React/TS and
pnpm lockfile versions remain those verified in stage 3.

The content list explicitly enumerates `/`, `/about` and two `/articles/:slug`
pages. The same path list drives prerendering, sitemap and local preview. Slugs
must be unique lowercase URL segments. HTML and `.data` navigation payloads are
built together; a serialized `builtAt` demonstrates a fixed build snapshot.
New content requires a rebuild, not a runtime server or an arbitrary-route fallback.

SSG production builds require `SITE_URL`, supplied through the environment or
Docker builder argument. It is a syntactically validated HTTPS DNS origin, not a
DNS reachability check. Credentials, paths, query/fragment, non-default ports,
loopback/local names and malformed hostnames are rejected. Development can omit
the origin, in which case no canonical URL is emitted. Metadata and sitemap never
derive their origin from the request host. All loader output is public; this
preset adds no private data source, CMS, API or authentication.

Nginx serves only static client artifacts, including deep-link HTML, navigation
data, sitemap and robots. Unknown routes, unknown slugs, missing data and assets
return HTTP 404 with a noindex error page. The framework's SPA fallback is removed
after build. Runtime inspection confirms no Node executable, node_modules or server
bundle. Publish the whole static directory as one release on other hosts and
configure equivalent routing rather than an index.html catch-all.

Three shared/frontend integration fixes were required:

- Root title now uses the route metadata API so SSG child metadata does not create
  duplicate titles; default CSR retains its title.
- Mode-owned `vite.preview.config.ts` keeps CSR SPA fallback but maps enumerated
  SSG paths to their own HTML. Generic Vite preview had returned the home document
  on an extensionless deep-link refresh. It is still not production Nginx.
- Explicit prebundling of shipped UI imports avoids a cold-start missing Rolldown
  cache chunk. JS-only counter/dialog triggers stay disabled until hydration via
  a shared `useSyncExternalStore` hook, avoiding lost clicks on prerendered HTML.
  Content and native links remain available without JS. Tests wait for hydration
  before specifically asserting client-side data navigation, and use a window
  marker instead of mutating React-owned HTML attributes.

Verified against generated special-text projects on macOS and Docker Desktop
29.8.0 / Linux arm64: frozen install, peers, format, typed lint/negative control,
TS 7, route types, four SSG unit/component cases and production build. macOS Chrome
passed four development and four static-preview tests. Actual Nginx passed six
initial Chrome tests, then all seven final Linux default Headless Shell tests,
including delayed JS, original HTML without JS, single title/canonical, sitemap,
stable query-independent data, client navigation, deep refresh and real 404s.
Linux development passed four tests on both a cold cache and a repeated launch.
CSR passed its complete macOS quality gate, two unit tests and two development
plus two static-preview browser cases after the shared changes.

Negative build probes confirmed missing SITE_URL, HTTP localhost, credentials and
subpaths fail with actionable errors. Core/platform/Android coverage is now
159 + 11 + 1 = 171 tests. A separate `frontend-ssg` exact-output golden and two
Python SSG contracts protect generation; other templates' baseline entries are
unchanged. Wheel/sdist checks include SSG resources and generate SSG from the
installed wheel outside the checkout, parsing seven configuration files. Running
Node/browser jobs from installed artifacts and full three-mode CI remain stage 6.
No native Linux host, amd64, optional full-dev image, SSR or remote CI result is
claimed. Test containers/network/volumes are cleaned; temporary source projects
and built images are retained for reproduction. No commit/push/release is implicit.

## Stage 5 implementation and verification (2026-09-21)

Implemented against stage 4 commit `9b94f52`. The new `ssr` resource layer owns
routes, the server-only request snapshot helper, explicit React server entry,
Node HTTP runtime, preview adapter, deployment files and runtime/browser tests.
No generator-core branch, dependency change, lockfile change or resource override
was needed. The only shared resource change includes `server/**/*` in TypeScript
checking and permits explicit `.ts` import extensions for Node 24's native type
stripping. CSR and SSG retain their previous source/deployment files.

Home loader data is request-local: a bounded public `visitor` query, random UUID
and timestamp. Duplicate, oversized and control-character input returns 400.
Private settings remain in `.server.ts`; the loader returns an explicit public
object, not the environment. Private configuration failures return sanitized 500
HTML and data, with generic application logs. Unknown routes return real 404.
HTML and navigation data are `private, no-store`; fingerprinted client assets
are immutable, and other public files revalidate. No shared request-data cache,
backend, authentication, database, CMS, cloud target or RSC was added.

The Node adapter uses the locked official `@react-router/node` request listener
for Fetch/HTTP lifecycle bridging. The small outer server handles public files,
HEAD/methods, path decoding/traversal and symlink boundaries, process health,
socket input timeouts and bounded shutdown. It ignores forwarded origin headers
by default; deployments still need TLS and allowed-host/proxy policy. Rendering
waits for all content to preserve error status, has a six-second abort deadline,
and cancels on disconnect. Suspense streaming optimization is not claimed.
SIGTERM/SIGINT stop acceptance, drain for ten seconds, then force close; successful
drain exits 0, forced drain exits 1. `/healthz` does not certify upstream services.

Docker uses frozen builder and production-only dependency stages, then runs Node
as the non-root `node` user. Runtime inspection confirms compiled server/client
output and runtime sources, without app sources, private env files, Vite, TS
compiler or React Router dev dependency. `CONTAINER_PORT` is passed as runtime
`PORT` as well as mapped; actual port 3100 was tested. Worktree-scoped Make,
Compose, cache, image and cleanup commands are preserved. `pnpm preview` uses
the real SSR handler through Vite; built-browser checks launch Node directly.

Verified on macOS and Docker Desktop 29.8.0/Linux arm64: frozen install, peer
constraints, strict formatting/lint plus negative control, TS 7 route/runtime
checking, 31 unit/component cases and production build. Tests cover request
isolation, server config boundaries, input errors, HEAD, render failure/deadline/
cancellation, public file safety and graceful/forced drain. macOS Chrome passed
seven direct Node acceptance cases, four development cases and five preview
cases. Five more cases passed against the actual Linux production image,
including special-text hydration, twelve concurrent request snapshots, HTML/data
cache headers, missing routes/assets and health. That image was healthy and
exited 0 on SIGTERM. Linux default Headless Shell also passed seven direct Node
checks, four development checks from a cold cache and four on a repeated launch,
and five actual production-image checks, including clean SIGTERM exit. Client
navigation refreshes loader snapshots without replacing the document. Browser
downloads were slow in Docker; the exact locked Linux arm64 Headless Shell and
FFmpeg archives were fetched with Playwright through the host network and copied
to this worktree's cache volume, then actually executed on Linux. The initial
production browser run skipped only the separately prepared browser-install
prerequisite, not build, runtime health, browser assertions or shutdown checks.
`pnpm browser:install --only-shell` subsequently passed inside Linux with normal
host-requirement validation. The redundant full Chromium download was cancelled;
completion of the full-browser installation command is not claimed for this run.

CSR and SSG both pass the full macOS quality gate after the shared TS config
change, with two CSR and four SSG static-preview browser cases. Python passes
161 core + 11 platform + one Android test (173 total), plus Ruff. Two new SSR
generation contracts and the `frontend-ssr` exact-output golden protect ownership,
determinism, special text and executable scripts. All non-frontend baseline
entries are unchanged. Wheel/sdist checks include SSR private-named resources and
generate all three modes outside the checkout, with seven parsed SSR configs and
Make checks. Installed-wheel Node/browser CI remains stage 6.

No native Linux host, Linux amd64, optional full-dev image, remote CI, load test,
external backend or other browser-engine coverage is claimed. No commit, push or
release is implicit in this implementation task.

Reproduction project: `/private/tmp/biucing-stage5.S6sQOR/ssr-check`; image
`ssr-check-aa2ddd01:dev`. Temporary test containers, Compose network and named
dependency/browser caches are cleaned after verification; source projects,
downloaded host browser cache and built images are retained. Cache removal is
recoverable by reinstalling dependencies/browsers, not a deletion of project data.

## Stage 6 implementation and local verification (2026-09-21)

Implemented after stage 5 commit `d53e749`. Generated templates, the generator
kernel, dependency locks, public JSON output and all existing goldens are unchanged.
The additional coverage lives in verification scripts, regression tests, CI and
documentation. See [frontend artifact acceptance](frontend-artifact-acceptance.md)
for commands, prerequisites, report retention, cleanup and platform limits.

`verify-distribution` now inventories all 325 template resource files, comparing
content hashes and all executable bits across the checkout, wheel and sdist. It
also rebuilds a wheel from the extracted sdist using the locked build environment
and checks the same inventory. Safe extraction rejects traversal, links and
special files, uses a fresh destination and never restores archive ownership or
setuid bits. Linux Python 3.11.2 exposed the absence of the later tarfile `filter`
API, so the implementation uses validated regular-file extraction compatible with
the project's minimum Python version. Both platforms' core regressions pass.

`verify-frontend` installs one explicit wheel into a fresh venv, verifies its
import location, clears source-path and external-browser-server overrides, and
generates each mode outside the checkout. It runs frozen native pnpm installation,
peer constraints, format/lint/negative control/TS7/unit/build checks, development
and built-browser checks. Optional deployment checks build actual images, inspect
their contents, require readiness and clean exit, and remove only owned UUID-scoped
containers/images even after browser failure. Logs, phase-specific screenshots
and a SHA-linked JSON report remain available for diagnosis. Eleven new Python-
only tests cover inventories, negative cases, safe extraction, workspace/env
isolation, failure/timeout reporting, cleanup and CI/release wiring.

The reusable frontend workflow contains exactly six jobs: Linux/macOS × three
modes, with one Python version. It consumes a separately built/verified wheel;
Linux jobs additionally test actual production images. Publishing consumes the
same artifact later given to `uv publish`, checks out the release tag for scripts,
and now waits for frontend acceptance in addition to existing verification and
platform jobs. Browser reports upload on failure as well as success. `actionlint`
1.7.7 and the workflow contract test passed. No Trusted Publisher change is needed.

Local installed-wheel evidence (Node 24.19.0 / pnpm 11.21.0, unchanged lockfile):

| Check | macOS arm64 | Docker Linux arm64 |
| --- | --- | --- |
| All three modes installed from wheel, frozen native deps and complete quality gates | Passed | Passed |
| Unit/component cases across CSR/SSG/SSR | 2 / 4 / 31 | 2 / 4 / 31 |
| Development browser cases | 2 / 4 / 4, installed Chrome | 2 / 4 / 4, default Headless Shell |
| Built-artifact browser/Node cases | 2 / 4 / 7, installed Chrome | 2 / 4 / 7, default Headless Shell |
| Actual production-image browser cases | 3 / 7 / 5, Chrome against Linux images | Linux images checked through the macOS invocation |

Both invocations tested wheel SHA-256
`24f8c776c0a83ab68307bfbd99334a6e7a9100e851084836eccdcb462223cd15`.
The macOS report has 54 successful stages; the Linux report has 27. Linux used
the exact previously downloaded Linux Headless Shell cache, with normal installer
checks and fresh Linux native dependencies, not copied macOS node_modules. Actual
production image checks cover static-only CSR/SSG and non-root SSR, private-input
sentinels, HTML/data/status behavior, health, clean shutdown and scoped cleanup.
Reports remain under `/private/tmp/biucing-stage6.4fM2Da/macos/reports` and
`/private/tmp/biucing-stage6.4fM2Da/linux/run/reports`. Test containers and temporary
runner images are cleaned; artifacts, generated projects, reports and task-local
dependency caches are retained for reproduction.

Final Python coverage is 172 core + 11 platform + one Android = 184 passing tests;
172 core cases also pass on Linux Python 3.11.2. Ruff, distribution verification,
Make-entry checks and diff whitespace checks pass. No output baseline was refreshed.
Maturity remains `validated`; no production-certification upgrade is implied.

Remaining external gate: the newly configured GitHub Actions matrix has not run
remotely because this task does not authorize a commit/push/workflow dispatch.
Hosted Linux amd64/macOS runners, apt browser-dependency setup on a fresh hosted
image, and the combined native-Linux browser-to-production-image CI job must be
confirmed by that run. No PyPI publication, release or version bump was performed.
