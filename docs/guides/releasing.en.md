---
title: "BiucingCLI Release Checklist"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# BiucingCLI Release Checklist

[中文](releasing.md) · Translation of the Chinese primary document.

This checklist is the repeatable release path for BiucingCLI `0.x`.

It is intentionally split into:

- repo product checks: does the CLI itself still behave correctly?
- template proof: do the seven shipped starters still meet their minimum release bar?
- release surface checks: are version, changelog, tag, and publication aligned?

Use this document together with [verification-matrix.md](verification-matrix.en.md).

## Release Surface Map

Use this map before every version bump so the release does not update only part of the repo surface.

| Surface | File | What to update |
| --- | --- | --- |
| README version target | `README.md` | Current repository release target and any user-facing release wording |
| Changelog entry | `CHANGELOG.md` | New version heading, date, and user-visible changes |
| Package version | `pyproject.toml` | `[project].version` |
| Dependency lock | `uv.lock` | Run `uv lock` after version/dependency changes |
| Runtime version constant | `src/biucingcli/__init__.py` | `__version__` |
| CLI version expectation | `tests/test_cli.py` | Expected `biucing --version` output |
| Release operations docs | `docs/guides/releasing.md`, `docs/guides/verification-matrix.md` | Update if the verification bar or release flow changed |

For release history and architecture context, also review:

- `docs/initiatives/feature/worktree-isolation/design.md`
- `docs/initiatives/feature/worktree-isolation/plan.md`
- `docs/engineering/worktree-isolation-contract.md`
- `docs/releases/0.6.0/validation.md`
- `docs/initiatives/improvement/worktree-hardening/design.md`
- `docs/initiatives/improvement/worktree-hardening/plan.md`
- `docs/releases/0.6.1/validation.md`
- `docs/releases/0.7.0/notes.md`
- `docs/releases/0.7.0/validation.md`
- `docs/releases/0.8.0/notes.md`
- `docs/releases/0.8.0/validation.md`
- `docs/initiatives/improvement/distribution-hardening/plan.md`
- `docs/releases/0.9.0/validation.md`
- `docs/releases/0.10.0/notes.md`
- `docs/releases/0.10.0/validation.md`
- `docs/README.md` and the domain indexes

## 1. Scope The Release

- Decide the target version number before editing any files.
- Confirm which templates changed in the release.
- Confirm whether the release is:
  - CLI-only hardening
  - template-content changes
  - release-surface/docs only

If any template changed, plan to gather at least the matrix evidence for that template before tagging.

## 2. Update Release Surfaces

Update these files together so the repo does not land in a half-bumped state:

- `README.md`
- `CHANGELOG.md`
- `pyproject.toml`
- `uv.lock` (refresh with `uv lock`)
- `src/biucingcli/__init__.py`
- `tests/test_cli.py`

Check that:

- the README version target matches the intended release;
- the changelog summary matches what actually shipped;
- the CLI `--version` expectation matches the new version string.

## 3. Run Repo-Level Product Checks

These checks should pass for every release, even if no template changed.

First run `uv sync --locked` to install the project and its development/build tools.

The full command blocks below require macOS tools. For the split release gates,
run `python scripts/run-tests --suite core` through uv on Linux/macOS and
`python scripts/run-tests --suite platform` through uv on macOS. Run the artifact
verifier with `--check-make` on macOS as well. See [testing.md](testing.en.md).
Both suites and generated configuration parsing must pass before publishing.

```bash
uv run --locked python scripts/check-docs
uv run --locked python -m unittest discover -s tests
uv run --locked ruff check --select E4,E7,E9,F src tests scripts
uv run --locked biucing validate
uv run --locked python scripts/verify-distribution
uv run --locked biucing list
uv run --locked biucing list --json
uv run --locked biucing info web-service
uv run --locked biucing info web-service --json
uv run --locked biucing info worker
uv run --locked biucing info worker --json
uv run --locked biucing info harmonyos
```

Release bar:

- all unit tests pass;
- `validate` reports `Template validation passed.`;
- `list/info` golden-backed output still matches the intended product surface;
- no new metadata or placeholder inconsistencies are introduced;
- the installed wheel can validate and generate every template outside the source tree.

Recommended local command block:

