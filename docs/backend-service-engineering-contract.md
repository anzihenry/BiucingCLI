# 后端服务工程契约（P0 / B01）

2026-09-26。范围是两类生成项目的工程边界、固定选型与验证入口。
架构目标见[整体架构](backend-service-architecture.md)，状态见[实施任务](backend-service-implementation-tasks.md)。
P0 的历史范围不包含持久化、登录会话、mTLS 或生产交付。
当前数据、迁移、协议与身份实现及依赖版本见 [P2 验证记录](backend-service-p2-verification.md)；生产交付仍属后续阶段。
出站调用与观测见 [P3 验证记录](backend-service-p3-verification.md)。

## 工程与依赖方向

一个生成项目就是一个独立 Go module 和 Docker 构建上下文，运行时不加载 BiucingCLI。
首先共享生成规则与测试契约，不引入跨服务共享业务包或大型基础框架。

| 目录 | 职责与依赖限制 |
| --- | --- |
| `cmd/server` | 组装配置、实现和 transport；唯一应用组装入口，不堆积业务逻辑 |
| `internal/config` | 类型化配置、校验；不得依赖 handler、service 或数据库连接 |
| `internal/handler` / `internal/transport` | HTTP / gRPC 协议转换；调用 service，不直接执行 SQL |
| `internal/service` | 应用操作与依赖接口；不依赖 HTTP/gRPC handler 或具体数据库驱动 |
| `internal/model` | 内部数据结构；公开协议变更在契约中评审，不直接暴露数据库结构 |
| `internal/repository` | 实现数据接口，后续 B09 接入 pgx；不被跨服务导入 |
| `internal/runtime` | 启停、健康、排空；不承载业务规则 |
| `internal/telemetry` | 观测接入；不能反向控制业务可用性 |
| `api` | 对外协议及生成代码；Web 的 OpenAPI 在 B11 加入，Micro 已有 Buf |
| `configs` / `deploy` / `scripts` | 配置示例、部署文件、项目自身工具；生产密钥不落库 |
| `tests` | 生成项目协议/集成检查；测试 fixture 不成为产品业务能力 |

上表约束后续实现；P0 没有重新拆分现有内存示例的应用层接口，相关组装在 B05 演进。
后续新增 `cmd/migrate`、worker 或适配包按相同规则组装，不预先创建空目录和空抽象。
独立服务只通过协议调用，各自持有数据；共享物理 PostgreSQL 也必须分角色/数据库。

## 固定选型

| 决策 | 选定方案 | 原因与替换边界 | 实施阶段 |
| --- | --- | --- | --- |
| HTTP / RPC | Gin / grpc-go + Protobuf/Buf | 延续现有 Go 工程；协议与应用层分离 | 现有 starter，B11/B12 补契约 |
| 数据访问 | pgx v5，无默认 ORM | SQL/事务显式；repository 接口隔离驱动 | B09 固定具体驱动版本并集成验证 |
| 迁移 | golang-migrate 4.20.1 | 版本 SQL、独立 CLI；不绑定运行进程，替换需转换历史版本记录 | B10 |
| 单机代理 | Caddy 2.11.4 | 单一参考实现，负责 TLS/路由；更换代理保持应用 HTTP 契约 | B20 |
| 本地测试 IdP | Dex 2.45.1 | 可配置本地静态身份用于 OIDC 测试；生产使用外部 IdP，不部署测试用户 | B13 |
| 本地 CA | Smallstep CLI 0.30.6 | 容器内生成测试根/叶证书，支持 SAN；不把测试 CA 当生产 PKI | B15 |
| 日志/遥测 | slog / OpenTelemetry | 标准接口；Collector 与存储后端分离 | B08/B18 |

