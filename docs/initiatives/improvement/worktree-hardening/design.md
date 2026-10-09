---
title: "BiucingCLI 0.6.1 计划"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-061-plan"></a>
# BiucingCLI 0.6.1 计划

[English](design.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

<a id="current-state"></a>
## 当时状态

0.6.0 七模板 ready、三命令、Docker project/卷/镜像/端口/依赖/缓存、原生主要冲突隔离。剩余为一致性、自诊断和证据打磨。

<a id="061-theme"></a>
## 0.6.1 主题

加固到平常可靠，不加模板或编排层，使行为一致易理解少误用。

<a id="release-thesis"></a>
## 发布主张

长工作流前显露身份/风险：统一确定身份，人可读/机器稳定，有用端口建议，无容器 Compose 检查，区分原生静态/doctor/构建，保守 Harmony 身份。默认可预测，异常可诊断，有重复证据。

<a id="planning-principles"></a>
## 规划原则

ID 简单可覆，七模板统一；显式建议不隐式修改；不自动改 env/Make/profile/signing；诊断快安全；准确说检查/跳过。

<a id="hardening-targets"></a>
## 加固目标

| 范围 | 0.6.0 | 0.6.1 |
| --- | --- | --- |
| 身份 | Docker 路径哈希，原生目录 slug | LABEL/ID/SLUG 统一 |
| 端口 | 默认警告 | 检占用/建议覆盖 |
| Docker | 文档 config 证据 | 可复用目标 |
| 原生 | 诊断/命令展开 | 分层证据 |
| Harmony 身份 | 属性传后缀，源不改 | 记录，可靠才可选临时 profile |
| 证据 | 专版文件 | 更强检查 |

<a id="unified-worktree-identity"></a>
## 统一身份

```make
WORKTREE_ROOT ?= $(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
WORKTREE_LABEL ?= $(shell basename "$(WORKTREE_ROOT)" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//; s/-$$//')
WORKTREE_ID ?= $(shell printf '%s' "$(WORKTREE_ROOT)" | shasum | cut -c1-8)
WORKTREE_SLUG ?= $(APP_NAME)-$(WORKTREE_ID)
```

LABEL 来自目录、人可读；ID 短哈希隔离；SLUG 运行名加 ID；仍可覆盖 main/alice-login/release-check。

<a id="workstreams"></a>
## 工作流

<a id="workstream-1-contract-tightening"></a>
### 1：契约收紧

先明确标准：计划、任务、README/路线、暂缓范围。

<a id="workstream-2-unified-identity"></a>
### 2：统一身份

统一 ROOT/LABEL/ID/SLUG，更新 Make/文档/单测/生成证据。

<a id="workstream-3-port-conflict-advisor"></a>
### 3：端口建议

小 shell/Make 检查覆盖 frontend/Web/micro，输出可复制覆盖；worker 明确无端口。

<a id="workstream-4-stronger-docker-diagnostics"></a>
### 4：Docker 诊断

生成 worktree-compose-config，doctor 调用或指向，不启动容器。

<a id="workstream-5-native-evidence-hardening"></a>
### 5：原生证据

分 static/doctor/real-build，添加命令，准确记环境限制。

<a id="workstream-6-harmonyos-debug-identity-boundary"></a>
### 6：Harmony 身份边界

检查边界；安全才可选写忽略临时输出，否则记录暂缓。

<a id="workstream-7-release-prep"></a>
### 7：发布准备

添加 0.6.1 validation；更新 README/路线/changelog/清单/矩阵；仓库及新生成证据。

<a id="non-goals"></a>
## 非目标

管理 worktree，daemon/端口 registry，自动改文件，保证用户共享外部服务无冲突，强改不明 Harmony 边界，要求所有机器全 SDK。

<a id="exit-criteria"></a>
## 退出标准

统一身份，端口建议，生成 Compose 目标，原生证据分级，Harmony 支持/暂缓决定，新证据。

<a id="suggested-changelog-direction"></a>
## Changelog 方向

身份统一、端口/Compose 诊断、原生证明、Harmony 边界、碰撞/清理证据。
