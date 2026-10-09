---
title: "添加内置模板"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="adding-a-built-in-template"></a>
# 添加内置模板

[English](template-authoring.en.md)

本文描述已交付的生成行为。可选资源变体扩展（已交付前端 CSR/SSG/SSR 使用）见[前端渲染计划](../initiatives/feature/frontend-rendering/plan.md)。

在 `src/biucingcli/template_data/<name>/` 下放置 `template.json` 和 `template/` 资源树，元数据名称必须等于目录名。描述性元数据（技术栈、成熟度、验证、worktree、命令等）仍必需；以下仅展示扩展字段。

```json
{
  "name": "python-api",
  "category": "backend",
  "contracts": [],
  "required_entries": ["pyproject.toml"],
  "rule": null,
  "derived_outputs": [],
  "render_outputs": [],
  "variables": [
    {"name": "project_name", "required": true, "validator": "project-name"},
    {"name": "greeting", "required": true, "validator": "text", "contexts": ["JSON"]}
  ]
}
```

双引号 JSON 字符串中使用 `{{GREETING_JSON}}`，Markdown 中使用 `{{GREETING}}`。通过 `--set greeting=...` 提供新变量；仅解析输入/默认值的模板无需新增 CLI 选项或注册规则。

<a id="file-contracts"></a>
## 文件契约

所有模板必需 `README.md`、`Makefile`、`.gitignore`、`scripts/doctor`，公共 Make 命令契约也仍为必需。可声明：

- `docker-compose`：`.dockerignore`、`compose.dev.yaml`；
- `go-backend`：`go.mod`、`go.sum`、`cmd`、`internal`、`configs`、`scripts`；
- `native-tools`：`.mise.toml`、`scripts`。

`required_entries` 增加模板特定文件/目录。路径必须是规范化相对 POSIX 路径，不允许路径穿越。category 和 tags 是展示元数据，不隐含 Go/原生契约。内置模板有项目规定的最低契约，删除声明是错误，不会移除底层文件检查。必需目录项的 golden 固定迁移前全部检查。

<a id="resource-and-generation-contract"></a>
## 资源与生成契约

普通模板选择公共 `template/` 树；变体再选择一个声明层。两者共用资源清单和暂存发布器。资源必须是规范化相对路径下的普通文件或目录。普通模板也拒绝符号链接（含悬空链接和资源根链接）、特殊文件、大小写/Unicode 规范化路径冲突。不要通过符号链接向模板引入外部源文件。

create/preview 先验证元数据，再解析输入，在任何写入前检查所选有效资源的必需目录项、Make 命令和占位符。完整 `validate` 检查每个声明变体。生成保留二进制和空目录，文本只渲染一次，恢复权限位，并根据项目相对路径给予文本脚本/gradlew 所有者执行权限。只读文本仅在暂存中临时可写，源权限不变。

计划包含源/元数据指纹。准备到发布间源有变化时，重新构建计划，不重试旧计划。它检查一致性，不是文件系统快照或并发锁。兼容 `render_template` 入口以已解析值使用相同检查和发布器，不应用默认值、提示或派生。刻意兼容变化见[统一生成记录](../initiatives/refactor/unified-generation/validation.md)。

<a id="variables-contexts-and-bindings"></a>
## 变量、上下文与绑定

变量/输出名使用符合 `[a-z][a-z0-9_]*` 的小写 snake 风格标识符，token 用大写。上下文必须显式声明，可为 JSON、XML、SWIFT、KOTLIN、JS_SINGLE、ANDROID、DOCKER；复用既有转义实现，除 Android 特有资源引号外不添加外围引号。按插入位置选择上下文。

text、display-name、URL 变量属于自由文本。choice 也属于自由文本，除非每个值只含字母、数字、点、下划线和连字符。Markdown 源文件以外拒绝原始自由文本 token。名字不豁免安全要求，新增 `greeting` 与已有 `display_name` 同样受保护。声明上下文不能证明作者使用了正确语言；仍需生成配置解析和目标语言测试。可读的下一步保持原有格式，生成器不会通过 shell 执行它们。

绑定不可冲突：JSON 上下文的 `title` 与名为 `title_json` 的变量冲突。模板不能使用其他模板的输入/输出。已声明但无值的可选变量仍渲染为空字符串。未知 token 在生成前失败；用户值中看似 token 的字面文本不重新处理。

<a id="complex-built-in-rules"></a>
## 复杂内置规则

只有需要计算的模板才需要纯 Python 规则模块。在 `template_rules/registry.py` 中显式注册，包含输出集合和允许覆盖的输入，并在元数据声明 `rule`、`derived_outputs`、`render_outputs`。不允许通过任意模块路径导入规则。输出要求已注册规则；元数据和实际结果键必须符合契约。仅渲染输出是内置代码产生的可信代码片段，不是将任意用户输入声明安全的绕过手段。

<a id="verification"></a>
## 验证

运行锁定核心测试和 `biucing validate`，再运行安装包检查。添加源/变体/配置测试，并在 `scripts/verify-distribution` 注册新发布冒烟场景（其预期模板集合刻意显式维护）。`tests/test_template_declarations.py` 中 fixture 展示完整加载、验证、预览和生成，它不是第八个交付模板。新模板需要语言/SDK 证明时增加平台测试。

内部文件契约/规则声明不通过 list/info JSON 暴露。变体模板只暴露选择器/默认值/可选值摘要，见 [JSON 契约](../engineering/json-contract.md#resource-variants)。不引入第三方插件执行或外部模板目录 CLI 选项。

<a id="contribution-checklist"></a>
## 贡献检查清单

1. 添加元数据和资源，只声明必需的契约、变量、转义上下文和目录项；`project_name` 保持既有项目名验证器约束。
2. 纯声明模板使用 `--set` 和通用生成流程，不在 CLI 或生成器新增模板名分支。
3. 计算值使用纯规则模块，显式注册可调用对象、输出集合和可覆盖输入；增加直接规则测试，区分清单可见派生与仅渲染片段。
4. 新共享契约加入 `template_rules/contracts.py` 并测试。内置最低策略和必需目录项 golden 只随经过评审的产品变化更新，不用于掩盖缺文件错误。
5. 增加核心输出/配置测试和代表性生成基线。原生编译器/shell 测试必须标记为 platform 或 Android，不能悄悄增加 core 工具要求，见[测试组织](testing.md)。
6. 扩展安装后 wheel 冒烟和预期模板清单，验证 `uv run --locked biucing validate`、锁定核心测试和安装包检查；运行相关平台测试，发布前要求 Linux/macOS CI。

直接 Python 集成使用 `catalog`、`models`、`variables`、`generation`、`presentation`。终端决策属于 CLI 适配器；渲染器和规则不能提示、打印诊断或终止进程。保留旧导入是为兼容，并非推荐扩展接口。
