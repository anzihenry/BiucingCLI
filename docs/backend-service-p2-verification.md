# 后端服务 P2 实施与验证

范围：B09–B15。两类模板保持独立生成和部署；没有新增业务模型或前端。
本文记录实际实现边界，不能据此宣称完成生产交付或高可用验收。

## 实现

| 任务 | 交付 |
| --- | --- |
| B09 | pgx pool、连接/查询预算、事务回滚与取消、启动/就绪检查；独立数据库与运行/迁移角色；无状态 Micro 不初始化 pool |
| B10 | 嵌入版本化 SQL 的独立迁移二进制、PostgreSQL advisory lock、dirty 失败阻断、schema 兼容检查；API 不自动迁移 |
| B11 | OpenAPI 与已提交基线、oasdiff breaking、真实响应契约测试；移除内存用户 CRUD，保留 ping 与身份入口 |
| B12 | 已提交 Proto 基线、Buf breaking、固定插件生成、安全 status/ErrorInfo、独立 API 消费者示例 |
| B13 | OIDC 授权码/S256 PKCE、state/nonce/浏览器绑定、单次回调、JWKS 缓存；独立 API audience 与 at+jwt 用途检查；开发 Dex |
| B14 | PostgreSQL 不透明会话、哈希 ID、登录轮换/注销/绝对到期、CSRF、精确 CORS；独立清理命令 |
| B15 | 强制 mTLS、已验证 SPIFFE URI 身份、方法白名单、按调用方/方法控制用户上下文、握手时重载证书与信任根、本地 CA |

## 本轮确定的边界

### 数据与迁移

运行角色为 `<service>_app`，迁移角色为 `<service>_migrator`。本地分别创建在每个服务的 PostgreSQL 容器中；
共享生产集群时必须为每个数据库撤销 PUBLIC CONNECT，再分别授予相应角色。
生产角色由平台预置，默认权限与模板 SQL 一致；可以用 DATABASE_RUNTIME_ROLE 指定实际运行角色。
应用不得创建表或写 schema_migrations；迁移凭据不传给运行中的 API。

`dev/up` 的脚本先运行一次迁移，再启动开发 API；这不是把迁移放进 API 进程。
发布流水线使用同一镜像中的 `/app/migrate` 和单独挂载的 MIGRATION_DSN_FILE。
脏版本不自动 force/down。先检查并修复，再由操作人员明确设置审核后的版本。
当前支持 schema version 1；滚动升级时先扩大旧/新版本的兼容区间，再按 expand → migrate → contract 演进。
已有 P1 卷不会被自动删除或重建，需要显式补角色/权限，或重建可丢弃的本地数据。

### Web 身份

浏览器只得到不透明 session cookie；服务端在登录交换后丢弃 IdP 的所有令牌。
不请求 offline_access、不保留 refresh token、不提供 refresh 接口；因此不存在并发 refresh-token 轮换路径。
会话最长一小时，且不超过登录 ID token 的到期时间。到期重新进行完整授权码流程，不做无限滑动续期。
这满足当前后端 API 的身份需求；未来需要代用户调用第三方时，再设计加密令牌保管和并发刷新。

本地 Dex 负责浏览器登录。移动端 API 接受 RS256、typ=at+jwt 的 JWT access token；
校验 issuer、独立 audience、签名、exp、nbf、iat、sub、client_id 和 jti，拒绝 ID token 和 opaque token。
移动端令牌测试使用独立签名测试发行方，不能把 Dex ID token 当作 API access token。
已有有效会话、可用缓存密钥验证的未过期令牌可以在 IdP 短时故障期间继续使用；新登录失败不能绕过验证。
JWKS 缓存为进程内缓存，重启后不保证在 IdP 故障期间恢复令牌验证。

Web 默认端口按 worktree 路径派生，IdP 使用相邻端口，以满足精确回调白名单；冲突时显式覆盖 HOST_PORT/IDP_PORT。
原 P1 的 Web 随机端口改为此策略，Micro 仍使用 Docker 分配的 loopback 端口。
Dex 只出现在开发 Compose，runtime Compose 使用外部 IdP 配置。

### Micro 身份

应用入口所有 RPC（包括 health）要求 mTLS。工作负载来自验证后的单个 URI SAN；不读取 CN 或伪造身份头。
方法名单和用户上下文委托名单分别配置，默认不允许委托；纯服务调用不需要用户主体。
每跳必须基于当前调用服务重新授权，不能盲目转发 metadata。Web 会剥离终端传入的 X-User-* 头。

证书和根在新握手时重新读取，错误替换拒绝新握手；用版本目录/原子符号链接更新。
既有 TLS 连接不会因根文件替换而重新握手：紧急撤销需要排空/重启连接。
每个新 RPC 还会检查已建立连接上的证书有效期。生产 PKI 签发与轮换仍由平台负责。

