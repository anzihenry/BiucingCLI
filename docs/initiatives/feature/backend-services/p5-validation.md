---
title: "Backend P5：Kubernetes 参考交付与验收边界"
status: active
owner: project-maintainers
updated: 2026-10-09
---

# Backend P5：Kubernetes 参考交付与验收边界

[English](p5-validation.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

日期：2026-09-28。B25/B26 已完成参考清单、工具、契约及本地验证；**B27 真实高可用演练待办**。
本机 kubectl 未配置集群 context，也没有可操作的跨可用区设施或托管 PG 切换环境。
因此没有执行集群 apply、节点/AZ 故障、托管 PG failover，未给出可用性百分比或生产 RPO/RTO 承诺。

## 实现内容

- 两模板新增 `deploy/kubernetes`：Kustomize base、production/autoscaling overlays、平台 ServiceAccount/NetworkPolicy、独立迁移 Job、容量模型、平台部署手册、故障演练清单和初始 `not-run` 报告。
- 复用 P4 OCI 镜像，不改业务或应用运行代码。非 root 65532、只读根文件系统、capabilities 全关、RuntimeDefault seccomp、关闭自动 API token、CPU/内存预算、tmpfs，以及分开的运行/迁移 Secret 引用。
- 默认三副本，滚动 maxSurge=1/maxUnavailable=0，稳定 ready 10 秒，进度截止180秒；hostname/zone 分散，zone 至少两个有效域；PDB minAvailable=2。这些都是控制器配置，尚未证明实际流量连续性或跨域可用性。
- 启动/存活检查 `/livez`、就绪检查 `/readyz`；admin 不进入应用 Service。原生 preStop sleep10秒 + 现有应用10秒排空/2秒遥测清理，Pod grace40秒；入口传播和客户端存量连接行为列入 B27。
- Web：ClusterIP + 平台 TLS Ingress；平台负责高可用入口、证书、日志脱敏、可信代理和下游链路保护。Micro：ready-only Headless Service，配合现有 DNS/round_robin gRPC 客户端与 mTLS 身份校验。
- NetworkPolicy 默认拒绝，限定 DNS、入口/调用方、管理探测、PG/Redis/IdP/OTel；DB/缓存策略按启用组件标签选择。IP 样例为文档网段，必须由平台替换，不把网络标签当成服务身份。无集群 RBAC 或真实 Secret。
- 可选 HPA min3/max6/CPU70%，带扩缩容速率和稳定窗口；overlay 移除 Deployment replicas，避免每次发布覆盖 HPA。切换 profile 仍需平台管理字段迁移，不能靠普通 apply 自动删除旧 HPA。
- `scripts/kube-release` 生成不可原地编辑的 bundle/checksum；验证 P4 签名/SBOM/provenance 和 server admission；PG Job 成功后才更新 Deployment；rollout 后还要求至少三个 available 副本以覆盖 HPA 初次启动窗口；失败不记成功，回退只应用先前成功的兼容 app 快照，不倒退 schema。平台策略独立审查/apply，CD 必须跨机器串行化整个发布。
- `scripts/kube-capacity` 检查声明的连接预算，显式计入 terminating Pod、surge、迁移、备份、运维和其他服务；示例需求125/可用170。它不是实测保证，实际池配置/扩容/角色连接硬限额仍需平台核对。
- `scripts/kube-evidence` 是只读观察入口；不自动注入故障、不读取 Secret、不把快照标为 HA 通过。DRILLS 与 JSON 报告覆盖坏发布、节点维护/失联、AZ失效、PG切换、证书轮换、隔离恢复和扩缩容压力。
- 生成项目新增独立 Kubernetes 验证 CI，固定 kubectl 1.36.1 与校验和，kubeconform 0.7.0 镜像固定 digest；作为镜像 release build 的前置依赖；没有集群写权限或部署凭据。

## 验证与证据

实际平台：macOS arm64；kubectl 1.36.1，内置 Kustomize 5.8.1；Docker 运行 kubeconform 0.7.0，按 Kubernetes 1.35.0 JSON schema 校验。
首次 schema 获取需要网络；“本地/离线验证”指不连接 Kubernetes API，不意味着第一次验证无需网络。

| 检查 | 结果与证据 |
| --- | --- |
| 六种组合 × 两种 overlay | `/tmp/biucing-p5-schema/evidence.json`：12 项渲染、结构不变量及 schema 全部通过；cluster/ha 均为 not-run |
| 结构不变量 | Secret 只引用、权限与资源限制、ConfigMap hash 引用、选择器/端口、ready/live、无状态 Micro 无迁移、HPA 无固定 replicas、迁移凭据不进入 API Pod |
| 脚本失败路径 | 核心测试中的 fake API 验证迁移失败/admission失败不更新应用、rollout失败不记成功、回退不执行 DDL、快照篡改拒绝、容量不足/命令注入拒绝、无状态 Micro 跳过迁移、HPA 暂时单副本不得完成发布；不作为真实集群证据 |
| 核心回归 | `/tmp/biucing-p5-core-acceptance.log`：213 项通过，包含9项新增 Kubernetes 发布/预算/变量与证据边界测试 |
| 安装包资源 | `/tmp/biucing-p5-distribution-acceptance.log`：wheel、sdist、sdist 重建 wheel 的资源字节/执行权限一致，安装后全部七模板和配置验证通过 |
| 安装包清单 | `/tmp/biucing-p5-packaged-acceptance/kubernetes-evidence.json`：wheel/sdist 的 Web/Micro 四项目均通过两种 overlay 的生成脚本、预算和 Docker schema 校验，cluster/ha 保持 not-run |

Ruff、模板 validate、Bash 语法与 `git diff --check` 通过。Docker 校验容器使用 `--rm`，临时渲染目录由各脚本清理；不操作已有服务或集群。前期 `/tmp/biucing-p5-structure` 的验收 harness 把 CLI 成功返回 None 误判成失败；已修复，以 `structure-v2` 和 `schema` 最终报告为准。

## 复现

```sh
uv run --locked python scripts/verify-backend-kubernetes --schema --output-dir /tmp/backend-kubernetes-new
uv run --locked python scripts/run-tests --suite core
uv run --locked python scripts/verify-distribution --backend-output-dir /tmp/backend-packages-new
# 在生成项目根目录：
./scripts/verify-kubernetes
# 接入目标集群后，按 deploy/kubernetes/README.md 做平台准备、preflight 与发布。
```

本轮应用/Go 依赖及 Docker 开发运行路径未改，不重复执行 P4 的 Go/Docker 故障矩阵；原证据仍见 [P4](p4-validation.md)。新增清单、脚本与包资源单独验收。

## B27 的实际交付条件

需要提供隔离目标集群（含执行 NetworkPolicy 的 CNI）、至少三个有真实 zone 标签和剩余容量的节点、跨区入口、可轮换 PKI、可执行 failover 的托管 PG、独立备份存储和授权流量发生器。先完成 admission/secret/DNS/mTLS/入口连通性，再逐项故障演练。
报告必须包含连续流量错误/延迟、注入与恢复时间、事务结果和数据一致性、人工步骤、剩余单点、证据文件；空项不能填零或 passed。节点维护不等于节点崩溃，PDB 不等于故障保证，本地 kind 的多个容器也不能替代真实 AZ/托管PG演练。

依据：[Deployment 退出实例与 surge](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)、[Pod 终止](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)、[PDB](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)、[NetworkPolicy 限制](https://kubernetes.io/docs/concepts/services-networking/network-policies/)、[HPA replicas 管理](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)、[kubeconform 校验边界](https://github.com/yannh/kubeconform)。
