---
title: "BiucingCLI 0.6.1 Worktree 加固任务拆分"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-061-worktree-hardening-task-breakdown"></a>
# BiucingCLI 0.6.1 Worktree 加固任务拆分

[English](plan.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

每阶段为可提交片段，验证后提交再进下一阶段。

<a id="phase-a-plan-and-task-breakdown"></a>
## 阶段 A：规划

<a id="goal"></a>
### 目标

改行为前定标准。

<a id="tasks"></a>
### 任务

加 design/任务，README/路线链接，聚焦现有加固。

<a id="acceptance-criteria"></a>
### 验收标准

不改模板，解释 ready/hardened 差别，片段清晰。

<a id="verification"></a>
### 验证

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
```

<a id="phase-b-unified-worktree-identity"></a>
## 阶段 B：统一身份

<a id="goal-1"></a>
### 目标

七模板一个模型。

<a id="tasks-1"></a>
### 任务

每 Make 加 LABEL，ROOT 统一为：

```make
WORKTREE_ROOT ?= $(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
```

ID 为 ROOT 八字符哈希且可覆；SLUG 运行名加 ID；info 显四变量；更新文档/测试。

### 验收标准

原生/Docker 同公式、手动 ID、全模板测试。

### 状态

完成；原生改 Git root/哈希，LABEL 可读，ID 可覆，文档区分。

### 验证

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
```

至少 Docker/原生各一：

```bash
make worktree-info
WORKTREE_ID=manual make worktree-info
```

本阶段 smoke：

```bash
PYTHONPATH=src python3 -m biucingcli.cli create frontend id-frontend --output-dir /tmp/biucing-061-phase-b.VL9zNf --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create apple id-apple --output-dir /tmp/biucing-061-phase-b.VL9zNf --platform ios --bundle-identifier com.example.idapple --organization-name Example --development-team ABCDE12345
```

两者默认哈希，manual 覆盖有效。

## 阶段 C：端口建议

### 目标

检测占用并建议。

### 任务

Make 小模式；frontend DEV_HOST_PORT/HOST_PORT，Web HOST_PORT，micro HOST_HTTP_PORT/HOST_GRPC_PORT/HOST_DEPENDENCY_STORE_PORT/HOST_OTEL_GRPC_PORT/HOST_OTEL_HTTP_PORT；worker 无端口；可复制建议。

### 验收标准

启动前警告，不改文件，默认警告可理解。

### 状态

完成；lsof 可用时检测，建议仅提示，worker 无端口。

### 验证

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
```

临时目录用 python3 -m http.server 18080 监听，确认报告。本轮 smoke：

```bash
python3 -m http.server 19173 --bind 127.0.0.1
PYTHONPATH=src python3 -m biucingcli.cli create frontend port-frontend --output-dir /tmp/biucing-061-phase-c.MK2u8I --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create microservice port-micro --output-dir /tmp/biucing-061-phase-c.MK2u8I --module-name github.com/example/port-micro --proto-package port.micro.v1 --non-interactive
make worktree-doctor DEV_HOST_PORT=19173 HOST_PORT=19174
make worktree-doctor HOST_HTTP_PORT=19173 HOST_GRPC_PORT=19174 HOST_DEPENDENCY_STORE_PORT=19175 HOST_OTEL_GRPC_PORT=19176 HOST_OTEL_HTTP_PORT=19177
```

两工程报告 19173 占用及覆盖建议。

## 阶段 D：Docker doctor

### 目标

无侵入 config 检查。

### 任务

四模板加目标，经 COMPOSE 执行 DEV_COMPOSE_FILE config；doctor 指向/调用；缺 Docker 明确；文档/测试。

### 验收标准

不启动，使用当前 project，四模板可用。

### 状态

完成；doctor 指向但不强迫每次 Docker，缺工具明确。

### 验证

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
```

生成工程：

```bash
make worktree-compose-config WORKTREE_ID=alpha
```

本轮：

```bash
PYTHONPATH=src python3 -m biucingcli.cli create frontend config-frontend --output-dir /tmp/biucing-061-phase-d.2Lmlls --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create worker config-worker --output-dir /tmp/biucing-061-phase-d.2Lmlls --module-name github.com/example/config-worker --non-interactive
make worktree-compose-config WORKTREE_ID=alpha DEV_HOST_PORT=15173
make worktree-compose-config WORKTREE_ID=alpha
```

两工程 config 显独立 project/卷。

## 阶段 E：原生证据

### 目标

精确可重复、不夸 SDK 覆盖。

### 任务

矩阵分 static/doctor/real-build，清单、三端命令、必需/可选规则。

### 验收标准

准确实际执行，make -n 非构建，SDK 限制可见。

### 状态

完成；结构、manifest、身份、签名、设置、依赖、构建测试目标变化必须真实构建；清单记录 tier/SDK。

### 验证

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
```

## 阶段 F：Harmony 身份决定

### 目标

是否安全可选临时 bundle 改写。

### 任务

检查 profile/metadata；安全写临时忽略输出，否则暂缓并保留诊断；文档/证据。

### 验收标准

源 AppScope 稳定，边界明确，不提交 signing/profile。

### 状态

完成决定：0.6.1 暂缓；源拥有 bundleName；worktree-debug-identity 只读打印基础/请求/诊断名/hvigor 属性；证据不暗示属性重写应用。

### 验证

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
```

## 阶段 G：发布准备

### 目标

变更落地后准备证据。

### 任务

专版 validation、文档表面、仓库检查、七工程加固验证。

### 验收标准

所有行为覆盖、限制记录、准备提交后干净工作区。

### 状态

完成；记录七模板/config/分级/Harmony 边界；更新入口。正式版本/tag/push/GitHub Release 留发布操作。

### 验证

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli list --json
```

## 建议提交片段

1. docs: plan worktree hardening 0.6.1
2. feat: unify worktree identity across templates
3. feat: add worktree port conflict advisors
4. feat: strengthen docker worktree diagnostics
5. docs: harden native worktree evidence matrix
6. docs: decide harmonyos debug identity boundary
7. docs: prepare 0.6.1 release evidence

## 风险登记

| 风险 | 缓解 |
| --- | --- |
| 哈希难读 | LABEL 人/ID 隔离 |
| 用户要语义 ID | 可覆 |
| 端口跨平台 | lsof 可用则用，否则明确提示 |
| 诊断慢 | 本地无侵入无容器 |
| 缺 Docker | 明确报错 |
| 构建依赖环境 | 三层证据 |
| Harmony 改写不安全 | 保持稳定源/暂缓 |
