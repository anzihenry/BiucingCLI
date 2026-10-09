---
title: "BiucingCLI 0.9.1"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-091"></a>
# BiucingCLI 0.9.1

[English](notes.en.md)

用 uv 统一 Python 依赖管理、验证、构建和发布，并引入 PyPI 分发。

- 提交覆盖开发/构建依赖的通用 uv.lock。
- 本地与 Python 3.11–3.14 CI 使用 uv sync --locked、uv run --locked。
- 以锁定 setuptools/wheel 构建，上传前精确验证 wheel/sdist。
- 验证包内资源及七模板生成。
- 通过 uv publish 和 PyPI/TestPyPI Trusted Publishing 发布，再从所选索引安装检查。

<a id="install"></a>
## 安装

要求 Python 3.11+，uv 可管理解释器。

```bash
uv tool install biucingcli==0.9.1
biucing --version
biucing list
```

开发和发布见 [uv 工作流](../../guides/development.md)。
