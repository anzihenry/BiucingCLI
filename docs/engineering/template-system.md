---
title: "模板系统"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="template-system"></a>
# 模板系统

[English](template-system.en.md)

<a id="goal"></a>
## 目标

BiucingCLI 使用内置、由元数据驱动的模板系统，以包内资源、声明变量和可预测的生成过程为基础。当前资源与发布契约见[模板编写](../guides/template-authoring.md)和[内核模块](kernel-modules.md)。

<a id="directory-shape"></a>
## 目录结构

```text
src/biucingcli/template_data/
  frontend/
    template.json
    template/
      ...
  web-service/
    template.json
    template/
      ...
```

模板位于 Python 包内部，使 wheel、源码分发安装与源码检出提供相同资源。生成器不得从 Git 仓库根目录推导模板路径。

<a id="template-metadata"></a>
## 模板元数据

<a id="context-aware-text-insertion"></a>
### 按插入上下文转义文本

源文件和配置中的自由输入（显示名称、组织名称、遥测 URL）必须使用明确的上下文后缀。转义占位符提供字符串**内容**，外围引号保留在模板中：

| 上下文 | 示例 | 说明 |
| --- | --- | --- |
| JSON/JSON5、双引号 JS/TS/Go、带引号 YAML | `"{{DISPLAY_NAME_JSON}}"` | JSON 兼容的字符串转义 |
| JSX 表达式 | `{"{{DISPLAY_NAME_JSON}}"}` | 避免将文本直接插入 JSX 标记 |
| HTML/XML | `{{DISPLAY_NAME_XML}}` | 转义标记和属性分隔符 |
| Swift | `"{{DISPLAY_NAME_SWIFT}}"` | 转义字符串并阻止插值 |
| Kotlin | `"{{DISPLAY_NAME_KOTLIN}}"` | 同时转义 `$` 插值 |
| 单引号 JS/ArkTS | `'{{DISPLAY_NAME_JS_SINGLE}}'` | 转义单引号和反斜杠 |
| Android 字符串资源 | `{{DISPLAY_NAME_ANDROID}}` | 包含资源引号和 XML 转义；使用 `formatted="false"` |
| Dockerfile ENV | `"{{OTEL_EXPORTER_ENDPOINT_DOCKER}}"` | 阻止 `$` 环境变量展开 |

Android 清单引用 `@string/app_name`。前端标题断言比较字面字符串，不用用户文本构造正则。可信生成代码片段保留原始占位符，但构造片段时须转义用户字符串，例如 Swift WindowGroup 标题。

替换只执行一遍：输入值中的 `{{PROJECT_NAME}}` 保持字面文本。`validate` 拒绝 Markdown 以外未经转义的自由文本占位符。README 正文和面向人的输出保留原始输入。新增上下文须定义自己的转义规则，不能借用不相关的规则。

回归测试解析生成的 XML/JSON，并在运行时可用时求值 JavaScript/Swift 字面量。若还需编译 Android 资源，运行 `AAPT2=/path/to/sdk/build-tools/VERSION/aapt2 uv run --locked python -m unittest discover -s tests -p test_escaping.py`。

各模板的 `template.json` 应包含模板名称、描述、类别、技术栈、标签、平台、成熟度、验证、worktree 支持、运行假设、工作流标签、变量定义和后续步骤。建议结构：

