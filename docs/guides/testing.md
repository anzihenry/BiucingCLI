---
title: "测试套件与配置验证"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="test-suites-and-configuration-validation"></a>
# 测试套件与配置验证

[English](testing.en.md)

内核拆分契约和生成快照见[阶段零基线](../initiatives/refactor/generation-kernel/baseline.md)；基础边界和 fixture-root API 见[内核模块](../engineering/kernel-modules.md)。

test_unified_generation.py 对普通/分层 fixture 使用相同契约，覆盖输出字节/权限、源变化、必需项/Make、链接、目标冲突、只读清理、取消和兼容入口。变体专项仍覆盖叠加、选择、遮蔽/未选择资源。以下测试总数属于各历史阶段；当前验收见[统一生成](../initiatives/refactor/unified-generation/validation.md)。不因内核改动重生成 golden。

前端扩展有独立[阶段零规范与基线](../initiatives/feature/frontend-rendering/plan.md)，逐阶段记录生成项目验收。阶段 6 增加[安装后 wheel 三模式运行器及 CI](frontend-acceptance.md)，不计作 Python core 证明；托管结果需真实 CI。阶段 1 在 test_resources.py 加 21 项纯 Python 声明/选择测试，阶段 2 在 test_variant_generation.py 加 17 项集成，阶段 3 在 test_frontend_variants.py 加 4 项已交付 CSR，阶段 4 加 2 项 SSG 契约及 frontend-ssg golden（总计 159 core、11 platform、1 Android）。fixture 与前端构建分开，仅刻意迁移 generation/list/required-file golden 的前端项，其他模板基线不变。

用 uv sync --locked 安装锁定开发/构建环境。

<a id="frontend-csrssgssr-toolchain-separate-from-python-core"></a>
## 前端 CSR/SSG/SSR 工具链（独立于 Python core）

生成新项目，在项目内执行下列命令。SSG（--set rendering=ssg）在 verify/build/生产浏览器前导出 SITE_URL=https://your-public-domain.example；仅开发可省略，此时不输出 canonical origin。源在构建时验证，不增加为生成器变量，不静默默认 localhost。

```bash
pnpm install --frozen-lockfile
pnpm peers check
pnpm verify
pnpm browser:install
pnpm browser:smoke
pnpm browser:smoke:build
make browser-smoke-production
```

使用 Node 24.19.x、pnpm 11.21.0。verify 包括格式、类型感知 lint、TS 7 版本断言、刻意无效的类型 lint 负控制、组件测试、路由类型生成、生产构建。browser:smoke:build 静态产物用 Vite preview；生产 Make 经 Docker 测真实 Nginx，需 daemon。本地可用 PLAYWRIGHT_CHANNEL=chrome，但不是 CI 打包 Chromium 结果。tests/interactions.ts 共享交互，测桌面/移动导航、刷新、计数器、对话框 Escape/焦点、溢出、错误。Nginx 专项还测壳 HTML、favicon、缺失资源及未知路由 CSR HTTP-200/客户端 not-found。

阶段 3 macOS 已装 Chrome 的冻结安装、质量关卡、开发/构建浏览器通过；显式 PLAYWRIGHT_CHANNEL=chromium 的构建也过（另两视口）。单独 Headless Shell 下载在清理时取消，不宣称该 macOS 默认通道成功。Docker Linux arm64 补验通过普通开发镜像、冻结安装、严格 peer、make verify、生产镜像、Nginx 健康/静态运行检查；macOS Chrome 另通过三项真实 Nginx 测试。SPA prerender 的 IPv4/IPv6 不匹配以 preview.host: "127.0.0.1" 和 Python 回归断言修复，之后 macOS/Docker 生产构建通过。不宣称可选全开发镜像、amd64/原生 Linux、远端 CI。完整安装后 wheel 三模式 Node/容器 CI 属阶段 6，不属于当时 Python 矩阵。

Docker Linux arm64 显式 Chromium 补验三项真实 Nginx 通过，随后不改 Make 的默认 Headless Shell 流程通过三项生产、两项开发。这是实际容器浏览器覆盖，区别于 macOS Chrome/Vite preview。

