---
title: "文档地图"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# 文档地图

[English](README.en.md)

## 阅读路径

- 使用项目：[BiucingCLI](../README.md) → [操作指南](guides/README.md)。
- 了解能力：[产品文档](product/README.md) → [工程文档](engineering/README.md)。
- 开发与验收：[使用 uv 开发、构建与发布](guides/development.md) → [测试套件与配置验证](guides/testing.md) → [BiucingCLI 验证矩阵](guides/verification-matrix.md)。
- 跟踪工作：[项目规划](planning/README.md) → [工作专题索引](initiatives/README.md)。
- 核对版本：[更新日志](../CHANGELOG.md) → [版本记录索引](releases/README.md)。
- 维护文档：[项目文档组织约定](documentation.md) → [文档结构迁移](initiatives/process/documentation-standard/README.md)。

## 组织边界

长期知识、操作指南、工作专题和版本事实分别维护。沿用 HarnessBrew 的目录模型，只创建有实际内容的领域；当前没有独立 research 和交互/视觉 design 材料，不创建空目录。

根入口、CHANGELOG 及 docs 下维护文档均提供中文主文件和英文 `.en.md`，可通过语言链接切换；索引链接指向对应语言。生成项目内的文档、原始日志与机器报告保持原始语言。

`src/biucingcli/template_data/` 内的文档属于生成项目资源，`shared/core/README.md` 属于源码就地说明；二者保留原位置。旧仓库文档路径已移除，不提供重定向。
