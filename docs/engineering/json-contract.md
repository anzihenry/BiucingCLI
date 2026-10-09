---
title: "JSON 输出契约"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="json-output-contract"></a>
# JSON 输出契约

[English](json-contract.en.md)

所有 JSON 命令结果和错误封装都包含以下顶层字段：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `schema_version` | integer | JSON 接口修订版本，目前为 `1` |
| `generator_version` | string | 产生结果的 BiucingCLI 版本 |

适用于选择 `--json` 的 `list`、`info`、`validate`、`create`、`create --plan`、`create --dry-run`，包括参数解析和取消错误。帮助/版本文本以及生成的配置文件不是 JSON 命令结果。

既有业务字段位置不变：list 使用 `templates`，info 使用顶层模板详情，成功验证使用 `ok/error_count/errors`，create 使用 `operation/template/resolved_variables/...`。版本标识只在顶层，不在嵌套对象重复。[错误处理](cli-errors.md)规定 stderr 和退出码行为。

`schema_version` 独立于包版本。兼容性新增可以加入字段、新模板或验证器标识而不提升 schema 版本。移除或重命名字段、改变类型或语义、修改封装结构则必须提升版本。消费者应忽略未知字段，检查支持的 schema 版本，不猜测未知验证器语义。`generator_version` 用于诊断和复现，不用于判断 JSON 兼容性。

<a id="variable-constraints"></a>
## 变量约束

`list --json` 和 `info TEMPLATE --json` 中每个变量保留 `name`、`required`、`default`、`default_from`、`prompt`，并包含：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `validator` | string | 命名验证规则，如 `text`、`slug`、`port`、`java-package` |
| `choices` | 字符串数组 | 允许的值；空数组表示没有枚举限制 |
| `minimum` | integer 或 null | 包含边界的数值下限；null 表示未指定或不适用 |
| `maximum` | integer 或 null | 包含边界的数值上限；null 表示未指定或不适用 |

数值约束反映实际验证：`port` 默认 1–65535；`positive-integer` 默认下限 1、无上限。显式边界覆盖默认值，包括显式设为零的下限。导出器和验证器共用边界计算。

例如，`info web-service --json` 暴露：

```json
{
  "name": "http_port",
  "required": false,
  "default": "8080",
  "default_from": null,
  "prompt": null,
  "validator": "port",
  "choices": [],
  "minimum": 1,
  "maximum": 65535
}
```

值和默认值仍是字符串，边界为 JSON 数字。`required` 表示值必须能解析出来（可以通过默认值），并不一定要求调用者传选项。枚举与命名验证规则同时生效。命名规则还包含语法和长度检查，数值边界并非全部规则。这些元数据不是 JSON Schema 或可移植正则规范；CLI 仍是输入验证的权威实现。create 的解析结果保留 `name/value/source`，声明通过 list/info 查询。

<a id="resource-variants"></a>
## 资源变体

声明资源变体的模板，其 list/info 详情额外包含 `variants` 对象：

```json
{"selector": "rendering", "default": "csr", "choices": ["csr", "ssg", "ssr"]}
```

这些模板的 create、plan 和 dry-run 结果包含顶层 `selected_variant` 对象，例如：

```json
{"selector": "rendering", "value": "ssg"}
```

默认值来自选择变量声明；所选值也带正常来源出现在 `resolved_variables`。数量、顶层目录项、下一步操作都描述公共资源加所选资源的有效集合。源路径、覆盖策略、一致性指纹属于内部信息，不输出。新增字段仍使用 schema 版本 1，在旧模板上不出现。验证保持原有成功/错误封装；变体资源诊断在错误字符串中包含 `template[option]` 上下文。

这些示例最初在资源迁移前通过 fixture 模板验证。当前已发布前端通过该选择器支持 CSR、SSG 和 SSR，见[前端验收指南](../guides/frontend-acceptance.md)。