```bash
uv run --locked python -m unittest discover -s tests
uv run --locked ruff check --select E4,E7,E9,F src tests scripts
uv run --locked biucing validate
uv run --locked python scripts/verify-distribution
uv run --locked biucing list
uv run --locked biucing list --json
uv run --locked biucing info web-service
uv run --locked biucing info web-service --json
uv run --locked biucing info worker
uv run --locked biucing info worker --json
uv run --locked biucing info harmonyos
biucing --version
```

## 4. Check Scriptability Paths

The current scriptability surface makes preview, scripting, and manifest output part of the product surface, so release verification should cover them explicitly.

Minimum checks:

```bash
uv run --locked biucing create frontend demo-app --output-dir /tmp/biucing-release-check --dry-run
uv run --locked biucing create web-service demo-service --output-dir /tmp/biucing-release-check --module-name github.com/example/demo-service --plan --json
uv run --locked biucing create frontend demo-app --output-dir /tmp/biucing-release-check --non-interactive --set project_name=demo-app
uv run --locked biucing create web-service demo-service --output-dir /tmp/biucing-release-check --non-interactive --set project_name=demo-service --set module_name=github.com/example/demo-service
```

Release bar:

- preview commands return the expected human-readable and JSON plan output;
- `--non-interactive` fails fast when required values are missing;
- `--set key=value` works for required values;
- explicit template flags still override `--set` when both are supplied;
- `create --json` remains stable enough for automation consumers.

The automated Python tests are the main proof here; these commands are a quick maintainer smoke check before publication.

## 5. Gather Template Evidence

Use [verification-matrix.md](verification-matrix.en.md) as the source of truth.

Rules:

- if a template did not change, existing release evidence plus passing repo checks are usually enough;
- if a template changed, re-run the minimum generated-project or Docker verification for that template;
- if a shared renderer or metadata feature changed, re-check at least one Dockerized template and one native template in addition to repo tests.

Practical expectation:

- `frontend`, `web-service`, `micro-service` should keep their Docker-based proof current;
- `worker` should keep its generated-project `go test ./...` proof current;
- `apple`, `android`, and `harmonyos` should label native proof as `static`, `doctor`, or `real-build`;
- `make -n` proof for native templates is useful static evidence, but it is never a real build;
- native real-build proof is required when generated platform structure, manifests, package identity, signing inputs, build settings, dependency files, or native build/test targets change;
- native real-build proof is optional, but valuable, for docs-only, CLI metadata-only, or diagnostic wording changes that do not alter generated native build behavior;
- `harmonyos` should keep generated-project static and doctor checks current, with real DevEco/HarmonyOS SDK builds recorded when the workstation is configured.

Suggested native worktree evidence block:

```bash
# Apple static plus doctor proof
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
make -n build test lint format WORKTREE_ID=beta

# Android static plus doctor proof
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
make -n build test test-ui lint install-debug WORKTREE_ID=beta

# HarmonyOS static plus doctor proof
make worktree-info WORKTREE_ID=alpha
make worktree-debug-identity WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
make -n build clean-worktree WORKTREE_ID=beta
```

When a native real-build is required, record the exact configured workstation commands that ran, for example `make generate && make build`, `./gradlew assembleDebug`, or `make build` for HarmonyOS.
If the workstation does not have the required SDKs, record that as an environment limitation instead of implying fresh real-build coverage.

## 6. Check Worktree Isolation

For `0.6.0` and later, every shipped template should expose the shared worktree command surface:

```bash
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
make clean-worktree WORKTREE_ID=alpha
```

Release bar:

- `biucing list --json` shows every shipped template as `worktree-ready`;
- generated Docker-first projects render distinct Compose project names and volume names for different `WORKTREE_ID` values;
- generated native projects print worktree-local cache paths and local config/signing paths;
- `make clean-worktree` only targets state owned by the current worktree.
- native worktree evidence is labeled as `static`, `doctor`, or `real-build` using [verification-matrix.md](verification-matrix.en.md).
- HarmonyOS evidence includes `make worktree-debug-identity` and treats per-worktree bundle rewriting as deferred unless a configured DevEco/hvigor workstation has verified the metadata hook.

Use [0.10.0-release-prep.md](../releases/0.10.0/validation.en.md) for the latest concrete evidence run.

## 7. Review Docs And Messaging

Before tagging, confirm the human-facing story is clean:

