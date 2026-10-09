---
title: "BiucingCLI 0.9.0"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-090"></a>
# BiucingCLI 0.9.0

[English](notes.en.md)

加固安装后分发和生成内核。

<a id="highlights"></a>
## 亮点

- 七模板打入 wheel/sdist，不依赖源码仓库布局。
- Apple、Android、Micro 派生值只在 CLI/--set 输入规范化与解析后计算。
- 未知模板、损坏元数据、目标冲突、生成 I/O 失败使用简明稳定错误。
- 项目在相邻临时目录渲染，全部文件完成后才发布。
- CI 覆盖 Python 3.11–3.14，在源码树外检查干净 wheel 安装。

<a id="compatibility"></a>
## 兼容性

命令、模板名、专用 create 选项、--set 优先级和成功 JSON 保留。apple_platform_name 改为系统派生值，不再是用户可设置输入。

传入的 --output-dir 必须存在且为目录，暂存前明确路径错误。

<a id="verification"></a>
## 验证

安装包、错误契约和证据见 [0.9.0 发布准备](validation.md)。
