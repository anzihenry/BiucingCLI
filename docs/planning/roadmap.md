---
title: "当前路线图"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# 当前路线图

[English](roadmap.en.md)

## 已有交付基线

源码版本 0.10.0；版本变化见[CHANGELOG](../../CHANGELOG.md)，历史候选验收见[版本索引](../releases/README.md)。版本号和本地标签不单独证明正式发布。

- 七类模板和包内资源、JSON/错误契约已建立。
- 前端 CSR/SSG/SSR 的实现与验证见[专题](../initiatives/feature/frontend-rendering/README.md)。
- 原生二进制组件及跨平台会话契约见[专题](../initiatives/feature/native-components/README.md)，设备覆盖仍按各平台证据判断。
- 后端 B01–B24 已完成对应范围交付，B25/B26 完成 Kubernetes 参考交付；任务状态只在[后端计划](../initiatives/feature/backend-services/plan.md)维护。
- 统一生成管线于 2026-10-06 记录最终验收，见[专题](../initiatives/refactor/unified-generation/README.md)。

## 当前安排与依赖

- B27 真实多可用区 HA 演练暂停；恢复需要目标集群、跨区入口、托管 PG、备份和授权，详见[后端专题](../initiatives/feature/backend-services/README.md)。不设定新的版本或工期。
- 本次文档结构迁移见[专题](../initiatives/process/documentation-standard/README.md)；正文完整双语翻译尚未纳入本次范围。
- 其余后端扩展按需求选择，不从旧计划推断为当前必须执行项。

## 延后边界

远程模板市场、自动 worktree 管理和通用工作流编排仍不属于当前产品范围。历史安排保存在[交付历史](delivery-history.md)。
