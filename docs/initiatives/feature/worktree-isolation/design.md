---
title: "BiucingCLI 0.6.0 计划"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-060-plan"></a>
# BiucingCLI 0.6.0 计划

[English](design.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

<a id="current-state"></a>
## 当时状态

0.5.0 七 starter；dry-run/plan/JSON/validate；Docker Make/Compose 开发检查打包；原生 doctor/release/signing/验证加强。下一缺口是多分支、多实验、多工程并行的重复使用。

<a id="060-theme"></a>
## 0.6.0 主题

worktree 优先：多处并行无需记忆性改端口、容器、缓存或保护签名。

<a id="release-thesis"></a>
## 发布主张

把 worktree 作为日常流程：一处开发、一处测试、一处发布构建、一处依赖升级，依赖/缓存/生成文件/应用身份/运行名称隔离。承诺并行开发测试打包不意外互扰。

<a id="planning-principles"></a>
## 规划原则

本地确定隔离、生成后简单、默认安全且可覆、Make/本地脚本控制、不引入重编排或服务、实工程验证。

<a id="worktree-isolation-contract"></a>
## 隔离契约

| 维度 | 要求 |
| --- | --- |
| 身份 | 路径或显式覆盖推导稳定 WORKTREE_ID/SLUG |
| 运行名 | 容器/project/卷/镜像/app 不冲突 |
| 端口 | 可覆/文档化，长期服务有预测避冲路径 |
| 依赖服务 | Postgres/Redis/OTel 按 project/卷/网络 |
| 缓存 | 共享会损可靠性时项目/worktree 本地 |
| 输出 | 构建/生成/包/IDE 无需删他处状态 |
| 本地秘密 | signing/local.properties/.env.local 忽略且本地 |
| 安装身份 | 必要时并行 Debug 标识 |
| 清理 | 当前范围 |
| 诊断 | 快速打印解析值 |

<a id="shared-generated-workflow"></a>
## 共享生成工作流

适用平台提供：

```bash
make worktree-info
make worktree-doctor
make clean-worktree
```

info 显示 repo/worktree root、ID/SLUG、project/原生后缀、缓存、端口、本地配置。doctor 对缺失/重复端口、非预期全局缓存、发布配置缺失、Debug 覆盖身份报错/警告。clean-worktree 只清自身，强目标外不得删共享镜像、SDK、无关容器/Gradle/根外文件。

<a id="workstream-1-contract-and-generator-support"></a>
## 工作流 1：契约与生成器

<a id="problem"></a>
### 问题

元数据未说明并行安全。

<a id="060-goal"></a>
### 0.6.0 目标

隔离成为正式质量要求。

<a id="candidate-deliverables"></a>
### 候选交付

契约文档、支持级元数据、info/JSON 展示、validate 声明要求、规则测试。

<a id="workstream-2-docker-first-template-isolation"></a>
## 工作流 2：Docker 隔离

<a id="problem-1"></a>
### 问题

长服务/端口/卷/多分支最有风险且价值高。

<a id="060-goal-1"></a>
### 0.6.0 目标

四 Docker 模板默认并行安全。

<a id="candidate-deliverables-1"></a>
### 候选交付

SLUG 推 project，卷/镜像身份化，端口可覆/诊断，Go/pnpm/Playwright/lint/输出缓存本地，README/Make 并行指导，至少两身份验证。

<a id="workstream-3-native-template-isolation"></a>
## 工作流 3：原生隔离

<a id="problem-2"></a>
### 问题

冲突来自缓存/IDE/安装/签名/SDK 输出。

<a id="060-goal-2"></a>
### 0.6.0 目标

Apple/Android/HarmonyOS 并行构建测试安全。

<a id="candidate-deliverables-2"></a>
### 候选交付

Apple 独立 DerivedData/适当 SwiftPM/Debug bundle/Tuist 路径；Android Gradle home/cache、ID 后缀、本地 signing/配置、安装说明；HarmonyOS hvigor/modules/output、工具支持时 Debug 后缀、签名诊断不打印值。

<a id="workstream-4-verification-and-release-evidence"></a>
## 工作流 4：验证与证据

<a id="problem-3"></a>
### 问题

安全易声称也易回退，需可重复证据。

<a id="060-goal-3"></a>
### 0.6.0 目标

发布隔离验证路径。

<a id="candidate-deliverables-3"></a>
### 候选交付

info smoke、Make 目标测试、双工程指导、矩阵、专版并行证据。

<a id="suggested-release-sequencing"></a>
## 建议发布顺序

<a id="phase-a-contract-and-audit"></a>
### 阶段 A：契约与审计

定义/七模板审计/风险分类/元数据。规划完成，见[契约](../../../engineering/worktree-isolation-contract.md)和[审计](audit.md)。

<a id="phase-b-generator-metadata-and-validation"></a>
### 阶段 B：元数据与校验

各 template.json、list/info/JSON、validate、golden/unit。生成器契约完成：全部声明，展示/校验结构。

<a id="phase-c-docker-first-template-implementation"></a>
### 阶段 C：Docker 实现

四模板命令/project/卷/镜像/端口/缓存，Compose/目标运行检查。完成，均 ready。

<a id="phase-d-native-template-implementation"></a>
### 阶段 D：原生实现

三模板缓存/输出/后缀，轻构建/doctor 验证。完成，均 ready，有诊断、清理、配置可见、身份 hook。

<a id="phase-e-release-hardening"></a>
### 阶段 E：发布加固

README/路线/系统/清单/矩阵/专版证据、测试、生成验证。完成，changelog 草稿和[发布准备](../../../releases/0.6.0/validation.md)反映实现及证据。

<a id="non-goals"></a>
## 非目标

完整 Git 管理 CLI、自动创建删除 worktree、daemon/registry/coordinator、用户手指同一外部服务仍无冲突的保证、替代平台工具，或超出文档指导的旧工程迁移。

<a id="exit-criteria"></a>
## 退出标准

全模板声明/诊断/清理；Docker project/卷/镜像/依赖/缓存/端口隔离；原生主要冲突点隔离；validate 发现缺失；矩阵显式并行；文档解释双处运行。

<a id="suggested-changelog-direction"></a>
## Changelog 方向

共享契约、Docker 并行、原生缓存签名身份、诊断清理、并行验证证据。
