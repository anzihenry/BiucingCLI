---
title: "BiucingCLI 发布清单"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-release-checklist"></a>
# BiucingCLI 发布清单

[English](releasing.en.md)

这是 0.x 可重复发布路径，分为仓库产品检查（CLI 行为）、模板证据（七模板最低门槛）、发布各位置检查（版本/变更/标签/发布一致）。配合[验证矩阵](verification-matrix.md)。

<a id="release-surface-map"></a>
## 发布位置地图

每次升版前检查，避免只改一部分。

| 位置 | 文件 | 更新 |
| --- | --- | --- |
| README 目标 | `README.md` | 当前目标和面向用户措辞 |
| 变更记录 | `CHANGELOG.md` | 新版本、日期、用户变化 |
| 包版本 | `pyproject.toml` | `[project].version` |
| 依赖锁 | `uv.lock` | 版本/依赖变化后 uv lock |
| 运行常量 | `src/biucingcli/__init__.py` | `__version__` |
| CLI 预期 | `tests/test_cli.py` | biucing --version 输出 |
| 操作文档 | `docs/guides/releasing.md`、`docs/guides/verification-matrix.md` | 门槛/流程改变时同步 |

历史和架构还查：

- `docs/initiatives/feature/worktree-isolation/design.md`
- `docs/initiatives/feature/worktree-isolation/plan.md`
- `docs/engineering/worktree-isolation-contract.md`
- `docs/releases/0.6.0/validation.md`
- `docs/initiatives/improvement/worktree-hardening/design.md`
- `docs/initiatives/improvement/worktree-hardening/plan.md`
- `docs/releases/0.6.1/validation.md`
- `docs/releases/0.7.0/notes.md`
- `docs/releases/0.7.0/validation.md`
- `docs/releases/0.8.0/notes.md`
- `docs/releases/0.8.0/validation.md`
- `docs/initiatives/improvement/distribution-hardening/plan.md`
- `docs/releases/0.9.0/validation.md`
- `docs/releases/0.10.0/notes.md`
- `docs/releases/0.10.0/validation.md`
- `docs/README.md` 和领域索引。

<a id="1-scope-the-release"></a>
## 1. 确定范围

- 编辑前决定目标版本。
- 确认改动模板。
- 确认仅 CLI 加固、模板内容或仅版本/文档变化。

有模板变化时，打标签前至少获取矩阵要求证据。

<a id="2-update-release-surfaces"></a>
## 2. 同步发布位置

一起更新 README、CHANGELOG、pyproject.toml、uv.lock（uv lock）、__init__.py、test_cli.py，避免版本半更新。

确认 README 目标符合计划、CHANGELOG 对应真实交付、CLI 预期匹配版本。

<a id="3-run-repo-level-product-checks"></a>
## 3. 仓库产品检查

每版本都需通过，即使无模板变化。先 uv sync --locked 安装项目及开发/构建工具。

完整块需 macOS；分组关卡在 Linux/macOS 经 uv 跑 core，macOS 跑 platform 和 --check-make，见[测试](testing.md)。发布前两套件及配置解析均通过。

```bash
uv run --locked python scripts/check-docs
uv run --locked python -m unittest discover -s tests
uv run --locked ruff check --select E4,E7,E9,F src tests scripts
uv run --locked biucing validate
uv run --locked python scripts/verify-distribution
uv run --locked biucing list
uv run --locked biucing list --json
uv run --locked biucing info web-service
uv run --locked biucing info web-service --json
uv run --locked biucing info worker
uv run --locked biucing info worker --json
uv run --locked biucing info harmonyos
```

门槛：

- 单测通过；
- validate 输出 Template validation passed.；
- list/info golden 匹配产品；
- 无新增元数据/占位符冲突；
- 安装 wheel 在源码树外验证/生成全部模板。

建议本地命令：

