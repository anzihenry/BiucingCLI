---
title: "Template System"
status: current
owner: project-maintainers
updated: 2026-10-09
---

# Template System

[中文](template-system.md) · Translation of the Chinese primary document.

## Goal

BiucingCLI uses a built-in metadata-driven template system with package-owned resources, declared variables and predictable generation.

The current resource and publication contracts are documented in [template authoring](../guides/template-authoring.en.md) and [kernel modules](kernel-modules.en.md).

## Directory Shape

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

Templates live inside the Python package so wheel and source-distribution installs expose the same resources as a source checkout. The generator must not derive template paths from a Git repository root.

## Template Metadata

### Context-aware text insertion

Free-form display names, organization names, and telemetry URLs require explicit
context suffixes in source/config files. Escaped placeholders provide **contents**;
the surrounding string quotes remain in the template:

| Context | Example | Notes |
| --- | --- | --- |
| JSON/JSON5, double-quoted JS/TS/Go, quoted YAML | `"{{DISPLAY_NAME_JSON}}"` | JSON-compatible string escaping |
| JSX expression | `{"{{DISPLAY_NAME_JSON}}"}` | Keep text out of JSX markup |
| HTML/XML | `{{DISPLAY_NAME_XML}}` | Escape markup and attribute delimiters |
| Swift | `"{{DISPLAY_NAME_SWIFT}}"` | Escape strings and prevent interpolation |
| Kotlin | `"{{DISPLAY_NAME_KOTLIN}}"` | Also escape `$` interpolation |
| Single-quoted JS/ArkTS | `'{{DISPLAY_NAME_JS_SINGLE}}'` | Escape apostrophes and backslashes |
| Android string resource | `{{DISPLAY_NAME_ANDROID}}` | Includes resource quoting and XML escaping; use `formatted="false"` |
| Dockerfile ENV | `"{{OTEL_EXPORTER_ENDPOINT_DOCKER}}"` | Prevent `$` environment expansion |

Android manifests reference `@string/app_name`. Frontend title assertions compare
literal strings instead of constructing regular expressions from user text.
Trusted generated code snippets retain their raw placeholders; escape any user
strings when constructing those snippets (for example, Swift WindowGroup titles).

Substitution is single-pass: `{{PROJECT_NAME}}` inside an input value remains
literal text. `validate` rejects raw free-text placeholders outside Markdown.
README prose and human-readable output retain raw user text. New insertion
contexts must define their own escaping rule instead of reusing an unrelated one.

Regression tests parse generated XML/JSON and evaluate JavaScript/Swift literals
when those runtimes are available. To also compile Android resources, run
`AAPT2=/path/to/sdk/build-tools/VERSION/aapt2 uv run --locked python -m unittest discover -s tests -p test_escaping.py`.

Each template should contain a `template.json` file with:

- template name;
- description;
- category;
- stack;
- tags;
- platforms;
- maturity;
- validation;
- worktree support;
- operating assumptions;
- workflow labels;
- variable definitions;
- next steps.

Suggested shape:

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

## Metadata Contract

The current product contract treats template metadata as a first-class interface, not a loose annotation layer.

At minimum, every template should define:

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

### Verification Tiers

`verification_tier` is used to normalize what the repo claims has been proven for a starter.

Current supported values:

- `generated-project`
- `real-build`

### Worktree Support

`worktree` metadata describes whether a generated starter participates in the `0.6.0` worktree-first contract.

Current supported `support_level` values:

- `planned`: the starter has declared worktree support as part of the `0.6.0` rollout, but implementation has not landed yet
- `partial`: some isolation behavior is implemented, but known gaps remain
- `worktree-ready`: the starter meets the worktree isolation contract

Current supported `isolation_dimensions` values:

- `runtime-names`
- `ports`
- `dependency-stores`
- `caches`
- `generated-output`
- `local-config`
- `installed-app-identity`
- `cleanup`
- `diagnostics`

`diagnostics` and `cleanup` should list generated-project commands rather than prose.
The default `0.6.0` command vocabulary is:

- `make worktree-info`
- `make worktree-doctor`
- `make clean-worktree`

See [worktree-isolation-contract.md](worktree-isolation-contract.en.md) for the full contract.

For `0.6.0`, every shipped template should declare `worktree-ready`.
`planned` and `partial` remain valid so future templates can enter the portfolio before their full isolation implementation lands.

### Workflow Labels

`workflow_labels` provide a small shared vocabulary across different starter families.

Current supported labels:

- `bootstrap`
- `doctor`
- `dev`
- `test`
- `verify`
- `build`
- `runtime`
- `generate`
- `format`
- `release`
- `ui-test`
- `open`
- `lint`

### Common Command Contract

Every generated project exposes the same portable entrypoints through Make:

