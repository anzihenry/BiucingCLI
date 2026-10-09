---
title: "BiucingCLI"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# BiucingCLI

[中文](README.md) · Translation of the Chinese primary document.

BiucingCLI is a project scaffold generator for independent developers, providing seven reusable starters around a consistent technical stack.

The current source version is **0.10.0**. Source versions, historical acceptance and formal publication are separate records; see the [Release record index](docs/releases/README.en.md).

## Install and quick start

Requires Python 3.11+; uv is the recommended installation tool.

```sh
uv tool install biucingcli==0.10.0
biucing --version
biucing list
biucing info frontend
biucing create frontend my-app --dry-run
biucing create frontend my-app
```

Templates: `frontend`, `web-service`, `micro-service`, `worker`, `apple`, `android`, `harmonyos`. See the guides and engineering documents for platform toolchains and verification limits.

## Develop from source

```sh
uv sync --locked
uv run --locked biucing list
uv run --locked python scripts/check-docs
uv run --locked python scripts/run-tests --suite core
```

Development defaults to Python 3.11. CI covers 3.11–3.14 and pins uv 0.12.16.

## Documentation

- [Documentation map](docs/README.en.md): usage, development, architecture, initiatives and versions.
- [Using BiucingCLI](docs/guides/using.en.md), [Development, builds, and publishing with uv](docs/guides/development.en.md), [Adding a built-in template](docs/guides/template-authoring.en.md).
- [Engineering documentation](docs/engineering/README.en.md), [Current roadmap](docs/planning/roadmap.en.md).
- [Project documentation conventions](docs/documentation.en.md), [Changelog](CHANGELOG.en.md).

## License

The repository currently has no standalone LICENSE file. This documentation migration does not introduce or infer license terms.