```bash
uv run --locked python -m unittest discover -s tests
uv run --locked ruff check --select E4,E7,E9,F src tests scripts
uv run --locked biucing validate
uv run --locked python scripts/verify-distribution
uv run --locked biucing list
uv run --locked biucing list --json
uv run --locked biucing info web-service
uv run --locked biucing info web-service --json
uv run --locked biucing info worker
uv run --locked biucing info worker --json
uv run --locked biucing info harmonyos
biucing --version
```

<a id="4-check-scriptability-paths"></a>
## 4. 脚本化检查

预览、脚本、清单属于产品，应显式覆盖。

最低检查：

```bash
uv run --locked biucing create frontend demo-app --output-dir /tmp/biucing-release-check --dry-run
uv run --locked biucing create web-service demo-service --output-dir /tmp/biucing-release-check --module-name github.com/example/demo-service --plan --json
uv run --locked biucing create frontend demo-app --output-dir /tmp/biucing-release-check --non-interactive --set project_name=demo-app
uv run --locked biucing create web-service demo-service --output-dir /tmp/biucing-release-check --non-interactive --set project_name=demo-service --set module_name=github.com/example/demo-service
```

门槛：

- 预览给出预期可读和 JSON plan；
- non-interactive 缺必填时快速失败；
- --set 提供必填值有效；
- 专用选项覆盖 --set；
- create JSON 足够稳定供自动化。

自动 Python 测试为主要证明，命令是发布前维护者快速冒烟。

<a id="5-gather-template-evidence"></a>
## 5. 模板证据

以[矩阵](verification-matrix.md)为准：未改模板通常可复用既有证据加仓库通过；改模板重跑最低生成/Docker 验证；共享渲染器/元数据变化除仓库外至少重测一个 Docker、一个原生。

实际要求：

- frontend/Web/Micro 更新 Docker 证据；
- Worker 更新生成 go test ./...；
- Apple/Android/HarmonyOS 原生证据标 static/doctor/real-build；
- make -n 有用但只静态，不是真实构建；
- 平台结构、manifest、包身份、签名输入、构建设置、依赖文件、原生 build/test 目标变化必须真实构建；
- 仅文档/CLI 元数据/诊断文字且不改原生构建行为时真实构建可选；
- HarmonyOS 保持 static/doctor，工作站配置 SDK 时记录真实构建。

建议原生 worktree 证据：

```bash
# Apple static plus doctor proof
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
make -n build test lint format WORKTREE_ID=beta

# Android static plus doctor proof
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
make -n build test test-ui lint install-debug WORKTREE_ID=beta

# HarmonyOS static plus doctor proof
make worktree-info WORKTREE_ID=alpha
make worktree-debug-identity WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
make -n build clean-worktree WORKTREE_ID=beta
```

需真实构建时记录准确命令，例如 make generate && make build、./gradlew assembleDebug、HarmonyOS make build。SDK 缺失应记录环境限制，不暗示新真实覆盖。

<a id="6-check-worktree-isolation"></a>
## 6. Worktree 隔离

0.6.0 及以后每模板提供共享命令：

```bash
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
make clean-worktree WORKTREE_ID=alpha
```

门槛：

- list JSON 全部 worktree-ready；
- 不同 WORKTREE_ID 渲染不同 Compose/卷名；
- 原生打印本地缓存、配置/签名路径；
- clean-worktree 仅当前 worktree 状态；
- 原生按[矩阵](verification-matrix.md)标证据等级；
- HarmonyOS 含 worktree-debug-identity，配置 DevEco/hvigor 验证元数据钩子前 bundle 改写仍延后。

最近具体证据见[0.10.0](../releases/0.10.0/validation.md)。

<a id="7-review-docs-and-messaging"></a>
## 7. 文档与措辞

打标签前确认 README 对应组合/成熟度，CHANGELOG 讲用户变化；worktree 设计、计划、后续版本计划不落后交付；新校验有可发现文档。

<a id="8-stage-the-release"></a>
## 8. 准备发布

