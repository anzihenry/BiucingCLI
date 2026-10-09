---
title: "Android 团队环境标准"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="android-team-environment-standard"></a>
# Android 团队环境标准

[English](android.en.md)

<a id="goal"></a>
## 目标

为中型 Android 团队定义开发环境，覆盖 Kotlin 应用、本地入职和日常开发、SDK/模拟器/依赖一致性，以及构建、测试、lint、发布自动化。采用 Android 原生工具链，以 `Gradle` 承担构建和工程自动化。

<a id="design-principles"></a>
## 设计原则

保持 Android Studio、Gradle、SDK、Emulator 原生构建路径；统一初始化和日常自动化入口；应用/模块默认 Kotlin；Gradle Wrapper 是唯一受支持的 Gradle 入口；仓库固定版本；区分本地与 CI；不提交机器 SDK 路径。

<a id="standard-stack"></a>
## 标准技术栈

<a id="core-android-toolchain"></a>
### Android 核心工具链

Android Studio 管理 IDE/SDK；Gradle Wrapper 提供规范 CLI 构建、测试、自动化；Android SDK 包含 platforms、build-tools、platform-tools、emulator；adb 支持设备、安装、logcat 和调试；Emulator 执行本地应用/UI 测试。

<a id="environment-and-tool-installation"></a>
### 环境与工具安装

macOS 用 Homebrew 安装工作站工具；mise 固定和激活 java 等运行时；cmdline-tools 提供 sdkmanager/avdmanager。SDK 根目录中的 `cmdline-tools/latest` 必须是真实目录，不能仅为指向其他工具目录的符号链接。

<a id="project-structure-and-build-logic"></a>
### 工程结构与构建逻辑

Gradle 负责构建图、依赖解析、模块组装和任务；Android Gradle Plugin 提供 Android 集成。

<a id="dependencies"></a>
### 依赖

默认 Maven Central；Android/Jetpack 使用 Google Maven；Version Catalog 集中依赖坐标和版本。

<a id="automation"></a>
### 自动化

Makefile 为开发者/CI 提供稳定入口；fastlane 自动化内测、内部分发、Play Store 和元数据。

<a id="tool-responsibilities"></a>
## 工具职责

<a id="android-studio"></a>
### Android Studio

负责 SDK 安装更新、设备/模拟器调试、布局检查、性能分析和本地工作流；不是唯一构建测试方式，也不是版本或构建逻辑的事实来源。

<a id="gradle-wrapper"></a>
### Gradle Wrapper

负责所有受支持的构建、测试、lint、打包、依赖解析、插件同步执行、模块组装和共享约定；不安装 SDK，也不掩盖应由 doctor 暴露的环境问题。

<a id="android-sdk-and-cmdline-tools"></a>
### Android SDK 与 cmdline-tools

负责平台、build-tools、platform-tools、模拟器镜像和许可，通过 sdkmanager、avdmanager、adb 管理；不固定 Java/Gradle 或定义构建逻辑。

<a id="homebrew"></a>
### Homebrew

从 Brewfile 安装工作站工具；不固定项目运行时。

<a id="mise"></a>
### mise

固定项目 java 等运行时并可重复地激活预期版本。

<a id="fastlane"></a>
### fastlane

定义内部、beta、release lane，自动化 Play 元数据、截图和部署；封装发布逻辑，让 CI 与本地用相同命令。

<a id="makefile"></a>
### Makefile

公开团队日常使用的小型稳定命令集。

<a id="standard-repository-layout"></a>
## 标准仓库布局

```text
.
├── app/
│   ├── build.gradle.kts
│   ├── src/
│   │   ├── main/
│   │   │   ├── AndroidManifest.xml
│   │   │   ├── java/
│   │   │   └── res/
│   │   ├── test/
│   │   └── androidTest/
├── core/
│   ├── designsystem/
│   ├── model/
│   ├── network/
│   └── testing/
├── feature/
│   ├── home/
│   ├── profile/
│   └── settings/
├── gradle/
│   ├── libs.versions.toml
│   └── wrapper/
├── build-logic/
│   └── convention/
├── fastlane/
│   ├── Fastfile
│   └── Appfile
├── scripts/
│   ├── bootstrap
│   ├── doctor
│   ├── setup-android-sdk
│   └── ci/
├── .mise.toml
├── Brewfile
├── Makefile
├── settings.gradle.kts
├── build.gradle.kts
├── gradle.properties
└── README.md
```

