---
title: "产品定位与范围"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# 产品定位与范围

[English](overview.en.md)

## 定位和用户

BiucingCLI 为经常启动新项目的独立开发者生成符合固定个人技术栈的项目骨架，减少重复配置。重点是少量可验证、可维护的模板。

## 当前能力

当前源码版本为 0.10.0，提供 frontend、web-service、micro-service、worker、apple、android、harmonyos 七类内置模板。CLI 支持模板发现、信息查询、输入校验、预览、JSON 输出和实际生成；命令示例见[使用指南](../guides/using.md)。

生成器采用包内资源和统一规划/发布管线；现行边界见[工程入口](../engineering/README.md)。原生设备、签名、商店交付和后端生产可用性按[验证矩阵](../guides/verification-matrix.md)中对应证据判断。

## 产品边界

不自动迁移已经生成的项目，不管理 Git worktree，不提供远程模板市场或通用 Agent 工作流。应用业务由生成项目维护者实现。

## 当前关注

保持模板交付、CLI 契约和安装包资源一致。后端 Kubernetes 是参考交付，B27 真实跨可用区 HA 验收暂停；HarmonyOS 真机和签名交付等边界以专题证据为准。跨专题安排见[路线图](../planning/roadmap.md)。

初版定位作为历史材料保存在[脚手架基线专题](../initiatives/feature/scaffold-baseline/README.md)。
