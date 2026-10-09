---
title: "BiucingCLI 验证矩阵"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-verification-matrix"></a>
# BiucingCLI 验证矩阵

[English](verification-matrix.en.md)

定义当前七模板及 CLI 的最低发布要求，让证据明确可复用，无须每提交重跑所有重型流程。

<a id="release-wide-checks"></a>
## 全发布检查

每次发布均适用。

| 范围 | 命令或证据 | 门槛 |
| --- | --- | --- |
| core | `uv run --locked python scripts/run-tests --suite core` | Linux/macOS Python 3.11–3.14 |
| platform | `uv run --locked python scripts/run-tests --suite platform` | macOS Python 3.11，无跳过 |
| 配置解析 | `uv run --locked python scripts/verify-distribution` | 各 core job 安装输出可解析 |
| Make 入口 | `uv run --locked python scripts/verify-distribution --check-make` | macOS gate |
| 元数据 | `uv run --locked biucing validate` | 零错误 |
| 人类 list | test_cli.py golden：biucing list | 通过 |
| JSON list | test_cli.py golden：list --json | 通过 |
| 人类 info | test_cli.py golden：info web-service | 通过 |
| JSON info | test_cli.py golden：info web-service --json | 通过 |
| Worker info | info worker 与 --json 测试 | 通过 |
| Harmony info | info harmonyos 测试 | 通过 |
| worktree | list --json/golden | 全部 ready |
| 脚本 create | set/non-interactive 测试 | 通过 |
| 预览/清单 | dry-run/plan --json/create --json | 通过 |
| 版本 | version 测试/文件一致 | 通过 |

<a id="template-matrix"></a>
## 模板矩阵

| 模板 | 状态 | 仓库证据 | 模板变化后的新证据 | 说明 |
| --- | --- | --- | --- | --- |
| frontend | real-build-verified | 渲染/字段 | 真生成/Docker test/docker-build | 行为/dev 改时 browser smoke |
| web-service | real-build-verified | 渲染/字段 | 真生成/Docker verify/docker-build | 镜像/Make 改时开发和运行均验 |
| micro-service | real-build-verified | 渲染/字段 | 真生成/Docker verify/up/docker-build | Compose/proto 改时独立 DB/cache 组合 |
| worker | generated-project-verified | 渲染/字段 | 真生成 go test ./...；Docker 改时打包 | 聚焦后台而非 HTTP/RPC |
| apple | generated-project-verified | 渲染/字段 | static/doctor；结构/Tuist/设置改时 real-build | 共享骨架大改重验 iOS/macOS |
| android | generated-project-verified | 渲染/字段 | static/doctor；Gradle/manifest/签名/打包/设置改时真实构建 | 结构/测试/tool 改时 UI |
| harmonyos | generated-project-verified | 渲染/字段 | static/doctor；metadata/hvigor/签名/打包/设置改时真实构建 | 区分生成能力和本机 SDK |

<a id="worktree-isolation-matrix"></a>
## Worktree 隔离矩阵

适用 0.6.0、0.6.1 及后续。

| 族 | 必需证据 | 门槛 |
| --- | --- | --- |
| 全部 | 新生成，`make worktree-info WORKTREE_ID=alpha`、`make worktree-doctor WORKTREE_ID=alpha` | 完成/显示身份、缓存输出、清理 |
| Docker | 显式 project/非默认端口执行 compose.dev config | 独立 project/卷/镜像/端口 |
| 原生 | `make -n build WORKTREE_ID=beta` 或相近 | 无重构建，展开独立缓存/Debug 后缀 |
| 清理 | 安全时 inspect/dry-run `make clean-worktree WORKTREE_ID=beta` | 仅自身，无全局 SDK/共享镜像/无关状态 |

<a id="native-evidence-tiers"></a>
## 原生证据层级

发布说明/准备使用精确层级。

| 层级 | 证明 | 不证明 |
| --- | --- | --- |
| static | 渲染/元数据/命令/dry-run | SDK/编译/设备/签名 |
| doctor | 本地工具/路径诊断，无全局修改 | 构建/产物/安装/行为 |
| real-build | 配置好的工作站编译或测试 | 跨机器一致/商店就绪/未跑的平台 |

make -n 永远是 static，即使命令看似正确也非构建。

<a id="native-evidence-commands"></a>
### 原生证据命令

新目录复现。

