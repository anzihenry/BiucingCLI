---
title: "BiucingCLI 0.6.0 Worktree 任务拆分"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-060-worktree-task-breakdown"></a>
# BiucingCLI 0.6.0 Worktree 任务拆分

[English](plan.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

将计划拆为可评审实施片段。每阶段须验证通过，大小适合一次提交。

<a id="phase-a-contract-and-audit"></a>
## 阶段 A：契约与审计

<a id="goal"></a>
### 目标

改行为前定义含义。

<a id="tasks"></a>
### 任务

加契约；审计七模板端口/容器/卷/镜像/缓存/输出/签名/安装；分类阻断/重要/可选；定元数据。

<a id="acceptance-criteria"></a>
### 验收标准

文档存在并链接；七模板覆盖；区分 Docker/原生；本阶段不改实现。

<a id="status"></a>
### 状态

规划完成。[契约](../../../engineering/worktree-isolation-contract.md)、[审计](audit.md)。

<a id="verification"></a>
### 验证

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
```

<a id="phase-b-metadata-and-validation"></a>
## 阶段 B：元数据与校验

<a id="goal-1"></a>
### 目标

生成器可见/约束支持。

<a id="tasks-1"></a>
### 任务

各 template.json、dataclass/JSON、list/info JSON 测试、人类 info、validate、golden、系统文档。

<a id="proposed-metadata-shape"></a>
### 建议结构

```json
{
  "worktree": {
    "support_level": "planned",
    "isolation_dimensions": [
      "runtime-names",
      "ports",
      "caches",
      "local-config"
    ],
    "diagnostics": [
      "make worktree-info",
      "make worktree-doctor"
    ],
    "cleanup": [
      "make clean-worktree"
    ]
  }
}
```

planned 未实现、partial 有缺口、worktree-ready 满足。

<a id="acceptance-criteria-1"></a>
### 验收标准

全部声明、缺失/畸形失败、info 显示、旧 JSON 字段稳定。

<a id="status-1"></a>
### 状态

完成：info 显示支持/维度/诊断/清理，JSON 含 worktree，validate 检查取值和重复。

<a id="verification-1"></a>
### 验证

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli list --json
PYTHONPATH=src python3 -m biucingcli.cli info frontend
PYTHONPATH=src python3 -m biucingcli.cli info frontend --json
```

<a id="phase-c-docker-first-template-isolation"></a>
## 阶段 C：Docker 模板

<a id="goal-2"></a>
### 目标

四模板并行安全。

<a id="shared-tasks"></a>
### 共享任务

ID/SLUG/project/CACHE_DIR/端口变量，三目标，project/卷/镜像身份化，Compose 传 project，README 示例，渲染测试。

<a id="frontend-specific-tasks"></a>
### 前端任务

隔离 node_modules/pnpm/Playwright/开发端口/运行镜像；FRONTEND_HOST_PORT 或 DEV_PORT/HOST_PORT 明确冲突；smoke 独立 URL。

<a id="web-service-specific-tasks"></a>
### Web 任务

隔离 Go/lint cache/热重载/镜像/HTTP；dev/verify/docker-run/clean 用同身份。

<a id="microservice-specific-tasks"></a>
### 微服务任务

隔离 HTTP/gRPC/依赖/OTel/卷/protobuf 输出假设；两存储变体。

<a id="worker-specific-tasks"></a>
### Worker 任务

隔离 Go/容器/镜像/定时状态，保证两模式。

<a id="acceptance-criteria-2"></a>
### 验收标准

两工程 info 不同；不同 ID Compose project 不同；无共享固定卷；命令仍熟悉。

<a id="status-2"></a>
### 状态

完成：四模板 ready，派生身份/镜像，COMPOSE 包装，端口可覆可见，三命令。

<a id="verification-2"></a>
### 验证

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli create frontend wt-frontend-a --output-dir /tmp/biucing-0.6-check --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create web-service wt-web-a --output-dir /tmp/biucing-0.6-check --module-name github.com/example/wt-web-a --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create microservice wt-micro-a --output-dir /tmp/biucing-0.6-check --module-name github.com/example/wt-micro-a --proto-package example.service.v1 --non-interactive
PYTHONPATH=src python3 -m biucingcli.cli create worker wt-worker-a --output-dir /tmp/biucing-0.6-check --module-name github.com/example/wt-worker-a --non-interactive
```

每工程：

```bash
make worktree-info
make worktree-doctor
WORKTREE_ID=alpha docker compose -f compose.dev.yaml config
WORKTREE_ID=beta docker compose -f compose.dev.yaml config
```

快 Compose 检查通过后再重构建。

<a id="phase-d-native-template-isolation"></a>
## 阶段 D：原生模板

<a id="goal-3"></a>
### 目标

三模板并行构建/测试/本地发布准备。

<a id="shared-tasks-1"></a>
### 共享任务

身份、本地缓存输出、签名配置、后缀，三命令，忽略本地文件，README 示例，Make/hook 测试。

<a id="apple-specific-tasks"></a>
### Apple 任务

DerivedData、SwiftPM 可见、Tuist/SwiftLint/SwiftFormat 缓存；DEBUG_BUNDLE_SUFFIX 传清单；fastlane/.env 本地诊断不泄密。

<a id="android-specific-tasks"></a>
### Android 任务

Gradle home/输出/配置/Debug ID；后缀从属性/env；Make 用身份 wrapper。

<a id="harmonyos-specific-tasks"></a>
### HarmonyOS 任务

hvigor/ohpm home、modules/entry 输出/签名；hvigor 传 ID/请求后缀；除明确支持本地改写外保持 AppScope 稳定。

<a id="acceptance-criteria-3"></a>
### 验收标准

三命令/ready；Apple 独立 DerivedData/后缀；Android 独立 home/applicationIdSuffix；Harmony 独立路径及请求行为可见。

<a id="status-3"></a>
### 状态

完成：身份/缓存/命令，Apple Tuist 后缀/xcodebuild 路径，Android biucing.worktree.applicationIdSuffix/home，Harmony 传属性但默认清单稳定。

<a id="verification-3"></a>
### 验证

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli create apple phase-d-apple --output-dir /tmp/biucing-phase-d --platform ios --bundle-identifier com.example.phasedapple --organization-name Example --development-team ABCDE12345
PYTHONPATH=src python3 -m biucingcli.cli create android phase-d-android --output-dir /tmp/biucing-phase-d --package-name com.example.phasedandroid --application-id com.example.phasedandroid.app --android-namespace com.example.phasedandroid
PYTHONPATH=src python3 -m biucingcli.cli create harmonyos phase-d-harmony --output-dir /tmp/biucing-phase-d --bundle-name com.example.phasedharmony --harmony-module-name entry --ability-name EntryAbility
```

每工程：

```bash
make worktree-info WORKTREE_ID=alpha
make worktree-doctor WORKTREE_ID=alpha
make -n build WORKTREE_ID=beta
```

<a id="phase-e-release-hardening"></a>
## 阶段 E：发布加固

<a id="goal-4"></a>
### 目标

证据和文档符合故事。

<a id="tasks-2"></a>
### 任务

更新 README、delivery-history、template-system、releasing、verification-matrix，添加 0.6.0 validation，changelog 草稿，仓库验证和目标生成证据。

<a id="acceptance-criteria-4"></a>
### 验收标准

文档契约一致；清单隔离检查；矩阵每模板证据；changelog 用户可靠性。

<a id="status-4"></a>
### 状态

完成：文档反映 ready，清单/矩阵 worktree，专版证据和 changelog 草稿。

<a id="verification-4"></a>
### 验证

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli list --json
```

<a id="suggested-commit-slices"></a>
## 建议提交片段

1. docs: plan worktree-first 0.6.0
2. docs: add worktree isolation contract
3. feat: expose worktree metadata in templates
4. feat: validate worktree metadata
5. feat: isolate frontend worktree workflows
6. feat: isolate web service worktree workflows
7. feat: isolate microservice worktree workflows
8. feat: isolate worker worktree workflows
9. feat: isolate apple worktree workflows
10. feat: isolate android worktree workflows
11. feat: isolate harmonyos worktree workflows
12. docs: prepare 0.6.0 release evidence

<a id="risk-register"></a>
## 风险登记

| 风险 | 缓解 |
| --- | --- |
| 端口自动选择难调试 | 先显式变量/诊断 |
| ID 意外变 | 路径默认且可覆 |
| 卷命名不一致 | Make 统一并测试 |
| 原生抗拒路径 | 记录支持层，暂缓危险 hack |
| 清理过量 | 当前范围，不删全局 |
| 字段无实施价值 | 绑定验证/info/证据 |
