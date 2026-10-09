---
title: "内核重构：阶段 0 基线"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="kernel-refactor-stage-0-baseline"></a>
# 内核重构：阶段 0 基线

[English](baseline.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

基线提交 8ebd568。阶段 0 仅测试/文档，生产 Python、模板资源和依赖锁不变。

<a id="generated-output-contract"></a>
## 生成输出契约

generation-baseline.json 记录 11 案例：七模板、四 Apple 平台、postgres/redis。自由文本含引号、Unicode、XML、反斜杠、美元和占位符形态；输入在 generation_baseline.py。记录 create JSON 和排序的相对路径、目录、精确 SHA-256、执行位；不解码二进制，包含空目录，未来 symlink 单列；排除受环境影响的读写位/归属/时间。

仅规范清单输出路径和生成器版本，文件字节绝不规范，schema 固定；不同临时根重复生成比较。收集器无 fixture 写入选项，直接执行仅 stdout 候选。不能为重构通过重生成预期；产品变化独立评审，哈希只定位，还须看内容解释。

<a id="existing-import-and-fault-injection-boundaries"></a>
## 既有导入和故障注入边界

以下是仓库依赖，不承诺完整公开 SDK。拆分时显式兼容常用导入，mock 按需移到实际执行边界。

| 边界 | 消费者/用途 |
| --- | --- |
| cli:main | console/subprocess/进程内测试 |
| cli.apple_platform_config/default_kotlin_module_name | 派生测试 |
| templates.TemplateVariable/加载/校验/渲染 | CLI/core |
| templates.REQUIRED_COMMAND_CONTRACT | Make 测试 |
| templates.templates_root | 合成 fixture |
| templates.shutil.copytree | I/O/中断清理注入 |
| cli.load_template/validate_templates | JSON 错误注入 |
| builtins.input/stdin.isatty | 交互 |

不通过隐性耦合维持旧 mock 路径。baseline 暂时导入 parser/context/resolver 特征函数，提取后可转新接口。

<a id="current-resolution-order-preserve-do-not-redesign-in-this-refactor"></a>
## 当时解析顺序（保留，不重设计）

1. 加载元数据，trim 项目名，parse set，重复最后胜。
2. 拒绝未声明 set/不支持显式项。
3. 位置项目名优先 set，flag 优先 set；display 两处缺失时由项目合成，当时 source=provided。
4. 声明顺序：trim 非空 provided、字面 default、已解析 default_from、必填；空白回落，default 不 trim，前向不重访，可选未解析省略。
5. 非交互聚合缺失；交互 trim/source=prompted；JSON/非 TTY 不提示。
6. 基于解析值派生，合并，再 Apple 片段/约束。
7. 无写计算路径/步骤/清单。
8. 预览格式化；create 暂存/复制/渲染/发布。target_exists 格式化时观测，不冻结。

前向解析、source 修正、新优先级均不属提取，另追踪行为变更。

<a id="coverage-and-verification"></a>
## 覆盖与验证

baseline 测清单/重复/敏感性/优先级/无写/default/source；CLI 测 golden/字段/派生/预览/冲突/工具；JSON 测 schema/version/golden；errors 测流/参数/EOF/SIGINT/2/130/清理；escaping/configurations 测上下文/parser；distribution 测安装七模板。每阶段 core/静态；具备前提时 platform/Android；资源/生成变化做产物。Linux/macOS Python 3.11–3.14 CI 为跨平台 gate，本地不替代。