| 模板 | `static` 证据 | `doctor` 证据 | `real-build` 证据 |
| --- | --- | --- | --- |
| `apple` | `make worktree-info WORKTREE_ID=alpha`, `make -n build test lint format WORKTREE_ID=beta` | `make worktree-doctor WORKTREE_ID=alpha`；Xcode/Tuist 安装后加 `make doctor` | 每个声称支持的平台运行 `make generate`，再 `make build` 或 `make test` |
| `android` | `make worktree-info WORKTREE_ID=alpha`, `make -n build test test-ui lint install-debug WORKTREE_ID=beta` | `make worktree-doctor WORKTREE_ID=alpha`；JDK/SDK 安装后加 `make doctor` | `./gradlew assembleDebug`；声称测试或设备覆盖时加 `./gradlew test` 或 `./gradlew connectedDebugAndroidTest` |
| `harmonyos` | `make worktree-info WORKTREE_ID=alpha`, `make worktree-debug-identity WORKTREE_ID=alpha`, `make -n build clean-worktree WORKTREE_ID=beta` | `make worktree-doctor WORKTREE_ID=alpha`；DevEco/ohpm/hvigorw/SDK 配置后加 `make doctor` | 配置 DevEco/SDK 后 `make build`；签名/打包流程变化时再加对应命令 |


结构、manifest、身份、签名输入、设置、平台依赖文件、构建/测试目标变化必须 real-build。仅文档、CLI 字段、诊断措辞且不改行为时可选。建议新 worktree 证据：

| 模板 | Worktree 证据 |
| --- | --- |
| `frontend` | `make worktree-info WORKTREE_ID=alpha`, `make worktree-doctor WORKTREE_ID=alpha`, `COMPOSE_PROJECT_NAME=demo-frontend-alpha DEV_HOST_PORT=5174 docker compose -f compose.dev.yaml config` |
| `web-service` | `make worktree-info WORKTREE_ID=alpha`, `make worktree-doctor WORKTREE_ID=alpha`, `COMPOSE_PROJECT_NAME=demo-service-alpha HOST_PORT=18081 docker compose -f compose.dev.yaml config` |
| `micro-service` | `make worktree-info WORKTREE_ID=alpha`, `make worktree-doctor WORKTREE_ID=alpha`, `COMPOSE_PROJECT_NAME=demo-micro-alpha HOST_HTTP_PORT=18080 HOST_GRPC_PORT=19090 HOST_DEPENDENCY_STORE_PORT=15432 HOST_OTEL_GRPC_PORT=14317 HOST_OTEL_HTTP_PORT=14318 docker compose -f compose.dev.yaml config` |
| `worker` | `make worktree-info WORKTREE_ID=alpha`, `make worktree-doctor WORKTREE_ID=alpha`, `COMPOSE_PROJECT_NAME=demo-worker-alpha DEV_IMAGE=demo-worker-alpha-dev DEV_TAG=dev docker compose -f compose.dev.yaml config` |
| `apple` | 静态加 doctor： `make worktree-info WORKTREE_ID=alpha`, `make worktree-doctor WORKTREE_ID=alpha`, `make -n build test lint format WORKTREE_ID=beta` |
| `android` | 静态加 doctor： `make worktree-info WORKTREE_ID=alpha`, `make worktree-doctor WORKTREE_ID=alpha`, `make -n build test test-ui lint install-debug WORKTREE_ID=beta` |
| `harmonyos` | 静态加 doctor： `make worktree-info WORKTREE_ID=alpha`, `make worktree-debug-identity WORKTREE_ID=alpha`, `make worktree-doctor WORKTREE_ID=alpha`, `make -n build clean-worktree WORKTREE_ID=beta` |


<a id="recommended-command-catalog"></a>
## 建议命令目录

需要新证据时优先使用：

| 模板 | 建议生成命令 | 建议验证命令 |
| --- | --- | --- |
| `frontend` | `uv run --locked biucing create frontend demo-frontend --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-frontend` | `make test`, `make docker-build` |
| `web-service` | `uv run --locked biucing create web-service demo-service --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-service --set module_name=github.com/example/demo-service` | `make verify`, `make docker-build` |
| `micro-service` | `uv run --locked biucing create micro-service demo-microservice --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-microservice --set module_name=github.com/example/demo-microservice --set proto_package=demo.v1` | `make verify`, `make up`, `make docker-build` |
| `worker` | `uv run --locked biucing create worker demo-worker --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-worker --set module_name=github.com/example/demo-worker` | `go test ./...`, Docker 路径变化时再 `make docker-build` |
| `apple` | `uv run --locked biucing create apple demo-apple --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-apple --set bundle_identifier=com.example.demoapple` | `make generate`，再 `make build` 或 `make test` |
| `android` | `uv run --locked biucing create android demo-android --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-android --set package_name=com.example.demoandroid` | `./gradlew assembleDebug`, 适用时再 `./gradlew assembleRelease` |
| `harmonyos` | `uv run --locked biucing create harmonyos demo-harmony --output-dir /tmp/biucing-verify --non-interactive --set project_name=demo-harmony --set bundle_name=com.example.demoharmony` | 配置 DevEco/SDK 后 `make doctor`、`make lint`、`make build` |


