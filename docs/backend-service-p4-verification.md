# Backend P4：单机生产交付验证

日期：2026-09-28。范围：B20–B24，模板交付与本机验收已完成。P5 跨机高可用不在本轮范围。

## 交付内容

- 两模板新增独立 `compose.prod.yaml`、生产配置与发布环境契约，外部 PG/IdP/PKI/遥测由平台提供；不叠加开发 Compose，不在生产机器构建。
- Web 使用 Caddy 2.11.4，平台挂载 TLS 证书；主动 `/readyz` 探测，禁止外部访问管理接口，禁用代理重试和会泄漏 OIDC code 的默认 access log。Micro 只接内部调用网络，不发布宿主 RPC/admin 端口。
- 应用 UID/GID 65532、只读根文件系统、capabilities 全关、no-new-privileges、tmpfs、CPU/内存/PID 上限、日志轮转和停止宽限。官方 Caddy 二进制自带 file capability，因此只为 edge 加回 NET_BIND_SERVICE，应用保持 cap_drop ALL。
- `scripts/release`：严格数据格式环境文件，不执行 shell；固定 digest；Cosign 校验签名、SBOM 与 provenance；独立迁移先行；候选未 ready 不写成功记录；兼容 schema 的旧镜像回退；版本输出与本地发布互斥。
- 生成项目 release CI 将验证/构建和发布权限分开，扫描 HIGH/CRITICAL 失败阻断，生成 SPDX SBOM、SLSA v1 格式来源证明，keyless 签署固定 digest。构建 job 不持有生产发布权限。本地签名另有固定公钥模式，明确不要求透明日志。
- `scripts/database-backup`：TLS verify-full、独立备份/恢复凭据、一致性逻辑快照、临时归档成功后原子改名；恢复只允许显式指定的空目标，单事务且无 `--clean`。
- 两套 `deploy/RUNBOOK.md` 包含网络/角色/密钥权限、首次发布、更新、迁移失败、镜像回退、证书轮换、备份保留和恢复记录。配置/secret 使用版本化目录，发布记录只保存路径，不能原地覆盖后指望回退。
- 增加仓库 `scripts/verify-backend-production`；`scripts/verify-distribution --backend-output-dir` 可保留 wheel 与 sdist 重建安装包生成的项目用于真实 Docker 验证。

## 扫描发现与修复

初始 Trivy 扫描发现 x/crypto、x/text 和 grpc-go 高危公告，Alpine 3.20 也已停止维护。
升级到 Alpine 3.23.6、grpc-go 1.83.2、x/crypto 0.55.0，并由 Go MVS 锁定 x/net 0.58.0、x/text 0.41.0 等兼容依赖。Go 仍为 1.26.8。
Cosign 使用修复相关 bundle 安全公告的 3.1.3，Trivy 为 0.67.2；供应链工具、Caddy 和备份工具均固定 digest。
实际扫描读取当前漏洞库，失败不豁免，扫描结果只代表当次库快照。

