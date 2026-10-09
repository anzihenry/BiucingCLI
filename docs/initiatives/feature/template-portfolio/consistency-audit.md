---
title: "BiucingCLI 0.4.0 模板一致性审计"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-040-template-consistency-audit"></a>
# BiucingCLI 0.4.0 模板一致性审计

[English](consistency-audit.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

<a id="purpose"></a>
## 目的

完成阶段 A 一致性评审，区分有意差异与 0.4.0 待统一项，不强迫相同目录。

<a id="audit-inputs"></a>
## 审计输入

检查 templates/*/template.json、顶层输出、README/路线表述；覆盖 frontend、web-service、microservice、apple、android。

<a id="shared-contract-already-present"></a>
## 已有共享契约

| 范围 | 基线 | 说明 |
| --- | --- | --- |
| 元数据 | 每模板 template.json | 发现/校验事实来源 |
| 核心字段 | name/description/category/stack/tags/platforms/maturity/validation/variables/next_steps | 已足以正式契约化 |
| README | 均提供 | 深度不同，文档存在一致 |
| 工作流 | Makefile/可执行后续步骤 | 名称不同，都有首跑路径 |
| ignore/配置 | 均 gitignore | 生态文件差异合理 |
| 验证信号 | 成熟度/证据声明 | 术语未统一 |

<a id="top-level-shape-snapshot"></a>
## 顶层结构快照

| 模板 | 工作流文件 | 特征 |
| --- | --- | --- |
| frontend | Dockerfile、Dockerfile.dev、Dockerfile.dev.full、compose.dev.yaml、Makefile | 浏览器开发/运行分离 |
| web-service | Dockerfile、Dockerfile.dev、compose.dev.yaml、compose.yaml、.air.toml、Makefile | Go 热重载/运行镜像 |
| microservice | Dockerfile、Dockerfile.dev、compose.dev.yaml、.air.toml、Makefile、deploy | Buf/gRPC/OTel/依赖 |
| apple | Tuist.swift、Workspace.swift、Makefile、scripts | 多平台 Tuist/SwiftPM |
| android | gradlew/gradlew.bat、Makefile、scripts、fastlane | 提交 Wrapper/较丰富发布 |

<a id="intentional-differences"></a>
## 有意差异

| 差异 | 原因 |
| --- | --- |
| Web Docker 优先，原生不同 | 符合平台约束 |
| Apple/Android 初始化文件更多 | 环境需要工作站指导 |
| microservice 有 api/deploy/遥测 | 目标不同于 Web |
| frontend 轻量/完整开发镜像 | 浏览器工具的实用分离 |

<a id="accidental-or-under-specified-differences"></a>
## 意外或定义不足的差异

| 范围 | 当时状态 | 0.4.0 意义 |
| --- | --- | --- |
| 验证术语 | generated-project-verified/real-build-verified 无完整层级说明 | 明确证明含义 |
| 后续步骤 | doctor/dev/GUI 各自侧重 | 统一产品词汇 |
| 初始化契约 | 有的 scripts 明确，有的依赖 README | validate 可强化 |
| runtime/deploy | docker-build/docker-run/up/verify 含义差异 | 降低跨模板学习成本 |
| 元数据扩展 | 缺运行假设/验证层级 | 适合增加结构化规则 |

<a id="proposed-040-minimum-product-contract"></a>
## 0.4.0 最低产品契约提案

<a id="required-metadata"></a>
### 必需元数据

继续要求 name、description、category、stack、tags、platforms、maturity、validation、variables、next_steps。

<a id="candidate-metadata-additions"></a>
### 候选新增字段

评估 operating_assumptions、verification_tier、workflow_labels 等小型统一机制。

<a id="required-starter-facing-files-by-family"></a>
### 按模板族要求的入口

按族而非全局统一：

| 族 | 候选文件/目录 |
| --- | --- |
| Web/容器 | README/Makefile/gitignore/dockerignore、开发镜像、运行镜像或明确打包路径 |
| Go 服务 | README/Makefile/go.mod/go.sum/cmd/internal/configs/scripts |
| 原生 | README/Makefile/.mise.toml/scripts、平台构建入口 |

<a id="required-workflow-labels"></a>
### 必需工作流标签

统一适用的 bootstrap、doctor、dev、test、verify、build、release/package 概念，生态实现可不同。

<a id="workstream-recommendations"></a>
## 工作流建议

<a id="highest-value-consistency-tasks"></a>
### 高价值一致性任务

定义/约束验证层级，统一步骤词汇，validate 检查族入口，更新模板系统文档。

<a id="tasks-to-avoid-overdoing"></a>
### 避免过度工作

不迫使原生 Docker 化、不要求此历史阶段所有模板完全相同 Make 目标、不另造独立大 schema。

<a id="phase-a-decision-summary"></a>
## 阶段 A 决策摘要

结构已有强基础，0.4.0 收紧契约：明确验证、统一词汇、将族入口纳入校验，让未来模板从起步遵循质量要求。
