---
title: "Web Service architecture"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="web-service-架构文档"></a>
# Web Service architecture

[中文](web-service.md) · Translation of the Chinese primary document.

Status recorded on 2026-09-26: Web entry specification for backend redesign, pending implementation at that time. Common components/Docker/runtime/acceptance follow [backend architecture](architecture.en.md). This replaces example-business design while preserving user/OIDC/session/PostgreSQL/internal-call boundaries. Subsequent implementation status is in [tasks and stage evidence](../../initiatives/feature/backend-services/plan.en.md).

<a id="定位"></a>
## Positioning

web-service generates Go HTTP APIs for browsers/mobile. It owns public APIs, user identity and app modules, optionally calling internal gRPC. No browser frontend is generated; frontend integrates via contracts. It runs independently of Micro.

<a id="专有组件"></a>
## Dedicated components

| Component | Target contract |
| --- | --- |
| HTTP | Gin routes, validation, size/time limits, request ID, trace, stable errors |
| Public API | OpenAPI/version/compatibility; pagination/idempotency/concurrency per API semantics |
| User auth | External OIDC, server browser sessions, mobile authorization code+PKCE then access token |
| Sessions | Shared PG, expiry/revoke, HttpOnly/Secure cookie, CSRF, explicit local exceptions |
| Authorization | Trusted Principal to app; default deny, resources/tenants/roles defined by owner |
| Browser defense | Origin/CORS, trusted proxies, Host/request limits, no forged forwarded headers |
| Outbound | Shared HTTP/gRPC, internal mTLS, budgets/error conversion/isolation |
| Admin | Live/ready/metrics/version/controlled diagnostics outside user routes |

Session entry may share API process; server performs OIDC exchange. Access only to this service need not retain provider tokens long-term. Design storage/renewal when downstream token delegation is added. Identity is (issuer, subject), not email. Valid tokens/sessions verified with trusted existing keys may survive short IdP outages; new login/refresh fails without bypassing validation.

<a id="docker-运行"></a>
## Docker operation

- Development: container/reload/PG/local test IdP; optional observability profiles.
- Single host: TLS proxy/pinned image/persistent data+sessions/mounted secrets.
- Multi-host: same image, replicas/shared external sessions/data, common HA reference.
- Defaults separate exposure of user APIs, internal dependencies and admin.

<a id="验收与实现现状"></a>
## Acceptance and implementation

Also test issuer/audience/expiry, cross-replica sessions/revoke, CSRF/CORS, unknown-subject rejection and stable outbound-failure responses. Use protocol/dependency fixtures, not a business example.

P1 implements Docker workflows, config/file-secret validation, budgets/default deny, private admin, bounded shutdown/logs. P2 removes memory CRUD and adds OpenAPI/OIDC/pgx/migration/PG sessions. Sessions have fixed lifetimes, discard provider tokens after login, request/store no refresh token, and require login after expiry. P3 adds clients/OTel. P4 adds production Compose/Caddy TLS/signed images/rollback/backup/restore. See [P2](../../initiatives/feature/backend-services/p2-validation.en.md), [P3 calls](../../initiatives/feature/backend-services/p3-validation.en.md) and [P4 limits](../../initiatives/feature/backend-services/p4-validation.en.md).

P5 Kustomize/release/rollback/capacity exist; real node/AZ/managed-DB failover awaits B27: [P5](../../initiatives/feature/backend-services/p5-validation.en.md).