### 协议与能力边界

OpenAPI/Proto baseline 是实际提交的契约快照，不在验证过程中自动更新。
测试故意删除公开 HTTP 路径和 Proto 字段，必须让 breaking 命令失败。
HTTP 的分页/幂等/乐观锁只定义扩展约定，不伪造通用业务持久化接口。
Redis 适配、出站客户端、完整指标/追踪、生产代理/发布/备份及多机高可用仍属于后续阶段。

## 验证入口与记录

- `scripts/verify-backends`：六种生成组合、lint、race tests、Buf/OpenAPI、编译、启用数据库时的真实集成测试。
- `scripts/verify-backend-worktrees`：真实双 worktree、端口/数据隔离、热更新、权限、运行镜像和独立迁移。
- 生成项目 `scripts/verify-container`：同一验证入口与失败清理；项目 CI 直接调用。
- Web 集成测试：回滚、超时、连接耗尽/替换、运行角色 DDL/迁移状态写入拒绝、并发迁移、dirty 失败阻断，
  以及真实 PostgreSQL 上的登录绑定、回调重放、共享会话、CSRF、注销和 IdP 故障。
- 身份单元测试：JWT 用途/audience/issuer/过期/签名/未知密钥；真实 TLS 握手、无证书/过期拒绝、叶证书与根替换、方法和用户委托拒绝。

验收日期：2026-09-27。本机为 Docker Desktop / Linux arm64、Go 1.26.8；未运行远端 amd64 CI，不把它计为通过。
以下证据保存在本机临时目录，可能被系统清理；持续回归入口保留在仓库。

| 验证 | 结果与证据 |
| --- | --- |
| 六种组件组合 | Web/Web+Redis 在 `/tmp/biucing-p2-matrix/evidence.json` 通过；该首轮 Micro+Redis 曾因遗漏导入失败，修复后四种 Micro 全部在 `/tmp/biucing-p2-micro-final/evidence.json` 通过 |
| 最终 Web 源码 | `/tmp/biucing-p2/web-complete.log`、`web-complete-integration.log`：lint、race、编译、真实迁移/权限/事务/会话通过 |
| 最终 Micro 源码 | `/tmp/biucing-p2/micro-complete.log`：lint、race、契约及编译通过 |
| 两种运行镜像 | `web-complete-image.log`、`micro-complete-image.log` 构建通过；`web-deploy-final.log`、`micro-deploy-final.log` 启动及私有 ready 探针通过；独立 rpc-probe 对最终 Micro 镜像的 mTLS Ping 通过 |
| 真实 Dex | `/tmp/biucing-p2/dex-final.json`：授权码/PKCE 登录、session、CSRF 注销与注销后拒绝通过；入口为仓库 scripts/verify-backend-login |
| 协议负例 | `/tmp/biucing-p2/protocol-evidence.json`：移除 HTTP 路径、移除 Proto 字段均被拒；重复代码生成一致 |
| 双 Git worktree | `/tmp/biucing-p2-worktrees/evidence.json`：隔离、热更新、UID、数据卷保留、运行镜像/迁移/停止均通过 |
| 角色隔离 | 真实测试 PostgreSQL 中，运行角色连接另一个撤销 PUBLIC CONNECT 的服务数据库被拒；测试库已删除 |
| CLI/打包 | `/tmp/biucing-p2/core-release.log`：203 项通过；最终生成基线 6 项通过；`distribution-final.log`：wheel/sdist 安装和全部七模板生成通过 |

另有模板 validate、Ruff 与 diff whitespace 检查通过。最后的 Compose/Air 停止宽限统一为 30 秒，
容纳 API 排空、最多五秒的 pool 清理及可选遥测清理；自定义更长预算时需同步扩大外层宽限。

## 依赖与依据

Go 模块和工具版本由 go.mod/go.sum、Dockerfile.dev、Buf 配置固定。
迁移 4.20.1 的依赖解析使 pgx 升至 5.9.2；Micro grpc-go/OTel 分别为 1.82.0/1.44.0，
两模板共有依赖保持一致。OIDC 3.14.1、OpenAPI 校验 0.133.0、oasdiff 1.11.7。

- [pgx pool](https://pkg.go.dev/github.com/jackc/pgx/v5/pgxpool)：连接池与 context。
- [golang-migrate pgx driver](https://pkg.go.dev/github.com/golang-migrate/migrate/v4/database/pgx/v5)：独立迁移和锁。
- [go-oidc](https://pkg.go.dev/github.com/coreos/go-oidc/v3/oidc)：令牌验证与 RemoteKeySet。
- [Dex token 文档](https://dexidp.io/docs/configuration/tokens/)：本地 OIDC fixture 的能力边界。
- [oasdiff 1.11.7](https://github.com/oasdiff/oasdiff/releases/tag/v1.11.7)：固定协议差异工具。
