---
title: "BiucingCLI 0.6.1 发布准备"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-061-release-prep"></a>
# BiucingCLI 0.6.1 发布准备

[English](validation.en.md)

记录 worktree 隔离加固版本的准备证据。

目标：`0.6.1`
验证日期：`2026-07-20`
证据目录：`/tmp/biucing-061-phase-g.qXARfS`

<a id="scope"></a>
## 范围

加固 `0.6.0` 的 worktree 支持：

- 七模板共享 WORKTREE_ROOT、WORKTREE_LABEL、WORKTREE_ID、WORKTREE_SLUG 模型；
- Docker 启动前端口冲突建议；
- Compose 模板提供 `make worktree-compose-config`；
- 原生证据区分 static、doctor、real-build；
- HarmonyOS 明确只读调试身份诊断，bundle 改写延后。

<a id="repo-level-evidence"></a>
## 仓库证据

通过以下检查：

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli list --json
```

结果：

- 单元测试 35 项通过；
- 模板验证：`Template validation passed.`；
- list JSON：七模板均为 `worktree.support_level = worktree-ready`。

<a id="generated-projects"></a>
## 生成项目

七模板均生成到新临时目录。

```bash
PYTHONPATH=src python3 -m biucingcli.cli create frontend hard-frontend --output-dir /tmp/biucing-061-phase-g.qXARfS --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create web-service hard-service --output-dir /tmp/biucing-061-phase-g.qXARfS --module-name github.com/example/hard-service --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create microservice hard-micro --output-dir /tmp/biucing-061-phase-g.qXARfS --module-name github.com/example/hard-micro --proto-package hard.micro.v1 --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create worker hard-worker --output-dir /tmp/biucing-061-phase-g.qXARfS --module-name github.com/example/hard-worker --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create apple hard-apple --output-dir /tmp/biucing-061-phase-g.qXARfS --platform ios --bundle-identifier com.example.hardapple --organization-name Example --development-team ABCDE12345 --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create android hard-android --output-dir /tmp/biucing-061-phase-g.qXARfS --package-name com.example.hardandroid --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create harmonyos hard-harmony --output-dir /tmp/biucing-061-phase-g.qXARfS --bundle-name com.example.hardharmony --harmony-module-name entry --ability-name EntryAbility --non-interactive
```

全部命令成功。

<a id="docker-first-evidence"></a>
## Docker 优先证据

使用显式 worktree ID，并在适用时覆盖默认发布端口。

| 模板 | 命令 | 证据 |
| --- | --- | --- |
| `frontend` | `make worktree-info WORKTREE_ID=alpha`; `make worktree-doctor WORKTREE_ID=alpha DEV_HOST_PORT=15173 HOST_PORT=18087`; `make worktree-compose-config WORKTREE_ID=alpha DEV_HOST_PORT=15173 HOST_PORT=18087` | Compose 渲染 `name: hard-frontend-alpha`、端口 `15173`、`hard-frontend-alpha_frontend-node-modules` 等卷 |
| `web-service` | `make worktree-info WORKTREE_ID=alpha`; `make worktree-doctor WORKTREE_ID=alpha HOST_PORT=18088`; `make worktree-compose-config WORKTREE_ID=alpha HOST_PORT=18088` | 通过 `COMPOSE_PROJECT_NAME=hard-service-alpha` 渲染 worktree 专属名称 |
| `microservice` | `make worktree-info WORKTREE_ID=alpha`; `make worktree-doctor WORKTREE_ID=alpha HOST_HTTP_PORT=18089 HOST_GRPC_PORT=19089 HOST_DEPENDENCY_STORE_PORT=15439 HOST_OTEL_GRPC_PORT=14319 HOST_OTEL_HTTP_PORT=14320`; `make worktree-compose-config WORKTREE_ID=alpha ...` | Doctor 报告 `Worktree slug: hard-micro-alpha`、非默认 HTTP/gRPC/依赖/OTel 端口及 `Compose config check: make worktree-compose-config` |
| `worker` | `make worktree-info WORKTREE_ID=alpha`; `make worktree-doctor WORKTREE_ID=alpha`; `make worktree-compose-config WORKTREE_ID=alpha` | Compose 渲染 `name: hard-worker-alpha`、镜像 `hard-worker-alpha-dev:dev`、卷 `hard-worker-alpha_worker-go-build-cache` |

只渲染配置，不启动容器。

<a id="native-evidence"></a>
## 原生证据

证据按等级标记，本阶段不宣称原生真实构建。

| 模板 | 等级 | 命令 | 结果 |
| --- | --- | --- | --- |
| `apple` | static 加生成 doctor | `make worktree-info WORKTREE_ID=alpha`; `make worktree-doctor WORKTREE_ID=alpha`; `make -n build test lint format WORKTREE_ID=beta` | 使用 `DerivedData/beta`、`.swiftlint-cache/beta`、`.swiftformat.cache/beta` |
| `android` | static 加生成 doctor | `make worktree-info WORKTREE_ID=alpha`; `make worktree-doctor WORKTREE_ID=alpha`; `make -n build test test-ui lint install-debug WORKTREE_ID=beta` | 使用 `.gradle/worktree/beta`、`biucing.worktree.applicationIdSuffix=.debug.beta` |
| `harmonyos` | static 加生成 doctor | `make worktree-info WORKTREE_ID=alpha`; `make worktree-debug-identity WORKTREE_ID=alpha`; `make worktree-doctor WORKTREE_ID=alpha`; `make -n build clean-worktree WORKTREE_ID=beta` | `com.example.hardharmony.alpha` 仅为诊断，bundleName 仍以 AppScope/app.json5 为准 |

<a id="known-limitations"></a>
## 已知限制

- 不启动 Docker，仅渲染 Compose 做非侵入隔离验证。
- 原生为 static 加 doctor，不是 SDK 真实构建。
- HarmonyOS 每 worktree bundle 改写延后，直到配置好的工作站验证 DevEco/hvigor 元数据钩子。

<a id="release-operation"></a>
## 发布操作

正式步骤：

```bash
git commit -m "chore: release 0.6.1"
git tag -a v0.6.1 -m "Release 0.6.1"
git push origin main
git push origin v0.6.1
gh release create v0.6.1 --title "BiucingCLI 0.6.1" --notes-file /tmp/biucing-0.6.1-release-notes.md
```

版本修改提交推送、GitHub 上存在附注标签、Release 指向 v0.6.1 后才就绪。
