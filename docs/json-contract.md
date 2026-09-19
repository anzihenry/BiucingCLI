# JSON output contract

All JSON command results and error envelopes include these top-level fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | integer | JSON interface revision; currently `1` |
| `generator_version` | string | BiucingCLI release that produced the result |

This applies to `list`, `info`, `validate`, `create`, `create --plan`, and
`create --dry-run` when `--json` is selected, including argument parsing failures
and cancellation errors. Help/version text and generated configuration files are
not JSON command results.

Existing business fields keep their current locations: `templates` for list,
top-level template details for info, `ok/error_count/errors` for successful
validation, and `operation/template/resolved_variables/...` for create output.
Version identifiers are top-level only, not repeated on nested objects.
See [error handling](cli-errors.md) for stderr and exit-code behavior.

`schema_version` is independent of the package version. Compatible additions
may introduce fields or new templates/validator identifiers without increasing
the schema version. Removing or renaming fields, changing their types or meaning,
or changing the envelope requires a schema version bump. Consumers should ignore
unknown fields, check supported schema versions, and not guess the semantics of
an unknown validator. `generator_version` is for diagnostics and reproduction,
not for determining JSON compatibility.

## Variable constraints

Every variable in `list --json` and `info TEMPLATE --json` includes its existing
`name`, `required`, `default`, `default_from`, and `prompt` fields, plus:

| Field | Type | Meaning |
| --- | --- | --- |
| `validator` | string | Named validation rule, such as `text`, `slug`, `port`, or `java-package` |
| `choices` | array of strings | Allowed values; empty means no enumeration restriction |
| `minimum` | integer or null | Inclusive numeric lower bound; null means none specified/applicable |
| `maximum` | integer or null | Inclusive numeric upper bound; null means none specified/applicable |

Numeric constraints reflect effective validation: `port` defaults to 1–65535,
and `positive-integer` defaults to a minimum of 1 and no maximum. Explicit bounds
override these defaults, including an explicit minimum of zero. The exporter
and validator share the same bounds calculation.

For example, `info web-service --json` exposes:

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

Values/defaults remain strings; bounds are JSON numbers. `required` indicates
that a value must resolve (possibly through a default), not necessarily that
the caller must pass a flag. Choices and the named validator both apply.
Named rules include syntax and length checks; numeric bounds alone are not the
entire rule. This metadata is not a JSON Schema or a portable regex specification.
The CLI remains authoritative for input validation. Resolved values in create
results retain `name/value/source`; obtain declarations through list/info.
