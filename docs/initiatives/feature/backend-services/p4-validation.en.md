---
title: "Backend P4: single-host production delivery verification"
status: active
owner: project-maintainers
updated: 2026-10-09
---

<a id="backend-p4单机生产交付验证"></a>
# Backend P4: single-host production delivery verification

[中文](p4-validation.md) · Translation of the Chinese primary document.

> Initiative material: stage background/design/acceptance; current usage: [map](../../../README.en.md).

2026-09-28, B20–B24 templates/local acceptance complete; P5 multi-host HA excluded.

<a id="交付内容"></a>
## Delivery

- Standalone compose.prod.yaml/config/environment contracts; external PG/IdP/PKI/telemetry platform-owned, no dev overlay/production build.
- Web Caddy 2.11.4 with mounted TLS/active ready, external admin blocked, retries/access logs disabled to prevent OIDC-code exposure. Micro private caller network, no host RPC/admin.
- UID/GID65532/read-only/cap_drop ALL/no-new-privileges/tmpfs/CPU-memory-PID limits/log rotation/grace. Official Caddy file capability needs edge-only NET_BIND_SERVICE; apps keep all dropped.
- release: strict data env, not shell; digest/Cosign signature+SBOM+provenance; migration first; unready candidates not successful; compatible old-image rollback/version records/local exclusion.
- Release CI separates build/publication privilege, HIGH/CRITICAL block, SPDX SBOM/SLSA v1 provenance/keyless digest signatures. Build has no production publishing authority. Local fixed-key mode explicitly no transparency log.
- database-backup: verify-full/separate credentials/consistent logical snapshots/atomic rename after temp success; restore only explicit empty target, one transaction/no --clean.
- RUNBOOK covers networks/roles/secret modes/first release/update/failed migration/rollback/cert rotation/retention/restore. Config/secrets use version directories; records save paths, not mutable files expected to roll back.
- verify-backend-production added; verify-distribution --backend-output-dir retains installed wheel/rebuilt-sdist projects for real Docker.

<a id="扫描发现与修复"></a>
## Scan findings and fixes

Initial Trivy found x/crypto/x/text/grpc-go high severity; Alpine3.20 EOL. Upgraded Alpine3.23.6/grpc-go1.83.2/x-crypto0.55.0, Go MVS x-net0.58.0/x-text0.41.0 compatible deps; Go1.26.8 retained. Cosign3.1.3 fixes bundle advisory, Trivy0.67.2; supply-chain/Caddy/backup tools pin digests. Real scans use current database without exemptions and prove only that snapshot.

References: [Alpine lifecycle](https://alpinelinux.org/releases/), [Cosign advisory](https://github.com/sigstore/cosign/security/advisories/GHSA-fx35-mq7g-6g98), [verification](https://docs.sigstore.dev/cosign/verifying/verify/), [Caddy health routing](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy).

<a id="实际环境和证据"></a>
## Actual environment and evidence

macOS arm64 host/Desktop4.92.0/Engine29.8.0 Linux arm64/Compose5.5.1. No native Linux/other CPU/Windows acceptance inferred. Hosted OIDC/GHCR publication not executed.

| Check | Evidence |
| --- | --- |
| Core | /tmp/biucing-p4-core-acceptance.log: 204, malicious env cannot execute, network/permissions/executable scripts |
| Worktrees | /tmp/biucing-p4-worktrees/evidence.json: ports/cache/volumes/reload/ownership/down retention/runtime/stop |
| Production faults | /tmp/biucing-p4-production-v5/evidence.json: scans/signature deploy/TLS/PG traffic removal+recovery/migration stop/unready rollback/isolated restore/full-storage failure |
| First restore | Same: snapshot UTC 2026-09-27T23:31:50.418372+00:00, marker restoration2.65s; small fixture, not production RTO |
| Packages | /tmp/biucing-p4-packaged-v2.log: wheel/sdist/rebuilt resources+flags/seven-template config generation |
| Six combinations | /tmp/biucing-p4-matrix/evidence.json: Web default/Redis, Micro none/PG/Redis/PG+Redis Docker lint/race/protocol/compile/real enabled integrations |
| Installed Docker dev | /tmp/biucing-p4-packaged-v2/docker-evidence.json: four Web/Micro from wheel/rebuilt sdist verify-container |
| Calls after upgrades | /tmp/biucing-p4-calls/evidence.json: 11 OIDC→Web→mTLS, policy/forgery/timeout/cancel/restart/rotation/IdP+telemetry/correlation |
| Final resources | /tmp/biucing-p4-distribution-final.log: updated metadata rechecked wheel/sdist/rebuilt/install/config |

Installed production /tmp/biucing-p4-production-package/evidence.json passed all13, including wrong signing key rejection, different-digest update/rollback, read-only backup role and empty-target guard. Snapshot UTC2026-09-27T23:43:20.458363+00:00 to23:43:23.585053+00:00; isolated restore+marker **4.576s**. Window is not a production transaction-recovery point promise, and fixture size does not establish RPO/RTO.

Ruff/validate/shell/whitespace passed. Harness-owned containers/networks/volumes cleaned by inventories; evidence/cache retained.

<a id="能力边界"></a>
## Capability boundaries

- Single-instance updates interrupt; host single point, no zero-downtime/multi-host HA. unhealthy is state, restart needs exit; Web removal needs independent Caddy ready checks.
- Local registry loopback/fixed temporary key/no transparency publication. Target repository must verify GitHub keyless/GHCR/protection/real identities.
- Rollback never reverses DB migration; operator confirms schema compatibility. Signed provenance does not claim a SLSA assurance level.
- Restore occurs in another isolated PG container, logical snapshot only. Platform owns independent remote storage/encryption/retention/PITR/complete-host-loss recovery/production RPO-RTO exercises.
- Real pg_dump writes to disposable1MiB filesystem, not host/DB disk; no production PG full-disk recovery proof.
- Admin visible to container-network members; platform controls admission/egress ACL. Bridge names are not workload identities.

Failed v1–v4 evidence /tmp/biucing-p4-production-v1 through v4 records Cosign/helper/digest/Caddy capability/test-URL problems, not acceptance. Only final success counts.

<a id="复现入口"></a>
## Reproduction

```sh
uv run --locked python scripts/verify-backends --output-dir /tmp/backend-matrix-new
uv run --locked python scripts/verify-backend-worktrees --output-dir /tmp/backend-worktrees-new
uv run --locked python scripts/verify-backend-calls --output-dir /tmp/backend-calls-new
uv run --locked python scripts/verify-distribution --backend-output-dir /tmp/backend-packages-new
# 对 wheel/ 与 sdist/ 下的两个项目分别执行 scripts/verify-container，构建运行镜像。
# 例：Web 使用 wheel 生成项目、Micro 使用 sdist 重建安装包生成项目。
uv run --locked python scripts/verify-backend-production \
  --web-project /tmp/backend-packages-new/wheel/edge-api \
  --micro-project /tmp/backend-packages-new/sdist/internal-api \
  --web-image <built-web-image> --micro-image <built-micro-image> \
  --output-dir /tmp/backend-production-new
```

Actual runs use .venv/bin/python, image tags biucing-p4-web:package and biucing-p4-micro:package. Keys/archives/reports remain private temporary files, not committed; finally removes owned containers/networks/volumes only, no global prune.