- `README.md` reflects the current template portfolio and maturity story;
- `CHANGELOG.md` highlights user-visible changes rather than implementation trivia;
- `docs/initiatives/feature/worktree-isolation/design.md`, `docs/initiatives/feature/worktree-isolation/plan.md`, and future version plans are not obviously behind shipped reality;
- any new validation behavior is documented somewhere discoverable.

## 8. Stage The Release

Recommended sequence:

```bash
git status --short
git add README.md CHANGELOG.md pyproject.toml uv.lock src/biucingcli/__init__.py tests/test_cli.py docs/guides/releasing.md docs/guides/verification-matrix.md
git commit -m "Prepare release X.Y.Z"
git tag -a vX.Y.Z -m "Release X.Y.Z"
```

If the version bump touches more files, expand `git add` intentionally instead of switching to a broad `git add .`.

Before pushing, double-check:

- the working tree is clean except for intentionally excluded files;
- the annotated tag points at the intended release commit.

## 9. Publish

Configure PyPI/TestPyPI Trusted Publishing following [uv-workflow.md](development.en.md)
before the first automated release. Run the Publish workflow manually against
the release tag with `target=testpypi` to rehearse. Publishing the GitHub Release
then triggers the uv build, verification, and production `uv publish` workflow:

```bash
git push origin main --follow-tags
# Rehearse Publish with target=testpypi before creating the release below.
gh release create vX.Y.Z --title "BiucingCLI X.Y.Z" --notes-file CHANGELOG.md
```

If you need to review the generated release notes manually, create the GitHub release after a final changelog inspection instead of rushing the one-liner.

## 10. Record Release Evidence

After publication, record the proof in the release notes, PR description, or rollout summary:

- date of the verification run;
- repo-level commands that passed;
- which templates received fresh generated-project or Docker verification;
- any known limitations that did not block the release.

That keeps the next release from needing to reconstruct evidence from scratch.

## Standard Evidence Template

Use this template in the PR body, release-prep note, or rollout summary:

```md
## Release Evidence

- Target version: `X.Y.Z`
- Verification date: `YYYY-MM-DD`
- Repo-level checks:
  - `uv run --locked python -m unittest discover -s tests`
  - `uv run --locked biucing validate`
  - `uv run --locked biucing list`
  - `uv run --locked biucing list --json`
  - `uv run --locked biucing info web-service`
  - `uv run --locked biucing info web-service --json`
  - `uv run --locked biucing info worker`
  - `uv run --locked biucing info worker --json`
  - `uv run --locked biucing info harmonyos`
- Fresh template proof:
  - `template-name`: `commands run and result`
- Worktree proof:
  - `template-name`: `worktree-info/doctor/config/build-command proof`
  - `native-template-name`: `static/doctor/real-build: commands run and result`
- Version surfaces updated:
  - `README.md`
  - `CHANGELOG.md`
  - `pyproject.toml`
  - `src/biucingcli/__init__.py`
  - `tests/test_cli.py`
- Known limitations:
  - `none` or explicit note
```

## Backend single-host delivery

- Run the six backend Docker component combinations, generation goldens and worktree regression after runtime/topology changes.
- Preserve wheel/sdist-generated backends with `scripts/verify-distribution --backend-output-dir <new-dir>` and verify their Docker workflows and production images.
- Run `scripts/verify-backend-production` against isolated local fixtures; retain scan/SBOM/signature, TLS, failed migration/release, previous digest rollback and real isolated restore evidence.
- Record image/platform versions, backup data point and restoration time. Keep full-disk tests bounded to disposable storage.
- Check generated `deploy/RUNBOOK.md`, metadata and architecture profiles against the evidence. Local pinned-key signing does not validate GitHub OIDC/GHCR publication, remote backup retention or multi-host availability; record those separately.

## Backend Kubernetes reference

- Render both production and autoscaling overlays for all six component combinations; check Kubernetes schemas and release failure guards.
- Verify installed wheel/sdist contain executable kube scripts, ConfigMaps, policy/Secret refs, migration Jobs and drill templates; run generated manifest verification.
- Preserve real-cluster/HA `not-run` when only Kustomize/schema or fake API tests ran. Require traffic, data and recovery evidence before changing B27 status.
- Review hard topology spread, PDB scope, HPA replicas ownership, terminating Pod connection allowance, immutable credential refs and external CNI/Ingress/PKI/PG contracts.
