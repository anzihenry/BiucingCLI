---
title: "CLI 输入与错误契约"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="cli-input-and-error-contract"></a>
# CLI 输入与错误契约

[English](cli-errors.en.md)

仅在 stdin 是终端且未指定 `--json`、`--non-interactive` 时使用交互提示。提示写入 stderr，使 stdout 保持用于成功结果。stdin 被重定向或关闭时，通过命令选项或 `--set` 提供必填值；不会把管道输入当作交互回答读取。

终端提示期间遇到 EOF 时，命令输出简明诊断并以退出码 2 结束。Ctrl+C 以 130 退出，不输出调用栈。若在暂存阶段中断，生成器删除临时目录；已经提交到目标目录的项目不会因取消而被删除。

<a id="machine-readable-failures"></a>
## 机器可读的失败

在 `list`、`info`、`validate`、`create` 上使用完整的 `--json` 选项。不支持长选项缩写。只要 `--json` 出现在 `--` 参数终止符之前，缺少参数、无效选择、未知选项等参数解析错误也使用相同格式。

```bash
biucing info unknown --json >result.json 2>error.json
```

命令以 2 退出，`result.json` 保持为空，并写入：

```json
{"schema_version": 1, "generator_version": "0.10.0", "ok": false, "error": {"code": "unknown_template", "message": "unknown template 'unknown'"}}
```

| 退出码 | 错误代码 | 含义 |
| --- | --- | --- |
| 2 | `usage_error` | 命令行参数无效 |
| 2 | `missing_input` | 缺少必填模板变量 |
| 2 | `input_ended` | 提示期间输入结束 |
| 2 | `invalid_input` | 变量值或 `--set` 语法无效 |
| 2 | `unknown_template` | 未找到模板 |
| 2 | `target_conflict` | 目标已存在 |
| 2 | `generation_failed` | 生成或输出路径失败 |
| 1 | `invalid_template` | 模板元数据无效 |
| 1 | `validation_failed` | 模板验证失败，`error.details` 列出失败项 |
| 1 | `io_error` | 其他文件系统 I/O 失败 |
| 130 | `cancelled` | 用户中断操作 |

为保持兼容，既有生成失败仍使用退出码 2，成功使用 0。所有 JSON 载荷包含 `schema_version`、`generator_version`；既有成功业务字段的位置不变，见 [JSON 契约](json-contract.md)。`--help` 和 `--version` 保持正常的可读成功输出。意外程序错误不会被转换成具有误导性的输入错误。

兼容说明：失败的 `validate --json` 现在向 stderr 输出错误封装，而不是向 stdout 输出 `ok: false` 验证报告。成功的 `validate --json` 仍返回原有 `ok/error_count/errors` 载荷。
