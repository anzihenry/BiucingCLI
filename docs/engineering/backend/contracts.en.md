---
title: "Backend engineering contracts (P0 / B01)"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="后端服务工程契约p0--b01"></a>
# Backend engineering contracts (P0 / B01)

[中文](contracts.md) · Translation of the Chinese primary document.

2026-09-26. Scope: generated-project boundaries, fixed choices and verification. Goals: [architecture](architecture.en.md); state: [tasks](../../initiatives/feature/backend-services/plan.en.md). Historical P0 excludes persistence, login sessions, mTLS and production delivery. Current data/migration/protocol/identity versions: [P2](../../initiatives/feature/backend-services/p2-validation.en.md); production belongs to later phases. Outbound/observability: [P3](../../initiatives/feature/backend-services/p3-validation.en.md).

<a id="工程与依赖方向"></a>
## Engineering and dependency direction

A project is one independent Go module and Docker context, never loading BiucingCLI at runtime. Share generation rules/testing contracts first, without shared business packages or large frameworks.

| Directory | Responsibility and dependency restriction |
| --- | --- |
| cmd/server | Compose config/implementations/transport; only app composition entry, no accumulated business logic |
| internal/config | Typed config/validation; no handler/service/DB connection dependencies |
| internal/handler / transport | HTTP/gRPC conversion, calls service without direct SQL |
| internal/service | Operations/interfaces, no handlers/concrete DB drivers |
| internal/model | Internal structures; public changes reviewed in contracts, not exposed DB shapes |
| internal/repository | Data-interface implementations; pgx in B09, no cross-service imports |
| internal/runtime | Start/stop/health/drain, no business rules |
| internal/telemetry | Integration without controlling business availability |
| api | Public/generated protocol; Web OpenAPI B11, Micro Buf exists |
| configs / deploy / scripts | Examples/deployment/project tools; no production secrets |
| tests | Protocol/integration; fixtures are not business capabilities |

These constrain later implementation. P0 does not re-layer the old in-memory example; B05 evolves composition. Later migrate/worker/adapters follow the same rules without empty directories/abstractions. Services communicate only via protocols and own data; shared physical PostgreSQL still separates roles/databases.

<a id="固定选型"></a>
## Fixed choices

| Decision | Choice | Reason/replacement boundary | Phase |
| --- | --- | --- | --- |
| HTTP/RPC | Gin / grpc-go + Protobuf/Buf | Existing Go stack, separate protocol/app | Existing starter, B11/B12 contracts |
| Data | pgx v5, no default ORM | Explicit SQL/transactions, repository isolates driver | B09 pins/integration tests |
| Migration | golang-migrate 4.20.1 | Versioned SQL/independent CLI; replacement converts version history | B10 |
| Single-host proxy | Caddy 2.11.4 | One TLS/routing reference; replacement preserves HTTP | B20 |
| Test IdP | Dex 2.45.1 | Static local OIDC identities; external production IdP, no test users | B13 |
| Local CA | Smallstep CLI 0.30.6 | Container test roots/leaves with SAN, not production PKI | B15 |
| Logs/telemetry | slog / OTel | Standard interfaces, separate Collector/storage | B08/B18 |

Official version references: [migrate](https://github.com/golang-migrate/migrate/releases/tag/v4.20.1), [Caddy](https://github.com/caddyserver/caddy/releases/tag/v2.11.4), [Dex](https://github.com/dexidp/dex/releases/tag/v2.45.1), [Smallstep](https://github.com/smallstep/cli/releases/tag/v0.30.6). [Dex local example](https://dexidp.io/docs/getting-started/) starts test config. P0 fixes decisions without claiming future integrations are compatible; actual protocol/failure tests are required.

go.mod/go.sum pin direct/transitive dependencies: Go minimum 1.26.0 (Docker 1.26.8), Gin 1.10.0, Micro grpc-go 1.81.1, OTel 1.43.0. Tools: Air 1.65.3, golangci-lint 2.12.2, Buf 1.70.0, pinned remote plugins. Local PostgreSQL 16.13, Redis 7.4.2, Collector 0.126.0. These are verification baselines, not latest/vulnerability-free promises; B20/B21 own production digests/scans/upgrades.

Upgrade Dockerfiles, tools, go.mod/go.sum and evidence together in a separate change; shared tools upgrade together. Do not merely change numbers/use latest to bypass compatibility. Document replacements and rerun gates if a chosen component becomes unavailable.

<a id="两模板能力矩阵"></a>
## Template capability matrix

| Capability | Web | Micro | Implementation |
| --- | --- | --- | --- |
| User HTTP | Main entry | Admin/technical HTTP; RPC main | Existing starter |
| gRPC server | Not default | Default | Existing starter |
| DB | Required PG for sessions | none/PG, default none | P2 pgx/migration/least privilege |
| Cache | none/Redis, default none | none/Redis, default none | Independent of DB, no cache adapter yet |
| Auth | OIDC+session/access token | mTLS+method authorization | B13–B15 done, P2 |
| Outbound/isolation | HTTP+gRPC | HTTP+gRPC | B16/B17, P3 |
| CI | Project Docker | Project Docker+Buf | P0–P3 generation/dependency/protocol/calls; P4 scans/SBOM/provenance/signature/production Compose/restore |

<a id="b02-配置契约与兼容"></a>
## B02 configuration and compatibility

Parameters: --database / --set database=..., --cache / --set cache=.... Web only allows database=postgres; Micro none|postgres; both caches none|redis. Invalid values/Web database=none fail before writes.

Old --dependency-store / --set dependency_store=... are rejected, without ambiguous mapping. Old PG becomes --database postgres --cache none; old Redis becomes --database none --cache redis (Micro). Old microservice is rejected. Existing projects remain unchanged; YAML/env migrations are explicit, never automatic user-file rewrites.

Runtime splits database.driver/dsn and cache.driver/dsn. Containers use service names; host examples localhost. DATABASE_DSN/CACHE_DSN are cleared for disabled components and no connections created. Old store/STORE_DSN are not read. P0 reads config only, without DB connections/health probes. Dependencies expose no host ports, preventing worktree collisions. PG volumes are Compose-project scoped; down retains data.

Local credentials are development-only. Platform owns production certificates/identity/secrets/managed DB/backups/telemetry storage; later templates provide contracts/integration, not whole platforms.

<a id="b03-验证入口与证据"></a>
## B03 verification and evidence

Run in repository without host Go:

```sh
uv run --locked python scripts/verify-backends --output-dir /tmp/backend-verification-new
# 快速仅生成六种组合，绝不标记 Docker 验证通过
uv run --locked python scripts/verify-backends --generate-only
# 单独选择一类，参数可重复
uv run --locked python scripts/verify-backends --case web --case micro
```

Output must not exist. Save evidence.json/case logs with generation/container outcomes, commands, Docker/Compose versions/times. Failures return nonzero; generation-only is rendered, unexecuted not-run. CLI remains covered by core; container checks do not pretend to test the generator.

Generated ./scripts/verify-container uses a distinct Compose project/dev image, doctor/lint/test/build, and removes only its own containers/temp volumes. It publishes no app ports and starts no DB/cache, proving current P0 independence; real data tests start at B09. Project Actions and six-case repository matrix use the same entry.

Later CI adds DB/migration/identity/cross-project calls/runtime/restore progressively, without checking off future capabilities prematurely.
