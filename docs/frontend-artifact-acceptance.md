# Frontend installed-artifact acceptance

Stage 6 keeps the Python-only suite separate from expensive generated-project
checks. No template dependency, generated file or output golden changes are needed.
Use `uv` for the generator's environment/build and the generated project's pinned
pnpm for frontend dependencies; do not install the checkout into acceptance venvs.

## Distribution integrity

```bash
uv sync --locked
uv run --locked python scripts/verify-distribution --check-make
```

The verifier compares every file under `biucingcli/template_data`, including
common and mode layers, hidden files, binary files and executable flags, against
both wheel and sdist. Missing, additional or changed resources fail. It then
extracts the sdist into an isolated directory, builds a wheel with the locked
build interpreter/dependencies and compares its resources again. This verifies
resource reproducibility, not byte-identical ZIP timestamps or all wheel metadata.
Extraction rejects traversal, links and special entries before writing; files
are created exclusively inside a fresh directory without archive ownership or
setuid attributes. This also supports early Python 3.11 releases.

The installed wheel is still independently checked for catalog/validation and
generation of all templates and all three frontend modes. This remains a Python-
only check; it does not require Node, browsers or Docker. `--check-make` is optional.

## Generated-project acceptance

Requires Node 24.19.0, pnpm 11.21.0 and uv. Docker is required only for `--docker`.
The work directory must not already exist and must be outside the checkout.

```bash
frontend_audit_root="$(mktemp -d)"
uv build --no-sources --no-build-isolation --out-dir "$frontend_audit_root/dist"
uv run --locked python scripts/verify-frontend \
  --dist-dir "$frontend_audit_root/dist" \
  --work-dir "$frontend_audit_root/run" --docker
```

All modes run sequentially by default. Use `--mode csr`, `--mode ssg` or
`--mode ssr` to select one, or repeat the flag. Parallel invocations need separate
workspaces/hosts: their generated development/preview servers use fixed local
ports. Production container host ports, names and image tags are allocated per run.

The runner creates a new venv, installs the explicit wheel with no dependencies,
clears Python path overrides and verifies the imported module is inside that
venv. All CLI invocations and generated projects live outside the checkout.
Special display text exercises quote, Unicode, markup and literal-placeholder
preservation. The wheel SHA-256, modes, browser channel, platform, stages and
timings are recorded under `reports/summary.json`.

Each mode runs frozen installation, peer checks, the full `pnpm verify` gate,
development browser checks and built-artifact browser checks. The latter uses
static preview for CSR/SSG and the production Node entry for SSR. `SITE_URL` is a
fixed public HTTPS test origin; SSR uses a harmless private sentinel, never a
real credential. Source-loader state or an already running development server
cannot satisfy acceptance by accident.

The default browser installation is Playwright's pinned Chromium Headless Shell
(`--only-shell`). On Linux CI, add `--install-browser-deps` to authorize system
package installation; it is deliberately opt-in on developer machines. An
explicit `--browser-channel chrome` can use installed Chrome on macOS, but is
reported separately and does not count as default-browser coverage. Cached
browser artifacts may be reused; native pnpm dependencies are installed per OS.

With `--docker`, the runner builds the generated Dockerfile, waits for image
health, runs the mode's production browser/HTTP suite, checks runtime contents,
stops the container and requires exit 0. CSR/SSG must not contain Node/runtime
server dependencies; SSR must be non-root and exclude app sources/private env/
development dependencies. These complement HTML/data/status/isolation assertions
in the generated tests. Docker uses a local daemon whose published ports are
reachable on 127.0.0.1; remote Docker hosts are not supported by this runner.

Logs and per-phase screenshots/results are retained on success and failure;
later Playwright runs cannot overwrite earlier diagnostics. Timeout/interruption
terminates the owned subprocess group. Finally blocks remove only UUID-scoped
test containers and images, including after browser failures. Workspaces, pnpm
stores and reports are retained for inspection; remove only the explicitly chosen
audit directory when no longer needed. No global Docker prune or user-worktree
cleanup is performed. Abrupt process/host termination may still require manual
cleanup of IDs recorded in the logs.

## CI and release gates

`.github/workflows/frontend.yml` is reused by CI and publishing. Its six jobs are
Linux/macOS × CSR/SSG/SSR, using one Python version rather than multiplying the
frontend work by the Python core matrix. Both operating systems install their
own native frontend dependencies and run default-browser tests. Linux additionally
tests real production images; hosted macOS does not assume Docker is available.

CI builds/verifies and uploads one distribution artifact for these jobs. Publishing
tests the same `python-distributions` artifact that the OIDC publish job later
uploads, and checks out the requested release tag for the acceptance scripts.
Publication now depends on core/distribution, platform and frontend gates. No
Trusted Publisher or secret changes are needed. Jobs upload only `reports/` for
seven days, never whole generated projects, node_modules or private env files.

Workflow contract tests and actionlint validate wiring locally. Actual hosted
runner success is a separate gate requiring a push/CI run; this implementation
does not automatically commit, push, dispatch workflows or publish a version.
See the stage 6 record in [the rendering plan](frontend-rendering-plan.md) for
local evidence and remaining hosted-platform limits. Maturity remains `validated`,
not a claim of production certification or all-browser/load coverage.
