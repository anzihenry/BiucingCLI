UV ?= uv
UV_PROJECT_ENVIRONMENT ?= .venv
export UV_PROJECT_ENVIRONMENT

.PHONY: install format lint typecheck test coverage clean

install:
	$(UV) sync --extra dev

format:
	$(UV) run black src tests

lint:
	$(UV) run ruff check src tests

typecheck:
	$(UV) run mypy src

test:
	$(UV) run pytest --cov=biucingcli --cov-report=term-missing

coverage:
	$(UV) run pytest --cov=biucingcli --cov-report=html

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov
