---
title: "微服务模板设计"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="microservice-template-design"></a>
# 微服务模板设计

[English](design.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

> 历史 starter 设计。2026-09-26 后的生产目标见[后端整体架构](../../../engineering/backend/architecture.md)和 [Micro Service 架构](../../../engineering/backend/micro-service.md)，早期范围限制不代表新目标。

<a id="goal"></a>
## 目标

定义 micro-service 首个实现目标：符合[微服务环境标准](../../../guides/environments/micro-service.md)的契约感知 Go starter，而非完整平台。

<a id="position-in-product-scope"></a>
## 产品范围定位

micro-service 面向内部服务/机器契约；web-service 面向客户 HTTP。身份授权边界不同。Web 保持客户入口，protobuf/生成/编排增加真实复杂度，须以更好的团队协作证明价值。

<a id="first-version-outcome"></a>
## 初版结果

生成 Go/protobuf、Buf 可重复生成、Makefile/bootstrap/doctor、服务与一个依赖的 Compose、Collector、解释单服务和编排的 README。不生成服务舰队、Kubernetes、mesh、大平台或所有传输模式。

<a id="recommended-stack"></a>
## 建议技术栈

Go、Gin、Protobuf、Buf、Compose、OpenTelemetry，实用且契约优先。

<a id="template-metadata-proposal"></a>
## 模板元数据提案

建议 templates/micro-service/template.json：

```json
{
  "name": "micro-service",
  "description": "Go microservice starter with Protobuf, Buf, Compose, and OpenTelemetry",
  "stack": ["Go", "Gin", "Protobuf", "Buf", "Docker Compose", "OpenTelemetry"],
  "variables": [
    { "name": "project_name", "required": true },
    { "name": "module_name", "required": true, "prompt": "Go module name: " },
    { "name": "service_name", "required": false, "default_from": "project_name" },
    { "name": "proto_package", "required": true, "prompt": "Proto package: " },
    { "name": "http_port", "required": false, "default": "8080" },
    { "name": "grpc_port", "required": false, "default": "9090" },
    { "name": "dependency_store", "required": false, "default": "postgres" },
    { "name": "otel_exporter_endpoint", "required": false, "default": "http://otel-collector:4318" }
  ],
  "next_steps": [
    "make bootstrap",
    "make doctor",
    "make proto",
    "make test",
    "make run",
    "make up"
  ]
}
```

<a id="variable-design"></a>
## 变量设计

<a id="core-variables"></a>
### 核心变量

project_name 为目录，module_name 为 Go module，service_name 为部署名/Compose key，proto_package 如 user.v1。

<a id="runtime-variables"></a>
### 运行变量

http_port 为健康/admin/gateway 端口，grpc_port 为内部 RPC，dependency_store 为 postgres/redis 等初始依赖，otel_exporter_endpoint 为本地导出。

<a id="placeholder-proposal"></a>
## 占位符提案

遵守简单替换。占位符：PROJECT_NAME、MODULE_NAME、SERVICE_NAME、PROTO_PACKAGE、HTTP_PORT、GRPC_PORT、DEPENDENCY_STORE、OTEL_EXPORTER_ENDPOINT（双花括号形式）。

<a id="directory-shape"></a>
## 目录结构

建议输出：

```text
my-microservice/
  README.md
  Brewfile
  .mise.toml
  Makefile
  Dockerfile
  cmd/
    server/
      main.go
  internal/
    config/
    handler/
    service/
    repository/
    router/
    transport/
    telemetry/
  api/
    proto/
      {{SERVICE_NAME}}/v1/
        service.proto
    buf.yaml
    buf.gen.yaml
    gen/
  configs/
    config.yaml
  deploy/
    compose.yaml
    otel-collector.yaml
  scripts/
    bootstrap
    doctor
  tests/
```

<a id="module-and-directory-responsibilities"></a>
## 模块与目录职责

<a id="cmdserver"></a>
### `cmd/server`

启动、依赖组装、HTTP/gRPC 引导。

<a id="internaltransport"></a>
### `internal/transport`

传输适配、请求响应转换、按需 gRPC 注册助手。

<a id="internaltelemetry"></a>
### `internal/telemetry`

OTel 设置、tracer/meter 初始化、共享集成。

<a id="apiproto"></a>
### `api/proto`

契约、请求响应 schema、版本命名空间。

<a id="build-and-generation-strategy"></a>
## 构建与生成策略

proto 调用 buf generate；lint 执行 Go/Buf lint；test 跑 Go；verify 执行 doctor/契约校验/lint/test；run 宿主单服务；up Compose。初版避免 README 原始 protoc、过多自定义脚本、多语言输出、多参数动态分支。

<a id="compose-expectations"></a>
## Compose 要求

服务、一个依赖、Collector；保持小且可读，说明开发拓扑，不冒充完整生产。

<a id="readme-expectations"></a>
## README 要求

说明工具、bootstrap、Buf、run/up 区别、契约/生成代码/遥测位置和事实来源；不默认承诺 Kubernetes/生产部署。

<a id="first-version-validation-plan"></a>
## 初版验证计划

健康样例应能 bootstrap、doctor、proto、test、run，以及 `docker compose -f deploy/compose.yaml up --build`。

<a id="relationship-to-web-service"></a>
## 与 web-service 的关系

按所有权/调用者选择。Web 拥有客户 HTTP/API/登录边界；micro 拥有内部能力、protobuf/gRPC 和自身数据。Web 调用 micro 时消费版本化客户端适配；micro 拥有契约/服务端。不能跨入对方 internal 或数据库。

[Web 架构](../../../engineering/backend/web-service.md)定义生产目标：workload identity/mTLS 验证服务；明确授权的 Web 可传可信用户 (issuer, subject)；micro 同时授权调用服务/方法和用户对资源操作。deadline、有界重试、trace、契约兼容、独立发布、下游失败属于边界。此历史阶段仅 Ping，没有生产认证或真实数据库业务。

<a id="cross-template-integration-acceptance"></a>
### 跨模板集成验收

1. 生成两工程，Web 消费固定发布契约，经 gRPC 客户端调用。
2. micro 仅接受 mTLS 预期身份；缺失、不可信、错误客户端证书在业务前失败。
3. 授权 Web 断言用户 (issuer, subject)，micro 施加对象授权；即便服务被允许，不同用户也不能取数据。
4. deadline/cancel 到服务端；依赖不可用映射稳定外部错误，不泄漏地址/详情。
5. 读重试有界，写在重试前须幂等设计；trace 关联外部/internal。
6. 兼容 protobuf 独立发布，破坏变更发布前契约检查失败。

本地 fixture 可生成临时 CA/workload 证书；生产签发、轮换、网络政策、信任域由部署环境提供并列为配置要求。不提交生产私钥，不默认生产明文 gRPC。

<a id="recommended-delivery-sequence"></a>
## 建议交付顺序

按调用者/业务所有权保持区分；micro 作为第二后端模板；单一路径/最少分支；用真实 make/Compose 验证后标就绪。
