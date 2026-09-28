# Kubernetes 参考部署（P5）

这里提供 Kustomize 清单和发布工具；同一 P4 OCI 镜像无需改应用代码。参考 API 基线 Kubernetes 1.35，开发仍使用 Docker；部署控制机另需兼容目标版本的 kubectl/Kustomize、Bash 和 Docker（Cosign）。本地渲染或 JSON schema 通过不等于集群部署、CNI、负载均衡或跨可用区高可用通过。

## 目录与平台责任

- `base`：三副本 Deployment、仅应用端口的 Service、PDB、带内容 hash 的 ConfigMap。Web 使用 ClusterIP；Micro 使用 ready-only Headless Service，现有 gRPC `dns:///` + `round_robin` 客户端才能看到多个 Pod IP。已有连接不会因为 DNS/EndpointSlice 更新而即时搬迁，依赖预算、重连和服务端排空仍然必要。
- `platform`：无 API 权限的独立运行/迁移 ServiceAccount（不挂载 API token）、默认拒绝 NetworkPolicy 和有限白名单。没有集群 RBAC、真实 Secret、数据库、IdP、CNI、Ingress controller 或 cert-manager 安装。
- `overlays/production`：固定三副本参考，Web 附带 `platform-public` IngressClass 的 TLS Ingress。
- `overlays/autoscaling`：可选 HPA，min=3、max=6、CPU 70%，按一分钟最多一 Pod 增减，缩容稳定窗口五分钟；不渲染 Deployment replicas，避免每次发布覆盖 HPA。先选定 profile，不能把 HPA 和固定副本 profile 任意来回套用。
- `migration`：独立 Job，只挂载迁移凭据。无状态 Micro 的发布 bundle 不包含迁移 Job。

部署方预创建命名空间 `backend-prod` 并实施 Pod Security restricted，提供至少三个有容量的节点，参考部署跨三个可用区。hostname 与 zone 的 hard spread 限制同类 Pod 偏斜，zone minDomains=2；缺乏有效 zone 标签或只剩一个可用域会阻止调度。这是明确的调度选择：保留已运行副本，不通过静默集中到一个域宣称 HA。PDB minAvailable=2、AlwaysAllow unhealthy eviction 只约束自愿 eviction，不约束节点失联、OOM 或控制器滚动更新。

平台必须提供支持 ingress/egress NetworkPolicy 的 CNI、CoreDNS、可靠镜像仓库和访问凭据、跨域入口/外部负载均衡器、外部 OIDC、托管 PostgreSQL writer endpoint、PKI、Collector 和告警存储。开启 HPA 还需要 Metrics Server；CPU 只是初始信号，要用真实延迟/排队/数据库容量校准，不能把加 Pod 当作数据库故障的修复办法。

网络规则是可审查的样例：PG `192.0.2.10/32:5432`、Redis `198.51.100.20/32:6380`、IdP `203.0.113.10/32:443` 均为文档地址，必须替换。PG/Redis 策略只选择启用了该组件的 Pod；删除不用的规则也可以。DNS 默认选择 kube-system/kube-dns，NodeLocal DNS、IPv6、云服务地址轮换、出口 NAT 与 Service DNAT 在具体 CNI 下可能不同，必须实测并调整。标准 NetworkPolicy 不能按 DNS 名做持续 FQDN 授权；不要因为托管 PG 地址会变就允许整个公网。通过平台出口网关、可维护的 provider 网段或 CNI 扩展解决，并记录边界。

Web 入口只允许 edge-system 中带 `app.kubernetes.io/component=ingress-controller` 的 Pod；Micro 只允许 backend-prod 中带 `backend.biucing.dev/caller-of=<目标服务名>` 的 Pod。这些标签的赋权必须限制在平台权限内；它们不能代替 mTLS URI SAN、方法 allowlist 和用户委托策略。namespace/pod selector 在同一项中是 AND。修改 namespace 时也要修改策略的 namespaceSelector，它不会被 Kustomize namespace 字段自动改写。

admin 9000 不进入 Service/Ingress，只允许 observability 中的 prober；kubelet 从节点来的探针是否受限制由 CNI 实现决定。OTel 使用可选 push 出口 4318，本模板不声称已提供 Prometheus `/metrics` scrape 端点。需要新出站依赖时同时审查源 egress、目标 ingress、DNS、证书 SAN/URI 和 deadline，不给默认所有 Pod 互通权限。

