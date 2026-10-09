---
title: "Web Service 架构文档"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# Web Service 架构文档

[English](web-service.en.md)

历史状态（2026-09-26）：本页定义通用后端重设计的 Web 入口规范，当时待实现。后续状态见[任务与阶段证据](../../initiatives/feature/backend-services/plan.md)。
共同组件、Docker 开发/部署、运行与验收以[后端服务整体架构](architecture.md)为准。
本版取代此前围绕业务示例展开的设计；保留终端用户、OIDC、会话、PostgreSQL 和内部调用边界。

## 定位

`web-service` 生成面向浏览器和移动端的 Go HTTP API 项目。
服务拥有公开 API、用户身份入口和自身应用模块；有需要时通过 gRPC 调内部服务。
生成物不含浏览器前端，前端通过契约接入。它可以独立运行，不必依赖 Micro Service。

## 专有组件

| 组件 | 目标契约 |
| --- | --- |
| HTTP | Gin 路由、请求校验、大小限制、超时、请求 ID、trace、稳定错误格式 |
| 公开 API | OpenAPI、版本和兼容检查；分页、幂等、并发版本工具按接口语义使用 |
| 用户认证 | 外部 OIDC；浏览器服务端会话，移动端授权码 + PKCE 后使用 access token |
| 浏览器会话 | PostgreSQL 共享存储、过期与撤销、HttpOnly/Secure Cookie、CSRF；本地例外显式配置 |
| 授权入口 | 将可信 Principal 传至应用；默认拒绝，具体资源/租户/角色由使用模板的项目定义 |
| 浏览器防护 | 显式 Origin/CORS、受信代理配置、Host 和请求限制；不信任客户端伪造的转发头 |
| 出站调用 | 统一 HTTP/gRPC 客户端，mTLS 内部调用、预算、错误转换和故障隔离 |
| 运维入口 | live/ready、指标、版本和受控诊断；不暴露到用户 API 路由 |

会话入口可与 API 同进程部署，由服务端完成 OIDC 登录交换；纯本服务访问无需长期保留 IdP 令牌。
新增下游令牌代调用时再设计保管和续期。对外身份使用 `(issuer, subject)`，不能以 email 当唯一稳定标识。
使用现有可信密钥验证的有效令牌/有效会话可在 IdP 短时故障时继续使用；新登录/刷新失败，不能绕过验证。

## Docker 运行

- 开发：开发容器、热重载、PostgreSQL、仅本地测试 IdP；观测等设施按 profile 启用。
- 单机生产：反向代理提供 TLS，API 使用固定镜像；数据与会话持久化，密钥挂载注入。
- 多机：同一镜像多副本，共享外部会话/数据服务；按整体架构的 HA 参考部署。
- 安全默认配置必须保证用户 API、内部依赖、管理端口有不同的暴露范围。

## 验收与实现现状

通用故障验收外，还需覆盖 OIDC 发行方/受众/过期验证、会话跨副本与撤销、CSRF/CORS、
未知用户主体拒绝、出站调用失败时的稳定公开响应。架构验收使用协议与依赖测试，不绑定某个业务示例。

P1 已实现统一 Docker 工作流、配置与文件密钥校验、HTTP 请求预算和默认拒绝策略、私有管理口、有限退出和结构化日志。
P2 已移除内存用户示例，接入 OpenAPI、OIDC、pgx/独立迁移及 PostgreSQL 会话。会话采用固定期限，
登录后丢弃提供方令牌，不请求或保存 refresh token；会话到期重新登录。P3 已加入出站客户端和 OTel 仪表化；P4 已提供独立生产 Compose、Caddy TLS、签名镜像发布、回退与备份恢复入口。
详见 [P2 验证记录](../../initiatives/feature/backend-services/p2-validation.md)。

P3 实现边界与互调验证见 [P3 验证记录](../../initiatives/feature/backend-services/p3-validation.md)。

P4 单机部署、供应链和恢复边界见 [P4 验证记录](../../initiatives/feature/backend-services/p4-validation.md)。

P5 已提供 Kustomize、集群发布/回退和容量契约，真实节点/AZ/托管数据库切换仍待 B27；见 [P5 验证记录](../../initiatives/feature/backend-services/p5-validation.md)。
