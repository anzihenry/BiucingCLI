---
title: "Micro Service architecture"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="micro-service-架构文档"></a>
# Micro Service architecture

[中文](micro-service.md) · Translation of the Chinese primary document.

Status recorded on 2026-09-26: internal entry specification, pending implementation at that time. Common Docker/runtime/acceptance follow [backend architecture](architecture.en.md). The old [template design](../../initiatives/feature/micro-service-starter/design.en.md) is historical starter material. Subsequent implementation status is in [tasks and stage evidence](../../initiatives/feature/backend-services/plan.en.md).

<a id="定位"></a>
## Positioning

micro-service creates Go services for authorized callers, using gRPC managed by Protobuf/Buf. Each independently publishes/scales and optionally owns data/calls peers. Production quality matches Web, with different identity/protocol boundaries.

<a id="专有组件"></a>
## Dedicated components

| Component | Contract |
| --- | --- |
| RPC server | grpc-go registration, validation, size/concurrency, deadlines, cancellation, controlled errors |
| Interceptors | Unary/stream ID, trace/log/auth/method policy/metrics/recovery |
| Service identity | mTLS peer workload, method permissions, certificate validity/trust |
| User context | Only allowed callers assert users; receiver owns resource authorization |
| Internal contract | Versioned proto, pinned generators, Buf lint/breaking, pinned client contracts |
| Outbound | Same HTTP/gRPC clients/config/connections/reliability budgets as Web |
| Data | Optional PG/migration; stateless services need no DB |
| Diagnostics | gRPC health/separate HTTP admin; restricted reflection/pprof |

mTLS establishes identity, not blanket RPC permission. Separate workload/user/observability context. Platform issues/rotates certificates; app provides safe loading/update. Local test certs are not production credentials. If a proxy terminates mTLS, explicitly deliver trusted identity and prevent bypass; never trust arbitrary identity headers.

Micro does not accept browser cookies, host public login or expose public business ports by default. Web provides public contracts/user boundaries when external access is needed.

<a id="docker-运行"></a>
## Docker operation

- Development: container/Buf/test CA+workload certificates, optional data/telemetry.
- Production: image digest/private network/production cert+config, no public RPC/admin mappings.
- Multi-host: same images/identity, independent instance group, verified discovery/reconnect/RPC distribution.
- Composition with other generated projects requires explicit communication networks/target names; separate Compose projects do not connect automatically.

<a id="验收与实现现状"></a>
## Acceptance and implementation

Beyond common runtime tests: reject wrong/expired identities, rotation, user delegation authorization, deadlines/cancellation, pinned clients, old/new compatibility, safe repeated operations and downstream isolation.

P1 implements Docker/config/file secrets/HTTP-gRPC unary+stream budgets/Principal+Policy default deny/private admin/bounded stop/logs, keeping Buf/trace provider/local Collector. P2 adds mTLS/method+delegation policy/cert reload/real pgx+migrations/real Proto breaking baseline. P3 clients/metrics/traces; P4 production Compose/private mTLS/signed images; multi-host HA remains P5. See [P2](../../initiatives/feature/backend-services/p2-validation.en.md), [P3](../../initiatives/feature/backend-services/p3-validation.en.md) and [P4](../../initiatives/feature/backend-services/p4-validation.en.md).

P5 Kustomize/release/rollback/capacity exist; real node/AZ/managed-DB failover awaits B27: [P5](../../initiatives/feature/backend-services/p5-validation.en.md).
