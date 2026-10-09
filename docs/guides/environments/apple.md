---
title: "Apple 团队环境标准"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="apple-team-environment-standard"></a>
# Apple 团队环境标准

[English](apple.en.md)

<a id="goal"></a>
## 目标

为中型 Apple 团队定义环境，覆盖 iOS/iPadOS/macOS/watchOS/tvOS、本地入职/开发、工程生成/依赖一致性、测试/构建/签名/交付自动化。以 Apple 原生工具链为核心，Tuist 负责工程生成。

<a id="design-principles"></a>
## 设计原则

使用 Xcode、xcodebuild、Simulator、Instruments 原生路径；统一初始化/日常入口；优先 SwiftPM；生成工程而不手改 .xcodeproj；仓库固定版本；区分本地与 CI；尽量避免临时本地签名设置。

<a id="standard-stack"></a>
## 标准技术栈

<a id="core-apple-toolchain"></a>
### Apple 核心工具链

Xcode 提供 IDE/SDK；生成包最低 Swift 6.4+ 编译器/SwiftPM，验证基线 Xcode 27，`SWIFT_VERSION=6.0` 选择 Swift 6 语言模式；C++20 核心以 SwiftPM/CMake 开发、静态 XCFramework 集成；xcodebuild 构建测试；xcrun 调用 simctl 等；Simulator 执行应用/UI 测试；Instruments 分析诊断。

<a id="environment-and-tool-installation"></a>
### 环境与工具安装

Homebrew 安装工作站工具；mise 固定/激活运行时；需要并行 Xcode 时用 xcodes 安装切换。

<a id="project-generation-and-modularization"></a>
### 工程生成与模块化

Tuist 生成 workspace/project，管理结构和模块约定。

<a id="dependencies"></a>
### 依赖

默认 SwiftPM；仅无法通过 SwiftPM 使用的旧供应商 SDK 允许 CocoaPods。

<a id="automation"></a>
### 自动化

Makefile 提供开发/CI 稳定命令；fastlane 负责发布、签名、截图、TestFlight/App Store。

<a id="tool-responsibilities"></a>
## 工具职责

<a id="xcode"></a>
### Xcode

负责 SDK、签名集成、本地调试/性能/界面编辑、设备/模拟器开发及需要时的 archive 校验；不作为工程结构事实来源，也不是唯一构建测试方式。

<a id="tuist"></a>
### Tuist

负责 workspace/project 生成、模块边界/目标图、共享约定、模块/功能模板生成；不负责包发布、签名策略或替代实际构建执行者 xcodebuild。

<a id="swift-package-manager"></a>
### Swift Package Manager

声明内外依赖，通过 Package.resolved 锁定版本，在合适边界提供内部复用库。

<a id="homebrew"></a>
### Homebrew

从 Brewfile 安装工作站工具；不固定项目运行时。

<a id="mise"></a>
### mise

固定 ruby、node、tuist 等项目运行时，并可重复激活预期版本。

<a id="fastlane"></a>
### fastlane

定义 test、beta、release、签名同步、上传 lane，封装同一套 CI/本地发布逻辑。

<a id="makefile"></a>
### Makefile

公开日常使用的小型稳定命令集。

<a id="standard-repository-layout"></a>
## 标准仓库布局

```text
Apps/{ios,macos,watchos,tvos}/   Tuist manifests, thin app shells and tests
Composition/                   Platform implementations, public factories, SafeDI graph
Dependencies/                  Exact declarations, committed binary lock
Components/                    One source-development package with multiple targets
Shared/Core/                   C++20, C ABI, Apple facade, CMake/SwiftPM tests
fastlane/                      Per-platform archive and delivery
scripts/components             Build, publish, resolve, override and verify SDKs
Tuist.swift / Workspace.swift  Shared project configuration
```

四壳一起生成。`--platform` 选择默认命令平台，`make build PLATFORM=macos` 可单次覆盖。各应用有平台后缀 bundle identifier 和独立生命周期。

<a id="directory-and-dependency-rules"></a>
## 目录与依赖规则

