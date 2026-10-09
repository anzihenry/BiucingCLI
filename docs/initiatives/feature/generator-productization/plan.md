---
title: "BiucingCLI 0.3.0 计划"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-030-plan"></a>
# BiucingCLI 0.3.0 计划

[English](plan.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

<a id="current-state"></a>
## 当时状态

0.2.0 已具备脚手架能力，深度主要在模板。依据 cli.py、templates.py、template.json、test_cli.py：list/info/create/version；五模板 frontend/web-service/microservice/apple/android；元数据加载、必填提示、default/default_from、渲染、脚本/gradlew 执行位；Apple 四平台与 postgres/redis 预设；16 单测覆盖 CLI/五模板输出。

<a id="capability-inventory"></a>
## 能力盘点

<a id="cli-product-surface"></a>
### CLI 产品入口

list 摘要，info 栈/变量/步骤，create 支持 output-dir/模板参数，version 安装版本。

<a id="template-portfolio"></a>
### 模板目录

frontend React/TS/Docker/Vitest/Playwright；Web Go/Gin/开发运行镜像/lint/test/doctor；micro Go/Gin/Protobuf/Buf/OTel/gRPC/可选依赖；Apple SwiftUI/Tuist/SwiftPM 四平台；Android Kotlin/Gradle/Compose/提交 Wrapper/模块/fastlane/UI smoke。

<a id="where-the-product-is-strong"></a>
### 优势

模板有差异且实用，元数据简单可读，输出有真实工作流，主要族有实际证据。

<a id="where-the-product-is-thin"></a>
### 薄弱点

无机器输出；成熟度/验证仅正文；无仓库校验；发布规划滞后；分阶段路线不符合实现。

<a id="030-theme"></a>
## 0.3.0 主题

产品化 CLI，稳定五模板，一版不扩广度，加强发现/自动化/验证/发布纪律。

<a id="proposed-scope"></a>
## 建议范围

<a id="1-cli-experience-hardening"></a>
### 1. CLI 体验加固

目标为可检查、安全自动化。list/info JSON，必填缺失明确失败的非交互，统一 --set key=value，解析值/默认摘要；改善重复自动化与工具集成。

<a id="2-metadata-evolution"></a>
### 2. 元数据演进

将故事结构化。增加 category/platforms/maturity/validation/tags，list/info 展示，区分必填/派生/默认；让 CLI 清晰解释差异。

<a id="3-verification-productization"></a>
### 3. 验证产品化

持续证明质量。字段/占位校验，适用 list/info golden，最低发布矩阵，可重复渲染/生成 smoke 清单；收拢 0.2.0 分散证据。

<a id="4-release-surface-cleanup"></a>
### 4. 发布表面整理

版本化路线/计划，可复用 0.x 清单，区分 CHANGELOG 与深度计划；弥补代码快于文档的操作缺口。

<a id="non-goals"></a>
## 非目标

大量新族、重型渲染引擎、远程/插件/agent 编排。

<a id="recommended-backlog-order"></a>
## 建议 backlog 顺序

先字段并对齐五模板，再 CLI 输出/参数，再校验，再发布/矩阵，测试覆盖后发布。

<a id="exit-criteria"></a>
## 退出标准

五模板仍生成，人类/机器细节双形式，元数据解释成熟度/验证，版本有清晰当前计划和证据。

<a id="suggested-changelog-direction"></a>
## Changelog 方向

产品加固：检查/脚本工作流，丰富元数据/成熟度，仓库验证/发布纪律。
