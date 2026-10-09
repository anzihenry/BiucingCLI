---
title: "BiucingCLI 0.9.0 计划"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-090-plan"></a>
# BiucingCLI 0.9.0 计划

[English](plan.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

目标版本 0.9.0。

<a id="theme"></a>
## 主题

发布与生成内核加固，以安装分发作为主要产品边界。

<a id="goals"></a>
## 目标

wheel/sdist 包含七模板；派生前解析规范输入；预期模板/文件失败转稳定错误；失败无部分目录；源树外跨 Python 验安装 wheel。

<a id="delivery-tracks"></a>
## 交付轨道

<a id="package-owned-resources"></a>
### 包所有资源

移到 src/biucingcli/template_data，明确 backend/src/package-data，验证隐藏/二进制资源。

<a id="deterministic-input-pipeline"></a>
### 确定输入管线

CLI 优先于 set；一次规范；解析 default/default_from；只从解析值计算 Apple/Android/micro 派生；写前校验最终声明变量。

<a id="stable-failure-boundary"></a>
### 稳定失败边界

未知模板、元数据、冲突、生成使用领域错误；用户可修请求/文件冲突退出 2，内置元数据/校验退出 1；开发期非预期编程错误保持可见。

<a id="artifact-verification"></a>
### 产物验证

临时构建，干净 venv 安装，源树外执行，七模板校验生成无需 SDK；CI Python 3.11–3.14。

<a id="non-goals"></a>
## 非目标

不新增模板/改栈，不加外引擎，不动态生成全部 CLI flag，不在包 smoke 跑 Xcode/Android/HarmonyOS/Docker/浏览器。

<a id="release-bar"></a>
## 发布门槛

```bash
python3 -m unittest discover -s tests
uvx ruff==0.16.6 check --select E4,E7,E9,F src tests scripts
PYTHONPATH=src python3 -m biucingcli.cli validate
./scripts/verify-distribution
git diff --check
```

源树外安装 wheel 无法 list/validate/生成七模板即阻断。
