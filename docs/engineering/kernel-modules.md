---
title: "内核模块与统一生成"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="kernel-modules-and-unified-generation"></a>
# 内核模块与统一生成

[English](kernel-modules.en.md)

当前 CLI 负责解析、终端策略、命令分派及错误到退出码的映射。`presentation.py` 负责文本/JSON 结果和 schema/生成器版本；`generation.py` 负责规划与执行；支持模块分别负责模型、目录、变量解析、声明、渲染和内置模板规则。历史拆分阶段和兼容决策另有记录。

<a id="current-generation-boundary"></a>
## 当前生成边界

所有模板现在使用统一的资源计划/发布管线。`resources.py` 选择仅公共层或公共层加变体，执行严格路径/类型检查并对所选源生成指纹。`validation.py` 检查有效必需文件、Make 目标和占位符。`generation.py` 创建类型化计划，并统一执行暂存、渲染、权限恢复、发布和清理。`render_template` 仍适配已解析值，不重复输入解析或派生。CLI/模块依赖方向没有改变。

每个正常 GenerationPlan 都包含资源清单和指纹。普通计划仍不在公共 JSON 中包含变体字段。提示之前检查元数据；输入选择资源后检查有效源内容。规划后源发生变化时抛出 GenerationError，需要新计划。指纹检查一致性，不是快照、锁或原子的禁止覆盖发布。

普通模板现在拒绝符号链接、特殊文件以及不安全/冲突路径，在创建时验证完整有效契约，并与变体共用只读文件及失败清理行为。故障注入针对 generation 中的 `shutil.copy2`、`render_text`、`os.replace`，不针对已删除的 copytree 分支。迁移决策和证据见[统一生成](../initiatives/refactor/unified-generation/validation.md)。

<a id="historical-implementation"></a>
## 历史实现

拆分阶段与原始兼容决策保存在[生成内核专题](../initiatives/refactor/generation-kernel/plan.md)，以上当前边界为权威依据。
