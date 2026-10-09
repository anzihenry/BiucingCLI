---
title: "更新日志"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="changelog"></a>
# 更新日志

[English](CHANGELOG.en.md)

详细历史记录与发布证据边界见[发布索引](docs/releases/README.md)。

<a id="0100---2026-09-30"></a>
## 0.10.0 - 2026-09-30

<a id="cli-and-packaging"></a>
### CLI 与打包

- 版本化 JSON 结果/错误、严格选项名、非交互输入、多语言/配置安全转义。
- 类型化创建计划、元数据文件契约，预览/校验/生成共享确定资源变体。
- 精确 wheel/sdist 资源、执行位、重建 wheel/安装输出；Python 3.11–3.14 core/platform 分层。

<a id="frontend"></a>
### 前端

- CSR/SSG/SSR React Router 预设，共享 React/TS/Tailwind、锁依赖、质量/浏览器验收。
- SSG 内容、元数据、sitemap、真实静态 404；SSR 请求隔离、私有配置、有界渲染/退出。
- Linux/macOS 安装工程、生产 Nginx/Node 容器矩阵。

<a id="native-components"></a>
### 原生组件

- iOS/macOS/watchOS/tvOS 消费版本化静态 XCFramework、精确锁、SafeDI，要求 Swift 6.4+。
- Android 手机/Wear/TV，Maven AAR、Dagger、JNI 会话、设备输入、独立身份。
- Harmony HAR/构造图/Node-API，共享权威 C++20。
- 跨平台所有权/取消/异步 close，无源码消费、完整性、显式覆盖验证。

<a id="backend"></a>
### 后端

- Docker task、独立数据库/缓存、文件秘密、私有健康/admin、有界请求退出。
- PG pool/锁迁移、Web OIDC/PG session、Micro mTLS/可信委托/协议兼容。
- HTTP/gRPC 客户端身份、预算、显式幂等重试、slog/OTel。
- 加固生产 Compose、签名镜像、迁移发布 guard、回退、隔离备份恢复。
- Kustomize 副本分散/HPA/network/连接预算/证据工具；B27 跨区 HA 暂停，不承诺生产可用性/恢复目标。
- 修复后端 help、macOS DNS 重连、Linux 证书 fixture 权限/恢复时序、Android CI SDK 初始化。

<a id="compatibility-changes"></a>
### 兼容性变化

- microservice 改为 micro-service，移除旧 CLI 名。
- 移除 dependency-store/dependency_store，改独立 database/cache；Micro 默认均无，Web 必需 PG。
- 移除 Web 内存 CRUD fixture，业务 API 由工程所有者添加。

<a id="091---2026-09-19"></a>
## 0.9.1 - 2026-09-19

- uv sync/提交 uv.lock 管理开发构建依赖。
- 锁工具执行 CI/产物检查。
- uv publish/Trusted Publishing 的 TestPyPI/PyPI 验证发布。

<a id="090---2026-09-07"></a>
## 0.9.0 - 2026-09-07

- 七模板打包，安装 CLI 不依赖源布局。
- 规范后派生平台/依赖。
- 未知模板/字段/目标/I/O 稳定错误。
- 暂存后原子发布。
- 跨版本 CI/七模板安装 gate。

<a id="080---2026-08-31"></a>
## 0.8.0 - 2026-08-31

- 统一输入校验和 bootstrap/doctor/lint/test/verify/build/clean/help。
- Android distribution/jar/checksum、AAB signer；Harmony 精确锁/SDK signer/profile/bundle 验证。
- Worker 耗尽、退避、周期继续、取消、注入时钟。
- HTTP 超时、signal 退出、health、HTTP/gRPC 排空。
- Apple Release 丢弃 Debug 后缀，签名上传前 workspace/archive 身份检查。
- 三原生忽略签名凭据，Harmony 注入恢复验证。
- Micro Ping 注册/Buf 生成运行前提。
- pnpm 锁/实际生产 Nginx Playwright。

<a id="070---2026-08-01"></a>
## 0.7.0 - 2026-08-01

- Apple/Android 配置凭据时签名 archive/upload/商店 track。
- Android 签名/AAB/BundleConfig.pb 校验。
- Harmony preflight/签名 HAP。
- 新原生真实证据：Apple iOS/macOS 生成构建测试模拟器；Android lint/unit/APK/AAB/UI；Harmony verify/test/HAP。
- 无对应账户/应用记录不声称真实商店上传。

<a id="061---2026-07-20"></a>
## 0.6.1 - 2026-07-20

- LABEL/哈希 ID/SLUG 统一。
- 端口建议/Compose config。
- static/doctor/real-build。
- Harmony 只读身份/暂缓改写。
- 七模板新证据。

<a id="060---2026-07-19"></a>
## 0.6.0 - 2026-07-19

- 共享隔离契约/证据。
- list/info/JSON/validate 展示支持。
- Docker project/卷/镜像/端口/依赖/缓存/诊断/清理。
- 原生缓存/签名配置/输出/后缀 hook。

<a id="050---2026-06-28"></a>
## 0.5.0 - 2026-06-28

- 实验 Harmony ArkTS/ArkUI/DevEco、参数/bootstrap/doctor/校验/渲染。
- 真实 hvigor 对齐、团队标准/lint guard/doctor/签名指导。
- 共享 app 配置/token/设置页/guard/本地签名 release。

<a id="040---2026-06-26"></a>
## 0.4.0 - 2026-06-26

- dry-run/plan/JSON 清单。
- 层级/假设/标签/族文件校验。
- scheduled/oneshot worker。
- 六模板发布/验证文档。

<a id="030---2026-06-19"></a>
## 0.3.0 - 2026-06-19

CLI 产品加固。

- category/tags/platforms/maturity/validation。
- list/info JSON。
- set/non-interactive。
- 元数据/占位校验。
- golden/发布清单/矩阵/专版准备。

<a id="020---2026-06-17"></a>
## 0.2.0 - 2026-06-17

模板系统扩展。

- Web 三模板 Docker 开发/构建/运行。
- Apple lint/format/doctor、iOS/macOS 输出、发布、AppServices。
- Android 格式/doctor/UI/签名/模块/设计。
- 完成原生路线、反复生成构建测试。

<a id="010---2026-06-06"></a>
## 0.1.0 - 2026-06-06

首个公开基线。

- 聚焦生成器 list/info/create 重写。
- frontend/apple/android/web-service/microservice starter。
- 文档围绕模板/团队环境。
- 实际生成/渲染验证。
