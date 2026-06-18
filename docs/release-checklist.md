# BiucingCLI Release Checklist

This checklist is the repeatable release path for BiucingCLI `0.x`.

It is intentionally split into:

- repo product checks: does the CLI itself still behave correctly?
- template proof: do the five shipped starters still meet their minimum release bar?
- release surface checks: are version, changelog, tag, and publication aligned?

Use this document together with [verification-matrix.md](verification-matrix.md).

## Release Surface Map

Use this map before every version bump so the release does not update only part of the repo surface.

| Surface | File | What to update |
| --- | --- | --- |
| README version target | `README.md` | Current repository release target and any user-facing release wording |
| Changelog entry | `CHANGELOG.md` | New version heading, date, and user-visible changes |
| Package version | `pyproject.toml` | `[project].version` |
| Runtime version constant | `src/biucingcli/__init__.py` | `__version__` |
| CLI version expectation | `tests/test_cli.py` | Expected `biucing --version` output |
| Release operations docs | `docs/release-checklist.md`, `docs/verification-matrix.md` | Update if the verification bar or release flow changed |

For `0.3.0`, also review:

- `docs/0.3.0-plan.md`
- `README.md` links under `Design Docs`

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
- `src/biucingcli/__init__.py`
- `tests/test_cli.py`

Check that:

- the README version target matches the intended release;
- the changelog summary matches what actually shipped;
- the CLI `--version` expectation matches the new version string.

## 3. Run Repo-Level Product Checks

These checks should pass for every release, even if no template changed.

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli list
PYTHONPATH=src python3 -m biucingcli.cli list --json
PYTHONPATH=src python3 -m biucingcli.cli info web-service
PYTHONPATH=src python3 -m biucingcli.cli info web-service --json
```

Release bar:

- all unit tests pass;
- `validate` reports `Template validation passed.`;
- `list/info` golden-backed output still matches the intended product surface;
- no new metadata or placeholder inconsistencies are introduced.

Recommended local command block:

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli list
PYTHONPATH=src python3 -m biucingcli.cli list --json
PYTHONPATH=src python3 -m biucingcli.cli info web-service
PYTHONPATH=src python3 -m biucingcli.cli info web-service --json
biucing --version
```

## 4. Check Scriptability Paths

The current `0.3.0` hardening work makes scripting part of the product surface, so release verification should cover it explicitly.

Minimum checks:

```bash
PYTHONPATH=src python3 -m biucingcli.cli create frontend demo-app --output-dir /tmp/biucing-release-check --non-interactive --set project_name=demo-app
PYTHONPATH=src python3 -m biucingcli.cli create web-service demo-service --output-dir /tmp/biucing-release-check --non-interactive --set project_name=demo-service --set module_name=github.com/example/demo-service
```

Release bar:

- `--non-interactive` fails fast when required values are missing;
- `--set key=value` works for required values;
- explicit template flags still override `--set` when both are supplied.

The automated Python tests are the main proof here; these commands are a quick maintainer smoke check before publication.

## 5. Gather Template Evidence

Use [verification-matrix.md](verification-matrix.md) as the source of truth.

Rules:

- if a template did not change, existing release evidence plus passing repo checks are usually enough;
- if a template changed, re-run the minimum generated-project or Docker verification for that template;
- if a shared renderer or metadata feature changed, re-check at least one Dockerized template and one native template in addition to repo tests.

Practical expectation:

- `frontend`, `web-service`, `microservice` should keep their Docker-based proof current;
- `apple` and `android` should keep their generated-project proof current.

## 6. Review Docs And Messaging

Before tagging, confirm the human-facing story is clean:

- `README.md` reflects the current template portfolio and maturity story;
- `CHANGELOG.md` highlights user-visible changes rather than implementation trivia;
- `docs/0.3.0-plan.md` or future version plans are not obviously behind shipped reality;
- any new validation behavior is documented somewhere discoverable.

## 7. Stage The Release

Recommended sequence:

```bash
git status --short
git add README.md CHANGELOG.md pyproject.toml src/biucingcli/__init__.py tests/test_cli.py docs/release-checklist.md docs/verification-matrix.md
git commit -m "Prepare release X.Y.Z"
git tag -a vX.Y.Z -m "Release X.Y.Z"
```

If the version bump touches more files, expand `git add` intentionally instead of switching to a broad `git add .`.

Before pushing, double-check:

- the working tree is clean except for intentionally excluded files;
- the annotated tag points at the intended release commit.

## 8. Publish

Proven publication sequence for this repo:

```bash
git push origin main --follow-tags
gh release create vX.Y.Z --title "BiucingCLI X.Y.Z" --notes-file CHANGELOG.md
```

If you need to review the generated release notes manually, create the GitHub release after a final changelog inspection instead of rushing the one-liner.

## 9. Record Release Evidence

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
  - `python3 -m unittest discover -s tests`
  - `PYTHONPATH=src python3 -m biucingcli.cli validate`
  - `PYTHONPATH=src python3 -m biucingcli.cli list`
  - `PYTHONPATH=src python3 -m biucingcli.cli list --json`
  - `PYTHONPATH=src python3 -m biucingcli.cli info web-service`
  - `PYTHONPATH=src python3 -m biucingcli.cli info web-service --json`
- Fresh template proof:
  - `template-name`: `commands run and result`
- Version surfaces updated:
  - `README.md`
  - `CHANGELOG.md`
  - `pyproject.toml`
  - `src/biucingcli/__init__.py`
  - `tests/test_cli.py`
- Known limitations:
  - `none` or explicit note
```
