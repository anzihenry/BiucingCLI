---
title: "BiucingCLI 0.10.0"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-0100"></a>
# BiucingCLI 0.10.0

[English](notes.en.md)

0.10.0 扩展前端渲染、原生二进制组件和后端交付，并加强生成与安装包验证。

<a id="highlights"></a>
## 亮点

- 前端：CSR、SSG、SSR 预设，共享 React Router 工具链、生产镜像、浏览器检查和安装包验收。
- Apple：iOS、macOS、watchOS、tvOS 壳，消费版本化静态 XCFramework、SafeDI 构造图和共享 C++20 核心。
- Android：手机、Wear OS、TV 壳，Maven AAR 组件、Dagger 图、JNI 会话；HarmonyOS 新增二进制 HAR 和 Node-API 桥。
- 后端：Docker 优先开发、配置验证、健康/管理端点、优雅关闭、PostgreSQL 迁移、Web OIDC 会话、Micro mTLS 身份、有界出站调用和 OpenTelemetry 集成。
- 交付：加固的生产 Compose、签名镜像验证、迁移/回退工具、隔离备份恢复检查，以及 Kubernetes/Kustomize 参考。
- CLI：版本化 JSON 结果/错误、更强输入转义和校验、确定性资源变体、精确 wheel/sdist 资源验证。

<a id="compatibility-changes"></a>
## 兼容变化

- `microservice` 改名为 `micro-service`，移除旧名称。
- 移除 `--dependency-store` / `dependency_store`，独立选择 `--database`、`--cache`；Micro 默认均不启用，Web 必需 PostgreSQL。
- 移除 Web 内存用户 CRUD 示例，生成后端为业务 API 提供通用基础设施和认证底座。
- Apple 要求 Swift 6.4+；前端使用生成文件中固定的工具链版本。

已生成的项目不会自动迁移。在既有项目采用新模板前，应检查生成结果和架构指南。

<a id="install"></a>
## 安装

```sh
uv tool install biucingcli==0.10.0
# For an existing uv tool installation:
uv tool upgrade biucingcli
biucing --version
biucing list
```

<a id="verification-boundaries"></a>
## 验证边界

使用 core/platform 测试、安装后 wheel/sdist 检查及生成前端/后端验证。原生构建和模拟器证据记录在仓库中，设备覆盖按平台不同。HarmonyOS 真机和签名交付仍为独立关卡。

Kubernetes 文件是参考部署。**B27 真实跨可用区高可用验收暂停**，不宣称实测生产 HA、RPO、RTO，证据见[版本验证](validation.md)。
