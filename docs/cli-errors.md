# CLI input and error contract

Interactive prompts are used only when stdin is a terminal and neither `--json`
nor `--non-interactive` is set. Prompts go to stderr, keeping stdout available
for successful command results. When stdin is redirected or closed, pass required
values through flags or `--set`; piped answers are not consumed as interactive input.

EOF during a terminal prompt ends the command with a concise diagnostic and exit
code 2. Ctrl+C exits with code 130 without a traceback. If interrupted during
staging, generation removes its temporary directory. A project already committed
to the target directory is not deleted by cancellation.

## Machine-readable failures

Use the full `--json` option on `list`, `info`, `validate`, or `create`.
Long option abbreviations are not supported. Argument parsing failures, including
missing arguments, invalid choices and unknown flags, use the same error format
when `--json` appears before the `--` argument terminator.

```bash
biucing info unknown --json >result.json 2>error.json
```

The command exits with code 2, leaves `result.json` empty, and writes:

```json
{"schema_version": 1, "generator_version": "0.9.1", "ok": false, "error": {"code": "unknown_template", "message": "unknown template 'unknown'"}}
```

| Exit | Error code | Meaning |
| --- | --- | --- |
| 2 | `usage_error` | Invalid command-line arguments |
| 2 | `missing_input` | Missing required template variables |
| 2 | `input_ended` | Input ended during prompting |
| 2 | `invalid_input` | Invalid variable values or `--set` syntax |
| 2 | `unknown_template` | Template not found |
| 2 | `target_conflict` | Target already exists |
| 2 | `generation_failed` | Generation or output-path failure |
| 1 | `invalid_template` | Invalid template metadata |
| 1 | `validation_failed` | Template validation failed; `error.details` lists failures |
| 1 | `io_error` | Other filesystem I/O failure |
| 130 | `cancelled` | User interrupted the operation |

Existing generation failures retain exit code 2 for compatibility. Success uses
exit code 0. All JSON payloads include `schema_version` and `generator_version`;
existing successful business fields remain in place. See [the JSON contract](json-contract.md).
`--help` and
`--version` retain their normal human-readable successful output. Unexpected
programming errors are not converted into misleading input errors.

Compatibility note: a failed `validate --json` now emits the error envelope to
stderr rather than an `ok: false` validation report to stdout. Successful
`validate --json` still returns its existing `ok/error_count/errors` payload.
