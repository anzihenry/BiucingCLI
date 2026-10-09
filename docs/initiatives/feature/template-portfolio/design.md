---
title: "BiucingCLI 0.4.0 计划"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-040-plan"></a>
# BiucingCLI 0.4.0 计划

[English](design.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

<a id="current-state"></a>
## 当时状态

0.3.0 将模板集产品化：list/info/create/validate/version，人类/JSON 输出，交互/set/non-interactive，丰富元数据，同源校验。此文更新后的六模板为 frontend、web-service、microservice、worker、apple、android。相较 0.2.0 更强，但生成计划/预览/生命周期、模板统一和慎重新增仍有空间。

<a id="040-theme"></a>
## 0.4.0 主题

可检查、一致、可有意扩展。三条等重轴：生成 UX、模板一致性、新模板。提高信任/扩展/持续维护，避免只扩大范围。

<a id="phase-a-status"></a>
## 阶段 A 状态

规划完成。[一致性审计](consistency-audit.md)、[候选选择](candidate-selection.md)已完成；非目标作为边界，收紧契约而非重写，选择 worker，暂缓 CLI/部署。

<a id="phase-b-status"></a>
## 阶段 B 状态

实施完成：dry-run 无写预览，plan 可结构化/JSON，create --json 成功返回清单，非交互一次报告所有缺失必填。

<a id="phase-c-status"></a>
## 阶段 C 状态

实施完成：verification_tier/operating_assumptions/workflow_labels；info/JSON 展示；validate 强化字段/模板族入口；系统文档更新。

<a id="phase-d-status"></a>
## 阶段 D 状态

实施完成：worker 一等模板，scheduled/oneshot，复用 Go/Docker/Makefile，不变成 microservice；真实 go test ./... 验证。

<a id="phase-e-status"></a>
## 阶段 E 状态

发布加固完成：专版准备文档，通用清单/矩阵反映六模板及 UX，changelog 草稿，README/计划链接。

<a id="planning-principles"></a>
## 规划原则

维护六模板健康；优先重复使用价值；保留可读内置系统；新增为产品决策；各项改善发现、维护或生成工程实用性。

<a id="scope-overview"></a>
## 范围概览

| 主题 | 意图 | 成功信号 |
| --- | --- | --- |
| 生成 UX | 检查、预览、自动化 | 写入前理解，生成后审计 |
| 模板一致性 | 共同质量要求 | 元数据/验证/文档/工作流有意对齐 |
| 新模板 | 慎重增加一个 starter/紧密族 | 符合栈理念及现有质量 |

<a id="workstream-1-generator-ux"></a>
## 工作流 1：生成 UX

<a id="problem"></a>
### 问题

原流程无值/文件预览、机器结果清单、易用输入检查；适合维护者但自动化/集成不足。

<a id="040-goal"></a>
### 0.4.0 目标

执行前可检查、执行后可审计。

<a id="candidate-deliverables"></a>
### 候选交付

<a id="1-create-preview-layer"></a>
#### 1. 创建预览层

dry-run 解析无写；plan 展示模板、解析/派生变量、目标、工作流/步骤；人类和 JSON 双形式。

<a id="2-input-discovery-improvements"></a>
#### 2. 输入发现

直接检查必填/可选；一次列全部缺失；优先聚焦 info 增强而不增加过多顶级命令。

<a id="3-generation-result-manifest"></a>
#### 3. 生成结果清单

成功后机器摘要至少含模板、项目、输出路径、变量、步骤，可含文件数/关键入口；决定 stdout、落盘或两者。

<a id="task-breakdown"></a>
### 任务拆分

<a id="phase-1-preview-and-error-design"></a>
#### 阶段 1：预览和错误设计

定义结构，区分用户/派生/默认来源，选择 create 参数或独立命令，先写错误/载荷测试。

<a id="phase-2-cli-implementation"></a>
#### 阶段 2：CLI 实现

扩 parser，复用解析避免漂移，人类/JSON 格式。

<a id="phase-3-result-manifest"></a>
#### 阶段 3：结果清单

稳定结构、字段语义测试、脚本依赖说明。

<a id="workstream-2-template-consistency"></a>
## 工作流 2：模板一致性

<a id="problem-1"></a>
### 问题

证据未归一到发布预期，步骤缺共享标准，文档/命令深度命名不同，质量仍靠隐性知识。

<a id="040-goal-1"></a>
### 0.4.0 目标

模板族有明确治理。

<a id="candidate-deliverables-1"></a>
### 候选交付

<a id="1-metadata-contract-tightening"></a>
#### 1. 收紧元数据

定义必填；评估运行假设、外部依赖、验证层级、成熟度；明确新模板标准。

<a id="2-validation-policy-expansion"></a>
#### 2. 扩展校验

在有价值处超越字段/占位符，检查族顶层入口、README/Makefile/doctor/bootstrap、元数据工作流一致、证据形态术语。

<a id="3-shared-output-standards"></a>
#### 3. 共享输出标准

统一 bootstrap/doctor/test/verify/release/runtime 说明，对齐 help、info、README 和 Make。

<a id="task-breakdown-1"></a>
### 任务拆分

<a id="phase-1-consistency-audit"></a>
#### 阶段 1：一致性审计

六模板共用检查表，区分有意/意外，记录最低契约。

<a id="phase-2-validation-and-metadata-enhancements"></a>
#### 阶段 2：校验与元数据

按需更新 template.json，谨慎扩展不造第二 schema，测试锁规则。

<a id="phase-3-template-surface-alignment"></a>
#### 阶段 3：模板表面对齐

统一文档/步骤，doctor/bootstrap/verify 命名，更新 README/系统文档。

<a id="workstream-3-new-template-surface"></a>
## 工作流 3：新模板

<a id="problem-2"></a>
### 问题

聚焦目录是优势，但仅加固不足以展示审慎扩展能力。

<a id="040-goal-2"></a>
### 0.4.0 目标

交付自然符合产品的新模板。

<a id="scope-rule"></a>
### 范围规则

最多一条 starter 或紧密相关族，避免多线并行初始化稀释进展。

<a id="candidate-evaluation-criteria"></a>
### 候选标准

真实维护者栈、已有模式、可信生成验证、增覆盖少重叠、不需重型引擎。

<a id="candidate-directions-to-evaluate"></a>
### 待评估方向

补充 Web/micro 的后端、支持服务/worker、生产力 CLI/自动化、仅窄且实用的部署/基础设施。

<a id="task-breakdown-2"></a>
### 任务拆分

<a id="phase-1-candidate-selection"></a>
#### 阶段 1：候选选择

选 2–3 实际候选，比标准、明确胜者/暂缓理由；规划已完成，见[候选选择](candidate-selection.md)。

<a id="phase-2-design-spec"></a>
#### 阶段 2：设计规格

定义元数据/变量/目录/步骤，实施前定义验证含义，判断占位符/派生是否必要。

<a id="phase-3-implementation-and-validation"></a>
#### 阶段 3：实现与验证

必要时才加 CLI，渲染/生成验证，一并更新文档/路线/目录。

<a id="suggested-release-sequencing"></a>
## 建议发布顺序

<a id="phase-a-planning-and-audit"></a>
### 阶段 A：规划和审计

锁主题/非目标，审计，选候选。完成。

<a id="phase-b-generator-ux-foundation"></a>
### 阶段 B：生成 UX 基础

预览/缺失输入/清单契约。完成。

<a id="phase-c-template-contract-strengthening"></a>
### 阶段 C：模板契约

校验、元数据/步骤、共享文档。完成。

<a id="phase-d-new-template-bring-up"></a>
### 阶段 D：新模板

设计实现、同标准验证、接 CLI/发布文档。完成。

<a id="phase-e-release-hardening"></a>
### 阶段 E：发布加固

路线/changelog、测试/校验、专版证据。完成。

<a id="non-goals"></a>
## 非目标

多个无关模板、完整引擎替换、远程/在线/插件生态、工作流编排器，以及超出轻量清单/指导的旧工程升级迁移。

<a id="exit-criteria"></a>
## 退出标准

可信预览，生成前后自动化可检查审计，共享元数据/验证契约，一个不降低质量的新模板，路线/文档/发布符合实现。

<a id="suggested-changelog-direction"></a>
## Changelog 方向

有纪律的产品扩展：预览/自动化 UX、模板质量一致性、一项慎重新增。
