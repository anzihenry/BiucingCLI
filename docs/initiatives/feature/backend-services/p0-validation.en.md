---
title: "Backend P0 verification"
status: active
owner: project-maintainers
updated: 2026-10-09
---

<a id="后端服务-p0-验证记录"></a>
# Backend P0 verification

[中文](p0-validation.md) · Translation of the Chinese primary document.

> Initiative material: background, design and acceptance for this stage. Current usage: [documentation map](../../../README.en.md).

2026-09-26; [B01–B03](plan.en.md).

<a id="完成内容"></a>
## Delivered work

- B01: directory/dependency contracts, capability matrix, migration/proxy/local IdP/test CA choices and upgrade limits.
- B02: independent database/cache, six legal combinations, config/Compose topology, invalid-value rejection, legacy migration notes, metadata/goldens.
- B03: repository verify-backends, generated verify-container, two-level Actions, JSON distinguishing generation/container verification.

To make verification pass, fixed existing health-response cleanup lint, Web config tests affected by container CONFIG_FILE, Micro login shell resetting Go PATH, and migrated Micro golangci-lint arguments to supported syntax.

<a id="验证环境与范围"></a>
## Environment and scope

Docker Desktop, Engine 29.8.0, Compose 5.5.1, Linux arm64 containers, Go 1.26.8. Used nondefault names, nested modules, platform.*.v2 proto packages. Linux amd64 Actions configured but not remotely run, so not verified.

| Combination | Config/topology | Dev image/doctor/lint/tests/build |
| --- | --- | --- |
| Web PG/no cache | Passed | Passed |
| Web PG/Redis | Passed | Passed |
| Micro no DB/no cache | Passed | Passed |
| Micro PG/no cache | Passed | Passed |
| Micro no DB/Redis | Passed | Passed |
| Micro PG/Redis | Passed | Passed |

All evidence/case logs: /tmp/biucing-p0-final/evidence.json, produced by:

```sh
.venv/bin/python scripts/verify-backends --output-dir /tmp/biucing-p0-final
```

Later pinned verification Compose commands/services/files to avoid inheriting production settings; failure-cleanup regression passed. Both templates' real Docker recheck: /tmp/biucing-p0-isolation-check/evidence.json. Temporary logs may disappear; rerun with a new output directory.

Other checks:

- 203 Python core tests including combinations, invalid/legacy inputs, generation-only evidence and cleanup isolation.
- validate, Ruff E4/E7/E9/F, syntax, git diff --check.
- wheel/sdist, rebuilt wheel, installed seven-template generation/config parsing.
- Final logs: /tmp/biucing-p0-core-complete.log and /tmp/biucing-p0-distribution-complete.log.

<a id="本阶段没有证明的能力"></a>
## Capabilities not proved

Containers deliberately used --no-deps without real PG/Redis. They verify component config/current starter, not connections/transactions/sessions/cache. Real integration begins B09; production B20–B24. OIDC/mTLS/migration/proxy/CA are choices only in P0.

Full host discovery did not substitute for core: early mixed runs failed from Swift cache permissions and socket sandboxing. Related Go passed in Docker. Existing maturity labels were not promoted to production/HA ready.
