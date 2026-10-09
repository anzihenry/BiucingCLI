---
title: "BiucingCLI 0.6.0 发布准备"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-060-release-prep"></a>
# BiucingCLI 0.6.0 发布准备

[English](validation.en.md)

记录 `0.6.0` worktree 优先版本的证据。

目标：`0.6.0`
验证日期：`2026-07-19`
证据目录：`/tmp/biucing-phase-e.u3FQny`

<a id="release-theme"></a>
## 发布主题

全部已交付模板支持 worktree，版本声明为：

> 每个生成 starter 都可在并行 Git worktree 中开发、测试、打包，不发生意外的跨 worktree 干扰。

<a id="scope"></a>
## 范围

覆盖模板：

- `frontend`
- `web-service`
- `microservice`
- `worker`
- `apple`
- `android`
- `harmonyos`

相对 `0.5.0` 的变化：

- 共享隔离契约和碰撞审计；
- 每个 template.json 新增 worktree 元数据；
- list/info/JSON/validate 暴露相关元数据；
- Docker 优先隔离 Compose 名称、卷、镜像标签、宿主机端口、依赖存储与缓存；
- 原生隔离缓存、签名/本地配置、生成输出及调试应用身份钩子；
- 每个 starter 提供 `make worktree-info`、`make worktree-doctor`、`make clean-worktree`。

<a id="repo-level-evidence"></a>
## 仓库证据

阶段 E 中通过：

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
```

预期结果：

- `Ran 35 tests ... OK`
- `Template validation passed.`

<a id="generated-project-evidence"></a>
## 生成项目证据

在 `/tmp/biucing-phase-e.u3FQny` 新建项目。

生成命令：

```bash
PYTHONPATH=src python3 -m biucingcli.cli create frontend pe-frontend --output-dir /tmp/biucing-phase-e.u3FQny --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create web-service pe-web --output-dir /tmp/biucing-phase-e.u3FQny --module-name github.com/example/pe-web --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create microservice pe-micro --output-dir /tmp/biucing-phase-e.u3FQny --module-name github.com/example/pe-micro --proto-package pe.micro.v1 --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create worker pe-worker --output-dir /tmp/biucing-phase-e.u3FQny --module-name github.com/example/pe-worker --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create apple pe-apple --output-dir /tmp/biucing-phase-e.u3FQny --platform ios --bundle-identifier com.example.peapple --organization-name Example --development-team ABCDE12345
PYTHONPATH=src python3 -m biucingcli.cli create android pe-android --output-dir /tmp/biucing-phase-e.u3FQny --package-name com.example.peandroid --application-id com.example.peandroid.app --android-namespace com.example.peandroid
PYTHONPATH=src python3 -m biucingcli.cli create harmonyos pe-harmony --output-dir /tmp/biucing-phase-e.u3FQny --bundle-name com.example.peharmony --harmony-module-name entry --ability-name EntryAbility
```

七个命令全部成功。

<a id="worktree-evidence"></a>
## Worktree 证据

<a id="docker-first-templates"></a>
### Docker 优先模板

`frontend`：

```bash
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
COMPOSE_PROJECT_NAME=pe-frontend-alpha DEV_HOST_PORT=5174 docker compose -f compose.dev.yaml config
```

观察到：

- slug：`pe-frontend-alpha`；
- Compose 项目：`pe-frontend-alpha`；
- 镜像：`pe-frontend-alpha:dev`；
- 卷名前缀：`pe-frontend-alpha_`；
- 开发宿主机端口覆盖渲染为 `5174`。

`web-service`：

```bash
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
COMPOSE_PROJECT_NAME=pe-web-alpha HOST_PORT=18081 docker compose -f compose.dev.yaml config
```

观察到：

- slug：`pe-web-alpha`；
- Compose 项目：`pe-web-alpha`；
- 镜像：`pe-web-alpha:dev`；
- 卷名前缀：`pe-web-alpha_`；
- HTTP 宿主机端口覆盖为 `18081`。

`microservice`：

```bash
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
COMPOSE_PROJECT_NAME=pe-micro-alpha HOST_HTTP_PORT=18080 HOST_GRPC_PORT=19090 HOST_DEPENDENCY_STORE_PORT=15432 HOST_OTEL_GRPC_PORT=14317 HOST_OTEL_HTTP_PORT=14318 docker compose -f compose.dev.yaml config
```

观察到：

- slug：`pe-micro-alpha`；
- Compose 项目：`pe-micro-alpha`；
- 镜像：`pe-micro-alpha:dev`；
- 卷名前缀：`pe-micro-alpha_`；
- HTTP、gRPC、Postgres、OTel 宿主机端口按指定覆盖。

`worker`：

```bash
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
COMPOSE_PROJECT_NAME=pe-worker-alpha DEV_IMAGE=pe-worker-alpha-dev DEV_TAG=dev docker compose -f compose.dev.yaml config
```

观察到：

- slug：`pe-worker-alpha`；
- Compose 项目：`pe-worker-alpha`；
- 开发镜像：`pe-worker-alpha-dev:dev`；
- 运行镜像：`pe-worker-alpha:dev`；
- 卷名前缀：`pe-worker-alpha_`；
- 默认不发布宿主机端口。

<a id="native-templates"></a>
### 原生模板

`apple`：

```bash
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
make -n build test lint format WORKTREE_ID=beta
```

观察到：

- DerivedData 位于 `DerivedData/alpha`；
- Tuist HOME 和 XDG cache/state/config/tmp 位于 `.cache/tuist/alpha/`；
- 调试 bundle ID 为 `com.example.peapple.alpha`；
- 构建/测试 dry-run 包含 `-derivedDataPath .../DerivedData/beta`；
- lint/format 缓存位于 beta worktree 身份下。

`android`：

```bash
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
make -n build test test-ui lint install-debug WORKTREE_ID=beta
```

观察到：

- Gradle 用户目录在 `.gradle/worktree/alpha`；
- 调试 application ID 为 `com.example.peandroid.app.debug.alpha`；
- dry-run 设置 `GRADLE_USER_HOME=.../.gradle/worktree/beta`；
- dry-run 传 `-Dorg.gradle.project.biucing.worktree.applicationIdSuffix=.debug.beta`。

`harmonyos`：

```bash
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
make -n build clean-worktree WORKTREE_ID=beta
```

观察到：

- hvigor home 位于 `.hvigor/worktree/alpha`；
- ohpm home 位于 `.ohpm/worktree/alpha`；
- 请求的调试 bundleName 为 `com.example.peharmony.alpha`；
- dry-run 传 `-p biucing.worktree.id=beta`、`-p biucing.worktree.bundleSuffix=.beta`；
- 清理仅针对 worktree 本地 hvigor/ohpm 路径、模块构建输出、build、`.biucing/release`。

<a id="known-limitations"></a>
## 已知限制

- 阶段 E 使用 Compose config 检查，没有执行重型镜像构建。
- 原生检查使用诊断和 dry-run 展开，没有真实 Xcode/Gradle/hvigor 构建。
- HarmonyOS 默认保持 AppScope/app.json5 稳定；请求后缀通过构建属性传入，只有本地 DevEco 工具链能可靠支持时才应接入 bundle 改写。

原记录认为这些限制不阻塞 worktree 优先版本声明：仓库与生成项目冒烟验证隔离契约表面，不依赖工作站 SDK 可用性。