例如 Web 调 Micro：给 Web Pod 增加 `backend.biucing.dev/caller-of: internal-api`，给 Web egress 增加精确 namespace+Micro Pod selector 与 TCP 9090；Micro 的方法 allowlist 再允许 Web 工作负载 URI。Web dependencies 地址使用 `dns:///internal-api.backend-prod.svc.cluster.local:9090`，校验的 server_name 必须在 Micro 证书 DNS SAN 中。转发用户上下文还须单独授权，不能直接透传终端请求头。

## 配置、Secret 与入口契约

先复制 production overlay 到项目内新的 overlay，再改 `base/config.yaml` 或为该 overlay 添加自己的 ConfigMap generator/patch。配置 hash 变化会触发新 Pod；配置不能含凭据。运行 Secret 默认 `<service>-runtime-v1`，迁移 Secret `<service>-migration-v1`，Web 入口 TLS Secret `<service>-edge-tls-v1`。Secret 由平台 provision，并使用不可变版本名；修改 Pod template 的引用完成轮换，保留旧引用供兼容回退。不要只改同名 Secret 后期待所有进程配置自动刷新。

运行 Secret key 与 P4 文件一致：PG 的 `database-dsn` 和 `ca.crt`，Redis 的 `cache-dsn`，Web 的 `oidc-client-secret`；Micro 的 `server.crt/server.key/ca.crt`。挂载路径 `/run/secrets`。迁移 Secret 仅 `dsn/ca.crt`，挂载 `/run/migration`。DSN 必须 verify-full，使用服务商稳定 writer DNS 名及正确 CA；运行角色最小权限，迁移角色单独授权。无状态 Micro 不需要数据库凭据，但需要 mTLS 文件。文件权限 0440 配合 fsGroup 65532，无 subPath。所有 Pod nonroot/read-only、capabilities 全关，tmpfs 16 MiB 计入内存限制；节点 PID 限制由 kubelet/平台配置。

Web 入口平台负责 TLS 终止、HTTPS 重定向、证书轮换和入口多副本/跨域容量。Ingress host、OIDC origin/callback 与 Secret 域名必须一致。平台还需禁止自动重试非幂等调用、限定代理超时/请求体，并脱敏访问日志的 query/Cookie/Authorization（OIDC code 不能直接进 access log）。Ingress 仅连应用端口，不能接 admin。跨不可信边界的 controller→Pod 链路需要平台另配加密，不能把本参考 HTTP hop 描述成端到端 TLS。

## 发布顺序

```sh
# 项目根目录；IMAGE 是 P4 已发布、扫描、签名的准确 digest。
./scripts/kube-release prepare backend-prod deploy/kubernetes/overlays/production "$IMAGE" .releases/k8s/release-001
# 设置精确 SIGNER_IDENTITY/SIGNER_ISSUER，或明确选择 P4 的固定公钥模式。
./scripts/kube-release preflight my-staging-context .releases/k8s/release-001
# 平台首次配置或有审查过的网络/账户变更时独立应用；它可能影响旧版本流量。
kubectl --context my-staging-context -n backend-prod apply -f .releases/k8s/release-001/platform.yaml
# Secret 由平台预置，不通过本脚本创建、读取或打印。
./scripts/kube-release deploy my-staging-context .releases/k8s/release-001
./scripts/kube-evidence my-staging-context backend-prod .releases/k8s/observation-001
```

prepare 不连接集群，生成固定 digest 的 app/platform/migration 快照、namespace、容量模型和 SHA256 清单；bundle 不能原地编辑。哈希只防意外改动，不是部署清单的签名信任。preflight 校验 P4 签名/SBOM/provenance，再做 server dry-run/admission；它不能证明 Secret 存在、网络可达、能调度或应用 ready。

deploy 再验证签名及 admission，计算容量；PG 模板创建一次独立迁移 Job，等待成功才 apply app 并等待 rollout，并确认至少三个 available 副本，避免初次 HPA 创建时暂时只有一个副本就过早报成功。Job activeDeadline=120s、backoffLimit=0，无自动 DDL 重试；失败保留 Job，TTL 一天，收集日志后按故障流程处理。Job 名每次 prepare 不同，create 拒绝重用已存在 Job；同一 bundle 不可重复 forward deploy，重新 prepare，并先确认前次 Job 已终止。数据库迁移还有已有 advisory lock。无状态 Micro 跳过迁移。

