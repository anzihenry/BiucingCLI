---
title: "Backend P3: calls and observability"
status: active
owner: project-maintainers
updated: 2026-10-09
---

<a id="后端服务-p3调用与可观测性"></a>
# Backend P3: calls and observability

[中文](p3-validation.md) · Translation of the Chinese primary document.

> Initiative material: stage background/design/acceptance; current usage: [map](../../../README.en.md).

As of 2026-09-27 B16–B19 complete; P4/P5 not yet complete at that point.

<a id="实现边界"></a>
## Implementation boundaries

Both templates share internal/outbound: named dependencies created at startup/closed at shutdown, none by default. HTTP reuses Transport, fixed HTTPS origin, bounded bodies, no redirects. gRPC uses peer public API with dns:///+round_robin and CA/DNS/serverAuth/exact SPIFFE checks. Files reread on handshake; urgent old-connection revocation needs drain/rebuild, not immediate file-based revocation.

Per dependency: concurrency isolation/no wait queue/total+attempt budgets/cancellation/up to three explicit idempotent retries/full jitter. Unknown operations reject; nonidempotent single attempt; errors/cancellation never become success. Circuit-breaker hook bounded and off by default; global quota/business idempotency/streams optional. Forward users only from verified Principal, never Cookie/Authorization/inbound metadata/baggage; authorize each hop.

HTTP/gRPC ingress, outbound attempts, PG queries create OTel spans; access logs trace/span IDs. Metrics traffic/errors/latency/in-flight/dependency rejection+retry/pools/export failures. Fixed route/operation labels; no SQL/parameters/identity/credentials/raw error. Bounded sampling/queues/cardinality/export/shutdown. Collector optional, not readiness; dev debug and alert examples provided, no long-term store.

<a id="验证入口"></a>
## Verification entrypoints

- verify-backend-calls --output-dir <new-directory>: independent nondefault modules/dev+runtime images/public proto consumers with real local PG/Dex/CA/Collector.
- scripts/fixtures/backend-p3 copied only by harness; user echo/fault routes never shipped.
- Tests absent/forged users, real OIDC, mTLS+correct user, valid cert but denied method/delegation, cancel, downstream pause/restart, rotation, IdP/Collector failure; compares exported trace IDs and both logs.
- verify-backends retains standard static/race/protocol/compile/real PG sessions.
- Outbound tests CA/DNS/URI/no-cert/rotation/retry/deadline/capacity/metadata sanitization.
- backends.yml independent call job uploads evidence/logs/OTLP only, no keys/cookies.

<a id="验证记录"></a>
## Verification records

Docker Desktop 4.92.0/Engine 29.8.0/Compose 5.5.1/Linux arm64/Go 1.26.8. Temporary evidence may disappear; remote amd64 not run.

| Check | Evidence/result |
| --- | --- |
| Independent calls | /tmp/biucing-p3-calls-v5/evidence.json: all 11, real OIDC/images/mTLS/policy/delegation/timeout/cancel/restart/rotation/IdP+Collector |
| Actual telemetry | otel/traces.json, otel/metrics.json, service.log: HTTP→RPC IDs match both services, PG spans/pool metrics |
| Web standard | /tmp/biucing-p3-matrix/web.log: lint/race/OpenAPI/compile/real PG+migration+sessions |
| Fixed outbound | /tmp/biucing-p3-dev/dns-cancel-final.log: race/static, DNS replacement/in-flight cancel/credential+budget negatives |
| Micro PG | /tmp/biucing-p3-micro-data-final/evidence.json: Buf/static/race/compile/real PG+migration |
| CLI/generation | /tmp/biucing-p3-core-final.log: 203 including all combinations/byte goldens |
| Packages | /tmp/biucing-p3-distribution.log: wheel/sdist rebuild/install/seven templates+configs |

Ruff/validate/whitespace passed; test containers/networks/volumes cleaned, evidence/cache retained. Not all P2 Redis Docker/worktree runs repeated; cache adapter E01, all generation combinations regressed.

Initial failures fixed gRPC cancel normalization to Canceled and harness DB-host/module-context issues; only final evidence counts. Extra direct escaping run failed host-sandbox Swift platform case, not claimed; standard P3 core passed.

<a id="运行限制与技术依据"></a>
## Runtime limits and references

- Semantic gRPC service-config retries disabled; transparent library resend may still occur before write/server handling. One API invocation is not one physical send; timeout does not prove nonexecution. [WithDisableRetry](https://pkg.go.dev/google.golang.org/grpc#WithDisableRetry), [Service Config](https://grpc.io/docs/guides/service-config/).
- DNS applies on resolution/reconnect, not instant reconfiguration; HTTP existing connections reused, forced switching needs drain.
- Outbound streaming returns Unimplemented; E07 defines long-lived auth renewal, no business streaming now.
- Trace queue 512/batch128/export1s; metrics period10s/timeout1s/cardinality256; total cleanup2s. Undelivered telemetry may be lost; platform owns durable audit. [Metric SDK](https://pkg.go.dev/go.opentelemetry.io/otel/sdk/metric), [OTel Go](https://opentelemetry.io/docs/languages/go/).
- Team chooses API publication repository/version. Local module replace connects independent projects, no shared runtime framework.