建议：

```bash
git status --short
git add README.md CHANGELOG.md pyproject.toml uv.lock src/biucingcli/__init__.py tests/test_cli.py docs/guides/releasing.md docs/guides/verification-matrix.md
git commit -m "Prepare release X.Y.Z"
git tag -a vX.Y.Z -m "Release X.Y.Z"
```

更多文件需要升版时显式扩大 git add，避免改用 git add .。推送前检查除主动排除文件外工作区干净，附注标签指向正确提交。

<a id="9-publish"></a>
## 9. 发布

首次自动发布前按[uv 工作流](development.md)配置 PyPI/TestPyPI Trusted Publishing。以标签和 target=testpypi 手动演练，再发布 GitHub Release，触发 uv 构建/验证/生产发布：

```bash
git push origin main --follow-tags
# Rehearse Publish with target=testpypi before creating the release below.
gh release create vX.Y.Z --title "BiucingCLI X.Y.Z" --notes-file CHANGELOG.md
```

需人工检查生成说明时，最终检查 CHANGELOG 后再创建 Release，不急着跑一行命令。

<a id="10-record-release-evidence"></a>
## 10. 记录发布证据

发布后在 Release/PR/上线摘要记录日期、通过仓库命令、哪些模板新验证、未阻塞发布的限制，便于下次复用。

<a id="standard-evidence-template"></a>
## 标准证据模板

用于 PR、准备记录或上线摘要：

```md
## Release Evidence

- Target version: `X.Y.Z`
- Verification date: `YYYY-MM-DD`
- Repo-level checks:
  - `uv run --locked python -m unittest discover -s tests`
  - `uv run --locked biucing validate`
  - `uv run --locked biucing list`
  - `uv run --locked biucing list --json`
  - `uv run --locked biucing info web-service`
  - `uv run --locked biucing info web-service --json`
  - `uv run --locked biucing info worker`
  - `uv run --locked biucing info worker --json`
  - `uv run --locked biucing info harmonyos`
- Fresh template proof:
  - `template-name`: `commands run and result`
- Worktree proof:
  - `template-name`: `worktree-info/doctor/config/build-command proof`
  - `native-template-name`: `static/doctor/real-build: commands run and result`
- Version surfaces updated:
  - `README.md`
  - `CHANGELOG.md`
  - `pyproject.toml`
  - `src/biucingcli/__init__.py`
  - `tests/test_cli.py`
- Known limitations:
  - `none` or explicit note
```

<a id="backend-single-host-delivery"></a>
## 后端单机交付

- 运行时/拓扑变化后跑六组件 Docker、生成 golden、worktree 回归。
- verify-distribution --backend-output-dir <new-dir> 保留安装包生成项目，测 Docker 和生产镜像。
- 对隔离 fixture 跑 verify-backend-production，保留扫描/SBOM/签名、TLS、迁移/发布失败、旧 digest 回退、真实隔离恢复。
- 记录镜像/平台、备份数据点、恢复时间；磁盘满测试限可丢弃存储。
- 对照证据检查生成 RUNBOOK、元数据、架构 profile。本地固定密钥签名不证明 GitHub OIDC/GHCR、远端备份保留、跨机可用，需另记。

<a id="backend-kubernetes-reference"></a>
## 后端 Kubernetes 参考

- 六组件各渲染 production/autoscaling，查 schema 和失败守卫。
- 检查安装 wheel/sdist 的可执行 kube 脚本、ConfigMap、策略/Secret 引用、迁移 Job、演练模板；跑生成 manifest 验证。
- 仅 Kustomize/schema 或 fake API 时，cluster/HA 保持 not-run；改变 B27 状态前需流量/数据/恢复证据。
- 复核硬拓扑分散、PDB 范围、HPA replicas 所有权、终止 Pod 连接预算、不可变凭证引用、外部 CNI/Ingress/PKI/PG 契约。