<a id="directory-rules"></a>
## 目录规则

<a id="app"></a>
### `app/`

安装应用模块：`build.gradle.kts` 为构建配置，`src/main/AndroidManifest.xml` 为清单，`src/main/java/` 为壳、导航及组装根，`src/main/res/` 为资源，`src/test/` 为 JVM 测试，`src/androidTest/` 为仪器/UI 测试。仅为启动、组装界面或声明 Android 组件而存在的代码归这里。

<a id="feature"></a>
### `feature/`

用户功能模块，包含界面流程、展示逻辑、功能状态和 UI。项目超出小型 starter 后，不应继续把功能堆到 app。

<a id="core"></a>
### `core/`

可复用设计系统、领域模型、网络、持久化和测试支持。可跨功能共享且不依赖壳的模块优先归这里。

<a id="build-logic"></a>
### `build-logic/`

共享 Gradle 约定插件和配置代码；提取重复逻辑，避免各模块复制插件和 Android 配置。

<a id="gradle"></a>
### `gradle/`

Wrapper 文件和版本目录必须提交；不依赖全局 gradle。

<a id="fastlane-1"></a>
### `fastlane/`

仅交付自动化。构建编排归 Makefile/scripts，发布/Play 编排归 fastlane。

<a id="scripts"></a>
### `scripts/`

初始化、环境检查、CI 包装；可调用 brew、mise、sdkmanager、adb、./gradlew，避免重复 Fastfile、Makefile 或 Gradle 任务中的逻辑。

<a id="source-of-truth"></a>
## 事实来源

Brewfile 定义工作站工具，.mise.toml 定义运行时，settings.gradle.kts 定义模块图和插件仓库，build.gradle.kts 定义根构建约定，gradle/libs.versions.toml 定义依赖/插件版本，gradle.properties 定义共享设置，Makefile 定义开发命令，fastlane/Fastfile 定义交付 lane。本地 SDK 路径、IDE 缓存和生成物不作为事实来源。

<a id="required-root-files"></a>
## 必需根文件

<a id="brewfile"></a>
### `Brewfile`

包含 mise、android-platform-tools、openjdk@17、fastlane；可选 gh、jq。

<a id="misetoml"></a>
### `.mise.toml`

至少固定 java；仅在仓库实际依赖时添加其他工具。

<a id="gradlelibsversionstoml"></a>
### `gradle/libs.versions.toml`

集中 AGP、Kotlin、Jetpack 和测试/lint 库版本。

<a id="makefile-1"></a>
### `Makefile`

定义 bootstrap、doctor、clean、build、test、test-ui、lint、format、install-debug、release-doctor、archive、beta、release。

<a id="scriptsbootstrap"></a>
### `scripts/bootstrap`

1. 确认 java 存在并匹配固定版本。
2. 从 Brewfile 安装 Homebrew 依赖。
3. 用 mise 安装固定运行时。
4. 检查 ANDROID_HOME 或 ANDROID_SDK_ROOT。
5. 检查 cmdline-tools、platform-tools 和所需 SDK 包。
6. 工作流允许时接受许可。
7. 执行基础 doctor。
8. 预热 Wrapper 和依赖解析。

<a id="local-repair-notes"></a>
## 本地修复记录

维护机验收时，sdkmanager/avdmanager 可用，但 `~/Library/Android/sdk/cmdline-tools` 最初通过符号链接指向 SDK 外。即使镜像存在，`avdmanager create avd` 仍报 `Package path is not valid. Valid system image paths are: null`。将 latest 复制为 SDK 内真实目录后恢复包注册行为。Gradle 可用，但受限环境可能需要可写的 GRADLE_USER_HOME。最终验证健康 AVD：`Biucing_API_35`。

工作站检查：`sdkmanager --licenses`、`avdmanager list avd`、`emulator -list-avds`、`./gradlew help`。目标状态：环境变量指向有效 SDK；latest/bin 下真实存在 sdkmanager/avdmanager；至少一个可启动 AVD；工程通过提交的 Wrapper 构建。

