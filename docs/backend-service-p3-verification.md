# 后端服务 P3：调用与可观测性

状态：2026-09-27 已完成 B16–B19。P4 单机生产交付和 P5 高可用尚未完成。

## 实现边界

两种模板提供相同的 `internal/outbound`：配置命名依赖、启动创建、退出关闭；默认无下游。
HTTP 使用复用 Transport、固定 HTTPS origin、有限响应体，不跟随重定向。
gRPC 消费者使用对方公开生成 API，基于 `dns:///` + round_robin，验证 CA、DNS、serverAuth 与精确 SPIFFE URI。
证书和根在新握手重读；既有连接的紧急撤销依赖排空/重建，不声称轮换文件立即撤销旧连接。

每个依赖独立并发隔离、无等待队列、总预算/每尝试预算、取消传递、最多三次显式幂等重试和 full jitter。
未知操作拒绝；非幂等操作必须单次，错误和取消不转换为伪成功。
熔断是有界实现的接入接口，默认不开启；全局配额、业务幂等和 streaming 仍是按需扩展。
只从已验证 Principal 转发用户上下文，不复制 Cookie、Authorization、入站 metadata 或 baggage；下游逐跳授权。

HTTP/gRPC 入口、出站尝试与 PG 查询都有 OTel span，访问日志带 trace/span ID。
指标覆盖流量、错误、时延、在途量、依赖拒绝/重试、数据库连接池和遥测导出失败。
固定路由/操作标签；不记录 SQL、参数、身份、凭据或错误原文。SDK 采样、队列、基数、导出与退出均有预算。
Collector 为可选接收/转发组件，不参与 readiness；开发 debug 输出及告警示例已提供，不预置长期存储。

## 验证入口

- `scripts/verify-backend-calls --output-dir <新目录>`：独立生成两个非默认 module 的项目；分别构建开发/运行镜像，
  使用公开 Proto API 消费。本地 PostgreSQL、Dex、测试 CA 和 Collector 构成真实验证环境。
- `scripts/fixtures/backend-p3` 仅被 harness 复制，不属于模板资源；其用户回显和故障控制路径不会出现在默认 API。
- harness 验证无用户/伪造头、真实 OIDC 会话、mTLS 与正确用户主体、有效证书但方法未授权、无委托权限、
  取消、下游暂停/重启、证书轮换、IdP 故障与 Collector 故障，并比对实际导出的 trace ID 和两服务日志。
- `scripts/verify-backends` 保留生成项目标准入口：静态检查、race tests、协议、编译，以及启用 PG 时真实数据/会话集成。
- 出站测试覆盖 CA/DNS/URI 校验、无证书拒绝、证书/根轮换、重试分类、deadline、容量隔离、metadata 清洗。
- `.github/workflows/backends.yml` 新增独立互调 job，只上传证据/日志/OTLP 文件，不上传测试密钥或 cookie。

## 验证记录

环境：Docker Desktop 4.92.0、Engine 29.8.0、Compose 5.5.1，Linux arm64，Go 1.26.8。
本机临时证据可能被系统清理，持续回归入口保留在仓库。远端 amd64 CI 尚未运行。

| 验证 | 结果与证据 |
| --- | --- |
| 独立 Web/Micro 互调 | `/tmp/biucing-p3-calls-v5/evidence.json`：11 项全部通过；包含真实 OIDC、独立运行镜像、mTLS、授权/委托、超时/取消、重启、轮换及 IdP/Collector 故障 |
| 实际遥测 | 同目录 `otel/traces.json`、`otel/metrics.json` 与 `service.log`：HTTP→RPC 的 trace ID 与两服务日志匹配，包含 PG span/池指标 |
| Web 标准流程 | `/tmp/biucing-p3-matrix/web.log`：lint、race、OpenAPI、编译、真实 PG/迁移/会话通过 |
| 修复后出站测试 | `/tmp/biucing-p3-dev/dns-cancel-final.log`：race 与静态检查通过；含 DNS 地址切换、在途取消及客户端凭据/预算负例 |
| Micro + PostgreSQL | `/tmp/biucing-p3-micro-data-final/evidence.json`：完整生成项目验证通过，含 Buf、静态检查、race、编译和真实 PG/迁移 |
| CLI/生成 | `/tmp/biucing-p3-core-final.log`：203 项核心测试通过，包含所有生成组合及字节级 golden |
| 安装包 | `/tmp/biucing-p3-distribution.log`：wheel、sdist 重建、安装及全部七模板/配置检查通过 |

Ruff、模板 validate 与差异空白检查通过。测试容器、网络和数据卷已清理；保留本机证据及构建缓存。
本轮没有重复 P2 的所有 Redis Docker 组合或双 worktree 演练；缓存适配仍属 E01，所有组合的生成基线已回归。

首轮发现并修复 gRPC 取消错误未规范为 Canceled、harness 数据库主机/独立模块构建上下文问题；
这些失败记录保留，只有上述最终证据计为通过。额外直接运行转义测试文件时，Swift 平台用例受宿主沙箱限制失败；
P3 的标准核心测试入口已通过，不将该额外平台检查计为通过。

## 运行限制与技术依据

- gRPC 禁用 service-config 语义重试；库仍可透明重发尚未写出或服务端未处理的请求。
  不能把一次 API 调用等同于一次物理发送，也不能据超时断言未执行。
  [grpc-go WithDisableRetry](https://pkg.go.dev/google.golang.org/grpc#WithDisableRetry)、
  [Service Config](https://grpc.io/docs/guides/service-config/)。
- DNS 更新在解析/重连时生效；不承诺即时重配置。HTTP 已有连接也会继续复用，强制切换须主动排空。
- 流式出站明确返回 Unimplemented，E07 再定义长期连接与认证续期；当前无业务 streaming。
- OTel trace queue 512、batch 128、export timeout 1s；metrics 10s 周期、1s 超时和基数上限 256。
  停机总清理预算 2s；无法送达的遥测可丢失，安全审计的持久化仍由平台负责。
  [OTel Go SDK metric](https://pkg.go.dev/go.opentelemetry.io/otel/sdk/metric)、
  [OTel Go](https://opentelemetry.io/docs/languages/go/)。
- 独立 API 发布仓库/版本由团队选择。验证使用本地 module replace 连接两个独立生成项目，不引入仓库级共享运行框架。