只有一个 CD 控制器可维护同一 context/namespace/service，流水线按此键串行化，迁移成功必须是 Deployment 阶段的硬依赖。脚本本地锁不跨机器，PG 锁只串行 DDL，不串行整个发布。部署身份只授予目标 namespace 内必要的 Deployment/ReplicaSet/Pod/Service/ConfigMap/Ingress/PDB/HPA/Job 及事件读写权限；平台账户/网络和 Secret provision 可由另一身份维护，运行 Pod 无 API 权限。仓库中没有通用 cluster-admin 绑定。

候选 image 拉取失败、配置失败或未 ready 时 rollout 超时退出，不写成功记录；`maxUnavailable=0/maxSurge=1/minReadySeconds=10` 尽量保留旧就绪副本，但不保证所有请求零错误。自动化流水线必须停止后续阶段，先观测再决定前向修复或兼容回退。执行：`scripts/kube-release rollback <context> <之前成功的bundle>`。脚本验证历史 context、签名和 manifest checksum，重新应用旧 app 快照，不运行逆向迁移，也不恢复平台策略或 Secret 内容。先人工确认 schema/协议兼容；不使用 `rollout undo` 猜测旧配置。

ConfigMap 和 Secret 旧版本要保留到回退窗口结束。脚本不自动 prune 集群资源或删除 HPA。首次启用 HPA 应在变更窗口按 Kubernetes 官方管理字段迁移步骤移交 replicas，避免移除字段时短暂默认到 1；从 HPA 切回固定副本也要先受控移除 HPA 并验证副本数。跨 profile 的回退不能只靠 apply 旧快照。

## 排空、容量与数据库切换

Pod 删除时 EndpointSlice 标记 terminating/ready=false；preStop 原生 sleep=10s 给入口和客户端传播时间，随后 SIGTERM 触发现有应用排空（默认10s）及遥测清理（2s），总 grace=40s 留余量。sleep 不等于 readiness 已及时传播，controller/mesh/客户端是否遵循 terminating 语义必须通过流量演练确认。调整应用 shutdown 配置时同步扩大 grace；长期流式请求仍不属于默认基线。

默认 requests 250m/128Mi，limits 1CPU/256Mi；按真实压力测试调节。三个可用区按失去最大一个区后仍承载目标流量规划剩余 CPU/内存、Pod IP、入口连接、数据库连接与 surge 空间。当前 manifest 不自动购买跨区容量，也不保证灾时集群能及时扩容。

`capacity.env` 示例公式：`(HPA上限6 + surge1 + 退出实例余量3) × pool10 + 迁移1 + 备份1 + 运维3 + 其他服务20 = 125`；DB max200减平台预留30可用170，余量45。固定三副本也按可能启用 HPA 的6上限预留。该脚本只计算声明模型，必须与实际 `data.max_connections`、HPA、其他服务和托管数据库限额核对。正在 terminating 的 Pod 可能使总数超过 replicas+surge；反复发布或失联节点可能超过余量3，不能把公式当硬上界。平台应为运行角色设置经过压测的连接上限（本示例100），为迁移/运维预留独立额度，观测池等待和剩余连接，超过预算就停止扩容/发布。

数据库切换由托管平台保证单写者 fencing、复制一致性、writer DNS 与凭据。应用遇到断连会 ready=false，live 保持；连接恢复后重新校验 schema/ready。稳定 DNS、连接池回收和查询 deadline 帮助恢复，但未保证瞬时切换。事务遇到连接丢失时结果可能不确定，业务必须使用幂等/查询确认，禁止无条件重试写事务。不要通过提高副本数或取消 TLS 校验绕过故障。恢复流程沿用 P4 备份手册；切换新库前核对 schema、数据检查、角色授权以及会话失效策略。

## 验收边界

`scripts/verify-kubernetes` 仅做离线 Kustomize 渲染、schema 和预算检查。仓库级 `scripts/verify-backend-kubernetes` 对六种组合与两种 overlay 进行结构/不变量验收，不连接集群。实际 server dry-run、调度、NetworkPolicy、负载均衡、mTLS 轮换、节点/AZ故障、托管PG切换必须执行 [DRILLS.md](DRILLS.md)，填写 [drill-report.json](drill-report.json)。没有真实测量时状态保持 not-run，不能填 HA passed。

参考：[Pod termination](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)、[Deployment 更新与退出实例](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)、[PDB 边界](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)、[NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)、[HPA 管理 replicas](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)。
