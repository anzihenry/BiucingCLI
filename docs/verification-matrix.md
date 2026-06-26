# BiucingCLI Verification Matrix

This matrix defines the minimum release bar for the current six templates and the CLI surface around them.

The goal is not to re-run every heavy workflow on every commit.
The goal is to make release proof explicit and reusable.

## Release-Wide Checks

These checks apply to every release regardless of which template changed.

| Area | Command or proof | Release bar |
| --- | --- | --- |
| Unit test suite | `python3 -m unittest discover -s tests` | Must pass |
| Template metadata validation | `PYTHONPATH=src python3 -m biucingcli.cli validate` | Must pass with zero errors |
| Human-readable list output | Golden-backed `tests/test_cli.py` coverage for `biucing list` | Must pass |
| JSON list output | Golden-backed `tests/test_cli.py` coverage for `biucing list --json` | Must pass |
| Human-readable info output | Golden-backed `tests/test_cli.py` coverage for `biucing info web-service` | Must pass |
| JSON info output | Golden-backed `tests/test_cli.py` coverage for `biucing info web-service --json` | Must pass |
| Worker info output | Python test coverage for `biucing info worker` and `biucing info worker --json` | Must pass |
| Scriptable create flow | Python test coverage for `--set` and `--non-interactive` | Must pass |
| Preview and manifest flow | Python test coverage for `--dry-run`, `--plan --json`, and `create --json` | Must pass |
| Version surface | `biucing --version` test expectation and version files aligned | Must pass |

## Template Matrix

| Template | Validation status | Repo-level proof | Minimum fresh proof when template changes | Notes |
| --- | --- | --- | --- | --- |
| `frontend` | `real-build-verified` | Python render tests plus metadata validation | Real generation plus Docker verification such as `make test` and `make docker-build` in the generated project | Browser smoke is valuable when frontend behavior or dev-server flow changes |
| `web-service` | `real-build-verified` | Python render tests plus metadata validation | Real generation plus Docker verification such as `make verify` and `make docker-build` in the generated project | Prefer both dev-image and runtime-image proof when Dockerfiles or Makefile flows change |
| `microservice` | `real-build-verified` | Python render tests plus metadata validation | Real generation plus Docker verification such as `make verify`, `make up`, and `make docker-build` in the generated project | Re-check dependency-store variants when compose wiring or protobuf flow changes |
| `worker` | `generated-project-verified` | Python render tests plus metadata validation | Real generation plus `go test ./...` in the generated project, plus Docker packaging sanity when Dockerfiles or Makefile flows change | Keep the proof narrow around background execution rather than HTTP or gRPC behavior |
| `apple` | `generated-project-verified` | Python render tests plus metadata validation | Real generated-project proof such as `make generate`, plus at least one platform `make build` or `make test` path | Re-run both `ios` and `macos` generation when Apple shared scaffolding changes materially |
| `android` | `generated-project-verified` | Python render tests plus metadata validation | Real generated-project proof such as `./gradlew assembleDebug` and, when release/setup changes, `./gradlew assembleRelease` | UI smoke should be re-checked when app structure, test wiring, or doctor/build tooling changes |

## Recommended Command Catalog

These are the default commands to reach for when fresh proof is needed.

| Template | Suggested generation command | Suggested verification commands |
| --- | --- | --- |
| `frontend` | `PYTHONPATH=src python3 -m biucingcli.cli create frontend demo-frontend --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-frontend` | `make test`, `make docker-build` |
| `web-service` | `PYTHONPATH=src python3 -m biucingcli.cli create web-service demo-service --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-service --set module_name=github.com/example/demo-service` | `make verify`, `make docker-build` |
| `microservice` | `PYTHONPATH=src python3 -m biucingcli.cli create microservice demo-microservice --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-microservice --set module_name=github.com/example/demo-microservice --set proto_package=demo.v1` | `make verify`, `make up`, `make docker-build` |
| `worker` | `PYTHONPATH=src python3 -m biucingcli.cli create worker demo-worker --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-worker --set module_name=github.com/example/demo-worker` | `go test ./...`, and when Docker paths changed `make docker-build` |
| `apple` | `PYTHONPATH=src python3 -m biucingcli.cli create apple demo-apple --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-apple --set bundle_identifier=com.example.demoapple` | `make generate`, then `make build` or `make test` |
| `android` | `PYTHONPATH=src python3 -m biucingcli.cli create android demo-android --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-android --set package_name=com.example.demoandroid` | `./gradlew assembleDebug`, and when relevant `./gradlew assembleRelease` |

When using these commands for release evidence, prefer a fresh empty output directory per template so the proof is easy to explain and reproduce.

## Change-Type Guidance

| Change type | Minimum expected verification |
| --- | --- |
| CLI-only change | Release-wide checks |
| Metadata-only change in one template | Release-wide checks plus `biucing info <template>` sanity check and, when semantics changed, fresh proof for that template |
| Shared renderer or placeholder change | Release-wide checks plus fresh proof for at least one Dockerized template and one native template |
| Dockerfile, Compose, or Makefile change in `frontend`, `web-service`, or `microservice` | Release-wide checks plus fresh generated-project Docker verification for the touched template |
| Background-worker template change in `worker` | Release-wide checks plus fresh generated-project `go test ./...` proof and, when Docker paths changed, Docker packaging verification |
| Native project structure change in `apple` or `android` | Release-wide checks plus fresh generated-project verification for the touched native template |
| Version bump and release-doc only | Release-wide checks, changelog/readme/version alignment review |

## Current Evidence Baseline

The current repository metadata declares:

- `frontend`, `web-service`, and `microservice` as `real-build-verified`;
- `worker`, `apple`, and `android` as `generated-project-verified`.

The current repo-level automated baseline includes:

- template rendering coverage in `python3 -m unittest discover -s tests`;
- metadata and placeholder consistency coverage through `biucing validate`;
- golden checks for `list/info` human-readable and JSON output;
- scripted create-flow coverage for `--set` and `--non-interactive`;
- preview and manifest coverage for `--dry-run`, `--plan --json`, and `create --json`;
- generated-project `go test ./...` proof for the new `worker` starter.

## Maintainer Notes

- Prefer evidence that can be rerun with a small number of explicit commands.
- If a release intentionally skips fresh heavy verification for an untouched template, say so explicitly in release notes instead of implying new proof exists.
- When environment issues block a heavy verification run, record whether the failure came from the local machine setup or from the template itself before deciding to delay the release.
- For a concrete version-prep walkthrough, use [0.4.0-release-prep.md](0.4.0-release-prep.md).