<a id="standard-initialization-commands"></a>
## 标准初始化命令

新机器：

```bash
brew bundle
mise install
make bootstrap
```

日常开发：

```bash
make build
make test
```

环境校验：

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

`make bootstrap` 初始化/修复；doctor 检查 Java、SDK、adb、模拟器和版本；clean 调用 `./gradlew clean`；build 调用 assembleDebug 或团队聚合任务；test 调用 `./gradlew test`；test-ui 调用 connectedDebugAndroidTest；lint 调用 `./gradlew lint`；format 使用 ktlintFormat/spotlessApply 等；install-debug 安装到活动设备；beta/release 调用对应 fastlane lane。

<a id="android-studio-version-policy"></a>
## Android Studio 版本策略

每条活跃分支固定主要 Android Studio/AGP 组合。本地和 CI 使用兼容 Java/AGP；Studio 升级须通过 PR 同步文档和 CI；Wrapper/AGP 升级按构建系统变更评审。

<a id="sdk-version-policy"></a>
## SDK 版本策略

固定 compileSdk、每条应用线的 minSdk 策略，以及按计划跟进平台要求的 targetSdk。变更须明确记录；CI/本地 UI 镜像匹配仓库预期；机器可安装额外包，但所需包须文档化并由 doctor 检查。

<a id="dependency-policy"></a>
## 依赖策略

新增依赖经过版本目录；优先 Jetpack 和维护良好的 Kotlin 库；像代码一样评审；保持 app 薄并提取共享逻辑；避免无明确理由并用重复框架。

<a id="module-boundary-policy"></a>
## 模块边界策略

壳负责 Application、导航根、依赖组装和清单；feature 负责流程/屏幕；core 负责共享设计、领域、数据和工具；测试支持负责 fixture、fake、仪器助手。不要全放一个 app。先以 app 加少量 feature/core 起步，提取重复逻辑，再按模块数量增加构建约定。

<a id="testing-standard"></a>
## 测试标准

三层：业务/ViewModel 的 JVM 测试、Android 集成仪器测试、仅关键用户流程的 UI 测试。优先快速本地测试，UI 测试聚焦且稳定，本地/CI 命令一致。

<a id="ci-standard"></a>
## CI 标准

使用本地同一入口：

```bash
make doctor
make build
make test
```

发布 CI：

```bash
make beta
make release
```

不能用隐藏的一次性脚本替代标准命令；明确准备 Java/SDK；使用提交的 Wrapper。

<a id="signing-and-release-standard"></a>
## 签名与发布标准

本地仅 Debug 签名；发布 keystore/Play 凭据由 CI 或安全存储集中管理；lane 负责 bundle、签名、分发。避免将未记录的手工 keystore 分享作为入职常规流程，或将关键签名逻辑留在个人机器。

<a id="recommended-adoption-path"></a>
## 建议采用步骤

1. 用 Brewfile、.mise.toml、Makefile 固定 Java/Android 预期。
2. 统一 ./gradlew 入口。
3. 添加 bootstrap/doctor。
4. 集中版本目录。
5. 添加 fastlane beta/release。
6. 随规模拆分 app、feature、core、build-logic。

<a id="non-goals"></a>
## 非目标

不定义 Flutter/React Native、所有客户端平台 monorepo 或大型定制构建集群标准；小 starter 无须从第一天过度模块化。

<a id="default-decision"></a>
## 默认决策

中型团队默认 Android Studio、macOS Homebrew、mise、Gradle Wrapper、SDK/cmdline-tools、Version Catalog、Makefile、fastlane，分别承担 IDE、工具安装、运行时固定、构建入口、设备管理、依赖版本、稳定命令、发布自动化。

<a id="binary-component-architecture-2026-09-23"></a>
## 二进制组件架构（2026-09-23）

当前模板将产品 Gradle 构建（app）与 SDK 开发（components，源码为 core/feature）分开，产品消费锁定 Maven AAR。Dagger 2.52 分别生成内部/壳图；共享 C++20 核心经 Kotlin/JNI 使用 NDK 28.2.13676358/CMake 3.22.1。首次产品构建前运行 `make components-bootstrap`。边界、锁定、本地二进制覆盖和验证见 [Android 壳/组件架构](../../engineering/native/android.md)。