```json
{
  "name": "web-service",
  "description": "Go + Gin web service starter",
  "category": "backend",
  "stack": ["Go", "Gin"],
  "tags": ["api", "docker", "go", "service"],
  "platforms": ["linux", "container"],
  "maturity": {
    "level": "validated",
    "summary": "Dockerized web service starter with live-reload, lint, test, and runtime image workflows."
  },
  "validation": {
    "status": "real-build-verified",
    "verification_tier": "real-build",
    "evidence": [
      "python unittest template rendering coverage",
      "real docker runtime image builds"
    ]
  },
  "worktree": {
    "support_level": "worktree-ready",
    "isolation_dimensions": [
      "runtime-names",
      "ports",
      "caches",
      "generated-output",
      "cleanup",
      "diagnostics"
    ],
    "diagnostics": [
      "make worktree-info",
      "make worktree-doctor"
    ],
    "cleanup": [
      "make clean-worktree"
    ]
  },
  "operating_assumptions": [
    "The starter is optimized for Go service development with Docker-based dev and runtime flows."
  ],
  "workflow_labels": ["bootstrap", "dev", "verify", "build", "runtime"],
  "commands": {
    "bootstrap": "make bootstrap",
    "doctor": "make doctor",
    "lint": "make lint",
    "test": "make test",
    "verify": "make verify",
    "build": "make build",
    "clean": "make clean",
    "help": "make help"
  },
  "variables": [
    { "name": "project_name", "required": true, "validator": "project-name" },
    { "name": "module_name", "required": true, "validator": "go-module" },
    { "name": "service_name", "required": false, "default_from": "project_name", "validator": "slug" },
    { "name": "http_port", "required": false, "default": "8080", "validator": "port" }
  ],
  "next_steps": [
    "go mod tidy",
    "go run ./cmd/server"
  ]
}
```

<a id="metadata-contract"></a>
## 元数据契约

模板元数据是产品的正式接口，而非松散注释。最低字段要求：

- `name`, `description`, `category`
- `stack`, `tags`, `platforms`
- `maturity`
- `validation.status`, `validation.verification_tier`, `validation.evidence`
- `worktree.support_level`, `worktree.isolation_dimensions`, `worktree.diagnostics`, `worktree.cleanup`
- `operating_assumptions`
- `workflow_labels`
- `commands`
- `variables`
- `next_steps`

<a id="verification-tiers"></a>
### 验证层级

`verification_tier` 统一仓库对 starter 已验证能力的表述。当前支持 `generated-project` 和 `real-build`。

<a id="worktree-support"></a>
### Worktree 支持

`worktree` 元数据说明生成工程是否参与 `0.6.0` 的 worktree 优先契约。`support_level` 支持：

- `planned`：已纳入 `0.6.0` 推进范围，尚未实现。
- `partial`：部分隔离已实现，仍有已知缺口。
- `worktree-ready`：满足隔离契约。

`isolation_dimensions` 支持 `runtime-names`、`ports`、`dependency-stores`、`caches`、`generated-output`、`local-config`、`installed-app-identity`、`cleanup`、`diagnostics`。

`diagnostics` 和 `cleanup` 应列生成工程命令，而不是正文说明。`0.6.0` 默认命令为 `make worktree-info`、`make worktree-doctor`、`make clean-worktree`。完整契约见 [worktree 隔离契约](worktree-isolation-contract.md)。`0.6.0` 发布模板均须声明 `worktree-ready`；保留 `planned`、`partial`，使未来模板可在隔离完成前进入目录。

<a id="workflow-labels"></a>
### 工作流标签

`workflow_labels` 为不同 starter 提供小型共享词汇。当前支持 `bootstrap`、`doctor`、`dev`、`test`、`verify`、`build`、`runtime`、`generate`、`format`、`release`、`ui-test`、`open`、`lint`。

<a id="common-command-contract"></a>
### 通用命令契约

所有生成工程通过 Make 提供相同的可移植入口：

- `make bootstrap`：准备本地开发环境。
- `make doctor`：检查所需工具和配置。
- `make lint`：静态分析。
- `make test`：自动化测试。
- `make verify`：完整本地验证，包括构建。
- `make build`：常规开发构建产物。
- `make clean`：清理生成的运行或构建状态。
- `make help`：打印通用命令摘要。

`commands` 必须将各名称精确映射为 `make <name>`。目标必须存在于模板 Makefile 并声明 `.PHONY`。模板可增加平台命令，通用契约保持一致。

<a id="variable-validators"></a>
### 变量校验器

各变量声明 `validator`。默认值和派生值解析后、创建目标目录前执行校验；用户输入先去除首尾空白，使 CLI 参数、交互提示和 `--set KEY=VALUE` 遵循同一规则。

