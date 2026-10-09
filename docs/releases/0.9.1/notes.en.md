---
title: "BiucingCLI 0.9.1"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

# BiucingCLI 0.9.1

[中文](notes.md) · Translation of the Chinese primary document.

This release unifies Python dependency management, verification, builds, and
publishing through uv and introduces PyPI distribution.

- Commit a universal uv.lock for development and build dependencies.
- Use uv sync --locked and uv run --locked locally and across Python 3.11–3.14 CI.
- Build with locked setuptools/wheel and verify the exact wheel and sdist before upload.
- Validate installed package resources and generation for all seven templates.
- Publish through uv publish with PyPI/TestPyPI Trusted Publishing, followed by
  installation checks from the selected index.

## Install

Requires Python 3.11 or later; uv can manage the Python interpreter.

```bash
uv tool install biucingcli==0.9.1
biucing --version
biucing list
```

For development and release operations, see [the uv workflow guide](../../guides/development.en.md).
