---
title: "使用 BiucingCLI"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="using-biucingcli"></a>
# 使用 BiucingCLI

[English](using.en.md)

BiucingCLI 为希望围绕稳定个人技术栈使用实用、可复用项目起点的独立开发者生成脚手架。

提供七类内置模板；当前边界见[产品范围](../product/overview.md)。

Apple 默认生成 iOS/macOS/watchOS/tvOS 四个薄壳，使用静态组件 SDK、精确依赖锁、SafeDI 2.0.0、共享 C++20 核心。--platform 选择默认操作平台，见[架构与实现](../engineering/native/apple.md)。

<a id="version"></a>
## 版本

当前仓库目标 0.10.0；变化和迁移见[版本说明](../releases/0.10.0/notes.md)。

```bash
biucing --version
```

最新摘要见[CHANGELOG](../../CHANGELOG.md)。

<a id="installation"></a>
## 安装

通过 uv 隔离安装 PyPI 版本：

```bash
uv tool install biucingcli==0.10.0
biucing --version
```

uv tool upgrade biucingcli 升级，或 uvx --from biucingcli biucing --help 临时运行。

安装当前检出：

```bash
git clone https://github.com/anzihenry/BiucingCLI.git
cd BiucingCLI
uv tool install .
biucing --version
```

贡献者使用 CI 固定 uv 0.12.16。Python 由 .python-version 默认 3.11，CI 测 3.11–3.14；uv 将项目及锁定开发/构建依赖安装进 .venv：

```bash
uv sync --locked
uv run --locked biucing list
uv run --locked python scripts/run-tests --suite core
uv run --locked ruff check --select E4,E7,E9,F src tests scripts
uv run --locked biucing validate
uv run --locked python scripts/verify-distribution
```

core 在 Linux/macOS 无原生 SDK 运行；macOS 工具集成、可选 Android 资源编译见[测试](testing.md)。模块拥有者/兼容边界见[内核](../engineering/kernel-modules.md)，新增模板见[编写](template-authoring.md)。[前端计划](../initiatives/feature/frontend-rendering/plan.md)记录 CSR/SSG/SSR。默认 CSR，可 --set rendering=csr 显式选择；ssg 生成静态内容站，生产构建必需公开 HTTPS SITE_URL 用于 canonical URL/sitemap；ssr 提供请求时 HTML、自托管 Node、私有服务配置、优雅关闭。安装 wheel 三模式与独立 CI/发布关卡见[前端验收](frontend-acceptance.md)。

用 uv add/add --dev/remove 管理依赖，pyproject.toml/uv.lock 一起提交。主动升级用 uv lock --upgrade-package PACKAGE，再 sync --locked 和测试。build 组锁定 setuptools/wheel，从同步环境执行 uv build --no-sources --no-build-isolation；普通隔离 uv build 不使用 uv.lock 的构建依赖版本。

本地构建、TestPyPI 演练、uv publish 自动发布见[开发发布指南](development.md)。

<a id="errors-and-automation"></a>
## 错误与自动化

脚本用 --json 禁止提示。成功 JSON 到 stdout，失败 stdout 空，stderr 一个含 schema_version、ok:false、error.code/message 的对象。[错误契约](../engineering/cli-errors.md)规定退出码和示例。所有 JSON 含 schema_version/generator_version；list/info 暴露验证器、choices、有效数值边界；兼容与字段语义见[JSON 契约](../engineering/json-contract.md)。

<a id="product-direction"></a>
## 产品方向

聚焦维护者实际使用的小模板组合：

