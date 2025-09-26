# Contributing to BiucingCLI

## Development Workflow

1. **Create an environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```
   Or use Hatch:
   ```bash
   hatch env create
   ```

2. **Run quality checks**
   ```bash
   make lint
   make typecheck
   make test
   ```

3. **Submit changes**
   - Format your code (`make format`).
   - Ensure tests pass with coverage (`make coverage`).
   - Update documentation and changelog when relevant.

## Commit Guidelines

- Use conventional commit messages when possible.
- Keep commits focused and small.
- Reference issues or discussions when applicable.

## Code Style

- Follow `black` formatting and `ruff` linting recommendations.
- Type hints are required; run `make typecheck`.
- Favor descriptive function names and docstrings where helpful.

## Testing

- Add tests for new functionality using `pytest`.
- Use fixtures and Typer's `CliRunner` utilities for CLI testing.

## Reporting Issues

- Provide reproduction steps.
- Include expected vs. actual behavior.
- Share environment details (OS, Python version, installation method).
