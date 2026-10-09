---
title: "项目文档组织约定"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# 项目文档组织约定

[English](documentation.en.md)

## 依据与范围

结构参考 HarnessBrew 2026-10-09 的 `docs/documentation.md`：长期知识、具体工作专题、版本事实分别维护；只创建有内容的领域；每个领域和专题提供入口。本项目沿用目录、导航和中文主文件/英文配对模型；发布审批制度单独维护。

适用范围：根 README/CHANGELOG 和 docs 内维护文档。`src/biucingcli/template_data/` 下的 Markdown 属于生成项目资源，`shared/core/README.md` 属于源码就地说明，不纳入此目录迁移。

## 目录职责

| 位置 | 内容 |
| --- | --- |
| 根 README | 用途、环境、最短示例和文档入口 |
| 根 CHANGELOG | 版本变化摘要，链接版本索引 |
| docs/README | 文档地图和阅读路径 |
| product | 当前产品定位、用户、能力和边界 |
| engineering | 当前架构、模块、接口与技术约束 |
| guides | 使用、开发、测试、环境、验收和发布操作 |
| planning | 跨专题优先级、依赖和交付历史 |
| initiatives/feature | 新增能力的目标、方案、任务和验证 |
| initiatives/improvement | 既有能力的改进 |
| initiatives/refactor | 内部结构与可维护性改进 |
| initiatives/process | 开发、文档和交付流程改进 |
| releases/版本 | 版本说明和对应历史验收 |

research、design、initiatives/research 仅在有独立实际材料时创建。需要长期保留的重大决策可在 engineering/decisions 建编号索引；本次未将架构中的每个表格条目机械转为 ADR。

## 唯一维护位置

当前事实以 product、engineering 和 guides 为准；旧专题计划不充当新的使用规范。活跃专题在入口声明唯一任务源，跨专题规划只引用。验证矩阵选择检查与汇总边界，详细验收只保留在专题或版本目录。每次实施应同步受影响长期文档。

原任务/阶段记录保留其历史背景。专题 `completed` 只代表既有记录范围，不补造独立评审、真机或发布证据。后端任务维护在专题 plan；迁移任务维护在本次专题 README。

## 元信息、状态和语言

维护文档使用 YAML 头部：title、status、owner、updated。负责人 `project-maintainers` 表示本仓库维护者；日期表示正文更新或有效性复核日期。

| 类型 | 状态 |
| --- | --- |
| 长期文档与导航 | draft、current、superseded |
| 专题及其材料 | proposed、active、paused、completed、cancelled |
| 发布目录 | recorded、planned、verified、released、cancelled、withdrawn |

`recorded` 是本项目历史版本归档状态：只保留现有说明和证据，未核实正式发布时间、地址和不可变产物身份；它是相对 HarnessBrew 规范的明确裁剪。升级为 verified/released 必须提供对应候选/发布证据，不能只依据版本号或本地标签。

根入口、CHANGELOG 和 docs 下所有维护文档采用中文主文件及 `.en.md` 英文配对，并互相链接。新增或实质改写时同步维护正文、元信息、命令与代码示例，索引指向本语言版本。翻译页保留源章节锚点以稳定文档引用。生成项目内文档、原始日志与机器报告不纳入翻译范围，保留原始语言。

## 路径与引用

目录和文件用英文小写及连字符，README 为入口，英文为 README.en.md。仓库内使用相对链接。迁移不提供旧路径重定向；所有引用、模板元数据中的证据路径及对应 CLI 预期值同步更新。

assets 和 evidence 就近存放；证据注明对应提交、候选或原始环境。迁移清单记录旧路径与原始哈希，只是审计材料。`/tmp` 路径仅是历史本地线索，不保证今天可用，也不视为可持续访问的发布证据。

## 检查与维护

自动检查：`uv run --locked python scripts/check-docs`。检查元信息、合法状态、命名、相对链接及章节锚点、全部维护文档的双语配对、owner/status/updated 一致性与代码块一致性、索引状态一致性和迁移路径覆盖。CI documentation job 执行同一命令。结构检查不能证明翻译语义或实际产品行为。

本次验证与作者内容核对记录在[结构迁移专题](initiatives/process/documentation-standard/README.md)。每次交付检查 product、engineering、guides、planning、专题、版本和根入口的影响；无独立 research/design 时说明不适用。维护者建议每 90 天复核 current 文档，不按日期自动失效。

没有修改远端分支保护或确认 GitHub required status checks；本地 CI 配置不等于远端强制门槛已经启用。
