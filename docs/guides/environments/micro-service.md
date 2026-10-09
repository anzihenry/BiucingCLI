---
title: "微服务团队环境标准"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="microservice-team-environment-standard"></a>
# 微服务团队环境标准

[English](micro-service.en.md)

> 通用架构及 Docker 开发/部署目标见[后端服务整体架构](../../engineering/backend/architecture.md)。本文件保留既有环境细节；与新目标冲突时以整体架构为准，实际支持仍以生成项目验证为准。

<a id="goal"></a>
## 目标

为中型 Go 微服务团队定义环境，覆盖多服务开发、入职/日常服务间开发、接口/生成/契约一致性、本地依赖编排、可观测/测试/构建/打包。初期采用 Compose 优先流程，保留向大型平台演进的清晰路径。

<a id="design-principles"></a>
## 设计原则

优先小而可靠的本地流程；每个服务独立可理解/运行；尽早统一接口和生成；多服务编排是开发体验的一部分；开发初期具备可观测；区分模板与生产平台职责；使用支持真实协作的最简方案。

<a id="standard-stack"></a>
## 标准技术栈

<a id="core-service-toolchain"></a>
### 服务核心工具链

Go 提供模块/编译/格式/测试；Gin 或 net/http 提供 HTTP 入口；需要强类型服务契约时使用 gRPC；Protobuf 定义接口和生成源；Buf 统一 lint、破坏性变更检查、生成。

<a id="environment-and-tool-installation"></a>
### 环境与工具安装

macOS Homebrew 安装工作站工具；mise 固定 Go、buf 等 CLI。

<a id="local-orchestration"></a>
### 本地编排

Docker Compose 组装服务，Compose Watch 可选同步/重建加快迭代，Makefile 提供稳定命令。

<a id="observability"></a>
### 可观测

OpenTelemetry 提供 trace/metric 基线；Collector 为开发环境接收导出入口。

<a id="dependencies-and-configuration"></a>
### 依赖与配置

每服务使用 Go Modules/校验和锁定；.env/.env.local 保存不提交的机器覆盖；安全 YAML/JSON 默认配置入库。后续确需 Kubernetes 开发循环时才加入 Tilt/Skaffold；Dapr 仅在调用、pub/sub、状态抽象成为明确平台决策时使用。

<a id="tool-responsibilities"></a>
## 工具职责

<a id="go-toolchain"></a>
### Go 工具链

编译测试、模块解析、单服务工作流；不负责跨服务编排、protobuf 治理或依赖启动策略。

<a id="protobuf-and-buf"></a>
### Protobuf 与 Buf

定义 RPC/事件契约、生成类型化代码、执行 lint/兼容检查；不负责运行时传输配置、业务逻辑或替代服务内包设计。

<a id="docker-compose"></a>
### Docker Compose

启动服务/依赖，配置发现和开发默认环境，提供集成本地入口；不能成为单服务唯一运行方式、替代 CI/部署/生产调度，或将基础设施决定全部藏到自定义脚本。

<a id="opentelemetry"></a>
### OpenTelemetry

让开发 trace/metric 可见，为未来工具提供基线；不选择生产供应商，也不替代日志/调试。

<a id="standard-repository-shapes"></a>
## 标准仓库形态

允许两种形态。

<a id="option-a-service-workspace"></a>
### 方案 A：服务工作区

一个仓库拥有多个紧密相关服务时：

```text
.
├── services/
│   ├── gateway/
│   │   ├── cmd/server/
│   │   ├── internal/
│   │   ├── configs/
│   │   ├── go.mod
│   │   └── Dockerfile
│   └── user/
│       ├── cmd/server/
│       ├── internal/
│       ├── configs/
│       ├── go.mod
│       └── Dockerfile
├── api/
│   ├── proto/
│   ├── buf.yaml
│   ├── buf.gen.yaml
│   └── gen/
├── deploy/
│   ├── compose.yaml
│   └── otel-collector.yaml
├── scripts/
│   ├── bootstrap
│   └── doctor
├── Brewfile
├── .mise.toml
├── Makefile
└── README.md
```