版本选择依据官方 [migrate release](https://github.com/golang-migrate/migrate/releases/tag/v4.20.1)、
[Caddy release](https://github.com/caddyserver/caddy/releases/tag/v2.11.4)、
[Dex release](https://github.com/dexidp/dex/releases/tag/v2.45.1)、
[Smallstep release](https://github.com/smallstep/cli/releases/tag/v0.30.6)。
Dex 的[本地示例](https://dexidp.io/docs/getting-started/)可作为测试身份配置起点。
这些未来接入项在 P0 只固定决策，不声称已验证相互兼容；接入任务必须执行真实协议/故障测试。

当前生成代码由 `go.mod/go.sum` 固定直接和传递依赖；Go module 最低版本 1.26.0（Docker 工具链固定 1.26.8）、Gin 1.10.0，
Micro 的 grpc-go 1.81.1、OTel 1.43.0。容器工具使用 Air 1.65.3、golangci-lint 2.12.2、
Buf 1.70.0；Buf 远端插件也固定版本，防止后续生成悄然漂移。
本地组件固定 PostgreSQL 16.13、Redis 7.4.2、Collector 0.126.0。
这些是当前验证基线而非“最新/无漏洞”承诺；生产 digest、供应链扫描和镜像升级由 B20/B21 完成。

升级以单独变更同步 Dockerfile、工具配置、go.mod/go.sum 和验证记录；两模板共用工具同步升级。
不能只改版本号或使用 latest 绕过兼容检查。若未来选定组件不可用，记录替换理由并重跑对应关卡。

## 两模板能力矩阵

| 能力 | Web | Micro | 当前实现状态 |
| --- | --- | --- | --- |
| 用户 HTTP 入口 | 主入口 | 管理/技术验证 HTTP；服务主入口为 RPC | 既有 starter |
| gRPC 服务 | 非默认 | 默认 | 既有 starter |
| 数据库 | PostgreSQL 必选，为会话留基础 | none / PostgreSQL，默认 none | P2 已接入 pgx、独立迁移与最小权限 |
| 缓存 | none / Redis，默认 none | none / Redis，默认 none | 与数据库独立，尚无缓存适配 |
| 认证授权 | OIDC + 会话/访问令牌 | mTLS + 方法授权 | B13–B15 已完成，见 P2 验证 |
| 出站调用/故障隔离 | HTTP + gRPC | HTTP + gRPC | B16/B17，实现与验收见 P3 |
| CI | 项目内 Docker 检查 | 项目内 Docker 检查 + Buf | P0–P3 生成/依赖/协议/互调检查；P4 增加扫描/SBOM/来源证明/签名、独立生产 Compose 与恢复验收 |

## B02 配置契约与兼容

生成参数：`--database` / `--set database=...`，`--cache` / `--set cache=...`。
Web 只允许 `database=postgres`；Micro 支持 `none|postgres`；二者缓存均为 `none|redis`。
错误值或 Web 的 `database=none` 在写文件前拒绝。

旧 `--dependency-store` / `--set dependency_store=...` 直接拒绝，不做有歧义的静默映射。
旧 PostgreSQL 选择迁移为 `--database postgres --cache none`；旧 Redis 选择迁移为
`--database none --cache redis`（Micro）。`microservice` 旧模板名仍拒绝。
已生成的项目保持原样；升级这些项目需显式迁移 YAML 与环境变量，不自动改写用户文件。

运行配置分为 `database.driver/dsn` 和 `cache.driver/dsn`；容器内使用各组件服务名，
宿主示例用 localhost。环境变量为 `DATABASE_DSN`、`CACHE_DSN`；停用组件清空 DSN，
不创建连接。旧 `store`/`STORE_DSN` 不再读取。P0 只读取配置，不执行数据库连接或健康探测。
本地依赖只在容器网络可达；不发布数据库/缓存宿主端口，避免并行 worktree 冲突。
启用的 PG 使用 Compose 项目隔离数据卷，普通 down 保留数据。

Compose 默认本地凭据仅用于开发。生产证书、身份系统、密钥分发、托管数据库、备份和遥测存储
由部署平台负责；模板后续提供配置契约和接入实现，不自动创建整个平台。

## B03 验证入口与证据

仓库内执行（无宿主 Go 依赖）：

```sh
uv run --locked python scripts/verify-backends --output-dir /tmp/backend-verification-new
# 快速仅生成六种组合，绝不标记 Docker 验证通过
uv run --locked python scripts/verify-backends --generate-only
# 单独选择一类，参数可重复
uv run --locked python scripts/verify-backends --case web --case micro
```

输出目录必须不存在，防止覆盖工作成果。每次保存 `evidence.json` 与各 case 日志；记录生成结果、
容器结果、命令、Docker/Compose 版本和时间。失败返回非零；仅生成标为 rendered，未运行标为 not-run。
CLI 测试仍由现有 core suite 执行；容器检查不冒充生成器检查。

生成项目自身运行 `./scripts/verify-container`：独立 Compose project、构建 dev 镜像、
执行 doctor/lint/test/build、退出时只删除本次验证的容器与临时卷。验证不发布应用端口，
不启动数据库/缓存，目的是证明当前代码不依赖这些设施可用；真实数据集成由 B09 开始追加。
项目内 GitHub Actions 与仓库六组合矩阵均调用同一入口。

后续 CI 逐步追加真实数据库/迁移、身份、跨项目互调、运行镜像和恢复演练；不为未来能力提前打勾。
