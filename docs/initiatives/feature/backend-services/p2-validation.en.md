---
title: "Backend P2 implementation and verification"
status: active
owner: project-maintainers
updated: 2026-10-09
---

<a id="后端服务-p2-实施与验证"></a>
# Backend P2 implementation and verification

[中文](p2-validation.md) · Translation of the Chinese primary document.

> Initiative material: stage background/design/acceptance; current usage: [map](../../../README.en.md).

B09–B15, independently generated/deployed templates, no new business model/frontend. Actual implementation scope does not establish production or HA acceptance.

<a id="实现"></a>
## Implementation

| Task | Delivery |
| --- | --- |
| B09 | pgx pools, connect/query budgets, rollback/cancel, startup/readiness, separate DB/runtime+migration roles; stateless Micro no pool |
| B10 | Independent embedded-SQL migration binary, advisory lock, dirty blocking, compatibility; no API auto-migration |
| B11 | OpenAPI committed baseline/oasdiff/response tests; remove CRUD, retain ping/identity |
| B12 | Committed Proto baseline/Buf breaking/pinned generation/safe status+ErrorInfo/independent consumer |
| B13 | OIDC code/S256 PKCE/state/nonce/browser binding/one-shot callback/JWKS cache/separate audience+at+jwt/development Dex |
| B14 | PG opaque sessions/hashed IDs/rotation/logout/absolute expiry/CSRF/exact CORS/cleanup command |
| B15 | Mandatory mTLS/verified SPIFFE URI/method allowlist/per-caller+method user context/handshake cert+root reload/local CA |

<a id="本轮确定的边界"></a>
## Agreed boundaries

<a id="数据与迁移"></a>
### Data and migration

Runtime <service>_app, migration <service>_migrator, locally separate PG containers. Shared production cluster must revoke PUBLIC CONNECT per DB then grant appropriate roles. Platform provisions roles matching SQL; DATABASE_RUNTIME_ROLE selects actual runtime role. Apps cannot create tables/write schema_migrations; migration credentials never enter running API.

dev/up runs migration once before API, not inside API. Release uses /app/migrate from same image and separate MIGRATION_DSN_FILE. Dirty versions never auto force/down; inspect/repair, then operator explicitly sets reviewed version. Schema 1 supported; widen old/new compatibility before expand→migrate→contract. P1 volumes not auto-deleted/recreated; explicitly add roles/permissions or recreate disposable local data.

<a id="web-身份"></a>
### Web identity

Browser gets opaque cookie only; server discards all provider tokens after login. No offline_access/refresh-token storage/refresh API, hence no concurrent refresh rotation. Sessions max one hour and no later than ID-token expiry; complete login again, no infinite sliding extension. Future delegated third-party calls need encrypted custody/concurrent refresh design.

Dex handles local browser login. Mobile APIs accept RS256 typ=at+jwt access JWTs, checking issuer/separate audience/signature/exp/nbf/iat/sub/client_id/jti; reject ID and opaque tokens. Mobile tests use independent signed issuer; Dex ID tokens are not API access tokens. Valid sessions/cached-key verified unexpired tokens survive short IdP outages; failed new login never bypasses checks. JWKS process cache does not guarantee recovery after restart during outage.

Web ports derive from worktree paths, IdP uses adjacent port for exact callback allowlists; explicitly override HOST_PORT/IDP_PORT on conflicts. This replaces P1 random Web port; Micro retains Docker loopback allocation. Dex only in dev Compose; runtime uses external IdP.

<a id="micro-身份"></a>
### Micro identity

All RPCs, including health, require mTLS. Identity is one verified URI SAN, not CN/headers. Methods/delegation lists separate; delegation denied by default, pure service calls need no user. Reauthorize current caller at every hop, never blindly forward metadata; Web strips incoming X-User-*.

Cert/root files reread at new handshake; invalid replacements reject new handshakes. Update version directories/atomic symlinks. Existing TLS does not rehandshake on root replacement; urgent revocation requires drain/restart. Each new RPC also checks existing connection certificate expiry. Platform owns production PKI/rotation.