每模板新空目录，使证据可解释复现。

<a id="change-type-guidance"></a>
## 按变化类型验证

| 变化 | 最低要求 |
| --- | --- |
| 仅 CLI | 全发布检查 |
| 单模板字段 | 全检查/info；语义变时新模板证据 |
| 共享渲染/占位 | 全检查、至少 Docker/原生各一 |
| worktree 字段/命令 | 全检查、每受影响模板 |
| Web 三模板 Docker/Compose/Make | 全检查及受影响生成 Docker |
| worker | 全检查/go test，Docker 改时打包 |
| Apple/Android 结构 | 全检查/static/doctor/real-build |
| Harmony 结构 | 全检查/static/doctor；SDK 可用时跑并记真实构建 |
| 版本/发布文档 | 全检查/changelog/readme/version 对齐 |

<a id="current-evidence-baseline"></a>
## 当前证据基线

metadata：前三 Web 模板 real-build-verified，其余四 generated-project-verified。自动覆盖：unittest 渲染、validate、list/info 双形式 golden、set/non-interactive、预览/JSON 清单、worker go test、全部 worktree/Make。0.7.0 [验收](../releases/0.7.0/validation.md)另外记录三原生真实构建，是工作站证据，不声称账户或外分发。

<a id="maintainer-notes"></a>
## 维护者说明

少量明确命令可重跑；未改模板有意跳重验证时说明，不暗示新证据；阻塞先区分机器或模板；原生标 tier。最新具体准备见 [0.10.0](../releases/0.10.0/validation.md)。

<a id="backend-p0-verification"></a>
## 后端 P0 验证

[契约](../engineering/backend/contracts.md)/[P0](../initiatives/feature/backend-services/p0-validation.md)。verify-backends 生成六 DB/cache 组合，Docker 入口和新目录证据；generate-only 仅生成非真实构建；生成 verify.yml 用 scripts/verify-container。P0 不等于认证/数据库/生产。

<a id="backend-p1-runtime-foundation"></a>
## 后端 P1 运行底座

[P1](../initiatives/feature/backend-services/p1-validation.md)。scripts/task verify 在 Docker 检配置/lint/协议/race/编译。`uv run --locked python scripts/verify-backend-worktrees --output-dir /tmp/new-worktree-evidence` 验隔离/reload/归属/保卷/runtime image。身份/数据/HA 分开。

<a id="backend-p2-data-and-identity"></a>
## 后端 P2 数据与身份

[P2](../initiatives/feature/backend-services/p2-validation.md)。容器实际 PG/迁移/权限/事务/session，Web OpenAPI breaking/签令牌，Micro 真实 proto 基线/TLS/轮换/方法委托；dev 后 scripts/verify-backend-login 验 Dex，runtime smoke 独立迁移。

<a id="backend-p3-call-chain"></a>
## 后端 P3 调用链

`uv run --locked python scripts/verify-backend-calls --output-dir <new-directory>` 验独立镜像/OIDC/mTLS/预算恢复/trace-log。fixture 路由不发布。实际范围见 [P3](../initiatives/feature/backend-services/p3-validation.md)。

<a id="backend-p4-production-delivery"></a>
## 后端 P4 生产交付

`uv run --locked python scripts/verify-backend-production --web-project <generated-web> --micro-project <generated-micro> --web-image <built-web> --micro-image <built-micro> --output-dir <new-directory>` 验隔离签名 registry digest、加固 Compose/TLS/故障/回退/真实备份。默认 edge-api/internal-api；harness 拥有临时设施，无需生产凭据。

`uv run --locked python scripts/verify-distribution --backend-output-dir <new-directory>` 保留安装 wheel/重建 wheel 工程；再跑 verify-container、构建 runtime、生产 harness。分发命令自身非 Docker 证据。[P4](../initiatives/feature/backend-services/p4-validation.md)说明平台/命令/外 CI/HA 限制。

<a id="backend-p5-kubernetes-reference"></a>
## 后端 P5 Kubernetes 参考

`uv run --locked python scripts/verify-backend-kubernetes --schema --output-dir <new-dir>` 真 Kustomize 六组合/两 overlay，检查政策/身份/容量，固定 kubeconform/Kubernetes 1.35 schema；不连集群，cluster/ha not-run；安装输出也跑 verify-kubernetes。API admission/CNI/scheduler/EndpointSlice/drain/managed PG/zone loss 需 B27。[P5](../initiatives/feature/backend-services/p5-validation.md)区分待验、结构和 mock 发布顺序。
