---
title: "HarmonyOS 团队环境标准"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="harmonyos-team-environment-standard"></a>
# HarmonyOS 团队环境标准

[English](harmonyos.en.md)

<a id="architecture-baseline-2026-09-24"></a>
## 架构基线（2026-09-24）

当前 starter 使用薄壳、独立版本字节码 HAR、Node-API 和权威 C++20 核心。源码布局、固定工具链和设备边界见 [HarmonyOS 架构](../../engineering/native/harmonyos.md)与[验证证据](../../initiatives/feature/native-components/harmonyos-validation.md)。先运行 components-bootstrap 再 bootstrap。`dependencies/toolchain.json` 为评审版本的权威来源；下述旧布局仅说明保留的壳/配置表面。

<a id="goal"></a>
## 目标

为中型团队定义 ArkTS/ArkUI、本地入职/开发、DevEco Studio/SDK/hvigor 一致性，以及构建、lint 配置、签名和发布交接。采用原生工具链，hvigorw 为 CLI 构建入口。

<a id="design-principles"></a>
## 设计原则

使用 DevEco Studio、SDK、ohpm、hvigorw；统一初始化/日常入口；优先 ArkTS/ArkUI；不提交 SDK 路径/签名；默认验证未签名 HAP；只有真实工作站上的行为稳定后才添加 CLI 测试/发布命令。

<a id="standard-stack"></a>
## 标准技术栈

<a id="core-harmonyos-toolchain"></a>
### HarmonyOS 核心工具链

DevEco Studio 提供 IDE/SDK/签名/预览/设备工作流；SDK 提供 ArkTS 工具链、资源和预览支持；ohpm 安装依赖；hvigorw 构建；ArkTS/ArkUI 为默认语言/声明式 UI。

<a id="environment-and-tool-installation"></a>
### 环境与工具安装

zsh 启动环境导出 DevEco/SDK 路径；mise 固定 Node.js；Makefile 提供受支持命令。macOS 建议环境：

```bash
export PATH="/Applications/DevEco-Studio.app/Contents/tools/ohpm/bin:/Applications/DevEco-Studio.app/Contents/tools/hvigor/bin:$PATH"
export DEVECO_SDK_HOME="/Applications/DevEco-Studio.app/Contents/sdk"
export HOS_SDK_HOME="/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony"
```

<a id="tool-responsibilities"></a>
## 工具职责

<a id="deveco-studio"></a>
### DevEco Studio

负责 SDK、签名设置、设备/模拟器、预览/性能/IDE lint；不是唯一构建方式，不能掩盖 CLI 缺失 SDK 环境。

<a id="hvigorw"></a>
### hvigorw

负责 CLI HAP 打包，执行与 IDE 相同图并暴露结构/兼容错误；不安装 IDE/SDK 或管理签名秘密。

<a id="ohpm"></a>
### ohpm

安装包依赖，保持生成工程依赖可重复。

<a id="makefile"></a>
### Makefile

公开开发命令，保持 CLI 验证简短可重复。

<a id="standard-repository-layout"></a>
## 标准仓库布局

```text
.
├── AppScope/
│   ├── app.json5
│   └── resources/
├── entry/
│   ├── build-profile.json5
│   ├── hvigorfile.ts
│   ├── oh-package.json5
│   └── src/
│       └── main/
│           ├── ets/
│           │   ├── core/
│           │   │   ├── config/
│           │   │   └── designsystem/
│           │   ├── entryability/
│           │   └── pages/
│           ├── module.json5
│           └── resources/
├── docs/
│   └── release-signing.local.properties.example
├── hvigor/
│   └── hvigor-config.json5
├── scripts/
│   ├── bootstrap
│   ├── doctor
│   ├── artifact-info
│   ├── lint
│   ├── release-build
│   ├── release-preflight
│   └── test
├── .mise.toml
├── Makefile
├── build-profile.json5
├── code-linter.json5
├── hvigorfile.ts
├── oh-package-lock.json5
├── oh-package.json5
└── README.md
```

<a id="source-of-truth"></a>
## 事实来源

- build-profile.json5：产品、模块、SDK、模式、签名结构。
- AppScope/app.json5：身份、bundle、标签、图标、版本。
- entry/src/main/module.json5：entry、ability、设备、路由。
- entry/src/main/ets/core/config/AppConfig.ets：生成 bundle/module/ability/version/channel 常量。
- entry/src/main/ets/core/designsystem/Tokens.ets：共享 ArkUI token。
- entry/src/main/ets/pages/：可路由页面，包括设置/配置。
- oh-package.json5、oh-package-lock.json5：包元数据/锁。
- hvigor/hvigor-config.json5：执行设置。
- code-linter.json5：IDE lint 配置。
- Makefile：CLI 命令。
- scripts/doctor：本地就绪检查。

<a id="supported-commands"></a>
## 受支持命令

```bash
make bootstrap
make doctor
make lint
make test
make build
make package
make artifact-info
make verify
make release-preflight
make release
make signing-info
make open
```

签名/分发前默认 gate 为 verify，执行 doctor、lint、test、build、artifact-info。配置好的工作站上 build 必须生成未签名 HAP；release-preflight 不修改工程即可校验签名；仅通过被忽略 local.properties 提供签名后才可 release。

<a id="lint-policy"></a>
## Lint 策略

提交 code-linter.json5，make lint 为静态配置保护：校验 JSON、检查未替换占位符，以及必需配置、页面、设计系统、发布脚本是否存在。完整 ArkTS lint 暂以 IDE 为主，直到 CLI 入口稳定验证。目前 hvigorw tasks 没有 lint，hvigorw lint 不是可用公开 HAP 任务，arkLinter 报生成 entry 不存在该任务。

<a id="testing-policy"></a>
## 测试策略

make test 调用 `hvigorw test --mode module -p module=entry` 执行 ArkTS/Hypium。工程须在 dev 依赖含 @ohos/hypium、在 entry/src/test/List.test.ets 含至少一个 smoke test，并在 bootstrap 未安装 Hypium 时明确失败。

当前发布门槛：生成、bootstrap、doctor、lint、test、build、确认未签名 HAP、artifact-info，提供签名时 release-preflight。

<a id="signing-and-release-policy"></a>
## 签名与发布策略

不提交签名秘密；使用 IDE 设置、本地 local.properties 或 CI 注入。make release 从 local.properties 读取签名，确认 certificate/profile/store 存在，临时在 build-profile.json5 注入 HarmonyOS release 配置，以 buildMode=release 执行 hvigor，结束后恢复原文件。