Apps 负责生命周期/根导航/应用配置；Composition 将公开工厂绑定平台实现；Components 用于独立源码开发测试，壳消费静态 XCFramework；Shared/Core 负责可移植规则/状态/C ABI，平台依赖位于外部适配器；Dependencies/components.json 声明精确 SDK，components.lock.json 锁完整闭包/产物清单；.artifacts 是默认不可变本地仓库，可显式设置 COMPONENT_REGISTRY；Dependencies/overrides.local.json 被忽略，CI/Release 拒绝覆盖，锁定二进制缺失/修改则普通构建失败；生成 project/workspace、DI 构造代码、解析二进制均为输出。

SafeDI 2.0.0 CLI 检查组件内部和壳公开构造图。图描述不进入 SDK API，生成构造代码对真实类型编译；无全局 locator 或跨二进制源码扫描。见[架构决策](../../engineering/native/apple.md)。

<a id="required-root-files"></a>
## 必需根文件

<a id="brewfile"></a>
### `Brewfile`

包含 mise、xcodes、swiftlint、swiftformat、fastlane；可选 gh、jq、xcbeautify。

<a id="misetoml"></a>
### `.mise.toml`

至少固定 ruby、node、tuist；只添加实际依赖。

<a id="makefile-1"></a>
### `Makefile`

定义 bootstrap、doctor、generate、clean、build、test、test-ui、lint、format、beta、release。

<a id="scriptsbootstrap"></a>
### `scripts/bootstrap`

检查完整 Xcode 和活动 developer directory；从 Brewfile 安装工具，用 mise 安装固定运行时，安装/激活 Tuist，解析 Swift 包，生成 workspace，执行 doctor。

<a id="standard-initialization-commands"></a>
## 标准初始化命令

新机器：

```bash
xcode-select -p
brew bundle
mise install
make bootstrap
```

日常开发：

```bash
make generate
make build
make test
```

环境验证：

```bash
make doctor
```

发布自动化：

```bash
make beta
make release
```

<a id="standard-make-targets"></a>
## 标准 Make 目标

bootstrap 初始化/修复；doctor 检查 Xcode 选择、模拟器、版本、签名前提；generate 按需 tuist install 再 generate；build 用 xcodebuild 构建主 scheme；test 用 xcodebuild test；test-ui 使用固定模拟器；lint 用 swiftlint；format 用 swiftformat；beta/release 调用对应 fastlane lane。

<a id="xcode-version-policy"></a>
## Xcode 版本策略

每条活跃分支固定主要版本。本地/CI 相同；升级 PR 同步文档和 CI；xcode-select 指向团队认可 Xcode；多版本通过 xcodes/xcode-select 明确切换。

<a id="dependency-policy"></a>
## 依赖策略

组件开发用 SwiftPM，产品壳精确锁二进制 SDK。只有必要 SDK 无法正确用 SwiftPM 时例外用 CocoaPods，仓库记录简短理由。提交 Package.resolved，评审依赖新增，保持 app 薄并提取内部模块。

<a id="module-boundary-policy"></a>
## 模块边界策略

壳负责导航/生命周期/组装/entitlements/环境；feature 负责流程/界面；共享包负责逻辑/基础设施；测试支持负责 fixture、mock、preview。不要全放一个 target。先少量功能模块，在 Components 开发并发布稳定 SDK，再按模块数/构建时间加强边界。

<a id="ci-standard"></a>
## CI 标准

本地同一入口：

```bash
make doctor
make generate
make test
```

发布 CI：

```bash
make beta
make release
```

不能用隐藏脚本替代标准命令；明确 Xcode 版本；可重新生成工程，但输入只能来自仓库。

<a id="code-signing-standard"></a>
## 签名标准

本地尽量自动签名；分发凭据通过 fastlane match 或 Apple 云证书集中管理；lane 负责 archive/upload。避免未记录的手工证书导入导出成为入职常态，或关键逻辑仅在个人机器。

<a id="recommended-adoption-path"></a>
## 建议采用步骤

固定 Xcode 并提交 Brewfile/.mise.toml/Makefile；引入 Tuist 清单；统一 bootstrap/generate/test；依赖迁向 SwiftPM；增加 fastlane beta/release；随规模拆 Apps/Components。

<a id="non-goals"></a>
## 非目标

不定义 Bazel monorepo、全手工 Xcode、多平台前后端总标准，或大型定制构建集群流程。

<a id="default-decision"></a>
## 默认决策

中型团队默认完整 Xcode、Homebrew、mise、Tuist、组件 SwiftPM/壳精确二进制 SDK 清单、Makefile、fastlane，分别负责原生工具、安装、版本固定、工程生成、依赖、命令和交付。
