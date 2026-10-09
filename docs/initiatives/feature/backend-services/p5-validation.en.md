---
title: "Backend P5: Kubernetes references and acceptance boundaries"
status: active
owner: project-maintainers
updated: 2026-10-09
---

<a id="backend-p5kubernetes-参考交付与验收边界"></a>
# Backend P5: Kubernetes references and acceptance boundaries

[中文](p5-validation.md) · Translation of the Chinese primary document.

> Initiative material: stage background/design/acceptance; current usage: [map](../../../README.en.md).

2026-09-28. B25/B26 references/tools/contracts/local verification complete; **B27 real HA exercises pending**. No kubectl context, usable multi-zone infrastructure or managed-PG failover. No apply/node-AZ faults/PG failover, availability percentage or production RPO/RTO claim.

<a id="实现内容"></a>
## Implementation

- deploy/kubernetes: base, production/autoscaling, platform ServiceAccount/NetworkPolicy, migration Job, capacity, platform manual, drills, initial not-run reports.
- Reuse P4 OCI, no app/runtime changes; UID65532/read-only/no caps/RuntimeDefault/no automatic token/CPU-memory/tmpfs/separate runtime+migration Secrets.
- Three replicas, surge1/unavailable0, ready10s/progress180s, hostname/zone spread≥2 zones, PDB minAvailable2. Controller settings are not measured continuity/cross-zone availability.
- Startup/live /livez, ready /readyz; admin excluded from Service. preStop10s+app drain10s/telemetry2s, Pod grace40s; propagation/existing clients deferred B27.
- Web ClusterIP+platform TLS Ingress; platform owns HA/certs/redaction/trusted proxies/downstream protection. Micro ready-only headless with DNS/round_robin/mTLS.
- Default-deny policy permits DNS/ingress/callers/probes/PG-Redis-IdP-OTel; component labels select DB/cache. Documentation IPs must be replaced; network labels are not identities. No cluster RBAC/real Secrets.
- Optional HPA min3/max6/CPU70 with rates/windows; overlay removes Deployment replicas to avoid overwrites. Profile switching needs managed-field migration, ordinary apply does not remove HPA automatically.
- kube-release makes immutable bundle/checksum, verifies P4 signature/SBOM/provenance/server admission, waits PG Job before Deployment; after rollout needs≥3 available for initial HPA window. Failed run not success; rollback only previous successful compatible app, never schema. Platform policies separately reviewed/applied; CD serializes full releases across machines.
- kube-capacity counts terminating/surge/migration/backup/ops/other-service connections; example demand125/available170, not measurement. Platform verifies actual pools/scaling/role hard limits.
- kube-evidence read-only: no faults/Secret reads/HA claims from snapshots. DRILLS/JSON cover bad release/node maintenance-loss/AZ/PG/rotation/restore/scaling pressure.
- Separate generated CI pins kubectl1.36.1/checksum and kubeconform0.7.0 digest, before image release build; no cluster writes/deployment credentials.

<a id="验证与证据"></a>
## Verification and evidence

macOS arm64/kubectl1.36.1/Kustomize5.8.1; Docker kubeconform0.7.0 against Kubernetes1.35.0 schemas. First schema fetch needs network; local/offline means no API contact, not no first-download network.

| Check | Evidence |
| --- | --- |
| Six×two overlays | /tmp/biucing-p5-schema/evidence.json:12 render/invariants/schema passed, cluster/ha not-run |
| Invariants | Secret refs only, privileges/resources, ConfigMap hash, selectors/ports/ready/live, stateless no migration, HPA no replicas, API no migration credentials |
| Failure paths | Fake API: migration/admission fails before app update, rollout not success, rollback no DDL, tampering/capacity/injection rejection, stateless skip, temporary HPA single-replica cannot finish; not real cluster evidence |
| Core | /tmp/biucing-p5-core-acceptance.log:213, including9 new release/budget/variable/evidence tests |
| Packages | /tmp/biucing-p5-distribution-acceptance.log:wheel/sdist/rebuilt bytes/flags/seven templates/configs |
| Installed manifests | /tmp/biucing-p5-packaged-acceptance/kubernetes-evidence.json:four Web/Micro, both overlays/scripts/budgets/Docker schemas, cluster/ha not-run |

Ruff/validate/Bash/diff passed. Validation containers --rm, scripts clean temporary renders, no existing services/clusters touched. Early /tmp/biucing-p5-structure harness incorrectly treated CLI success None as failure; fixed, structure-v2/schema final reports authoritative.

<a id="复现"></a>
## Reproduction

```sh
uv run --locked python scripts/verify-backend-kubernetes --schema --output-dir /tmp/backend-kubernetes-new
uv run --locked python scripts/run-tests --suite core
uv run --locked python scripts/verify-distribution --backend-output-dir /tmp/backend-packages-new
# 在生成项目根目录：
./scripts/verify-kubernetes
# 接入目标集群后，按 deploy/kubernetes/README.md 做平台准备、preflight 与发布。
```

No app/Go/development/runtime changes, so P4 full Go/Docker fault matrix not repeated; [P4](p4-validation.en.md) remains evidence. New manifests/scripts/resources separately accepted.

<a id="b27-的实际交付条件"></a>
## B27 delivery prerequisites

Isolated target cluster with enforcing CNI,≥3 real-zone nodes/spare capacity, multi-zone ingress, rotatable PKI, failover-capable managed PG, independent backups, authorized load generator. First admission/secrets/DNS/mTLS/ingress, then individual faults.

Report continuous errors/latency, injection/recovery times, transactions/consistency, manual steps, single points and evidence. Empty fields are not zero/passed. Maintenance is not node crash, PDB not failure guarantee, local kind containers not real AZ/managed-PG exercises.

References: [Deployment surge/terminating](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), [Pod termination](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/), [PDB](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/), [NetworkPolicy limits](https://kubernetes.io/docs/concepts/services-networking/network-policies/), [HPA replicas](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/), [kubeconform boundaries](https://github.com/yannh/kubeconform).
