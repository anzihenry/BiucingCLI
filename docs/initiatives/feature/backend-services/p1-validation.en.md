---
title: "Backend P1 implementation and verification"
status: active
owner: project-maintainers
updated: 2026-10-09
---

<a id="后端服务-p1-实施与验证"></a>
# Backend P1 implementation and verification

[中文](p1-validation.md) · Translation of the Chinese primary document.

> Initiative material: stage background/design/acceptance; current usage: [map](../../../README.en.md).

B04–B08 provide runtime foundations. Real identity/persistence/production remain later phases.

<a id="已实现的边界"></a>
## Implemented boundaries

| Task | Implementation |
| --- | --- |
| B04 | Root runtime/separate dev Compose, scripts/task, optional Make; dynamic loopback ports, worktree project/volume/image isolation, UID/GID, Air reload, explicit data deletion |
| B05 | Strict single YAML document, precedence, port/timeout/budget checks, value/_FILE conflict rejection, file-size limits, production credential guards, redacted config, explicit composition/build info |
| B06 | HTTP/gRPC unary/stream IDs, size/concurrency/time budgets, cancellation, panic isolation, validators, Principal/Policy default deny, no internal exception text |
| B07 | Separate admin, live/ready/version, init/drain state, critical checks, partial bind cleanup, bounded stop, no reflection |
| B08 | slog JSON, levels/IDs/fixed access+security fields, sensitive-key redaction, 100 events/s budget and drop summary |

Only HTTP GET /api/v1/ping explicitly public; example user resources deny anonymous. gRPC standard health Check/Watch public, Ping protected. Verifiers arrive B13–B15; X-User-ID/Authorization/Cookie cannot self-assert verified identity.

<a id="开发命令与兼容"></a>
## Development commands and compatibility

No host Go/Buf/Make needed: ./scripts/task bootstrap/dev/verify/image/up/down/logs/doctor, with Make wrappers. dev/up now background; use logs. Migration fails explicitly before B10. Legacy docker-build remains; Micro deploy/compose.yaml includes root config.

Compose files run independently, not merged, preventing port/env/mount ambiguity; [merge rules](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/). Docker allocates dev ports; DB/cache/Collector/admin publish none. down retains data; CONFIRM_DELETE_DATA=yes ./scripts/task clean-worktree deletes project volumes.

Admin defaults to container 127.0.0.1:9000. Public /healthz removed; admin keeps alias. Docker uses /livez; deployment /readyz. Liveness excludes DB; readiness only accepts context-respecting critical checks, never telemetry.

_FILE reads only at startup; rotate then explicitly restart. Production requires explicit DSN, rejects starter PG passwords/non-verify-full, and requires Redis TLS. Not a substitute for B09 roles/connections or B20 secrets.

<a id="验证记录"></a>
## Verification records

Docker Desktop/Linux arm64, Go 1.26.8. amd64 CI configured but not run. Temporary evidence may disappear; regression scripts remain.

- Six combinations via verify-backends: generation/dev/config/Buf/lint/race/compile, /tmp/biucing-p1-final/evidence.json.
- Both final templates rechecked: /tmp/biucing-p1-resumed/evidence.json, passed.
- 203 core, validate/Ruff/diff, wheel/sdist/seven-template generation passed.
- Initial full HTTP/RPC and non-root dev: /tmp/biucing-p1-check2/evidence.json, both passed.
- Two real worktrees: /tmp/biucing-p1-runtime/evidence.json; distinct names/ports, isolated reload, UID, retained PG volume; Web runtime/private readiness/stop passed.
- Micro runtime/mounted secrets/production rejection: /tmp/biucing-p1-micro-runtime/evidence.json.
- Final worktree harness: /tmp/biucing-p1-worktrees-final/evidence.json, all passed.
- Repeat: uv run --locked python scripts/verify-backend-worktrees --output-dir /tmp/new-p1-worktrees; new directories and owned-resource cleanup only.

Regression covers forged headers, policy still required for verified users, unknown-length oversized bodies, panic redaction, timed-out handlers retaining budget, streaming auth/deadline, dependency failure affecting ready not live, partial bind cleanup, conflicting/missing files, production credential rejection, no body/query/cookie/auth logs, bounded audit floods.

<a id="尚未承诺的能力"></a>
## Unclaimed capabilities

- No OIDC/sessions/mTLS/real data adapters/migrations yet; choices are config/local facilities.
- Buffered HTTP TimeoutHandler returns 503; no business streaming until E07.
- Cannot kill arbitrary Go functions ignoring context; slots remain occupied until process exit. RPC deadline/size use [grpc-go](https://pkg.go.dev/google.golang.org/grpc).
- Budgeted logs may drop, not lossless audit. Platform owns stdout backpressure/retention. No full OTel traces/metrics claimed.
- Single-host startup is not production or multi-host HA acceptance; maturity not production-ready.