依据：[Alpine 生命周期](https://alpinelinux.org/releases/)、[Cosign 安全公告](https://github.com/sigstore/cosign/security/advisories/GHSA-fx35-mq7g-6g98)、[Cosign 验证](https://docs.sigstore.dev/cosign/verifying/verify/)、[Caddy 健康路由](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)。

## 实际环境和证据

宿主 macOS arm64，Docker Desktop 4.92.0，Engine 29.8.0（Linux arm64），Compose 5.5.1。
没有据此声明原生 Linux 宿主、其他 CPU 架构或 Windows 已验收。CI runner 上的 GitHub OIDC/GHCR 发布尚未执行。

| 检查 | 证据 |
| --- | --- |
| 核心 CLI/生成回归 | `/tmp/biucing-p4-core-acceptance.log`：204 项通过，含恶意 release 环境值不能执行命令、生产网络/权限结构与可执行脚本 |
| 双 worktree | `/tmp/biucing-p4-worktrees/evidence.json`：端口/缓存/卷隔离、热更新、权限、down 保留状态、运行镜像与退出通过 |
| 源码生产故障验收 | `/tmp/biucing-p4-production-v5/evidence.json`：两模板扫描/签名部署，TLS 路由、PG 故障摘流与恢复、迁移失败停止、未就绪回退、真实隔离恢复和满盘写入失败通过 |
| 初次真实恢复 | 同上：快照开始 UTC `2026-09-27T23:31:50.418372+00:00`，恢复并验证 marker 耗时 2.65 秒；这是小型 fixture 数据，不是生产 RTO |
| 安装包资源 | `/tmp/biucing-p4-packaged-v2.log`：wheel、sdist、sdist 重建 wheel 的全部资源字节/执行权限一致；安装后生成全部七模板/配置检查通过 |
| 六种组件组合 | `/tmp/biucing-p4-matrix/evidence.json`：Web 默认/Redis、Micro 无状态/PG/Redis/PG+Redis 全部 Docker 验证通过，包含 lint、race、协议、编译与启用组件的真实集成测试 |
| 安装包 Docker 开发 | `/tmp/biucing-p4-packaged-v2/docker-evidence.json`：wheel 与 sdist 重建安装包生成的 Web/Micro 四项目均通过 `scripts/verify-container` |
| 更新依赖后的跨服务回归 | `/tmp/biucing-p4-calls/evidence.json`：11 项通过，包含 OIDC→Web→mTLS Micro、权限/伪造拒绝、超时/取消、重启/证书轮换、IdP/遥测故障与 trace/日志/指标关联 |
| 最终资源复查 | `/tmp/biucing-p4-distribution-final.log`：元数据证据更新后再次通过 wheel/sdist/重建 wheel 的资源一致性、安装与配置验证 |

安装包生产复验 `/tmp/biucing-p4-production-package/evidence.json` 的 13 项全部通过，额外覆盖错误签名公钥拒绝、不同镜像 digest 之间的更新/回退、专用只读备份角色以及空目标恢复保护。实际快照窗口 UTC `2026-09-27T23:43:20.458363+00:00` 至 `23:43:23.585053+00:00`；隔离恢复与 marker 校验耗时 **4.576 秒**。快照窗口不等同于生产事务恢复点承诺，fixture 规模也不能用来推断生产 RPO/RTO。

Ruff、模板 validate、shell 语法与差异空白检查通过。本次最终测试容器、网络及数据卷按各 harness 的资源清单清理；保留证据和构建缓存。

## 能力边界

- 单实例 Compose 更新有中断，宿主机是单点；没有声称滚动零停机或跨机 HA。unhealthy 只是状态，重启依赖进程退出；Web 摘流依赖 Caddy 的独立 ready 检查。
- 本地测试 registry 只绑定 loopback，使用临时固定公钥签名且不向公共透明日志写入。GitHub keyless 签名、GHCR 权限、环境保护和真实生产 identity 必须在目标仓库补验。
- 镜像回退不执行数据库逆向迁移；需要人工确认旧应用兼容当前 schema。来源证明是签名元数据，不声明某一 SLSA 保证等级。
- 真实恢复发生在另一个隔离 PostgreSQL 容器，备份只是逻辑快照。远端独立存储、加密留存、PITR、宿主彻底失效后的切换和生产 RPO/RTO 由平台实施并演练。
- 容量不足测试将真实 pg_dump 写入 1 MiB 临时文件系统，不填满宿主或数据库卷；不宣称生产 PG 满盘恢复已实测。
- 管理端口对容器网络成员可见，网络准入与出口 ACL 仍由平台控制。没有给 Docker bridge 网络赋予服务身份含义。

失败的早期验收保留在 `/tmp/biucing-p4-production-v1` 至 `v4`，分别用于发现 Cosign 参数/凭据助手、registry digest 选择、Caddy file capability 和测试 URL 问题；不计作通过。只有最终成功报告计入验收。

## 复现入口

```sh
uv run --locked python scripts/verify-backends --output-dir /tmp/backend-matrix-new
uv run --locked python scripts/verify-backend-worktrees --output-dir /tmp/backend-worktrees-new
uv run --locked python scripts/verify-backend-calls --output-dir /tmp/backend-calls-new
uv run --locked python scripts/verify-distribution --backend-output-dir /tmp/backend-packages-new
# 对 wheel/ 与 sdist/ 下的两个项目分别执行 scripts/verify-container，构建运行镜像。
# 例：Web 使用 wheel 生成项目、Micro 使用 sdist 重建安装包生成项目。
uv run --locked python scripts/verify-backend-production \
  --web-project /tmp/backend-packages-new/wheel/edge-api \
  --micro-project /tmp/backend-packages-new/sdist/internal-api \
  --web-image <built-web-image> --micro-image <built-micro-image> \
  --output-dir /tmp/backend-production-new
```

实际验收使用 `.venv/bin/python` 执行同一仓库脚本，构建标签分别为 `biucing-p4-web:package`、`biucing-p4-micro:package`。
本地测试的密钥、归档与报告保留在私有临时目录，不提交仓库；容器/网络/卷在 harness finally 中按本次资源清单清理，不做全局 prune。