<a id="协议与能力边界"></a>
### Protocol and capability boundaries

OpenAPI/Proto baselines are committed snapshots, not auto-updated by verification. Deleting HTTP paths/Proto fields must fail breaking checks. Pagination/idempotency/optimistic locking are extension conventions, not fabricated generic data APIs. Redis adapters/outbound/full telemetry/production proxy+release+backup/HA remain later stages.

<a id="验证入口与记录"></a>
## Verification entrypoints and records

- verify-backends: six combinations, lint/race/Buf/OpenAPI/compile/real DB integration when enabled.
- verify-backend-worktrees: real pair, ports/data/reload/ownership/runtime/migration.
- Generated verify-container: same gate/cleanup, used by project CI.
- Web integration: rollback/timeouts/pool exhaustion+replacement/runtime DDL+migration-write rejection/concurrent migration/dirty blocking; real PG login binding/callback replay/shared sessions/CSRF/logout/IdP outage.
- Identity units: token purpose/audience/issuer/expiry/signatures/unknown keys; real TLS/no or expired cert/leaf+root replacement/method+delegation rejection.

Acceptance 2026-09-27, Docker Desktop/Linux arm64/Go 1.26.8; remote amd64 not counted. Temporary local evidence may disappear; regression entrypoints remain.

| Check | Evidence/result |
| --- | --- |
| Six combinations | Web/Web+Redis passed /tmp/biucing-p2-matrix/evidence.json; initial Micro+Redis missing-import failure fixed, all four Micro passed /tmp/biucing-p2-micro-final/evidence.json |
| Final Web | /tmp/biucing-p2/web-complete.log and web-complete-integration.log: lint/race/compile/real migrations+roles+transactions+sessions |
| Final Micro | /tmp/biucing-p2/micro-complete.log: lint/race/contracts/compile |
| Runtime images | web/micro-complete-image.log builds, web/micro-deploy-final.log startup/private-ready, independent mTLS Ping rpc-probe |
| Real Dex | /tmp/biucing-p2/dex-final.json: code/PKCE/session/CSRF logout/post-logout rejection, verify-backend-login |
| Negative protocols | /tmp/biucing-p2/protocol-evidence.json: removed HTTP/Proto rejected, repeat generation identical |
| Two worktrees | /tmp/biucing-p2-worktrees/evidence.json: isolation/reload/UID/retained volumes/runtime+migration+stop |
| Role isolation | Runtime denied another test DB after PUBLIC CONNECT revoked; test DB removed |
| CLI/package | /tmp/biucing-p2/core-release.log: 203; final generation baseline 6; distribution-final.log: wheel/sdist/seven templates |

validate/Ruff/whitespace passed. Compose/Air grace unified to 30s for drain, up to 5s pool cleanup and optional telemetry; longer custom budgets require larger outer grace.

<a id="依赖与依据"></a>
## Dependencies and references

Pinned by go.mod/go.sum, Dockerfile.dev, Buf. migrate 4.20.1 resolution upgraded pgx 5.9.2; Micro grpc-go/OTel 1.82.0/1.44.0, common dependencies aligned. OIDC 3.14.1, OpenAPI validation 0.133.0, oasdiff 1.11.7.

- [pgxpool](https://pkg.go.dev/github.com/jackc/pgx/v5/pgxpool): pools/context.
- [migrate pgx](https://pkg.go.dev/github.com/golang-migrate/migrate/v4/database/pgx/v5): migration/locks.
- [go-oidc](https://pkg.go.dev/github.com/coreos/go-oidc/v3/oidc): tokens/RemoteKeySet.
- [Dex tokens](https://dexidp.io/docs/configuration/tokens/): local fixture limits.
- [oasdiff](https://github.com/oasdiff/oasdiff/releases/tag/v1.11.7): pinned compatibility tool.
