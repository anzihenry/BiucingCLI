---
title: "初始产品设计"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="product-design"></a>
# 初始产品设计

[English](design.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

<a id="purpose"></a>
## 目的

帮助独立开发者用熟悉技术栈快速开始，生成会长期保留的干净起点，而非替开发者设计整套工程。

<a id="primary-user"></a>
## 主要用户

经常使用稳定个人技术栈、希望避免重复配置的独立开发者。初期重点：前端 React/TypeScript、后端 Go/Gin、Apple Swift/Tuist/SwiftPM、序列化 Protobuf、后续 Kotlin 移动端。

<a id="problem"></a>
## 问题

新项目常要手工重建或复制含无关包袱的旧仓库。通用脚手架广而不够贴合真实工作流。BiucingCLI 通过少量高质量、风格一致的 starter 解决。

<a id="product-principles"></a>
## 产品原则

少量强模板；第一天有用、第三十天仍可读；选择少/默认合理；反映真实习惯；已有模板稳定后再扩目录。

<a id="core-workflow"></a>
## 核心流程

```text
choose template -> fill a few variables -> generate project -> start coding
```

<a id="first-version-commands"></a>
## 初版命令

<a id="1-biucing-list"></a>
### 1. `biucing list`

展示模板和简述。

<a id="2-biucing-info-template"></a>
### 2. `biucing info <template>`

说明生成内容、技术栈和选择场景。

<a id="3-biucing-create-template-project-name"></a>
### 3. `biucing create <template> <project-name>`

从内置模板生成，替换项目/module/端口等少量变量。

<a id="first-version-templates"></a>
## 初版模板

<a id="frontend"></a>
### `frontend`

React/TypeScript；开箱入口、克制的 components/pages/hooks/services/types、最少配置、有用 README。

<a id="web-service"></a>
### `web-service`

面向客户 HTTP，内部 API 属于 micro-service；生产/身份目标见 [Web 架构](../../../engineering/backend/web-service.md)。Go/Gin；cmd/server、internal handler/service/repository/router/model/config、基础配置、Docker、README/HTTP 测试。

<a id="apple"></a>
### `apple`

Swift/Tuist/SwiftPM/fastlane，支持 iOS/macOS/watchOS/tvOS。初始预期：根 Tuist.swift/Workspace.swift，App/Project.swift 应用/测试，Brewfile/.mise.toml/Makefile/bootstrap，Packages 下内部包，解释环境的 README。

<a id="micro-service"></a>
### `micro-service`

Go/Protobuf/Buf/Compose/OTel；契约 starter、可重复生成、服务/依赖/Collector 编排，解释 proto/run/up。

<a id="what-biucingcli-is-not"></a>
## 产品非目标

不是大型市场、完整应用一键生成、架构判断替代，也不在初版提供远程分发。

<a id="first-version-scope"></a>
## 初版范围

本地工作流：仓库内置模板、每模板小元数据、少量高价值变量、简洁后续步骤。

<a id="future-direction"></a>
## 未来方向

后续可加 gin/protobuf profile、Kotlin Android，以及核心验证后的更丰富参数。
