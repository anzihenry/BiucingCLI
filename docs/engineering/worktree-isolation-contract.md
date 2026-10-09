---
title: "Worktree 隔离契约"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="worktree-isolation-contract"></a>
# Worktree 隔离契约

[English](worktree-isolation-contract.en.md)

本契约定义 BiucingCLI 所说的 worktree 优先 starter，适用于生成工程。目标是让开发者同时使用同一仓库的多个 Git worktree 时，starter 仍可靠运行。

<a id="user-promise"></a>
## 用户承诺

生成工程应支持多 worktree 并行而不会意外干扰。至少可以在一个 worktree 开发、另一个测试、第三个构建/打包；在一处解析安装依赖而不改变另一处缓存或安装状态；使用不经 Git 共享的本地签名/环境文件；清理一处运行状态而不损坏另一处。

<a id="identity-model"></a>
## 身份模型

各 starter 应公开 worktree 身份：

| 变量 | 含义 |
| --- | --- |
| `WORKTREE_ID` | 当前 worktree 的简短稳定标识 |
| `WORKTREE_SLUG` | 可读的运行名称前缀，通常为项目名加 `WORKTREE_ID` |

默认推导应确定且本地完成：基于当前 worktree 根路径，长度适合 Docker、应用 ID 和文件名；允许环境变量或 Make 变量覆盖；不能只依赖可能过长、复用或含特殊字符的分支名。建议默认结构：

```makefile
WORKTREE_ROOT ?= $(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
WORKTREE_ID ?= $(shell printf '%s' "$(WORKTREE_ROOT)" | shasum | cut -c1-8)
WORKTREE_SLUG ?= {{PROJECT_NAME}}-$(WORKTREE_ID)
```

模板可按平台调整哈希命令，覆盖行为应一致。

<a id="required-commands"></a>
## 必需命令

平台允许时，各 starter 提供：

```bash
make worktree-info
make worktree-doctor
make clean-worktree
```

<a id="make-worktree-info"></a>
### `make worktree-info`

打印当前隔离值，包括适用的根目录、`WORKTREE_ID`、`WORKTREE_SLUG`、Compose 项目名、镜像标签、宿主端口、缓存路径、依赖安装/模块缓存路径、构建输出路径、原生应用标识或后缀、本地配置文件。不得打印秘密，可以报告秘密文件是否存在。

<a id="make-worktree-doctor"></a>
### `make worktree-doctor`

检查可能冲突及缺失的本地前提：常用默认宿主端口、可能意外共享的全局缓存路径；报告适用的 `.env.local`、`local.properties` 是否存在，以及已安装 Debug 应用的身份选择。避免网络访问和重型构建。

<a id="make-clean-worktree"></a>
### `make clean-worktree`

仅清理当前 worktree 所有的状态：本 Compose 项目的容器、网络、卷，根目录下的项目缓存和构建输出，以及独立预览/测试报告。默认禁止清理全局镜像、SDK、Gradle/Xcode/pnpm/ohpm/Go 缓存、工程根目录以外文件，以及签名或含秘密配置。需要更强清理时，使用明确的独立目标（如 `clean-all-local`）并说明风险。

<a id="isolation-dimensions"></a>
## 隔离维度

各模板声明并实现适用维度：

| 维度 | 适用范围 | 契约 |
| --- | --- | --- |
| 运行名称 | Docker、原生 | 容器、Compose 项目、镜像和已安装应用身份默认不冲突 |
| 端口 | 长期运行服务 | 宿主端口可覆盖且可诊断 |
| 依赖服务 | 服务模板 | 数据库、Redis、OTel 等按 Compose 项目、网络、卷隔离 |
| 缓存 | 全部 | 可能损坏、减慢或混淆工作流的缓存/安装状态使用项目或 worktree 本地路径 |
| 生成输出 | 全部 | 平台无额外要求时，构建及生成文件位于 worktree 根目录下 |
| 本地配置 | 全部 | `.env.local`、`local.properties`、签名等机器本地文件被 Git 忽略 |
| 安装应用身份 | 原生 | 需要并行安装时，Debug 支持独立 worktree 身份 |
| 清理 | 全部 | 清理目标限定当前 worktree |
| 诊断 | 全部 | 显示隔离决策 |

