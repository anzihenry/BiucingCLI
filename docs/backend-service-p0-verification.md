# 后端服务 P0 验证记录

日期：2026-09-26。对应 [B01–B03](backend-service-implementation-tasks.md)。

## 完成内容

- B01：工程目录/依赖契约、两模板能力矩阵、迁移/代理/本地 IdP/测试 CA 选型和升级边界。
- B02：独立 `database` / `cache` 参数、六种合法组合、运行配置/Compose 拓扑、非法值拒绝、旧参数迁移说明、metadata/golden 更新。
- B03：仓库 `scripts/verify-backends`、生成项目 `scripts/verify-container`、两级 GitHub Actions、可区分生成与容器验证的 JSON 证据。

为使现有验证真正通过，同时修复了已有健康探测响应清理的 lint 问题、
Web 默认配置测试受容器 CONFIG_FILE 影响的问题、Micro 的 login shell 重置 Go PATH 问题，
并将 Micro 的 golangci-lint 参数迁移到当前工具版本支持的形式。

## 验证环境与范围

本机 Docker Desktop；Engine 29.8.0、Compose 5.5.1、容器 Linux arm64、Go 1.26.8。
使用非默认项目名、嵌套 Go module、`platform.*.v2` Protobuf package。
GitHub Actions 的 Linux amd64 检查已配置，本次未在远端触发，不算已验证平台。

| 生成组合 | 配置与拓扑解析 | Docker 开发镜像 / doctor / lint / tests / build |
| --- | --- | --- |
| Web：PostgreSQL / 无缓存 | 通过 | 通过 |
| Web：PostgreSQL / Redis | 通过 | 通过 |
| Micro：无数据库 / 无缓存 | 通过 | 通过 |
| Micro：PostgreSQL / 无缓存 | 通过 | 通过 |
| Micro：无数据库 / Redis | 通过 | 通过 |
| Micro：PostgreSQL / Redis | 通过 | 通过 |

六组合完整证据由以下命令产生，保存在本机 `/tmp/biucing-p0-final/evidence.json` 及同目录 case 日志：

```sh
.venv/bin/python scripts/verify-backends --output-dir /tmp/biucing-p0-final
```

随后显式固定验证用 Compose 命令、服务和文件，防止继承用户的生产配置；对应失败清理回归测试通过。
两模板对这一脚本调整的真实 Docker 复查记录在 `/tmp/biucing-p0-isolation-check/evidence.json`。
临时日志可能被系统清理；上述命令可在新的输出目录复现。

其他检查：

- 核心 Python 套件：203 项；包含六组合、非法参数、旧名拒绝、仅生成证据、失败清理隔离测试。
- 模板 `validate`、Ruff E4/E7/E9/F、脚本语法与 `git diff --check`。
- wheel/sdist 构建、从 sdist 重建 wheel、安装后七模板生成和配置解析。
- 最终日志：`/tmp/biucing-p0-core-complete.log`、`/tmp/biucing-p0-distribution-complete.log`。

## 本阶段没有证明的能力

本次容器验证故意使用 `--no-deps`，没有启动真实 PostgreSQL/Redis，验证的是组件配置与当前 starter 代码，
不证明连接、事务、会话或缓存可用性。真实依赖集成从 B09 开始；生产镜像/部署在 B20–B24 验收。
OIDC、mTLS、迁移、反向代理和测试 CA 在 P0 只固定选型，尚未集成测试。

未以宿主完整 discovery 代替核心套件：早期混合运行包含 Swift 缓存权限和宿主 socket 沙箱限制引起的失败；
P0 相关 Go 代码在 Docker 中运行通过。原有 starter 成熟度标签未提升为生产或高可用就绪。