- frontend：React Router Framework Mode CSR/SSG/SSR，React 19.3、TS 7、Tailwind 4、shadcn/ui；共享 pnpm 锁、Vitest、Playwright。
- web-service：Go/Gin，Docker 开发/运行。
- micro-service：Go/Protobuf/Buf/Compose，gRPC、OTel、本地依赖编排。
- worker：Go 后台任务，scheduled/oneshot。
- apple：Swift 6.4/SwiftUI/Tuist/SafeDI，四薄壳、版本化静态 XCFramework、精确锁、可移植 C++20；Android/HarmonyOS 适配器仍属后续集成。
- android：Kotlin/Gradle/Compose，fastlane、已提交 wrapper。
- harmonyos：ArkTS/ArkUI，DevEco Studio 项目。

价值在于克制、可读、值得用作真实基础的 starter，而非广泛覆盖生态。

<a id="intended-users"></a>
## 目标用户

- 经常新建项目的独立开发者。
- 希望保持个人栈一致、不反复选择框架的构建者。
- 希望启动时减少配置决策的开发者。

<a id="first-commands"></a>
## 首批命令

```bash
biucing list
biucing info frontend
biucing info web-service
biucing info micro-service
biucing info worker
biucing info apple
biucing info android
biucing info harmonyos
biucing create frontend my-app --dry-run
biucing create web-service user-service --plan --json
biucing create frontend my-app
biucing create web-service user-service
biucing create micro-service user-service
biucing create worker email-worker
biucing create apple my-apple-app
biucing create android my-android-app
biucing create harmonyos my-harmony-app
```

<a id="project-status"></a>
## 项目状态

内部小型模板系统提供七个流程：

- `frontend`
- `web-service`
- `micro-service`
- `worker`
- `apple`
- `android`
- `harmonyos`

成熟度：

- 前端/Web/Micro 有 Docker 开发、验证、运行；前端迁移限制见[渲染计划](../initiatives/feature/frontend-rendering/plan.md)。
- Worker 提供后台定时/单次执行、生成项目 go test ./...、Docker 打包。
- Apple/Android 是一等原生 starter，有更强 doctor、发布指南、结构和多次真实项目验证。
- HarmonyOS 是实验 starter，DevEco 可打开，提供 bootstrap/doctor/lint/build/签名指引。

生成 UX：

- create --dry-run 不写文件，预览解析值、路径、文件数、下一步；
- --plan --json 给脚本可读预览；
- create --json 在真实生成后给清单；
- 非交互失败一次报告全部缺必填值；
- 建目标前规范化/验证名字、包身份、端口、版本、URL、数值界限、枚举。

一致性：

- 元数据暴露验证等级、环境假设、工作流；
- 每模板实现 bootstrap/doctor/lint/test/verify/build/clean/help 公共 Make 契约；
- validate 检查元数据、验证器定义、匹配 .PHONY 目标、家族必需目录项；
- info 直接展示这些字段。

Worktree 优先：

- 七模板都声明 worktree-ready；
- 提供 worktree-info/worktree-doctor/clean-worktree；
- Docker 隔离 Compose 名、卷、镜像、宿主机端口、依赖存储、缓存；
- 提供端口冲突建议与非侵入 worktree-compose-config；
- 原生隔离构建缓存、本地签名/配置、生成输出和平台支持的调试安装身份；
- 原生证据标 static/doctor/real-build，不夸大 SDK 覆盖。

本地 Android：

- 已提交 wrapper；
- 真实 lint、JVM 单测、debug APK/release AAB 和 AAB 完整性通过；
- 工作站在 Biucing_API_35 验证 Compose UI 冒烟。

本地 Apple：

- iOS/macOS 真实 make generate 通过；
- iOS 有移动专用结构，真实 make build 通过；
- macOS 有桌面专用结构，真实 make test 通过。

本地 HarmonyOS：

- 安装 DevEco/SDK 后真实 bootstrap/verify 通过；
- verify 含 doctor/lint/ArkTS-Hypium test/未签名 HAP/指纹；
- release-preflight/release 使用仅本地签名，local.properties 缺失/不完整快速失败。

<a id="documentation"></a>
## 文档

架构、贡献指南、专题、版本见[文档地图](../README.md)。
