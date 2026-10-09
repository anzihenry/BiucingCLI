---
title: "0.10.0 版本验证"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="0100-release-verification"></a>
# 0.10.0 版本验证

[English](validation.en.md)

验证日期：2026-09-30（Asia/Shanghai）。

<a id="scope"></a>
## 范围

包含 v0.9.1 之后的 CLI 校验与资源变体、前端 CSR/SSG/SSR、原生二进制组件和后端 P0–P5 参考交付。兼容变化见[版本说明](notes.md)。

<a id="local-release-checks"></a>
## 本地发布检查

- `uv lock`、`uv sync --locked` 通过，包/运行时/CLI/golden 版本一致。
- `uv run --locked python scripts/run-tests --suite core`：213 项通过。
- `uv run --locked python scripts/run-tests --suite platform`：12 项通过，无跳过。
- Ruff（`E4,E7,E9,F`）、`biucing validate` 通过。
- `uv build --no-sources --no-build-isolation` 构建 0.10.0 wheel 和 sdist。
- `scripts/verify-distribution --dist-dir /tmp/biucing-010-dist --check-make`：七类模板的资源精确性、执行位、sdist 重建、安装后生成和配置解析通过。

本地日志：`/tmp/biucing-010-{core,platform,distribution}.log`。工具环境：macOS arm64、uv 0.12.19；托管任务固定 uv 0.12.16。

<a id="release-fixes"></a>
## 发布修复

- 后端 task help 列出可用命令及 Make 对应项，包含 help。
- DNS 重连测试在 IPv4/IPv6 回环间切换，避免 macOS 未配置的 127.0.0.2 别名，仍测试真实 DNS 地址变化。
- 调用链证书 fixture 使用调用者 UID/GID，使 Linux bind mount 能读取本地 CA 密钥而不放宽权限。
- Android CI 在 sdkmanager 前初始化 SDK，避免已移除的旧 `tools` 包。
- Linux fixture 挂载让非 root 服务可读公开证书，CA 私钥仍仅所有者可读。恢复检查允许默认 30 秒 DNS 解析间隔，记录真实恢复时间而非假设 5 秒。
- Docker 调用链补验：`/tmp/biucing-010-calls-v2/evidence.json` 中 11 项全部通过；重启恢复 28.936 秒，叶证书轮换恢复 1.039 秒。它是 fixture 证据，不是生产 SLO。

生成快照只刷新两个刻意改动的后端文件，发布准备未改变原生和前端输出快照。

<a id="hosted-candidate-verification"></a>
## 托管候选验证

代码候选 `d106d88` 通过：

- [CI](https://github.com/anzihenry/BiucingCLI/actions/runs/36716267566)：8 个核心任务、macOS 平台检查、6 个安装包前端任务。
- [后端生成项目](https://github.com/anzihenry/BiucingCLI/actions/runs/36716267094)：Linux 上 6 种数据库/缓存组合及 Web→Micro 调用链。

本地 Kubernetes 渲染/schema 检查通过全部 12 组合：`/tmp/biucing-010-kubernetes/evidence.json`，结果 `structure-verified`；集群和 HA 仍为 `not-run`。共享 C++ 同步和 Twine 元数据也通过。后续发布文档不改变模板输出。

首次 TestPyPI 执行因补充验证发现可移植性问题，在上传前取消，不计为成功发布证据。

<a id="template-evidence-and-limits"></a>
## 模板证据与限制

对未变化的运行时/原生源码复用实现证据：[前端](../../guides/frontend-acceptance.md)、[原生会话契约](../../initiatives/feature/native-components/cross-platform-validation.md)、[Android](../../initiatives/feature/native-components/android-validation.md)、[HarmonyOS](../../initiatives/feature/native-components/harmonyos-validation.md)、[后端 P4](../../initiatives/feature/backend-services/p4-validation.md)、[后端 P5](../../initiatives/feature/backend-services/p5-validation.md)。

托管 CI 和 TestPyPI/PyPI 结果记录在 GitHub Release 与 Actions。包上传成功后必须从对应索引安装，验证版本和模板。

按用户要求，B27 真实跨可用区 HA 验收仍暂停。本次版本不包含云基础设施或故障注入。原生真机、商店签名和生产平台验收保留原记录限制。
