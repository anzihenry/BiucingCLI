---
title: "BiucingCLI 0.9.0 发布准备"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-090-release-prep"></a>
# BiucingCLI 0.9.0 发布准备

[English](validation.en.md)

目标版本：`0.9.0`

验证日期：`2026-09-07`

<a id="scope"></a>
## 范围

加固分发打包、输入解析、预期 CLI 错误、原子生成和安装包验证。

<a id="required-evidence"></a>
## 必需证据

```bash
python3 -m unittest discover -s tests
uvx ruff==0.16.6 check --select E4,E7,E9,F src tests scripts
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli list --json
./scripts/verify-distribution
git diff --check
```

<a id="artifact-contract"></a>
## 产物契约

- wheel/sdist 含七模板定义。
- 隐藏文件和 Android wrapper JAR 保留。
- 干净虚拟环境在仓库外执行 list/validate/create。
- 七模板非交互生成成功。
- doctor 可执行，公共 make help 可用。
- 文本无未解析占位符。

<a id="error-contract"></a>
## 错误契约

- 未知模板/既有目标：退出 2，无调用栈。
- 无效打包元数据：退出 1，无调用栈。
- 生成 I/O 失败清理暂存，不创建目标。
- 意外程序错误对维护者仍可见。

<a id="current-evidence"></a>
## 当时证据

- Python 3.11、3.12、3.13、3.14 各 55 项通过。
- 本地 wheel/sdist 及七模板安装后验证通过。
- macOS 各 Python 版本 CI 通过：[Actions 34115674721](https://github.com/anzihenry/BiucingCLI/actions/runs/34115674721)。

<a id="known-boundaries"></a>
## 已知边界

- 分发关卡验证生成及静态契约，不验证外部 SDK/容器构建。
- 注册表发布是独立操作；选定目的地前仅记录本地仓库安装。
