---
title: "0.10.0 release verification"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

# 0.10.0 release verification

[中文](validation.md) · Translation of the Chinese primary document.

Verification date: 2026-09-30 (Asia/Shanghai).

## Scope

This release includes changes since v0.9.1: CLI validation and resource variants,
frontend CSR/SSG/SSR, native binary components and backend P0–P5 reference delivery.
See [release notes](notes.en.md) for compatibility changes.

## Local release checks

- `uv lock` and `uv sync --locked`: passed; package/runtime/CLI/golden versions agree.
- `uv run --locked python scripts/run-tests --suite core`: 213 passed.
- `uv run --locked python scripts/run-tests --suite platform`: 12 passed, no skips.
- Ruff (`E4,E7,E9,F`) and `biucing validate`: passed.
- `uv build --no-sources --no-build-isolation`: built 0.10.0 wheel and sdist.
- `scripts/verify-distribution --dist-dir /tmp/biucing-010-dist --check-make`:
  exact package resources, executable flags, sdist rebuild, installed generation and
  configuration parsing passed for all seven templates.

Local logs: `/tmp/biucing-010-{core,platform,distribution}.log`.
Local tooling: macOS arm64, uv 0.12.19; hosted jobs use pinned uv 0.12.16.

## Release fixes

- Backend task help lists usable commands and their Make equivalents, including help.
- DNS reconnection tests move between IPv4 and IPv6 loopback, avoiding an unconfigured
  127.0.0.2 alias on macOS while still exercising real DNS address changes.
- The call-chain certificate fixture uses the invoking UID/GID so Linux bind mounts
  permit reading the local CA key without relaxing its permissions.
- Android CI initializes the SDK before calling sdkmanager and avoids the removed
  legacy `tools` package.
- Linux fixture mounts make public certificates readable by the non-root service;
  the CA private key stays owner-only. Recovery checks allow the default 30-second
  DNS resolution interval and record actual recovery time instead of assuming 5s.
- Docker call-chain follow-up: all 11 checks passed in
  `/tmp/biucing-010-calls-v2/evidence.json`; restart recovery was 28.936s and leaf
  rotation recovery was 1.039s. This is fixture evidence, not a production SLO.

Only the two intentionally changed backend files were refreshed in generation
snapshots; native and frontend output snapshots are unchanged by release preparation.

## Hosted candidate verification

The code candidate `d106d88` passed:

- [CI](https://github.com/anzihenry/BiucingCLI/actions/runs/36716267566):
  eight core jobs, macOS platform checks and six installed-artifact frontend jobs.
- [Backend generated projects](https://github.com/anzihenry/BiucingCLI/actions/runs/36716267094):
  six database/cache combinations and the Web-to-Micro call chain on Linux.

Local Kubernetes rendering/schema checks passed all 12 combinations:
`/tmp/biucing-010-kubernetes/evidence.json`, result `structure-verified`;
cluster and HA remain `not-run`. Shared C++ source synchronization and Twine metadata
checks also passed. Follow-up release documentation does not change template output.

The first TestPyPI run was cancelled before upload when supplemental validation
found portability issues. It is not counted as successful release evidence.

## Template evidence and limits

The release reuses implementation evidence for unchanged runtime/native sources:
[frontend](../../guides/frontend-acceptance.en.md),
[native session contracts](../../initiatives/feature/native-components/cross-platform-validation.en.md),
[Android](../../initiatives/feature/native-components/android-validation.en.md),
[HarmonyOS](../../initiatives/feature/native-components/harmonyos-validation.en.md),
[backend P4](../../initiatives/feature/backend-services/p4-validation.en.md),
[backend P5](../../initiatives/feature/backend-services/p5-validation.en.md).

Hosted CI and TestPyPI/PyPI run outcomes are recorded on the GitHub release and
Actions runs. A successful package upload must be followed by installation and
version/template validation from the selected index.

B27 real multi-zone HA acceptance remains on hold at the user's request. No cloud
infrastructure or fault injection is part of this release. Native real-device,
store signing and production platform acceptance retain the limits in those records.
