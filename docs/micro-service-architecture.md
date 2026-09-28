# Micro Service 架构文档

状态：2026-09-26 通用后端重设计的内部服务入口规范，待实现。
共同组件、Docker 开发/部署、运行与验收以[后端服务整体架构](backend-service-architecture.md)为准。
旧[模板设计](microservice-template-design.md)保留作 starter 阶段的历史说明。

## 定位

`micro-service` 生成面向其他获准服务的 Go 服务项目；默认业务协议是 gRPC，契约由 Protobuf/Buf 管理。
每个项目可以独立发布、扩缩容，并按需要持有数据或调用其他服务。
其生产质量要求与 Web Service 一致，入口身份和协议有所不同。

## 专有组件

| 组件 | 目标契约 |
| --- | --- |
| RPC 服务端 | grpc-go 注册、请求校验、大小/并发限制、截止时间、取消及受控错误 |
| 拦截器 | unary/stream 请求 ID、trace、日志、认证、方法授权、指标和恢复 |
| 服务身份 | mTLS，校验对端工作负载身份、方法权限、证书有效期和信任范围 |
| 用户上下文 | 仅获准的调用服务可断言用户主体；资源权限由接收方检查 |
| 内部契约 | 版本化 proto、固定生成工具、Buf lint/breaking、固定客户端契约版本 |
| 出站调用 | 与 Web 相同的 HTTP/gRPC 客户端、依赖配置、连接管理和可靠性预算 |
| 数据 | PostgreSQL 适配与迁移可启用；无持久状态的服务不强制启动数据库 |
| 运行与诊断 | gRPC health，独立 HTTP 运维端口；reflection、pprof 默认受限 |

mTLS 建立服务身份，不自动授予所有 RPC 权限。服务身份、用户主体和观测上下文分别处理。
证书签发与轮换由部署环境提供，应用提供安全加载/更新机制；本地测试证书不得成为生产凭据。
有代理终止 mTLS 时必须明确可信身份如何交付应用并阻止绕过代理，不能信任任意身份请求头。

Micro Service 默认不会接收浏览器 Cookie、承担公开登录页面或发布公网业务端口。
需要对外暴露能力时，由 Web Service 提供公开契约和相应用户身份边界。

## Docker 运行

- 开发：开发容器、Buf 工具链、本地测试 CA/工作负载证书；数据和遥测设施按需求启用。
- 单机生产：镜像 digest、内部网络、生产证书与配置文件；RPC/运维口默认不映射公网。
- 多机：相同镜像和身份契约，独立实例组，验证发现、重连及实际 RPC 负载分布。
- 与其他生成项目组合时，显式配置共享通信网络和目标服务名；不同 Compose 项目不会自动互通。

## 验收与实现现状

除通用运行验收，还需证明错误身份/过期证书被拒、证书轮换、用户上下文授权、
截止时间和取消、客户端固定版本消费、旧新服务兼容、重复安全操作及下游隔离。

P1 已实现统一 Docker 工作流、配置与文件密钥校验、HTTP/gRPC unary/stream 请求预算、
Principal/Policy 默认拒绝策略、私有管理口、有限退出和结构化日志。保留 Buf、trace provider 和本地 Collector。
P2 已接入 mTLS 工作负载身份、方法/委托授权、证书重载与真实 pgx/独立迁移，
以及实际 Proto baseline 的 breaking 检查。P3 已加入出站客户端、指标与链路观测；P4 已提供独立生产 Compose、内网 mTLS 部署和签名镜像发布；多机高可用仍属 P5。
详见 [P2 验证记录](backend-service-p2-verification.md)。

P3 实现边界与互调验证见 [P3 验证记录](backend-service-p3-verification.md)。

P4 单机部署、供应链和恢复边界见 [P4 验证记录](backend-service-p4-verification.md)。

P5 已提供 Kustomize、集群发布/回退和容量契约，真实节点/AZ/托管数据库切换仍待 B27；见 [P5 验证记录](backend-service-p5-verification.md)。
