# Development, builds, and publishing with uv

Use uv 0.12.16, matching both GitHub workflows. `.python-version` selects Python
3.11 for development; package support remains Python >=3.11. uv can download
the interpreter when needed. CI overrides the default to test 3.11–3.14.

## Dependencies and local checks

```bash
uv sync --locked
uv run --locked biucing --version
uv run --locked ruff check --select E4,E7,E9,F src tests scripts
uv run --locked python scripts/run-tests --suite core
uv run --locked biucing validate
uv run --locked python scripts/verify-distribution
```

`uv sync` installs the project in editable mode and the default `dev` and `build`
groups. Ruff and Twine are development tools (Twine only checks metadata;
uploads use uv). Setuptools and wheel belong to `build`. These groups do not
become runtime dependencies for CLI users. PyYAML and json5 are development-only
configuration parsers. Core tests run on Linux/macOS without native tools;
the separate platform suite requires macOS and its documented toolchain.
See [testing.md](testing.md) for commands and prerequisites.

- Add a runtime dependency: `uv add PACKAGE`.
- Add a developer tool: `uv add --dev PACKAGE`.
- Add a build tool: `uv add --group build PACKAGE`.
- Remove a developer tool: `uv remove --dev PACKAGE`.
- Upgrade deliberately: `uv lock --upgrade-package PACKAGE`, then `uv sync --locked`.
- For setuptools upgrades, update its matching pins in `build-system.requires`
  and the `build` group before refreshing the lockfile. This also pins the backend
  used for isolated editable installs and source installs by downstream users.
- After editing metadata or bumping the version, run `uv lock` and commit the
  updated `pyproject.toml` and `uv.lock` together.

CI uses `--locked` so stale locks fail instead of silently changing resolutions.
Do not hand-edit `uv.lock`. `.venv` remains ignored. Historical release evidence
documents retain the commands actually executed at the time.

## Build and verify the same artifacts

From a clean checkout, choose a new/empty output directory:

```bash
uv sync --locked
uv build --no-sources --no-build-isolation --out-dir release-dist
uv run --locked python scripts/verify-distribution --dist-dir release-dist
uv publish --dry-run --trusted-publishing never release-dist/*
```

The build runs with the backend installed by `uv sync`; `--no-build-isolation`
is intentional because isolated build dependencies are not governed by the
project lockfile. Setuptools remains the PEP 517 backend so template packaging
rules stay intact. The default `uv build` produces an sdist, then builds its
wheel from that sdist.

The verifier requires exactly one wheel and one sdist, checks metadata with
Twine, inspects embedded template resources, creates an isolated environment
using `uv venv`, installs the wheel with `uv pip`, and generates all seven
templates outside the repository and parses their generated configuration files.
Add `--check-make` on macOS to also verify generated Make entrypoints.
Without `--dist-dir`, it builds into a
temporary directory and removes those artifacts when finished.

`uv publish --dry-run` checks the upload path without publishing; it does not
prove that your PyPI account or OIDC configuration will authorize an upload.

## One-time PyPI setup

Create and verify a PyPI account and enable two-factor authentication. Ensure
you control the project name `biucingcli` or that it is available for creation.
In account Publishing, add a pending Trusted Publisher for a new project (or
use project Publishing for an existing project):

| Field | Production | Rehearsal |
| --- | --- | --- |
| Index | PyPI | TestPyPI |
| Project | `biucingcli` | `biucingcli` |
| Repository owner | `anzihenry` | `anzihenry` |
| Repository | `BiucingCLI` | `BiucingCLI` |
| Workflow filename | `publish.yml` | `publish.yml` |
| Environment | `pypi` | `testpypi` |

TestPyPI accounts and publishers are separate. Configure the corresponding
GitHub repository environments with matching names. Production can restrict
deployments to release tags and require maintainer review. The upload job alone
has `id-token: write`; neither a stored API token nor a password is needed.

## Automated release

1. Update the release surfaces listed in [release-checklist.md](release-checklist.md),
   including the lockfile, and commit the changes.
2. Push an annotated `vX.Y.Z` tag containing the new workflow and lockfile.
3. Run the **Publish** workflow manually with that tag and `target=testpypi`.
4. After rehearsal succeeds, publish the GitHub Release for the same tag.
   `release.published` triggers production PyPI publishing automatically.
   Manual dispatch with `target=pypi` is also supported.
5. Confirm both the upload and post-upload installation checks succeed.

Only stable `vX.Y.Z` tags are accepted, and the tag, package metadata, and runtime
version must agree. All eight Linux/macOS Python matrix jobs and the macOS
platform job must pass before upload. The macOS Python 3.11 job's tested wheel
and sdist are transferred as a GitHub artifact
and uploaded unchanged. The publishing job then installs the exact version
from the selected index and checks version, template listing, and validation.

The old `v0.9.0` tag does not contain this workflow or lockfile. Use a new release
tag for this migration; do not move the existing tag. To publish the original
0.9.0 separately, retrieve and verify its original GitHub Release assets first.
Adding this workflow does not replay earlier GitHub Release events.

If upload succeeds but the installation check fails, inspect the index before
retrying. uv can skip identical files already uploaded. Do not rebuild different
contents under a published filename; publish a new version for changed contents.

## Manual publishing with uv

If CI is unavailable, build and verify first as above. Set `UV_PUBLISH_TOKEN`
securely in your local environment using a token for the chosen index:

```bash
# TestPyPI (requires a TestPyPI token)
uv publish --index testpypi --trusted-publishing never release-dist/*

# Production (requires a PyPI token)
uv publish --trusted-publishing never release-dist/*
```

Never commit credentials. The two commands are alternatives, not a command
block to run with the same token. Explicit output paths avoid publishing old
files left in `dist`.

After actual PyPI publication, users can install with
`uv tool install biucingcli==X.Y.Z`, upgrade with `uv tool upgrade biucingcli`,
or run temporarily with `uvx --from biucingcli==X.Y.Z biucing --help`.

## References

- [uv dependency locking](https://docs.astral.sh/uv/concepts/projects/sync/)
- [uv builds and publishing](https://docs.astral.sh/uv/guides/package/)
- [uv GitHub Actions integration](https://docs.astral.sh/uv/guides/integration/github/)
- [PyPI pending Trusted Publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
