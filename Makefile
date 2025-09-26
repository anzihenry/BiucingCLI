PYTHON ?= python3

.PHONY: install format lint typecheck test coverage clean

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .
	$(PYTHON) -m pip install black ruff mypy pytest pytest-cov

format:
	hatch run format

lint:
	hatch run lint

typecheck:
	hatch run typer-check

test:
	hatch run test

coverage:
	hatch run test --cov-report=html

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov
