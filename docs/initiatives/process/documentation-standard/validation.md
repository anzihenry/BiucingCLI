---
title: "文档结构迁移验证"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

# 文档结构迁移验证

[English](validation.en.md)

## 内容身份与范围

基线提交：`9ee0efb1bdd20969808f8bffbea42bef72e9a142`。被审对象为本次未提交工作区的仓库文档、证据路径元数据、预期 JSON、文档检查脚本和 CI；源路径与原始哈希见[迁移清单](evidence/migration-inventory.json)，双语补齐的源快照与配对范围见[翻译清单](evidence/translation-inventory.json)。

## 影响清单

| 领域 | 处理 |
| --- | --- |
| research / design | 不适用：没有独立研究或交互/视觉材料；原 product-design 是产品初版背景，归入专题 |
| product | 已更新：增加当前产品定位和边界，中英文配对 |
| engineering | 已更新：架构与契约归入长期领域，专题背景明确标识 |
| guides | 已更新：详细 README 拆成 using，开发/测试/环境/发布指南归类 |
| planning | 已更新：当前 roadmap 与历史记录分开，修正版本与后端摘要 |
| initiatives | 已更新：稳定主题目录、入口、范围、任务源与证据链接 |
| releases | 已更新：按版本归档，recorded 不推断正式发布 |
| 根入口 / CHANGELOG | 已更新：精简双语 README，CHANGELOG 链接版本索引；历史条目已补齐中文和英文 |
| 模板资源与实现 | 只更新仓库证据路径元数据与相应 JSON 预期；生成项目 Markdown 正文和源码不迁移 |
| 自动检查 / CI | 已接入结构检查命令与 documentation job；远端必过设置未操作 |

## 检查与评审

已完成作者内容核对，未执行独立评审；本次沿用目录与双语组织约定，不宣称复制 HarnessBrew 的完整评审和发布流程。后续按用户要求补齐全部维护正文的双语版本，生成项目内文档和原始证据不翻译。文档结构检查不验证旧本地 SDK/容器/集群日志；历史证据未重新执行。

## 结构迁移阶段检查（2026-10-09，Asia/Shanghai）

- 文档结构：148 个 Markdown 文件、66 条迁移路径通过；原文件哈希与基线提交逐份一致。
- 文档检查失败场景：最终 6 项通过，覆盖无效文件/锚点、非法元信息、语言配对、索引漂移、旧路径和孤立导航。
- 核心回归：228 项通过（27.071 秒）；随后增加的孤立导航测试包含在上述 6 项专测中。
- Ruff E4/E7/E9/F、模板 validate 和 git diff --check：通过。
- wheel/sdist：637 个资源的字节与执行权限、sdist 重建 wheel、七类模板及前端 SSG/SSR 的安装后生成/配置解析通过。默认 uv 缓存受沙箱限制，最终检查使用可写的 `UV_CACHE_DIR=/tmp/biucing-doc-uv-cache`，没有放宽权限。

原始执行日志：[核心回归](evidence/core.log)、[安装包验证](evidence/distribution.log)。翻译前的文件哈希与核对范围见[结构阶段快照](evidence/structural-workspace-checks.json)，最终工作区身份见[工作区检查记录](evidence/workspace-checks.json)。这份记录不充当独立评审或不可变发布产物证明。

## 内容核对与遗留边界

修正 roadmap 仍以 0.9.0 为 Current、后端摘要与 P4/P5 记录冲突、模板系统仍描述 copytree 生成的问题。旧模板目录示例与内核拆分阶段已转入历史专题；所有旧路径被移除，元数据与 CLI JSON 预期同步。无源码实现、依赖锁、生成项目 Markdown 或生成内容 golden 的修改。

未执行真机/原生 SDK、生产容器、集群故障和正式发布；这些历史验收边界保留。维护正文的双语补齐在下述后续阶段完成；独立评审仍未执行。

最终结论：本次结构迁移、维护正文双语补齐及本地自动检查通过，负责人 project-maintainers；工作区身份以基线提交与检查记录内文件哈希为准。

## 双语补齐阶段检查（2026-10-09，Asia/Shanghai）

- 70 份原单语正文补齐另一语言；最终 218 个 Markdown 文件、109 组中文主文件与英文配对，包括根 README、CHANGELOG 和 docs 全部维护文档。
- 语言切换、同语言导航、索引标题、章节锚点与元信息一致性检查通过；152 个代码块在中英文版本中一致。原生、后端与历史计划的验证范围和未完成项保留。
- 自动检查扩展为全正文配对、owner/status/updated 一致和代码块一致；8 项失败场景测试通过。
- 核心回归 231 项通过（30.179 秒）；Ruff E4/E7/E9/F、模板 validate、git diff --check 通过。
- 安装包验证通过：wheel/sdist/重建 wheel 的 637 项资源字节与执行位一致，七模板及前端 SSG/SSR 的安装后生成与配置解析通过。

新执行日志：[核心回归](evidence/bilingual-core.log)、[安装包验证](evidence/bilingual-distribution.log)。[翻译清单](evidence/translation-inventory.json)记录源快照、语言方向和最终配对范围。结构检查不替代翻译语义核对；本次为作者核对，未执行独立评审或远端 CI。
