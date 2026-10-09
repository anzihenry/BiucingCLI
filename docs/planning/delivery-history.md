---
title: "交付历史与历史路线"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="delivery-history-and-historical-roadmap"></a>
# 交付历史与历史路线

[English](delivery-history.en.md)

> 历史记录。当前源码版本和跨专题优先级见[路线](roadmap.md)。以下规划属于原始背景，不是当前 backlog。

<a id="shipped"></a>
## 已交付

<a id="010---scaffold-generator-baseline"></a>
### 0.1.0：脚手架基线

元数据系统、list/info/create/version、frontend/web-service/micro-service/apple/android 五模板、聚焦产品方向。

<a id="020---template-maturity-expansion"></a>
### 0.2.0：模板成熟度

Web 三模板完整 Docker 开发/打包；Apple Tuist/SwiftPM/平台/doctor/lint/release；Android Kotlin/Compose/Wrapper/doctor/UI/签名占位；反复真实构建测试。

<a id="030---productize-the-generator"></a>
### 0.3.0：生成器产品化

validate 与 JSON，set/non-interactive/解析，丰富字段，校验/golden，版本化发布/验证文档。

<a id="040---sharpen-the-product-normalize-the-portfolio-add-one-new-surface"></a>
### 0.4.0：UX、一致性、一个新模板

dry-run/plan/机器清单，共享字段/验证/文档/流程，worker 第六模板；写前可预览，成功后稳定摘要，清晰契约，不降低验证。

<a id="050---harmonyos-starter"></a>
### 0.5.0：HarmonyOS

实验 ArkTS/ArkUI/DevEco，bootstrap/doctor/lint/build/signing 指导，七模板，区分生成验证/工作站 SDK。

<a id="060---worktree-first-starters"></a>
### 0.6.0：Worktree 优先

共享契约、Docker project/卷/端口/镜像/依赖/缓存，原生输出/缓存/签名/身份，三命令，验证证据。A–D 与 E 完成，均 ready。见[计划](../initiatives/feature/worktree-isolation/design.md)、[任务](../initiatives/feature/worktree-isolation/plan.md)、[验收](../releases/0.6.0/validation.md)。

<a id="061---worktree-isolation-hardening"></a>
### 0.6.1：Worktree 加固

统一身份、端口建议、无侵入 config、精确原生证据、Harmony 安全边界。见[计划](../initiatives/improvement/worktree-hardening/design.md)、[任务](../initiatives/improvement/worktree-hardening/plan.md)、[验收](../releases/0.6.1/validation.md)。七模板同模型，Docker 诊断，static/doctor/real-build，Harmony 改写暂缓只读诊断。

<a id="070---native-release-readiness"></a>
### 0.7.0：原生发布就绪

Apple archive/TestFlight/App Store lane，Android signing/AAB/Play internal-production，Harmony preflight/release HAP，新真实构建。见[说明](../releases/0.7.0/notes.md)、[验收](../releases/0.7.0/validation.md)。账户凭据和实际商店提交仍不入模板配置。

<a id="080---cross-template-runtime-and-release-hardening"></a>
### 0.8.0：跨模板运行与发布加固

输入、通用 Make、生产浏览器、后端生命周期、worker 重试、原生发布验证。见[说明](../releases/0.8.0/notes.md)、[验收](../releases/0.8.0/validation.md)。

<a id="historical-090-planning-snapshot"></a>
## 历史 0.9.0 规划快照

<a id="090---distribution-and-generator-core-hardening"></a>
### 0.9.0：分发与生成内核

安装分发为边界：七模板 wheel/sdist、规范后派生、稳定错误/原子生成、Python 3.11–3.14 产物。见[计划](../initiatives/improvement/distribution-hardening/plan.md)、[验收](../releases/0.9.0/validation.md)。

<a id="historical-backend-planning-snapshot"></a>
## 历史后端规划快照

方向已批准，实施与当前发布范围分开，未指定版本。[架构](../engineering/backend/architecture.md)、[任务](../initiatives/feature/backend-services/plan.md)。27 基线任务覆盖运行、协议身份、数据、调用、遥测、Docker/Compose、独立 Kubernetes HA；14 扩展按需。已有 starter 证据不代表整体完成。

<a id="deferred"></a>
## 暂缓

一版多个无关模板、重型外引擎、远程/插件/市场、通用平台/编排器、自动 Git worktree 管理。