<a id="stage-4-ssg-acceptance"></a>
## 阶段 4 SSG 验收

SSG 共享 CSR 锁/质量关卡。app/lib/site.test.ts 测 origin 和内容查找，共享组件还检查服务端 HTML 禁用操作。4 项单元/组件通过；Linux 默认 Headless Shell 生产 7 项通过：桌面/移动交互和数据导航、延迟 JS hydration、原始 HTML/元数据/sitemap/固定数据、真实静态 404。Linux 开发冷缓存/重复启动均 4 项通过；macOS Chrome 开发/静态 preview 各 4 项通过；默认 CSR 开发/preview 各 2 项和完整质量关卡通过。

构建期 SITE_URL 负测拒绝缺失/无效源。preview 按模式拥有：SSG 映射已知路径预渲染文档，CSR 保持 SPA fallback。Nginx 状态/头部用生产 Make；Vite preview 不证明部署正确。Python 包含 SSG golden、全模式配置解析、wheel/sdist SSG 资源、安装后生成。当阶段尚未覆盖安装 wheel 的 Node/浏览器、amd64、远端 CI；范围/冷启动修复见阶段 4。

上述是各阶段当时证据。阶段 6 不改生成输出而加安装后执行，macOS/Linux 结果和当时待完成托管关卡见[产物验收](frontend-acceptance.md)及阶段 6 记录。

<a id="stage-5-ssr-acceptance"></a>
## 阶段 5 SSR 验收

--set rendering=ssr 生成，共享锁和质量命令。pnpm browser:smoke:build 直接启动生产 Node，7 项检查含隔离错误配置服务探针（脱敏 HTML/data 500）及客户端 bundle 私有模块扫描。pnpm preview 用 Vite host，也渲染请求但非生产进程。make browser-smoke-production 测实际非 root 镜像，注入无害私有标记、查健康、跑 5 项浏览器/HTTP，再断言 SIGTERM 干净退出；不要用真实秘密作 fixture。macOS Chrome 和 Docker Linux arm64 默认 Headless Shell 通过；Linux 冷缓存/重复开发通过。因容器下载慢，通过主机网络预取精确 Linux 浏览器，未跳过断言。Linux pnpm browser:install --only-shell 正常依赖验证也通过；冗余全 Chromium 下载在 Shell 验收后取消，不计成功。

31 项生成单元/组件覆盖请求快照、无效输入、私有配置错误、SSR HEAD/状态/期限/取消、静态路径/链接、缓存头及优雅/强制连接排空。4 项开发覆盖桌面/移动、12 个并发请求独立 HTML、状态码、特殊输入 hydration。新增 SSR ownership/确定性 Python 和输出 golden 将总数带至 161 core+11 platform+1 Android=173；安装 wheel/sdist 包含 SSR 资源和独立生成配置。阶段 6 实现安装运行器及六任务 Node/browser CI，真实托管仍需推送；11 项产物/runner/CI 回归使总数 172+11+1=184，随后缓存污染检查使 173+11+1=185。

污染检查覆盖公共/模式前端资源层中的本地依赖/构建产物，含 Git 不追踪的空目录。不要在模板源内运行包管理器，生成仓库外项目检查。三个前端 golden 曾误含 .pnpm-store/v3 空目录，只移除这些目录记录。修正后的 173 项 core 在带修复补丁的新 Git archive 也通过，未复制忽略/未追踪工作区文件。

实际平台和限制见渲染计划阶段 5；生成项目检查独立于纯 Python core CI。

<a id="core-linux-and-macos"></a>
## Core：Linux 与 macOS

```bash
uv run --locked python scripts/run-tests --suite core
uv run --locked python scripts/verify-distribution
```

只需 Python 和锁定依赖，不需 Go/Node/Java/zsh/Xcode/Android SDK。CI/发布在 Ubuntu/macOS 各 Python 3.11–3.14 执行及安装验证。

解析生成 JSON、JSON5、YAML、TOML、XML、plist、entitlements，含隐藏配置目录。拒绝 JSON/JSON5/YAML 重复键，YAML 用支持 merge 的安全 loader。失败标出相对路径。覆盖七模板、Apple 平台、Micro 依赖、特殊文本、坏文件、不安全 YAML tag。分发验证也解析仓库外安装 wheel 的生成文件。解析器属开发依赖，不是 CLI 依赖。

