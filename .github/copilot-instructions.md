# BiucingCLI Automation Playbook

## 1. Mission Overview
- **Project name**: BiucingCLI
- **Purpose**: Deliver a Typer-based CLI that curates end-to-end toolchains for frontend, mobile, desktop, backend, testing, and DevOps engineers.
- **Primary outcomes for this cycle**:
  - Expand and refine command coverage across the different practice areas.
  - Keep configuration-driven recommendations (`config/biucingcli.yaml`, `src/biucingcli/data/defaults.yaml`) accurate and discoverable.
  - Maintain fast feedback loops via linting, type checking, and tests in CI.
- **Deliverables to watch**:
  - CLI command implementations and option surfaces under `src/biucingcli/commands`.
  - Documentation updates (`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`).
  - Configuration and data templates shipped in `config/` and `src/biucingcli/data/`.

## 2. Communication Guardrails
- Tone & style: Conversational, concise, and action-oriented. Lead with next steps instead of restating context.
- Language: Default to English unless a task explicitly requests another language. If the user engages in Chinese, you may respond in kind while keeping technical terms in English.
- Terminology to preserve: Command namespace `biucing`, subcommands like `frontend`, `backend`, `devops`, `configure`, and artifacts such as `defaults.yaml`.
- Escalation triggers: Missing requirements, conflicting instructions, inability to satisfy quality gates, or uncertainty about command behavior.

## 3. Task Checklist Framework
- [ ] Understand the user’s request and capture all explicit/implicit requirements.
- [ ] Inspect the relevant CLI modules, configuration files, tests, and docs.
- [ ] Implement code/doc/test updates that fulfill the request while respecting existing architecture.
- [ ] Run `make lint`, `make typecheck`, and `make test` (or `uv run pytest`) after substantive changes.
- [ ] Summarize modifications, verification results, and next steps for reviewers.

## 4. Tooling & Environment Notes
- Python ≥ 3.14.
- Preferred dependency workflow: `uv sync --extra dev`; alternative: editable install via `pip install -e .[dev]`.
- Helpful commands:
  - `make install`
  - `make lint`
  - `make typecheck`
  - `make test`
  - `uv run biucing [command]` for local smoke tests.
- Key configuration artifacts:
  - `config/biucingcli.yaml`
  - `src/biucingcli/data/defaults.yaml`
  - Typer entry point at `src/biucingcli/cli.py`.

## 5. Quality Gates
- ✅ Linting passes (`make lint`).
- ✅ Static typing clean (`make typecheck`).
- ✅ Tests pass with coverage targets (`make test` or `uv run pytest --cov`).
- Documentation expectations: Update `README.md`, `CONTRIBUTING.md`, and `CHANGELOG.md` whenever user-facing behavior shifts.
- Release hygiene: Record noteworthy CLI changes in `CHANGELOG.md` and ensure new commands expose `--help` descriptions.

## 6. Review Tips
- Keep pull requests scoped to a single command area or feature whenever possible.
- Validate Typer command signatures, option defaults, and Rich output styling.
- Ensure new recommendations are wired into `defaults.yaml` and referenced in tests.
- Cover new CLI flows with `pytest` + `CliRunner` fixtures (`tests/test_cli.py` or dedicated test modules).
- Double-check that updated configuration examples remain parsable YAML.

## 7. Open Questions or Follow-ups
- [ ] Should we introduce scenario-based integration tests (e.g., golden-file outputs) for complex command combinations?
- [ ] Are there additional language localizations or alias commands users are requesting?
