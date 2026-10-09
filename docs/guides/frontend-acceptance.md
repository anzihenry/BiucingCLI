---
title: "前端安装包验收"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="frontend-installed-artifact-acceptance"></a>
# 前端安装包验收

[English](frontend-acceptance.en.md)

阶段 6 将纯 Python 套件与成本较高的生成项目检查分开，无需改模板依赖、生成文件或输出 golden。生成器环境/构建用 uv，前端依赖用生成项目固定的 pnpm；不要在验收 venv 安装源码检出。

<a id="distribution-integrity"></a>
## 分发完整性

```bash
uv sync --locked
uv run --locked python scripts/verify-distribution --check-make
```

验证器将 biucingcli/template_data 全部文件（公共/模式层、隐藏、二进制、执行位）与 wheel/sdist 比较，缺失、多余、变化都失败。再隔离解包 sdist，以锁定解释器/构建依赖重建 wheel 并比较资源。它验证资源可复现，不保证 ZIP 时间戳或全部 wheel 元数据字节相同。解包写入前拒绝穿越、链接、特殊项；文件仅在新目录排他创建，不带归档所有权或 setuid，也支持早期 Python 3.11。

安装后 wheel 独立检查目录、验证、七模板和三前端模式生成。仍是纯 Python，不需 Node、浏览器或 Docker；--check-make 可选。

<a id="generated-project-acceptance"></a>
## 生成项目验收

需要 Node 24.19.0、pnpm 11.21.0、uv；只有 --docker 需要 Docker。工作目录不能存在且必须在仓库外。

```bash
frontend_audit_root="$(mktemp -d)"
uv build --no-sources --no-build-isolation --out-dir "$frontend_audit_root/dist"
uv run --locked python scripts/verify-frontend \
  --dist-dir "$frontend_audit_root/dist" \
  --work-dir "$frontend_audit_root/run" --docker
```

默认依次运行所有模式。--mode csr/ssg/ssr 可选单一模式或重复选项。并行运行需独立工作区/主机：生成开发/预览服务器使用固定端口；生产容器端口、名称、镜像标签按每次运行分配。

创建新 venv，安装显式 wheel 且不安装依赖，清除 Python 路径覆盖，并确认导入模块在该 venv。CLI 和生成项目全部在仓库外。特殊展示文本测试引号、Unicode、标记、字面占位符保留。wheel SHA-256、模式、浏览器通道、平台、阶段、时间记入 reports/summary.json。

每模式执行冻结安装、peer 检查、完整 pnpm verify、开发浏览器和构建产物浏览器检查。CSR/SSG 使用静态 preview，SSR 使用生产 Node 入口。SITE_URL 是固定公开 HTTPS 测试源；SSR 注入无害私有标记，不使用真实凭证。不能靠源 loader 状态或已有开发服务器意外满足验收。

默认装 Playwright 固定版本 Chromium Headless Shell（--only-shell）。Linux CI 加 --install-browser-deps 授权系统包安装，开发机刻意需主动选择。macOS --browser-channel chrome 可用已安装 Chrome，但单独报告，不计默认浏览器覆盖。可复用浏览器缓存，pnpm 原生依赖按 OS 安装。

--docker 构建生成 Dockerfile，等待健康，运行模式生产浏览器/HTTP 套件，查运行镜像内容，停止容器并要求退出 0。CSR/SSG 不含 Node/运行服务依赖；SSR 非 root，不含应用源码、私有 env、开发依赖。补充生成测试的 HTML/数据/状态/隔离断言。Docker 需本地 daemon，发布端口能在 127.0.0.1 访问，不支持远端 Docker 主机。

成功和失败都保留日志、各阶段截图/结果，后续 Playwright 不覆盖早期诊断。超时/中断终止自己创建的进程组。finally 只删 UUID 专属容器和镜像，浏览器失败也清理；工作区、pnpm store、报告保留供检查，不需要后仅删除显式选定审计目录。不全局 prune Docker，不清用户 worktree。进程/主机突然终止仍可能需按日志 ID 手动清理。

<a id="ci-and-release-gates"></a>
## CI 与发布关卡

frontend.yml 供 CI/发布复用，六任务为 Linux/macOS × CSR/SSG/SSR，仅一个 Python 版本，不随 core 矩阵倍增。两个 OS 各自安装原生前端依赖并运行默认浏览器；Linux 还测生产镜像，托管 macOS 不假设有 Docker。

CI 构建/验证并上传一份分发产物。发布测试随后 OIDC 上传的同一 python-distributions artifact，验收脚本检出指定标签。发布依赖 core/distribution、platform、frontend，无需修改 Trusted Publisher 或秘密。只上传 reports/，保留七天，不上传整项目、node_modules、私有 env。

工作流契约测试和 actionlint 本地验证连接；托管 runner 成功仍需推送/CI，本文实现不自动提交、推送、调度或发布。本地证据和托管限制见[渲染计划](../initiatives/feature/frontend-rendering/plan.md)阶段 6。成熟度仍 validated，不宣称生产认证或全浏览器/负载覆盖。
