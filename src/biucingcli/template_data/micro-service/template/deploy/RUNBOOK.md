# 单机生产运行手册

本项目的生产入口是独立的 `compose.prod.yaml`。不要与开发 `compose.yaml` 或 `compose.dev.yaml` 合并。
生产只使用经过检查的 registry digest，不现场构建、不挂载源码。开发仍使用 `scripts/task`。
单机部署存在宿主机、单实例应用和入口单点；Compose 不提供跨机 HA，也不提供滚动零停机。

## 1. 平台先决条件

- Docker Engine + Compose v2、Bash、可访问的镜像仓库。生产凭据及部署权限由运维平台管理。
- 预创建 `DEPENDENCY_NETWORK`，配置外部 PostgreSQL/IdP/遥测出口 DNS、TLS 和防火墙；Micro 还需 `SERVICE_NETWORK`，只让获准调用方接入。桥接网络并不提供细粒度出口 ACL；需要宿主机防火墙/平台策略。
- PostgreSQL 16、独立服务数据库、运行角色和迁移角色。运行角色不可创建 schema，不能修改 `schema_migrations`；迁移角色负责 DDL 和运行角色授权。`deploy/postgres-init.sql` 仅展示开发角色结构，禁止复制其密码进生产。使用独立管理员创建真实角色及数据库，撤销 PUBLIC 默认权限，保留迁移程序要求的默认表/序列授权。
- Web：外部 OIDC 提供方、准确注册的 HTTPS origin/callback、访问令牌 audience。浏览器 Cookie 安全策略保持启用。生产不启动测试 IdP。
- Web：部署方提供有效的域名证书链 `tls.crt` 和私钥 `tls.key`；Caddy 不运行 ACME。证书到期告警、签发、轮换归平台。
- Micro：部署方提供工作负载证书 `server.crt`、私钥 `server.key`、信任根 `ca.crt`，以及精确的 URI SAN 方法 allowlist。只允许内部 mTLS RPC 调用，无公网 RPC 端口。
- 可选 Redis 必须提供受支持的 TLS DSN 和凭据；OTLP 地址为空则不启用导出。Collector 的留存、告警和访问控制由平台提供。

应用非 root UID/GID `65532:65532`，文件系统只读，应用关闭全部 capabilities；官方 Caddy 二进制带有文件 capability，入口仅恢复 `NET_BIND_SERVICE` 以允许执行，限制 CPU/内存/PID，日志轮转为 10 MiB × 3。Web 仅 Caddy 发布 HTTPS 端口；应用、RPC、PG、admin 都不发布宿主端口。管理监听在容器网络上可见，网络成员必须可信，禁止把该网络接入不受信容器。

## 2. 配置和密钥

复制 `deploy/config.prod.yaml` 到宿主版本目录，例如 `/srv/service/releases/r1/config.yaml`；按实际数据库、OIDC、证书身份和调用地址修改。生产配置校验拒绝开发凭据/不安全 TLS。禁用组件不读取对应 secret 文件。

`RUNTIME_SECRETS` 的文件：启用 PG 时 `database-dsn`，启用 Redis 时 `cache-dsn`；Web 还需 `oidc-client-secret`；Micro 还需工作负载证书文件。PG DSN 示例结构：`postgres://<runtime-role>:<password>@<db-host>:5432/<database>?sslmode=verify-full&sslrootcert=/run/secrets/ca.crt`。迁移使用另外的 `MIGRATION_SECRETS` 目录，文件 `dsn` 和 `ca.crt`，DSN 中 rootcert 路径改为 `/run/migration/ca.crt`。应用容器永不挂载迁移凭据。无状态 Micro 不运行迁移，不需要迁移目录。

宿主 secret 目录属主 65532、权限 0500，文件 0400；配置可为只读 0444。备份工具使用执行者 UID，备份凭据单独归该账号所有，`pgpass` 必须 0600。Compose bind mount 不替你修改宿主文件权限。不要使用示例测试脚本的宽松 fixture 权限作为生产方案。

密钥与配置使用新的不可变版本目录，发布环境文件只写路径，不写凭据。不要覆盖旧目录：发布历史仅保存路径和 digest，不复制配置/密钥内容。宿主加密、备份、读权限、审计和旧版本清理由平台负责。路径含空格可作为未加引号的值；不支持 shell 变量展开、引号或多行值。环境文件不能执行代码。

## 3. CI 和镜像信任