- `make bootstrap`: prepare the local development environment;
- `make doctor`: check required tools and project configuration;
- `make lint`: run static analysis;
- `make test`: run automated tests;
- `make verify`: run the template's complete local verification gate, including a build;
- `make build`: create the normal development build output;
- `make clean`: remove generated runtime or build state;
- `make help`: print the common command summary.

The `commands` object must map each name to exactly `make <name>`. Each target must exist in the template Makefile and be declared `.PHONY`. Templates may expose additional platform-specific commands without changing this common contract.

### Variable Validators

Each variable declares a `validator`. Validation runs after defaults and derived values are resolved but before the target directory is created. User-provided values are trimmed first, so CLI flags, prompts, and `--set KEY=VALUE` follow the same rules.

Supported validator families cover:

- human and filesystem names: `text`, `display-name`, `project-name`, `slug`;
- language/package identities: `identifier`, `npm-package`, `go-module`, `java-package`, `protobuf-package`, `bundle-identifier`, `team-id`;
- versions and numbers: `semantic-version`, `apple-version`, `harmony-sdk-version`, `positive-integer`, `port`;
- constrained and network values: `choice`, `url`.

`choice` variables must define `choices`. Numeric variables may define inclusive `minimum` and `maximum` bounds. Defaults are checked against the same rules during `biucing validate`.

## Variable Replacement

The first version should support simple placeholder replacement only.

Suggested placeholders:

- `{{PROJECT_NAME}}`
- `{{DISPLAY_NAME}}`
- `{{PACKAGE_NAME}}`
- `{{MODULE_NAME}}`
- `{{SERVICE_NAME}}`
- `{{HTTP_PORT}}`
- `{{APPLICATION_ID}}`
- `{{ANDROID_NAMESPACE}}`
- `{{COMPILE_SDK}}`
- `{{MIN_SDK}}`
- `{{TARGET_SDK}}`
- `{{VERSION_CODE}}`
- `{{VERSION_NAME}}`
- `{{JAVA_VERSION}}`
- `{{KOTLIN_MODULE_NAME}}`
- `{{BUNDLE_NAME}}`
- `{{HARMONY_MODULE_NAME}}`
- `{{ABILITY_NAME}}`
- `{{COMPATIBLE_SDK_VERSION}}`
- `{{TARGET_SDK_VERSION}}`
- `{{MIN_API_VERSION}}`
- `{{HARMONY_VERSION_CODE}}`
- `{{HARMONY_VERSION_NAME}}`
- `{{BUNDLE_IDENTIFIER}}`
- `{{MINIMUM_OS_VERSION}}`
- `{{DEVELOPMENT_TEAM}}`
- `{{ORGANIZATION_NAME}}`
- `{{SWIFT_MODULE_NAME}}`
- `{{APPLE_PLATFORM}}`
- `{{APPLE_PLATFORM_NAME}}`
- `{{TUIST_DESTINATIONS}}`
- `{{TUIST_DEPLOYMENT_TARGETS}}`
- `{{XCODEBUILD_DESTINATION}}`

This keeps template files readable and avoids introducing a heavy rendering layer too early.

## Validation Policy

Repo-level validation should keep using the same source of truth as rendering.

It currently checks:

- metadata completeness;
- worktree metadata shape and supported values;
- the eight-command metadata contract and matching `.PHONY` Make targets;
- supported variable validators, choice sets, numeric bounds, and valid defaults;
- variable-to-placeholder mapping support;
- placeholder legality inside template files and `next_steps`;
- template folder naming consistency;
- family-level required starter entries.

Family-level required entries are intentionally not global one-size-fits-all rules.
They vary by starter type, for example:

- web/container starters should ship `README.md`, `Makefile`, `.gitignore`, `.dockerignore`, and `compose.dev.yaml`;
- Go backend starters should ship `go.mod`, `go.sum`, `cmd/`, `internal/`, `configs/`, and `scripts/`;
- native starters should ship `.mise.toml`, `scripts/`, and their platform build entrypoints.

## Template catalog

The current catalog and platform capabilities are described in [usage](../guides/using.en.md) and each template's `template.json`. Query `biucing info TEMPLATE` for resolved metadata. [Initial template shapes](../initiatives/feature/scaffold-baseline/template-shapes.en.md) are historical examples.

## CLI behavior

Creation validates metadata, resolves and validates inputs, selects effective resources, and prepares a typed generation plan. Preview returns the plan without writes. Execution verifies source fingerprints, renders into staging, restores permissions and publishes the target. Interactive prompting follows terminal policy; `--json` disables prompts. See [kernel modules](kernel-modules.en.md), [JSON](json-contract.en.md) and [errors](cli-errors.en.md) for the current boundaries.

## Product boundaries

Remote registries and dynamic plugins remain outside the product scope. Built-in resource variants use explicit metadata and declared layers; generation does not fetch template resources from registries. See [product scope](../product/overview.en.md).
