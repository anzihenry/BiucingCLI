# BiucingCLI Instruction Template

Use this template to craft project-specific guidance for automation agents (for example, GitHub Copilot or other AI collaborators). Tailor each section to reflect the current goals, tooling, and contributor expectations of the BiucingCLI project.

## 1. Mission Overview
- **Project name**: BiucingCLI
- **Purpose**: Curate full-stack development toolchains via a Typer-based CLI.
- **Primary outcomes for this cycle**:
  - 
- **Deliverables to watch**:
  - 

## 2. Communication Guardrails
- Tone & style preferences:
  - Conversational, concise, and action-oriented.
- Languages:
  - Default to English unless a task explicitly requests another language.
- Naming conventions or terminology to preserve:
  - Retain command names such as `biucing`, `frontend`, `devops`, etc.
- Escalation triggers:
  - 

## 3. Task Checklist Framework
List the recurring steps an automation agent should follow. Mark items done (`[x]`) as progress updates are shared.

```
- [ ] Understand the user’s goal and clarify unknowns.
- [ ] Inspect relevant source files (CLI commands, config, tests).
- [ ] Update or add code/docs/tests per requirements.
- [ ] Run linting, type checks, and tests (`make lint`, `make typecheck`, `make test`).
- [ ] Summarize changes, verification results, and next steps.
```

Add or remove checklist items to match the Deliverables defined above.

## 4. Tooling & Environment Notes
- Python version: 3.14+
- Dependency manager: `uv` (preferred) or editable `pip` install.
- Key commands:
  - `make install`
  - `make lint`
  - `make typecheck`
  - `make test`
  - `uv run biucing ...`
- Configuration files of interest:
  - `config/biucingcli.yaml`
  - `src/biucingcli/data/defaults.yaml`

## 5. Quality Gates
Document the gates an agent must satisfy before marking work as complete.

- Required checks:
  - ✅ Linting passes (`make lint`).
  - ✅ Type checks succeed (`make typecheck`).
  - ✅ Tests pass with coverage goals (`make test` / `uv run pytest`).
- Documentation expectations:
  - Update `README.md`, `CONTRIBUTING.md`, and `CHANGELOG.md` when behavior changes.
- Release hygiene:
  - Note new commands or flags in `CHANGELOG.md`.

## 6. Review Tips
Provide heuristics for reviewers or future agents.

- Prefer incremental PRs that focus on a single command or domain module.
- Ensure CLI help text remains consistent (`typer`) after modifications.
- Confirm new recommendations appear in `defaults.yaml` or config profiles.
- When adding commands, include corresponding tests in `tests/test_cli.py` or dedicated modules.

## 7. Open Questions or Follow-ups
Track items that require clarification or future work.

- [ ] 
- [ ] 

---
Copy this template into `.github/copilot-instructions.md` (or similar workflows) and adapt each section for the current milestone before kicking off a new automation session.