`.github/workflows/verify.yml` 执行项目验证；标签 `v*` 触发 `release.yml`。verify → build/scan/SBOM/nonroot smoke → publish 顺序执行。build 无 packages 写权限及 OIDC 权限；publish 使用 GitHub `release` environment 和独立 packages/id-token 权限，推送同一镜像 archive 后签署 digest、SPDX SBOM、SLSA v1 格式 provenance。仓库管理员应保护标签和 release environment；该 provenance 不等同于某一 SLSA 保证等级。

Trivy 扫描 HIGH/CRITICAL 默认失败，包括有公告但无修复的依赖。升级依赖/基础镜像并重新测试后再发布；如确需豁免，必须在单独评审中记录精确 CVE/组件/版本、影响分析、负责人、截止日期和补偿措施，以受版本管理的最小规则修改关卡。模板不提供全局跳过扫描开关。工具镜像固定版本与 digest，升级时复核上游安全公告。扫描库需要网络更新，下载失败也阻止发布；通过一次扫描不代表未来没有新漏洞。

默认部署使用 `SIGNER_IDENTITY`（精确的仓库 workflow/tag 身份，不用宽泛正则）和 `SIGNER_ISSUER=https://token.actions.githubusercontent.com`，验证签名、透明日志和两种 attestation。另可设置项目相对路径 `SIGNER_KEY`，使用管理员预先固定的 Cosign 公钥；该模式验证签名和 attestation，但明确不要求透明日志，仅用于明确选择私有 PKI 的环境。公钥不能来自待验证镜像或不受信发布附件。两种模式不能混淆信任声明。

Cosign 在容器内执行，不能调用 Docker Desktop 的宿主凭据助手。私有 registry 可先使用专用目录执行 `docker --config <dir> login`，再设置 `SECURITY_DOCKER_CONFIG=<绝对目录>`；其中应为容器可读取的直接 auth 配置。该目录按密钥管理，不写入发布环境记录。GitHub runner 的 docker login 使用其常规配置。

生成/检查本地镜像不需要生产发布凭据：`scripts/task image`、`scripts/security scan <image> <out-dir>`、`scripts/security sbom <image> <out-dir>`。签名私钥不进入构建上下文，`.secrets`/`.releases`/备份均被排除。CI keyless 发布需在真实仓库开通 GHCR、OIDC 和环境保护后验收；本地私钥验收不能替代它。

## 4. 首次发布与更新

1. 准备数据库角色、网络、证书和版本化配置/secret 目录。审查连接预算：应用副本数 × pool 上限 + 迁移 + 运维连接不能超出数据库预算。
2. 复制 `deploy/release.env.example` 到不入库的 `.release.env`，填入 app digest、固定 Caddy digest（Web）、宿主路径、网络名和信任信息。环境文件只使用注释、空行和允许的 `KEY=value`，不要 source。
3. 执行 `./scripts/release preflight .release.env`。验证签名/SBOM/provenance、pull 固定镜像、解析 Compose 并执行一次配置校验，不改变运行实例。
4. 执行 `./scripts/release deploy .release.env`。同项目目录锁阻止并发发布；迁移程序另有数据库锁。PG 模板先执行一次独立迁移，失败停止；应用不会在启动时迁移。替换应用后私网检查 ready，成功后启动 Web 入口并写入 `.releases/<project>/current.env`、版本信息和历史。
5. 执行 `./scripts/release status .release.env`，通过真实 HTTPS 或授权 mTLS 探测业务协议。查看 `.releases/<project>/version.json`，核对发布 commit/version；观察错误率、延迟、连接池、日志和入口健康状态。完成值班交接后再结束发布观察期。

只允许一个部署控制器维护同一 Compose project；本地锁不能协调不同宿主目录/机器。锁残留时先确认无发布进程，再人工移除。每个环境使用独立项目名。生产 compose 的 `pull_policy: never` 要求由 release 入口完成拉取；直接 compose up 不是经过供应链验证的发布路径。

单实例更新会终止旧实例并等待候选就绪，存在中断窗口。候选可能在进程启动后失败；脚本不会自动撤销已完成的迁移，也不会把失败候选标为成功。Caddy 主动探测 `/readyz`（2 秒间隔，1 秒超时），恢复后重新路由；Compose 的 HEALTHCHECK 只是状态，unhealthy 本身不触发 restart 或摘流。进程退出后由 restart policy 处理；失去 PG 时 live 保持可用、ready 失败，由 Caddy 的独立检查停止转发。微服务调用方必须通过既有 deadline/背压和重连机制处理不可用，Docker DNS 不提供 ready 摘流。

