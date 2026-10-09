---
title: "Android 模板设计"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="android-template-design"></a>
# Android 模板设计

[English](design.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

保留初版设计背景，不代表当前实现完整状态；2026-09-23 的 Apple 对齐方案见 [Android 壳工程与组件架构](../../../engineering/native/android.md)。

<a id="goal"></a>
## 目标

定义 BiucingCLI android 首个实现目标：生成符合 [Android 团队环境标准](../../../guides/environments/android.md)的 Kotlin 优先 starter，而非所有架构。

<a id="position-in-product-scope"></a>
## 产品范围定位

在 frontend、web-service、apple 系统稳定后推进 Android：环境面更广，需要协调 Gradle、SDK、模拟器、签名；当时仅简单占位替换，初版应小。

<a id="first-version-outcome"></a>
## 初版结果

create 生成 Kotlin 应用、app/feature/core 小型多模块、Wrapper 命令、Makefile/bootstrap/doctor、解释本地准备和构建的 README。初期不生成多 flavor、Play 凭据、复杂生成流水线或数十模块。

<a id="recommended-stack"></a>
## 建议技术栈

Kotlin、AGP、Wrapper、Jetpack Compose、AndroidX/Jetpack、fastlane，符合现代 Kotlin 工作流。

<a id="template-metadata-proposal"></a>
## 模板元数据提案

建议 templates/android/template.json：

```json
{
  "name": "android",
  "description": "Kotlin Android app starter for mid-sized teams",
  "stack": ["Kotlin", "Android", "Gradle", "Jetpack Compose", "fastlane"],
  "variables": [
    { "name": "project_name", "required": true },
    { "name": "display_name", "required": false, "default_from": "project_name" },
    { "name": "package_name", "required": true, "prompt": "Android package name: " },
    { "name": "application_id", "required": false, "default_from": "package_name" },
    { "name": "organization_name", "required": false, "default": "Example Team" },
    { "name": "compile_sdk", "required": false, "default": "35" },
    { "name": "min_sdk", "required": false, "default": "26" },
    { "name": "target_sdk", "required": false, "default": "35" },
    { "name": "version_code", "required": false, "default": "1" },
    { "name": "version_name", "required": false, "default": "1.0.0" },
    { "name": "java_version", "required": false, "default": "17" },
    { "name": "android_namespace", "required": false, "default_from": "package_name" },
    { "name": "kotlin_module_name", "required": false }
  ],
  "next_steps": [
    "make bootstrap",
    "make build",
    "make test",
    "open -a \"Android Studio\" ."
  ]
}
```

<a id="variable-design"></a>
## 变量设计

<a id="core-variables"></a>
### 核心变量

project_name 目标目录；display_name 文档/资源应用名；package_name 如 com.example.app；application_id 默认 package_name。

<a id="sdk-and-version-variables"></a>
### SDK 与版本变量

compile_sdk 为仓库编译 SDK，min_sdk 为最低版本，target_sdk 为行为/政策兼容目标，version_code/version_name 为初始版本，java_version 为构建工具链。

<a id="naming-variables"></a>
### 命名变量

android_namespace 默认 package_name；kotlin_module_name 提供文档/示例 PascalCase 名；organization_name 仅文档/归属。

<a id="placeholder-proposal"></a>
## 占位符提案

保持简单替换约束。新增 APPLICATION_ID、ANDROID_NAMESPACE、COMPILE_SDK、MIN_SDK、TARGET_SDK、VERSION_CODE、VERSION_NAME、JAVA_VERSION、KOTLIN_MODULE_NAME 的双花括号占位符；沿用 PROJECT_NAME、DISPLAY_NAME、PACKAGE_NAME、ORGANIZATION_NAME。

<a id="directory-shape"></a>
## 目录结构

建议输出：

```text
my-android-app/
  README.md
  Brewfile
  .mise.toml
  Makefile
  settings.gradle.kts
  build.gradle.kts
  gradle.properties
  app/
    build.gradle.kts
    src/
      main/
        AndroidManifest.xml
        java/
        res/
      test/
      androidTest/
  core/
    designsystem/
      build.gradle.kts
      src/
    model/
      build.gradle.kts
      src/
  feature/
    home/
      build.gradle.kts
      src/
  fastlane/
    Fastfile
    Appfile
  gradle/
    libs.versions.toml
    wrapper/
  scripts/
    bootstrap
    doctor
    setup-android-sdk
```

<a id="module-plan"></a>
## 模块计划

<a id="app"></a>
### `app`

负责清单、入口、导航根、依赖组装和顶层 Compose 壳。

<a id="featurehome"></a>
### `feature/home`

一个示例功能、屏幕和最低展示逻辑，示范新增功能；证明模式即可，不生成大量猜测性空目录。

<a id="coremodel"></a>
### `core/model`

共享领域模型和应用类型。

<a id="coredesignsystem"></a>
### `core/designsystem`

主题、可复用 Compose 基元、字体/颜色 token，提供有用共享路径而不过度复杂。

<a id="build-file-strategy"></a>
## 构建文件策略

settings.gradle.kts 模块/仓库，根 build.gradle.kts 仅共享插件声明，libs.versions.toml 集中版本，模块 build.gradle.kts 配置 Android/Kotlin。初版避免重型插件、大型 buildSrc、flavor 矩阵、无必要 KSP/kapt。

<a id="readme-expectations"></a>
## README 要求

说明工具、bootstrap、主动刷新 Wrapper 时的 make wrapper、build/test/install-debug、模块位置及事实来源。不声称默认配好发布签名；说明 gradle-wrapper.jar 已提交且刷新后仍须版本管理。

<a id="scripts-and-makefile-expectations"></a>
## 脚本与 Makefile 要求

<a id="makefile"></a>
### `Makefile`

首批 bootstrap、doctor、clean、build、test、test-ui、lint、format、install-debug。

<a id="scriptsbootstrap"></a>
### `scripts/bootstrap`

检查 Java，brew 可用时安装，mise install，检查 ANDROID_HOME/ANDROID_SDK_ROOT、adb/sdkmanager/SDK，运行 doctor。

<a id="scriptsdoctor"></a>
### `scripts/doctor`

检查 Java、SDK、adb、sdkmanager、至少一个模拟器/设备、Wrapper。说明默认提交 Wrapper 并用 ./gradlew；缺失/主动刷新时用本地 gradle 生成再提交。

<a id="testing-shape"></a>
## 测试形态

共享模块一个 JVM 测试，稳定时一个应用仪器/UI smoke test，最低 lint；避免大面积空测试目录。

<a id="cli-impact"></a>
## CLI 影响

增加 Android create 参数、templates.py 映射、类似 Swift 的 kotlin_module_name 默认推导、变量/后续步骤测试。沿用元数据模式，属于低风险扩展。

<a id="recommended-implementation-order"></a>
## 建议实现顺序

<a id="phase-1-metadata-and-placeholder-support"></a>
### 阶段 1：元数据与占位符

扩展映射、CLI 参数/默认值、变量解析与输出测试。

<a id="phase-2-template-skeleton"></a>
### 阶段 2：模板骨架

添加 template.json、Gradle/版本目录/Makefile/脚本、app、feature/home、core/model、core/designsystem。

<a id="phase-3-verification-net"></a>
### 阶段 3：验证网

测试 create 文件集、settings/gradle.properties/manifest 渲染值，以及后续步骤可读一致。

<a id="phase-4-docs-alignment"></a>
### 阶段 4：文档对齐

更新 README、docs/engineering/template-system.md；统一 Wrapper jar 提交政策；Android 从后续转为实施计划时更新 scaffold-baseline/design 和 delivery-history。

<a id="default-decision"></a>
## 默认决策

仅 Kotlin、Compose、Gradle Kotlin DSL、Wrapper 唯一入口、一个 app 加极少共享/功能模块，通过 Brewfile、.mise.toml、Makefile、scripts 初始化。
