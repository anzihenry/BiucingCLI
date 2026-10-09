---
title: "BiucingCLI 0.6.0 Worktree 冲突审计"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-060-worktree-collision-audit"></a>
# BiucingCLI 0.6.0 Worktree 冲突审计

[English](audit.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

记录阶段 B 实施前七模板 frontend/web-service/microservice/worker/apple/android/harmonyos 的状态；仅审计，不修改模板。

<a id="classification"></a>
## 分类

| 类别 | 含义 |
| --- | --- |
| 阻断 | 声称 0.6.0 worktree 优先前必须解决 |
| 重要 | 版本内应解决，平台受限时可记录 |
| 可选 | 不阻断发布主张的后续 |

<a id="cross-template-findings"></a>
## 跨模板发现

<a id="blocking"></a>
### 阻断

均无三个 worktree 命令/元数据；Docker 未一致传 Compose project，依赖默认/硬编码；固定宿主端口阻止并行。

<a id="important"></a>
### 重要

latest 镜像易互覆盖，原生身份固定会覆盖安装，清理仅通用而非明确 worktree 范围。

<a id="optional"></a>
### 可选

元数据先 planned 再 partial/ready；显式端口/诊断不足前暂缓自动选端口。

<a id="template-audit-matrix"></a>
## 模板审计矩阵

| 模板 | 优势 | 冲突 | 阻断缺口 | 后续 |
| --- | --- | --- | --- | --- |
| frontend | Docker、源码挂载、忽略依赖/输出/报告 | 固定 5173、三个命名卷、latest、运行 8080 | 命令/project/卷/端口诊断/镜像 | smoke URL 感知身份 |
| web-service | Docker Go、.cache、端口模板化 | app-dev、固定 Go/lint 卷、固定端口/latest、部署映射 | 命令/project/卷/镜像/端口 | 忽略 .cache |
| microservice | Docker/依赖、Go/lint 缓存、HTTP/gRPC 模板化 | 固定缓存卷、依赖/OTel 4317/4318 端口/latest、部署重复 | 命令/project/卷/镜像/依赖/全部端口 | 双存储变体验证 |
| worker | Docker，无宿主端口，忽略 cache/bin | 固定 dev/latest/缓存卷、定时容器 project | 命令/project/dev/runtime/缓存 | 两模式不变 |
| apple | 已忽略 build/cache/DerivedData/Tuist/IDE，lint/format 本地 | 无 derivedDataPath、固定 bundle、输出未诊断、无并行指导 | 命令/DerivedData/Debug 后缀 | 真工程验证 SwiftPM/Tuist |
| android | 忽略 gradle/build/local.properties/IDE，本地签名，已有 .debug | 固定后缀、缓存无诊断、本地配置不显示 | 命令/可覆身份/诊断 | 决定本地 Gradle 默认或可选 |
| harmonyos | 忽略 hvigor/ohpm/build/modules/signing/包/log | 固定 bundle、缓存不显示、签名仅发布检查、身份无说明 | 命令/输出/签名诊断/后缀支持或暂缓 | 验证前不实现 bundle 改写 |

<a id="detailed-findings"></a>
## 详细发现

<a id="frontend"></a>
### frontend

检查 templates/frontend/template 的 Makefile、compose.dev.yaml、ignore 文件。开发字面 5173:5173 不使用已有 DEV_PORT；运行默认 8080:80；卷 frontend-node-modules/frontend-pnpm-store/frontend-playwright-cache 固定；镜像 PACKAGE_NAME:latest；无归属诊断。阶段 C 要求端口可覆盖、卷 project 化、镜像身份化，info 显示端口/project/镜像/卷。

<a id="web-service"></a>
### web-service

检查同模板 Makefile、compose.dev.yaml、compose.yaml、ignore。开发/运行均 HTTP_PORT:HTTP_PORT，docker-run 同默认；卷 web-service-go-build/web-service-golangci-lint 固定，SERVICE_NAME:latest；Make 设置 .cache Go/lint 而未忽略。阶段 C 全 Compose 传 project，dev/run/deploy 端口一致可覆，隔离卷/镜像，忽略缓存。

<a id="microservice"></a>
### microservice

检查 Makefile、compose.dev.yaml、deploy/compose.yaml、ignore。HTTP/gRPC/依赖/OTel 4317/4318 固定，部署重复，microservice-go-build/microservice-golangci-lint 卷固定，latest，依赖靠默认 project。阶段 C 公开五端口，传 project，隔离缓存/镜像，验 postgres/redis。

<a id="worker"></a>
### worker

检查 Makefile、compose.dev.yaml、ignore。WORKER_NAME-dev:latest、WORKER_NAME:latest、worker-go-build-cache 固定；定时进程默认 project 会重叠。阶段 C 身份化 project/镜像/缓存，诊断模式/tick/关闭 timeout，保持 scheduled/oneshot。

<a id="apple"></a>
### apple

检查 Makefile、gitignore、App/Project.swift。已忽略 .build/.cache/DerivedData/Tuist 缓存依赖/project/workspace/xcuserdata。xcodebuild 无路径，BUNDLE_IDENTIFIER 与 .tests 固定，安装互覆，无诊断。阶段 D 诊断、独立 DerivedData、支持或说明 Debug 后缀，输出保持本地。

<a id="android"></a>
### android

检查 Makefile、gitignore、app/build.gradle.kts。已忽略 .gradle/build/模块输出/local.properties/IDE，签名从本地/env；后缀 .debug 固定，缓存/配置不可见，安装无身份。阶段 D 可覆后缀，缓存/配置诊断，说明本地 Gradle home 默认或可选。

<a id="harmonyos"></a>
### harmonyos

检查 Makefile、gitignore、AppScope/app.json5、build-profile.json5、release-build。忽略 .hvigor/.ohpm/build/entry/build/node_modules/oh_modules/local.properties/包/log；缺配置快速失败，签名不提交。bundle 固定，输出无诊断，签名仅发布时显示，身份无指导。阶段 D 显示缓存/modules/输出/签名存在；仅 DevEco/hvigor 验证后支持后缀，否则明确暂缓。

<a id="metadata-recommendation-for-phase-b"></a>
## 阶段 B 元数据建议

全部先声明 planned：

```json
{
  "worktree": {
    "support_level": "planned",
    "isolation_dimensions": [
      "diagnostics",
      "cleanup"
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

| 模板 | 初始维度 |
| --- | --- |
| frontend | runtime-names、ports、caches、generated-output、cleanup、diagnostics |
| web-service | runtime-names、ports、caches、generated-output、cleanup、diagnostics |
| microservice | runtime-names、ports、dependency-stores、caches、generated-output、cleanup、diagnostics |
| worker | runtime-names、caches、generated-output、cleanup、diagnostics |
| apple | caches、generated-output、local-config、installed-app-identity、cleanup、diagnostics |
| android | caches、generated-output、local-config、installed-app-identity、cleanup、diagnostics |
| harmonyos | caches、generated-output、local-config、installed-app-identity、cleanup、diagnostics |

<a id="phase-a-decision-summary"></a>
## 阶段 A 决策摘要

主题可行且契合目录。顺序：元数据/校验可见，Docker 最直接冲突，原生缓存/身份，发布证据防回退。阶段 A 结束时尚无 ready，符合预期。