## 5. 回退、迁移和轮换

- 坏 digest、签名、证明或配置在替换前停止。迁移失败先检查 dirty 状态、迁移日志及锁；禁止盲目 force schema 版本。
- 候选未就绪时：恢复仍兼容 schema 的最近成功配置，执行 `./scripts/release rollback .releases/<project>/current.env`。成功升级后要回退上一个版本，则先评审 `.releases/<project>/previous.env` 再把它作为 rollback 参数。脚本只接受记录过的环境文件，重新验证签名和 ready，不执行逆向数据库迁移。
- 变更数据库使用 expand→migrate→contract。旧应用不能理解已收缩 schema 时，不允许直接回退；先采取前向修复，或走经过验证的数据恢复与切换方案。
- 密钥/配置轮换：新目录 + 新环境文件 + preflight/deploy。出站/入站工作负载证书支持已有重载路径，但本运行手册统一采用受控重新部署并验证新旧信任窗口。Caddy 证书目录换版本后重新创建 edge（路径变化由 Compose 识别），验证证书链与有效期。轮换根证书先重叠信任，再换叶证书，再移除旧根。
- 排障优先使用 compose logs/ps、私网 `server healthcheck` 和 `server version`，不临时把 admin/metrics/pprof 暴露公网。日志默认不记录令牌、Cookie 或请求体；Caddy 不启用 access log，避免 OIDC code 查询参数进入日志。平台需要入口日志时先设计脱敏规则。

## 6. PostgreSQL 备份与恢复

volume 保留不能替代备份。模板提供逻辑一致性快照，不提供 WAL/PITR。生产数据库服务商的自动备份、PITR、加密、跨故障域副本和恢复凭据需要另行配置并演练。

准备 `PG_SECRETS`，包含 `deploy/backup-service.conf.example` 对应的 `pg_service.conf`、私有 `pgpass` 和 CA。backup 使用专用只读备份角色（CONNECT、schema USAGE、全部所需表 SELECT；新表默认授权同样覆盖），restore 使用隔离目标的 DDL 账号。目标主机/数据库必须与生产不同，操作者显式复核；脚本要求空 public schema 并拒绝已有表，但这不能替代目标身份核对。服务配置只能保存连接配置，不能包含 shell 操作。

```sh
export PG_TOOLS_IMAGE=postgres@sha256:4e6e670bb069649261c9c18031f0aded7bb249a5b6664ddec29c013a89310d50
export PG_SECRETS=/srv/backup/credentials
export PG_NETWORK=service-backup
./scripts/database-backup backup /srv/backup/staging/snapshot.dump
# 将加密备份及校验和复制到独立故障域，校验上传结果后才能清理 staging。
# 在空的隔离数据库恢复；核对 pg_service.conf 中的 restore 目标。
CONFIRM_ISOLATED_RESTORE=yes ./scripts/database-backup restore /srv/backup/staging/snapshot.dump
```

失败只留下可清理的临时输出，不发布完成归档。恢复使用单事务且不带 `--clean`，不会自动覆盖现有数据。还原后重新应用运行角色授权/默认权限，检查 schema 版本、业务完整性、会话安全影响和应用 ready。默认归档不含角色密码、平台配置、证书或 OIDC 设置，必须有独立安全恢复流程。会话数据库回到旧时间点可能恢复已注销会话，正式切换前应失效所有旧会话并要求重新登录。

记录：快照开始/结束 UTC、源/目标数据库标识（无凭据）、备份 digest、独立存储对象版本、schema 版本、恢复开始/结束、数据验证、权限重建、应用探测、实际恢复耗时与最后可恢复数据点、负责人和剩余问题。先得到记录，再约定 RPO/RTO。备份调度、保留/销毁、容量告警和演练频率由平台负责。

## 7. 故障演练边界

仓库级 `scripts/verify-backend-production` 只创建临时独立 Docker 资源：镜像扫描/私钥签名、TLS 路由、重建持久性、PG 断连/恢复、迁移失败、未就绪发布/回退、隔离真实恢复与有界临时文件系统容量不足。不会填满宿主磁盘，也不会操作真实生产。
慢依赖与遥测中断由 `scripts/verify-backend-calls` 和生成项目已有可靠性测试覆盖。实际生产需另行验证磁盘告警、数据库满盘后的运维恢复、远端备份取回和宿主完全丢失的恢复；这些设施行为不能用容器探针或本地文件系统测试代替。单机停电/损坏时服务中断，必须在新宿主重建基础设施、恢复数据和版本化配置，再切换入口。
