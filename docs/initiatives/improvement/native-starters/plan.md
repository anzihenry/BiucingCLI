---
title: "Apple 与 Android 模板路线"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="apple-and-android-template-roadmap"></a>
# Apple 与 Android 模板路线

[English](plan.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

把 backlog 拆为聚焦提交，完善操作、首跑、验证测试，并保持小片段可交付。

<a id="principles"></a>
## 原则

每次一个工作流；模板/README/按需 CLI 步骤/测试一起更新；真实命令验证；原生流程虽异但质量一致。

<a id="p0"></a>
## P0

<a id="1-android-add-a-real-formatting-workflow"></a>
### 1. Android：真实格式化

提交 android: add real formatting workflow with spotless。已有 format 空位却无实际工作，低成本高价值。

- [ ] 选择 spotless + ktlint 或 ktfmt。
- [ ] 加插件/配置。
- [ ] spotlessApply 接 make format。
- [ ] 加 CI check。
- [ ] 更新 README。
- [ ] 生成测试断言。
- [ ] 真实工程格式化。

目标：生成工程任务成功。

<a id="2-apple-add-default-swiftlint-and-swiftformat-configuration"></a>
### 2. Apple：默认 lint/format 配置

提交 apple: add swiftlint and swiftformat starter config。已有命令须真实配置和可预测默认。

- [ ] 加 .swiftlint.yml。
- [ ] 加 .swiftformat。
- [ ] 确认命令使用。
- [ ] 初始化/文档统一安装。
- [ ] 更新 README。
- [ ] 测试配置/命令。
- [ ] 真实 lint/format。

目标：无缺配置意外。

<a id="3-android-improve-doctor-checks-for-sdk-jdk-and-emulator-readiness"></a>
### 3. Android：SDK/JDK/模拟器 doctor

提交 android: improve doctor checks for sdk jdk and emulator。环境漂移浪费时间，应在 Gradle 失败前检查。

- [ ] JAVA_HOME/活动 JDK。
- [ ] SDK 根。
- [ ] cmdline-tools/latest。
- [ ] adb。
- [ ] 模拟器/设备路径。
- [ ] 明确修复步骤。
- [ ] README 范围。
- [ ] 输出测试。
- [ ] 实工程 doctor。

目标：明确可预测报缺依赖。

<a id="4-apple-improve-doctor-checks-for-xcode-tuist-fastlane-and-simulator-readiness"></a>
### 4. Apple：Xcode/Tuist/fastlane/模拟器 doctor

提交 apple: improve doctor checks for xcode tuist and simulators。原生环境决定工作流，降低首跑脆弱性。

- [ ] xcodebuild/版本。
- [ ] tuist。
- [ ] fastlane。
- [ ] simctl 可见 runtime。
- [ ] 缺工具错误。
- [ ] README。
- [ ] 行为/脚本测试。
- [ ] 实工程 doctor。

目标：generate/test 前暴露环境问题。

<a id="p1"></a>
## P1

<a id="5-android-add-a-minimal-compose-ui-smoke-test-path"></a>
### 5. Android：Compose UI smoke

提交 android: add compose ui smoke test starter。已有 test-ui 应有真实示例。

- [ ] 最小 connectedDebugAndroidTest。
- [ ] 测现有屏幕。
- [ ] 测试依赖。
- [ ] README 设备前提。
- [ ] 文件/连接测试。
- [ ] 可行时实 UI 验证。

目标：真实路径而非占位。

<a id="6-apple-expand-starter-test-coverage-with-mocks-or-view-model-examples"></a>
### 6. Apple：mock/ViewModel 测试

提交 apple: expand starter test coverage with mocks。已有基础测试，补真实场景。

- [ ] 状态/ViewModel 示例。
- [ ] 适当 mock/service 示例。
- [ ] 小且易理解。
- [ ] README 结构。
- [ ] 文件断言。
- [ ] 实测试。

目标：超出平凡 smoke。

<a id="7-android-extend-the-modular-project-skeleton"></a>
### 7. Android：模块扩展

提交 android: extend modular project skeleton。现结构仍偏 demo，补生产层。

- [ ] core/network 或等价。
- [ ] core/testing 或等价。
- [ ] 考虑第二 feature。
- [ ] settings/Gradle 一致。
- [ ] README。
- [ ] 文件测试。
- [ ] 实构建。

目标：接近中型应用。

<a id="8-apple-specialize-structure-for-ios-and-macos-first"></a>
### 8. Apple：先专化 iOS/macOS

提交 apple: specialize starter structure for ios and macos。支持已有，可少改 CLI 提升平台真实感。

- [ ] 确定差异文件。
- [ ] iOS scene/navigation。
- [ ] macOS scene/window/sidebar。
- [ ] watch/TV 保持稳定。
- [ ] README 差异。
- [ ] 两平台断言。
- [ ] 两平台生成验证。

目标：输出有意适配。

<a id="p2"></a>
## P2

<a id="9-android-add-release-environment-and-signing-placeholders"></a>
### 9. Android：发布/签名占位

提交 android: add release environment and signing placeholders。交接有价值但晚于基线。

- [ ] 签名策略。
- [ ] env/本地属性说明。
- [ ] Debug/staging/release 策略。
- [ ] fastlane beta/release。
- [ ] README。
- [ ] 可行占位测试。

目标：清晰接入发布。

<a id="10-apple-document-signing-and-release-integration"></a>
### 10. Apple：签名/发布文档

提交 apple: document signing and release integration。已有 fastlane/team，需要更好入职说明。

- [ ] development_team。
- [ ] bundle identifier。
- [ ] beta/release 前提。
- [ ] 用户签名输入。
- [ ] README/模板。
- [ ] 契约重要文本测试。

目标：不需猜测。

<a id="11-android-expand-the-design-system-starter-layer"></a>
### 11. Android：设计系统

提交 android: expand design system starter layer。长期规模价值，次于可靠性。

- [ ] 清晰 token。
- [ ] 一两个组件。
- [ ] 暗色指导/token。
- [ ] README/布局。
- [ ] 文件测试。
- [ ] 实构建。

目标：有意 UI 基础。

<a id="12-apple-expand-shared-package-architecture"></a>
### 12. Apple：共享包架构

提交 apple: expand shared package architecture。已有 Packages/DesignSystem，增加扩展模式。

- [ ] 决定 utilities/services 包。
- [ ] 边界易理解。
- [ ] Tuist/引用。
- [ ] README。
- [ ] 文件测试。
- [ ] 生成/实测试。

目标：可扩内部包示例。

<a id="suggested-commit-order"></a>
## 建议提交顺序

依上述 1–12 顺序，分别采用各项给出的提交标题。

<a id="recommended-working-style"></a>
## 建议工作方式

每项一提交；提交后匹配生成验证；README/测试与实现同提交；先完整 P0 再 P1。
