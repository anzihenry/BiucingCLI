---
title: "BiucingCLI 0.9.0"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

# BiucingCLI 0.9.0

[中文](notes.md) · Translation of the Chinese primary document.

`0.9.0` hardens the installed distribution and the generator core.

## Highlights

- All seven starter templates are bundled inside wheel and source-distribution artifacts instead of depending on the source repository layout.
- Apple, Android, and Microservice derived values are computed only after CLI and `--set` inputs have been normalized and resolved.
- Unknown templates, malformed bundled metadata, target conflicts, and generation I/O failures now produce concise, stable CLI errors.
- Project rendering uses a temporary sibling directory and only publishes the completed project after every file has been rendered.
- CI covers Python 3.11 through 3.14 and runs a clean-wheel installation gate outside the source tree.

## Compatibility

Existing commands, template names, dedicated create flags, `--set` precedence, and successful JSON payloads remain available. `apple_platform_name` is now a system-derived value rather than a user-settable template input.

Generation now requires the supplied `--output-dir` to exist and be a directory. This makes path failures explicit before staging begins.

## Verification

See [0.9.0 Release Prep](validation.en.md) for artifact checks, error contracts, and current evidence.