支持的校验器族：

- 人类文本和文件名：`text`、`display-name`、`project-name`、`slug`。
- 语言/包标识：`identifier`、`npm-package`、`go-module`、`java-package`、`protobuf-package`、`bundle-identifier`、`team-id`。
- 版本和数值：`semantic-version`、`apple-version`、`harmony-sdk-version`、`positive-integer`、`port`。
- 受限值和网络地址：`choice`、`url`。

`choice` 必须定义 `choices`。数值可声明包含端点的 `minimum`、`maximum`。`biucing validate` 用相同规则校验默认值。

<a id="variable-replacement"></a>
## 变量替换

初版仅支持简单占位符替换。建议占位符：

`{{PROJECT_NAME}}`、`{{DISPLAY_NAME}}`、`{{PACKAGE_NAME}}`、`{{MODULE_NAME}}`、`{{SERVICE_NAME}}`、`{{HTTP_PORT}}`、`{{APPLICATION_ID}}`、`{{ANDROID_NAMESPACE}}`、`{{COMPILE_SDK}}`、`{{MIN_SDK}}`、`{{TARGET_SDK}}`、`{{VERSION_CODE}}`、`{{VERSION_NAME}}`、`{{JAVA_VERSION}}`、`{{KOTLIN_MODULE_NAME}}`、`{{BUNDLE_NAME}}`、`{{HARMONY_MODULE_NAME}}`、`{{ABILITY_NAME}}`、`{{COMPATIBLE_SDK_VERSION}}`、`{{TARGET_SDK_VERSION}}`、`{{MIN_API_VERSION}}`、`{{HARMONY_VERSION_CODE}}`、`{{HARMONY_VERSION_NAME}}`、`{{BUNDLE_IDENTIFIER}}`、`{{MINIMUM_OS_VERSION}}`、`{{DEVELOPMENT_TEAM}}`、`{{ORGANIZATION_NAME}}`、`{{SWIFT_MODULE_NAME}}`、`{{APPLE_PLATFORM}}`、`{{APPLE_PLATFORM_NAME}}`、`{{TUIST_DESTINATIONS}}`、`{{TUIST_DEPLOYMENT_TARGETS}}`、`{{XCODEBUILD_DESTINATION}}`。

这样保持模板可读，避免过早引入复杂渲染层。

<a id="validation-policy"></a>
## 校验策略

仓库校验与渲染使用相同事实来源。当前检查元数据完整性、worktree 结构和取值、八个通用命令及 `.PHONY` 目标、变量校验器/选项/数值边界/默认值、变量到占位符映射、模板和 `next_steps` 占位符合法性、目录命名，以及各模板族要求的入口。

模板族入口要求按 starter 类型区分：

- Web/容器：`README.md`、`Makefile`、`.gitignore`、`.dockerignore`、`compose.dev.yaml`。
- Go 后端：`go.mod`、`go.sum`、`cmd/`、`internal/`、`configs/`、`scripts/`。
- 原生：`.mise.toml`、`scripts/` 和平台构建入口。

<a id="template-catalog"></a>
## 模板目录

当前目录和平台能力见[使用指南](../guides/using.md)及各 `template.json`。`biucing info TEMPLATE` 查询解析后的元数据。[初始模板结构](../initiatives/feature/scaffold-baseline/template-shapes.md)保留历史示例。

<a id="cli-behavior"></a>
## CLI 行为

创建过程校验元数据、解析并校验输入、选择有效资源并准备类型化生成计划。预览只返回计划；执行检查源指纹、在暂存目录渲染、恢复权限并发布目标。交互提示遵循终端策略，`--json` 禁用提示。当前边界见[内核模块](kernel-modules.md)、[JSON](json-contract.md)和[错误](cli-errors.md)。

<a id="product-boundaries"></a>
## 产品边界

远程注册中心和动态插件不在产品范围。内置资源变体使用明确元数据和声明层；生成过程不从注册中心下载资源。见[产品范围](../product/overview.md)。
