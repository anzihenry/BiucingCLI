# 后端服务 P1 实施与验证

对应 B04–B08。P1 提供运行底座；真实身份验证、持久化和生产交付仍按后续阶段实施。

## 已实现的边界

| 任务 | 实现 |
| --- | --- |
| B04 | 两模板根目录 runtime Compose、独立 dev Compose、Docker 工具入口 scripts/task、可选 Make 包装；动态 loopback 端口、worktree 项目/卷/镜像隔离、UID/GID、Air 热更新、显式数据删除 |
| B05 | 严格单文档 YAML、覆盖顺序、端口/超时/请求预算校验、直接值与 _FILE 冲突拒绝、文件大小限制、生产开发凭据防护、脱敏配置检查、显式 app 组装和构建信息 |
| B06 | HTTP 和 gRPC unary/stream 的请求 ID、大小/并发/时间预算、取消、panic 隔离、基础校验工具、Principal/Policy 默认拒绝；协议错误不携带内部异常文本 |
| B07 | 独立 admin listener、live/ready/version、初始化与排空状态、关键依赖检查接口、部分 bind 失败清理、有限退出；关闭 gRPC reflection |
| B08 | slog JSON、日志级别、关联 ID、固定字段的访问/安全事件、敏感键脱敏、100 条/秒事件预算和丢弃摘要 |

默认边界：HTTP 只显式公开 `GET /api/v1/ping`；示例用户资源拒绝匿名访问。
gRPC 只公开标准 health Check/Watch，Ping 默认受保护。验证器在 B13–B15 接入，
不接受 X-User-ID、Authorization 或 Cookie 自行冒充已验证身份。

## 开发命令与兼容

无需宿主 Go/Buf/Make，可执行 `./scripts/task bootstrap/dev/verify/image/up/down/logs/doctor`。
Make 只是同名包装。`dev`/`up` 改为后台启动，查看输出用 `logs`；迁移命令在 B10 前明确失败。
旧 `docker-build` 等命令保留，Micro 旧 `deploy/compose.yaml` 转为根文件 include。

两个 Compose 文件独立使用，不叠加，避免端口、环境和挂载的合并歧义；相关规则参见
[Docker Compose 合并规则](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/)。
开发端口默认由 Docker 分配，数据库、缓存、Collector、admin 不发布宿主端口。
`down` 保留数据，`CONFIRM_DELETE_DATA=yes ./scripts/task clean-worktree` 才删除本项目卷。

管理地址默认容器内部 `127.0.0.1:9000`。原公开 `/healthz` 被撤下；管理口保留同名兼容别名。
Docker 健康检查使用 `/livez`，发布就绪检查使用 `/readyz`。liveness 不检查数据库；
readiness 只接纳遵守 context 的关键检查，遥测不得成为就绪前提。

`_FILE` 仅启动时读取；轮换文件后显式重启实例。APP_ENV=production 要求显式 DSN，
拒绝 starter PostgreSQL 密码及非 verify-full 连接，Redis 要求 TLS。
这不替代 B09 的数据库角色/连接策略或 B20 的生产密钥交付。

## 验证记录

本机环境为 Docker Desktop / Linux arm64；Go 1.26.8。Linux amd64 CI 已配置但未远端运行。
以下原始证据在本机临时目录，可能被系统清理；持续回归入口保留在仓库。

- 六种组件组合：`scripts/verify-backends`，包含生成、dev 镜像、实际配置检查、Buf、lint、`go test -race ./...`、编译；输出 `/tmp/biucing-p1-final/evidence.json`。
- 最终源码两模板复验：`/tmp/biucing-p1-resumed/evidence.json`，均通过。
- Python core 203 项、模板 validate、Ruff 和 diff 检查通过；wheel/sdist 安装及全部七个模板生成验证通过。
- 首轮两模板验证：`/tmp/biucing-p1-check2/evidence.json`；均通过，验证了完整 HTTP/RPC 管线与非 root 开发流程。
- 两个真实 Git worktree：`/tmp/biucing-p1-runtime/evidence.json`；不同项目名和动态端口、一个热更新而另一个响应不变、输出 UID、down 保留 PostgreSQL 数据卷均通过；Web runtime 镜像启动、私有就绪探针与停止通过。
- Micro runtime 镜像与挂载密钥/生产拒绝场景：`/tmp/biucing-p1-micro-runtime/evidence.json`。
- 仓库 worktree 验收脚本最终复验：`/tmp/biucing-p1-worktrees-final/evidence.json`，全部通过。
- 工作树验证的可重复入口：`uv run --locked python scripts/verify-backend-worktrees --output-dir /tmp/new-p1-worktrees`，仅使用新目录并清理自己创建的项目。

重点回归涵盖：伪造用户头无法绕过授权、已验证主体仍需策略、未知长度超大请求、panic 文本不外泄、
超时后未退出的 handler 继续占用预算、RPC streaming 不能绕过认证/截止时间、
关键依赖失败影响 ready 而不影响 live、监听部分失败释放资源、秘钥文件冲突/缺失、生产凭据拒绝、
日志不包含请求体/查询参数/Cookie/Authorization、审计洪泛有界。

## 尚未承诺的能力

- OIDC、浏览器会话、mTLS、真实 PostgreSQL/Redis 数据适配和迁移尚未实现；数据源选择仍是配置与本地设施。
- 默认 HTTP TimeoutHandler 有缓冲，超时返回 503，不支持业务 streaming；E07 单独实现。
- 无法强制终止忽略 context 的任意 Go 函数；预算槽位保持占用，进程停止最终回收它。RPC 截止时间与大小限制使用
  [grpc-go 服务端拦截器和配置](https://pkg.go.dev/google.golang.org/grpc)。
- 日志按预算可能丢弃，不是无损合规审计账本；stdout 背压与日志留存属于部署平台。P1 不宣称完成 OTel 全链路追踪或指标。
- 单机启动验证不是生产部署或多机高可用验收，模板成熟度没有提升为 production-ready。
