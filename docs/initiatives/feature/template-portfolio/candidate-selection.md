---
title: "BiucingCLI 0.4.0 模板候选选择"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-040-template-candidate-selection"></a>
# BiucingCLI 0.4.0 模板候选选择

[English](candidate-selection.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

<a id="purpose"></a>
## 目的

完成 0.4.0 阶段 A 选型，在实施前明确新增模板方向。

<a id="selection-criteria"></a>
## 选择标准

符合维护者真实栈，复用已有模式，有可信生成工程验证，增加覆盖而非重叠，无须重型引擎新能力。

<a id="candidates-reviewed"></a>
## 已评估候选

| 候选 | 概述 | 优点 | 主要顾虑 |
| --- | --- | --- | --- |
| worker | 后台任务/执行器 | 补充 Web/micro，复用 Go/Docker/Makefile，适合定时/消费者/异步 | 需明确边界，避免第二个 microservice |
| cli | 命令行应用 | 符合生产力取向，适合内部工具 | 与当前目录/语言组合契合度较弱 |
| deployment/基础设施 | 窄部署 starter | 支持后端运维 | 容易配置过重、通用复用弱 |

<a id="chosen-direction"></a>
## 选定方向

0.4.0 增加 worker。

<a id="why-worker-wins"></a>
## worker 胜出的原因

<a id="1-it-complements-the-current-portfolio-cleanly"></a>
### 1. 清晰补充现有目录

已有浏览器 frontend、请求响应 web-service、契约 microservice、原生 apple/android。缺少定时、队列消费者、维护任务、非 HTTP 长进程的正式后台 starter；缺口真实。

<a id="2-it-reuses-proven-repo-patterns"></a>
### 2. 复用已验证模式

沿用 Go、Makefile、开发/运行镜像、适当本地缓存、配置加环境覆盖、适用健康/readiness，不重新发明产品体系。

<a id="3-it-adds-new-coverage-without-forcing-a-new-engine-model"></a>
### 3. 新覆盖无需新引擎模型

不需要条件继承、远程解析、profile 膨胀或大型元数据抽象，适配当前渲染模式。

<a id="what-worker-should-mean"></a>
## worker 的含义

窄范围后台执行服务，公共 HTTP 不是核心，一两个队列/定时模式，配置、日志、优雅退出、容器。不变成 gRPC starter、工作流平台或消息总线展示。

<a id="initial-design-boundaries"></a>
## 初始设计边界

Go、Makefile/README/ignore 文件、开发/运行 Docker、配置/环境覆盖、cmd/worker、internal 配置/运行/任务、测试及可信本地执行。0.4.0 避免同时多个队列后端、定时和消费者两套一等专门模式、无轻量理由的 OTel、覆盖所有异步形态的承诺。

<a id="deferred-candidates"></a>
## 暂缓候选

<a id="cli"></a>
### cli

虽有吸引力，但将目录拉向内部工具，较 worker 与当前故事联系弱。

<a id="deployment-or-infra-helper"></a>
### 部署或基础设施助手

容易依赖特定环境、配置繁重，与项目 starter 承诺较弱。

<a id="follow-on-tasks-for-phase-d"></a>
## 阶段 D 后续任务

实现前确定变量、目录、可比后端验证，以及首版偏定时、消费者还是窄混合。

<a id="phase-a-decision-summary"></a>
## 阶段 A 决策摘要

仅新增 worker，保持窄、贴近后端、可复用；CLI/部署模板留待以后。
