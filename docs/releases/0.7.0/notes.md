---
title: "BiucingCLI 0.7.0"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-070"></a>
# BiucingCLI 0.7.0

[English](notes.en.md)

Apple、Android、HarmonyOS starter 具备更规范的分发前工作流。

<a id="highlights"></a>
## 亮点

- Apple 提供 Fastlane archive、TestFlight、App Store Connect 通道，明确签名与 Connect 预检要求。
- Android 验证 release keystore，生成并校验 App Bundle，提供 Google Play 内测与生产草稿 Fastlane 通道。
- HarmonyOS 提供本地签名预检和 release HAP 流程，构建后恢复源 build profile。
- 新原生证据：Apple iOS/macOS 构建与测试，Android lint/单元/APK/AAB/模拟器 UI，配置 DevEco 的 HarmonyOS lint/test/HAP。

<a id="important-boundary"></a>
## 重要边界

starter 自动化本地及需凭证的交付步骤，但不宣称真实商店提交。Apple Connect、Google Play、AppGallery/企业交付仍需产品自己的账户、签名、应用记录、元数据和审核配置。

<a id="verification"></a>
## 验证

完整证据和命令见 [0.7.0 发布准备](validation.md)。