<a id="docker-first-requirements"></a>
## Docker 优先要求

适用于 `frontend`、`web-service`、`micro-service`、`worker`：通过 worktree 感知的 `COMPOSE_PROJECT_NAME` 执行 Compose；避免跨 worktree 硬编码共享卷；默认镜像标签含 `WORKTREE_SLUG` 或明确限定本 worktree；发布的宿主端口均为 Make 变量并说明并行覆盖方法；依赖服务属于独立 Compose 项目；语言缓存和依赖安装目录限定项目/worktree；`clean-worktree` 只对当前项目执行 `docker compose down --remove-orphans --volumes`。

建议命名：

```makefile
COMPOSE_PROJECT_NAME ?= $(WORKTREE_SLUG)
IMAGE ?= $(WORKTREE_SLUG)
TAG ?= dev
```

Compose 命令传入：

```bash
COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) docker compose -f $(DEV_COMPOSE_FILE) ...
```

<a id="native-requirements"></a>
## 原生要求

适用于 `apple`、`android`、`harmonyos`：本地签名文件位于 worktree 且被忽略；`worktree-info` 显示构建/缓存路径；避免根目录外分支共享生成输出；说明是否支持并行安装 Debug 应用；平台支持时提供应用身份后缀覆盖。

| 模板 | 重点 |
| --- | --- |
| `apple` | Xcode DerivedData、SwiftPM 输出、Tuist 缓存/输出、Debug bundle identifier 后缀 |
| `android` | Gradle user home/构建缓存/依赖元数据、Debug `applicationIdSuffix`、`local.properties`、模拟器安装行为 |
| `harmonyos` | `.hvigor`、ohpm home、`oh_modules`、构建输出、本地签名；仅在 DevEco/hvigor 良好支持时增加 bundle-name 后缀 |

<a id="metadata-contract"></a>
## 元数据契约

阶段 B 为每个模板添加 worktree 元数据。建议：

```json
{
  "worktree": {
    "support_level": "planned",
    "isolation_dimensions": [
      "runtime-names",
      "ports",
      "caches",
      "local-config"
    ],
    "diagnostics": [
      "make worktree-info",
      "make worktree-doctor"
    ],
    "cleanup": [
      "make clean-worktree"
    ]
  }
}
```

`support_level` 允许 `planned`（纳入推进但未实现）、`partial`（部分实现且有缺口）、`worktree-ready`（满足契约）。`isolation_dimensions` 包括 `runtime-names`、`ports`、`dependency-stores`、`caches`、`generated-output`、`local-config`、`installed-app-identity`、`cleanup`、`diagnostics`。

<a id="verification-contract"></a>
## 验证契约

仓库验证始终包括：

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
```

生成工程最低验证：

```bash
make worktree-info
make worktree-doctor
```

Docker 优先模板还应提供快速身份检查：

```bash
WORKTREE_ID=alpha make worktree-info
WORKTREE_ID=beta make worktree-info
WORKTREE_ID=alpha docker compose -f compose.dev.yaml config
WORKTREE_ID=beta docker compose -f compose.dev.yaml config
```

原生模板额外检查可能冲突的诊断值：Apple 的 DerivedData/bundle identifier，Android 的 Gradle 缓存/Debug application ID，HarmonyOS 的 hvigor/ohpm 输出和本地签名文件状态。

<a id="non-goals"></a>
## 非目标

本契约不要求 CLI 创建/删除 Git worktree、通过守护进程协调、通过注册中心动态分配端口、管理外部云资源、自动迁移旧生成工程，或清理全局工具缓存。