这是语法检查，不是 schema 验证或原生构建证明；biucing validate 保持元数据验证职责。

<a id="platform-integrations-macos"></a>
## 平台集成：macOS

```bash
uv run --locked python scripts/run-tests --suite platform
uv run --locked python scripts/verify-distribution --check-make
```

需匹配生成项目的 Go、Node、Swift、Git、Make、zsh、JDK keytool/jarsigner、/usr/libexec/PlistBuddy。CI 用 Go 1.26.x、Node 24、runner Swift/JDK、Python 3.11。独立 job 验证 shell/Make、Go 测试、Java 签名 fixture、Apple 身份、JS/Swift 转义，属于发布关卡。

<a id="optional-android-sdk-integration"></a>
## 可选 Android SDK 集成

```bash
AAPT2=/absolute/path/to/sdk/build-tools/VERSION/aapt2 \
  uv run --locked python scripts/run-tests --suite android
```

用真实 SDK 编译生成资源，不属于无 SDK core。指定套件缺前提或跳过测试就失败，缺工具不能静默满足覆盖。

各套件 --list 可查看成员。未标记为 core；suite_support.py 的 platform_test/android_test 纳入工具依赖组。--suite all 和普通 unittest discover 保留完整执行（那里可跳过可选工具）。

<a id="test-organization-after-kernel-extraction"></a>
## 内核拆分后的测试组织

| 范围 | 模块 |
| --- | --- |
| CLI、优先级、交互 | `test_cli.py`、`test_cli_errors.py` |
| 公共输出 | `test_json_contract.py`、`test_presentation.py` |
| 模型、目录、加载 | `test_catalog.py` |
| 声明与结构验证 | `test_template_declarations.py`、`test_template_validation.py` |
| 纯渲染/规则 | `test_rendering.py`、`test_rule_helpers.py`、`test_template_rules.py` |
| 规划/文件系统执行 | `test_generation_plan.py`、`test_generation.py` |
| 资源变体/有效生成 | `test_resources.py`、`test_variant_generation.py` |
| 生成内容 | `test_native_outputs.py`、`test_service_outputs.py` |
| 外部工具 | `test_platform_integration.py` 及标记的转义测试 |
| 转义/配置解析 | `test_escaping.py`、`test_configurations.py` |
| 稳定生成输出 | `test_refactor_baseline.py`、`generation_baseline.py`、`golden/` |

cli_support.py 仅共享 fixture，无发现测试。只检查文件的原生断言属于 core，位置不决定套件；需工具的方法保持显式标记。阶段 6 保留全部 122 个既有测试方法各一次，加 5 项 presentation（115 core、11 platform、1 Android）。

新单测导入拥有者模块；旧导入检查只放显式兼容测试。移动 mock 要定位实际使用符号的模块，不保留隐含耦合。不为迁就重构刷新 golden，应检查刻意输出变化。

阶段 6 对此前已过期、局部 CLI 断言未使用的 info-web-service.txt 恢复直接断言。成熟度摘要按阶段前已提交 CLI 输出协调，不从新实现推断。生成和 JSON golden 未变。

HarmonyOS 二进制架构在 core 加 test_harmony_components.py，覆盖锁闭包、独立升级、override、安装 SDK 篡改、源码替换、DI 拒绝、规范核心同步。可选 harmonyos-components.yml 需 harmonyos-sdk611 标签 runner，评审工具在 PATH。生成项目提供 make core-test/test-native/verify-di/verify/build-device-tests。实际执行及主机测试、测试包编译、设备运行的区别见[HarmonyOS 验证](../initiatives/feature/native-components/harmonyos-validation.md)。

<a id="documentation-gate"></a>
## 文档关卡

uv run --locked python scripts/check-docs 验证维护 Markdown、导航、证据路径。失败场景由 uv run --locked python -m unittest discover -s tests -p test_documentation.py 覆盖，并纳入 core 和 CI documentation。生成项目 Markdown 属模板载荷，不属仓库导航关卡。
