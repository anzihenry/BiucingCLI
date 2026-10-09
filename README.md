---
title: "BiucingCLI"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# BiucingCLI

[English](README.en.md)

BiucingCLI 是面向独立开发者的项目脚手架生成器，围绕固定技术栈提供七类可复用的项目起点。

当前源码版本为 **0.10.0**。源码版本、历史验收和正式发布是不同记录，详见[版本记录索引](docs/releases/README.md)。

## 安装与快速开始

需要 Python 3.11+；推荐使用 uv 管理安装。

```sh
uv tool install biucingcli==0.10.0
biucing --version
biucing list
biucing info frontend
biucing create frontend my-app --dry-run
biucing create frontend my-app
```

可用模板：`frontend`、`web-service`、`micro-service`、`worker`、`apple`、`android`、`harmonyos`。实际平台工具链与验证边界见模板指南和工程文档。

## 从源码开发

```sh
uv sync --locked
uv run --locked biucing list
uv run --locked python scripts/check-docs
uv run --locked python scripts/run-tests --suite core
```

开发环境使用 Python 3.11，CI 覆盖 3.11–3.14，并固定 uv 0.12.16。

## 文档

- [文档地图](docs/README.md)：按使用、开发、架构、专题和版本查找。
- [使用 BiucingCLI](docs/guides/using.md)、[使用 uv 开发、构建与发布](docs/guides/development.md)、[添加内置模板](docs/guides/template-authoring.md)。
- [工程文档](docs/engineering/README.md)、[当前路线图](docs/planning/roadmap.md)。
- [项目文档组织约定](docs/documentation.md)、[更新日志](CHANGELOG.md)。

## 许可证

当前仓库未提供独立 LICENSE 文件；本次文档整理不新增或推断许可条款。
