---
title: "使用 uv 开发、构建与发布"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="development-builds-and-publishing-with-uv"></a>
# 使用 uv 开发、构建与发布

[English](development.en.md)

使用与 GitHub 工作流一致的 uv 0.12.16。`.python-version` 为开发选择 Python 3.11，包支持 Python >=3.11；必要时 uv 下载解释器。CI 覆盖默认版本以测试 3.11–3.14。

<a id="dependencies-and-local-checks"></a>
## 依赖与本地检查

```bash
uv sync --locked
uv run --locked biucing --version
uv run --locked ruff check --select E4,E7,E9,F src tests scripts
uv run --locked python scripts/run-tests --suite core
uv run --locked biucing validate
uv run --locked python scripts/verify-distribution
```

uv sync 以 editable 安装项目以及默认 dev/build 组。Ruff、Twine 属于开发工具（Twine 只检查元数据，上传用 uv）；setuptools/wheel 属于 build。这些组不成为 CLI 用户运行依赖。PyYAML/json5 是仅开发使用的配置解析器。core 在 Linux/macOS 无原生工具运行；独立 platform 套件需 macOS 和规定工具链，命令与前提见[测试](testing.md)。

- 运行依赖：`uv add PACKAGE`。
- 开发工具：`uv add --dev PACKAGE`。
- 构建工具：`uv add --group build PACKAGE`。
- 删除开发工具：`uv remove --dev PACKAGE`。
- 主动升级：`uv lock --upgrade-package PACKAGE`，再 `uv sync --locked`。
- 升级 setuptools 时，先同步 build-system.requires 与 build 组固定版本，再刷新锁；同时固定下游隔离 editable/source 安装的构建后端。
- 修改元数据或提升版本后运行 uv lock，并一起提交 pyproject.toml 与 uv.lock。

CI 使用 --locked，让过期锁失败而非静默改变解析。不要手改 uv.lock；.venv 继续忽略。历史发布记录保留当时实际执行命令。

<a id="build-and-verify-the-same-artifacts"></a>
## 构建并验证同一组产物

干净检出中选择新的/空输出目录：

```bash
uv sync --locked
uv build --no-sources --no-build-isolation --out-dir release-dist
uv run --locked python scripts/verify-distribution --dist-dir release-dist
uv publish --dry-run --trusted-publishing never release-dist/*
```

构建使用 uv sync 安装的后端。--no-build-isolation 是刻意选择，因为隔离构建依赖不受项目锁控制。setuptools 仍是 PEP 517 后端，模板打包规则保持有效。默认 uv build 先产出 sdist，再从 sdist 构建 wheel。

验证器要求恰好一个 wheel 和 sdist，用 Twine 查元数据、检查嵌入资源、uv venv 创建隔离环境、uv pip 安装 wheel，在仓库外生成七模板并解析配置。macOS 加 --check-make 验证 Make 入口。没有 --dist-dir 时构建到临时目录，结束删除产物。

uv publish --dry-run 检查上传路径但不发布，也不能证明 PyPI 账户或 OIDC 会授权上传。

<a id="one-time-pypi-setup"></a>
## 首次 PyPI 设置

创建并验证 PyPI 账户、启用双因素，确认控制 biucingcli 名称或名称可用。在账户 Publishing 为新项目添加 pending Trusted Publisher；既有项目用项目 Publishing：

| 字段 | 生产 | 演练 |
| --- | --- | --- |
| 索引 | PyPI | TestPyPI |
| 项目 | `biucingcli` | `biucingcli` |
| 仓库所有者 | `anzihenry` | `anzihenry` |
| 仓库 | `BiucingCLI` | `BiucingCLI` |
| 工作流文件 | `publish.yml` | `publish.yml` |
| 环境 | `pypi` | `testpypi` |

TestPyPI 账户/发布者独立，GitHub 仓库环境需同名。生产可限制仅发布标签并要求维护者评审。只有上传 job 拥有 id-token: write，无需存储 API token 或密码。

<a id="automated-release"></a>
## 自动发布

1. 更新[发布清单](releasing.md)列出的各位置，含锁文件，并提交。
2. 推送包含新工作流和锁的附注 vX.Y.Z 标签。
3. 以该标签和 target=testpypi 手动运行 Publish。
4. 演练成功后发布同标签 GitHub Release；release.published 自动触发生产 PyPI，也支持 target=pypi 手动调度。
5. 确认上传和上传后安装检查均成功。

只接受稳定 vX.Y.Z，标签、包元数据、运行时版本必须一致。上传前八个 Linux/macOS Python 矩阵任务和 macOS platform 都必须通过。macOS Python 3.11 测过的 wheel/sdist 通过 artifact 转移，原样上传；发布 job 从所选索引安装精确版本，查版本、模板列表、验证。

旧 v0.9.0 不含工作流和锁，不移动旧标签；此次迁移使用新标签。若单独发布原 0.9.0，先取回并验证原 GitHub Release 资产。加入工作流不会重放旧 Release 事件。

上传成功而安装失败时，重试前先检查索引。uv 可跳过已上传的相同文件。不能在已发布文件名下重建不同内容；内容改变必须新版本。

<a id="manual-publishing-with-uv"></a>
## 用 uv 手动发布

CI 不可用时先按上文构建和验证，在本地安全设置所选索引 token 到 UV_PUBLISH_TOKEN：

```bash
# TestPyPI (requires a TestPyPI token)
uv publish --index testpypi --trusted-publishing never release-dist/*

# Production (requires a PyPI token)
uv publish --trusted-publishing never release-dist/*
```

不提交凭证。两条命令是替代方案，不应使用同一个 token 连续执行。显式输出路径避免上传 dist 残留旧文件。

实际发布后，用户可 uv tool install biucingcli==X.Y.Z 安装、uv tool upgrade biucingcli 升级，或 uvx --from biucingcli==X.Y.Z biucing --help 临时运行。

<a id="references"></a>
## 参考

- [uv 依赖锁](https://docs.astral.sh/uv/concepts/projects/sync/)
- [uv 构建与发布](https://docs.astral.sh/uv/guides/package/)
- [uv Actions 集成](https://docs.astral.sh/uv/guides/integration/github/)
- [PyPI pending Trusted Publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)

<a id="documentation-checks"></a>
## 文档检查

修改仓库文档或证据引用时运行 uv run --locked python scripts/check-docs。CI documentation job 也执行失败场景测试。范围与语言边界见[组织约定](../documentation.md)。