<a id="option-b-single-service-repository"></a>
### 方案 B：单服务仓库

每仓库一个可部署服务，但共享契约/本地流程时：

```text
.
├── cmd/server/
├── internal/
├── configs/
├── api/
│   ├── proto/
│   ├── buf.yaml
│   ├── buf.gen.yaml
│   └── gen/
├── deploy/
│   ├── compose.yaml
│   └── otel-collector.yaml
├── tests/
├── scripts/
│   ├── bootstrap
│   └── doctor
├── Brewfile
├── .mise.toml
├── Makefile
├── go.mod
├── go.sum
└── README.md
```

BiucingCLI 初版 micro-service 选择 B，保持可理解，同时统一区别于普通 Web 的契约、可观测和编排。

<a id="directory-rules"></a>
## 目录规则

<a id="api"></a>
### `api/`

存 protobuf 定义和生成配置；.proto/Buf 配置为事实来源。生成代码可提交或统一再生成，但须有明确政策。

<a id="deploy"></a>
### `deploy/`

仅本地编排，compose.yaml 面向开发；不与生产部署清单混合。

<a id="internal"></a>
### `internal/`

传输适配、业务、仓储、配置和编排实现；不手改生成 protobuf。

<a id="scripts"></a>
### `scripts/`

bootstrap/健康检查，可调用 brew、mise、buf、go、docker、make；不能成为隐藏的第二构建系统。

<a id="source-of-truth"></a>
## 事实来源

Brewfile 管工具，.mise.toml 管固定运行时/CLI，api/proto/*.proto 管契约，api/buf.yaml/api/buf.gen.yaml 管 lint/生成，go.mod/go.sum 管依赖锁，deploy/compose.yaml 管本地编排，deploy/otel-collector.yaml 管遥测，Makefile 管开发命令。个人别名、临时容器和复制的生成代码不作事实来源。

<a id="required-root-files"></a>
## 必需根文件

<a id="brewfile"></a>
### `Brewfile`

mise、go、buf、docker、jq；可选 grpcurl、gh。

<a id="misetoml"></a>
### `.mise.toml`

至少固定 go、buf；其他仅实际需要时添加。

<a id="makefile"></a>
### `Makefile`

定义 make bootstrap、doctor、proto、lint、test、verify、run、up、down、logs、docker-build。

<a id="deploycomposeyaml"></a>
### `deploy/compose.yaml`

至少启动服务，按需 postgres/redis 等依赖，以及标准包含的 Collector。初版优先清晰。

<a id="standard-local-workflow"></a>
## 标准本地流程

<a id="first-time-onboarding"></a>
### 首次入职

从 Brewfile 安装工具，mise 激活，依次 bootstrap、doctor、proto、test、up。

<a id="daily-development"></a>
### 日常开发

有意修改契约，proto 再生成，test；单服务迭代 run，跨服务/依赖集成 up，推送前 verify。

<a id="contract-and-code-generation-rules"></a>
## 契约与生成规则

Buf 是 lint/生成唯一入口；入库配置可重复生成；已发布契约的破坏性变更检查进入 CI；不要求开发者记忆 protoc 原始调用。

<a id="observability-rules"></a>
## 可观测规则

每服务结构化日志、健康端点、标准 Collector 开发 trace。指标可以少，但初期就应有埋点路径。

<a id="current-product-positioning"></a>
## 当前产品定位

web-service 保持轻量 HTTP 单服务。此文规划的 micro-service 强化契约优先、默认多服务编排、基础可观测及团队协作环境。

<a id="recommendation"></a>
## 建议

默认 Go/Protobuf/Buf、Compose、OpenTelemetry、Homebrew/mise/Makefile。初版不直接引入 Kubernetes 循环、未验证契约前的 Dapr/mesh，或多空服务大型 monorepo。推进顺序：环境标准、模板设计、带契约/编排/遥测的单服务 starter、验证 run/up 双路径。
