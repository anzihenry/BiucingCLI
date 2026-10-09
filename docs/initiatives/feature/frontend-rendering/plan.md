---
title: "前端渲染变体：设计与实施计划"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="frontend-rendering-variants-design-and-implementation-plan"></a>
# 前端渲染变体：设计与实施计划

[English](plan.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

状态：阶段 6 实施和本地安装产物验收完成；托管 CI/发布 gate 等待 push，不声称远端成功。最初记录于 2026-09-20，基于 070841f，与已完成内核提取 0–6 分开。示例表达规划行为，当前接受 rendering=csr|ssg|ssr，默认 csr。

当前内核说明：历史阶段 1/2 保留 copytree 的决定已被[统一生成](../../refactor/unified-generation/validation.md)替代。普通/变体共享严格资源/指纹/有效校验/发布器。下述保留迁移经过，前端组合/payload 不变。

<a id="scope-and-decisions"></a>
## 范围与决策

一个 frontend，三预设/default csr；React Router Framework/Vite；React 19.3+/TS 7.0+，测试稳定版本并锁；Tailwind 4/shadcn 小组件入库；共享 pnpm/package/锁/TS/质量；CSR/SSG 静态，SSR 默认自托管 Node；SSR 为页面/BFF，不隐含 DB/业务后端。无实验 RSC、自动 Query、认证/CMS/插件/cloud 依赖。生成时预设，不承诺运行 env 一键转架构。

<a id="evidence-and-limits-of-the-feasibility-spike"></a>
## 可行性实验的证据与限制

macOS 实验 Node 24.19.0、pnpm 11.21.0、React/DOM 19.3.0、TS 7.0.2、Router 8.4.0、Vite 8.3.0、Tailwind 4.3.3、shadcn CLI 4.21.0，官方 Base UI/nova Button/Dialog。仅验证候选，不强制永远保持传递版本。

冻结安装、三生产构建、route types/TS7、一个 Vitest/Testing Library、目标 typed lint、HTTP HTML/metadata/status、固定 SSG/两输入变化 SSR、浏览器 counter/dialog/deep refresh 通过。1280x800/390x844 无溢出；初始 favicon 404，无应用/hydration 错误。

两发现须延续：typescript-eslint 8.70.0 不接 TS7，实验用 @typescript/native=npm:typescript@7.0.2 做 tsc，typescript=npm:@typescript/typescript6@6.0.2 做 lint API；tsc 仍7、peer/lint通过，但不证明 lint 理解未来 TS7 全语法，须测试子集、记录角色，不能降 checker/禁规则。临时 shadcn CLI Zod exports 错用 ^3.25.76 override 继续；采用前复现缩小，不能默认全局 override；组件/许可证入库，生成不拉 registry。

实验 /private/tmp/biucing-frontend-spike.tbAWKM/probe 临时非 CI 依赖。未验生产 Docker/Nginx、Linux、其他浏览器、完整 lint、真实 API/auth、负载；静态 harness 非 Nginx。证明可行，不是生产认证/成熟度升级。

<a id="resource-ownership"></a>
## 资源所有权

```text
frontend/
  template.json
  template/                       # common resources
    package.json
    pnpm-lock.yaml
    components.json
    tsconfig.json
    vite.config.ts
    app/root.tsx
    app/app.css
    app/components/ui/
    app/features/
    app/lib/
  variants/
    csr/template/
    ssg/template/
    ssr/template/
```

根内路径直接映输出，variants/template.json 不复制，不引入输出路径模板。

| 共享 | 模式所有 |
| --- | --- |
| 依赖/锁 | Router config |
| UI/token/style/纯 helper/type | route/data entry |
| TS/Vite/lint/format | SSR server/private env |
| 组件/共享浏览器测试 | SSG path/data |
| ignore/真正同脚本 | Docker/Compose/Nginx |
| 测试 helper | README/Make/env/渲染断言 |

小部署/文档可重复整文件，不拼代码片段；Make 公共名一致，保留隔离/诊断/清理。doctor 真相同才 common，否则整文件 mode-owned。一个 package/锁，不 JSON merge/生成时解依赖；静态镜像只 client，SSR 留生产依赖；CSR 安装带 SSR 包为可接受代价，安装脚本/native CI 验。

<a id="metadata-contract-internal"></a>
## 内部元数据契约

variants 可省略，表示原单目录；null/错类型/空 options/未知 key 错；不借此全局收紧旧解析。片段：

```json
{
  "variables": [
    {"name": "rendering", "required": true, "validator": "text",
     "choices": ["csr", "ssg", "ssr"], "default": "csr"}
  ],
  "variants": {
    "selector": "rendering",
    "options": {
      "csr": {
        "source": "variants/csr/template",
        "required_entries": ["nginx.conf"],
        "forbidden_entries": ["app/entry.server.tsx"],
        "overrides": []
      },
      "ssg": {
        "source": "variants/ssg/template",
        "required_entries": ["nginx.conf"],
        "forbidden_entries": ["app/entry.server.tsx"],
        "overrides": []
      },
      "ssr": {
        "source": "variants/ssr/template",
        "required_entries": ["app/entry.server.tsx"],
        "forbidden_entries": ["nginx.conf"],
        "overrides": [],
        "next_steps": ["make bootstrap", "make build"]
      }
    }
  }
}
```

只一个 selector，引用已声明、有非空 choices/在 choices 内字面 default 的输入，option keys 精确匹配且标识合法。default 仅归变量；无独立 default/default_from/规则选择覆盖。source 必需，template.json 相对规范 POSIX 严格位于 variants 下，检查该 mode 时须目录；各根不可别名/嵌套/重叠 common。

required/forbidden/overrides 可省略空，无重复；required 仅加现有契约，针对有效输出；forbidden 含后代，矛盾错，无 glob/条件。next_steps 替代，省略继承、空列表无步，scoped 渲染仍用。无 mode 变量/契约/命令/成熟度任意继承；Make 名共享、实现不同，整体成熟度不能暗示未验模式。

| 非法输入 | 分类 |
| --- | --- |
| missing_variable selector | 未声明模板错误 |
| auto default/缺 ssr | 默认/选项不匹配 |
| ../other/template/绝对 source | 不安全 |
| override Dockerfile 缺双方 | stale |
| 双方 Dockerfile 无 override | 冲突 |
| assets 文件及 assets/logo.svg | 文件目录冲突 |
| rendering=auto | 输入不支持，无写 |

<a id="deterministic-composition-and-safety"></a>
## 确定组合与安全

先 common 再 mode，保空目录/权限/二进制。同目录合并，同文件除精确 override 均错，整文件替代，每 override 一次，不能替代目录。变体拒绝绝对/点段/反斜杠/空段/NUL/越根/特殊文件/symlink，包括 template 下根祖先。NFC/casefold 及父段碰撞拒，不改名，不承诺 Windows。排序、源层诊断，不忽略隐藏/二进制/空目录。无删除指令/deep merge/多 selector/Python import/command/外根。历史普通行为保留，此功能不借机改无关输出（后续统一内核已替代旧语义）。

<a id="kernel-integration"></a>
## 内核集成

models 增类型声明/资源/不可变选择；catalog/declarations 校 schema；resources 枚举组合冲突，无 CLI/渲染/目标写；validation 有效必需/Make/占位、源输出诊断、全选项无提示；generation 解析/派生（不可改 selector）/输入校验/选择，同计划计数执行、一次暂存；presentation 可选摘要、无源路径；CLI 薄，set 无 frontend 分支。

解析前检查全部声明；create 仅所选内容，未选缺失由完整 validate 报，不因创建成功暗示全部验过。规划记录源 inventory/type/mode/content 和选择，暂存前复查，不重解析变更；drift GenerationError 要新计划。非持久快照/跨进程锁/任意并发防护；转义/单遍不变，无 atomic no-replace 新承诺。

<a id="cli-and-json-contract"></a>
## CLI 与 JSON 契约

以下为全部模式交付目标；此历史设计阶段仅 CSR/SSG 接受，SSR 无写拒绝：

```bash
biucing info frontend
biucing create frontend demo --set rendering=ssg --plan --json
biucing create frontend demo --set rendering=ssr --non-interactive
biucing validate --json
```

无参数 CSR；info 加 modes/default，list 一个 frontend。list/info 可选 variants 仅 selector/default/choices；default 从输入算。create/plan/dry-run 可选 selected_variant selector/value，source 记录 rendering，计数有效输出。普通省两字段，schema1 增量，见 [JSON](../../../engineering/json-contract.md)，不泄路径/override，不变既有类型语义，破坏需升级。validate 保 ok/error_count/errors，带 mode，如 frontend[ssg] 缺 nginx；无新 envelope/exit。用户 bad choice 输入错，资源/声明 InvalidTemplateError，目标 Conflict，JSON stderr；见[错误](../../../engineering/cli-errors.md)。

<a id="phases-and-gates"></a>
## 阶段与关卡

| 阶段 | 交付 | 关卡 |
| --- | --- | --- |
| 0 | 规格/实验/基线 | 仅文档/旧测试 |
| 1 | 类型/loader/resolver fixture | 确定/空目录/二进制/路径覆盖碰撞，无写 |
| 2 | 计划/校验/执行/展示 | 预览一致/全选项/drift/清理，七旧基线不变 |
| 3 | 共享工具/CSR | 冻结/质量/browser，仅前端有意 golden |
| 4 | SSG 内容/metadata/deploy | HTML/构建数据/导航/deep/404，无运行 Node |
| 5 | SSR request/env/deploy | 隔离/hydration/error/health/shutdown |
| 6 | 安装/部署/CI/docs | wheel 三模式、Linux/macOS jobs |

1–2 只 fixture，3 可先仅 CSR，未实现不宣传；前端有意迁移非逐字节兼容，其余 golden 保留。无自动提交/push/version/publication 授权。

<a id="final-acceptance-matrix"></a>
## 最终验收矩阵

core schema/default/selector/无覆盖/containment/dotfile/NFC/override/forbidden/token/未选 invalid/count/drift/conflict/cleanup；兼容 import/error/EOF/cancel/JSON/precedence/golden，不为通过刷新；分发全层/hidden/wheel外生成/sdist重建；工程冻结/TS7断言/route/负lint/format/unit/build/锁一致；实际静态/SSR容器导航/资源/HTML/404/数据隔离/无私密/error/键盘焦点/移动桌面；SSG 显式 URL 验证，无生产 localhost，动态路径枚举；Python CI 与 Node/browser/container 分开，三模式不乘全部 Python，原生依赖验；保 worktree，成熟度按实际证据，实验非发布。

<a id="stage-0-baseline-record"></a>
## 阶段 0 基线

2026-09-20 macOS/070841f/uv0.12.17，仅文档。core115、platform11、AAPT2（/Users/xiejinheng/Library/Android/sdk/build-tools/35.0.1/aapt2）Android1、validate、distribution 七模板通过。core 含重复/基线，无 golden 再生，SHA：

```text
7cc9696fb264be2e60674b5688d01abd915e35b62a5ecf95ec2bc04e6c05847c  tests/golden/generation-baseline.json
41dd067d7a2cbab73a9add55ab558125a8af9882f6f7adc111380badb8728d5f  tests/golden/required-entries.json
```

仅本地非 Linux/远端/三模式认证，distribution 未 check-make，平台套件有既有 Make。无运行/变量/JSON/版本/golden 变化。

<a id="stage-1-implementation-boundary-historical"></a>
## 阶段 1 实施边界（历史）

models 定义 Variant/Variants/Entry/ResolvedResources，集合复制 tuple/只读；Definition variants=None，此阶段不进 to_dict。variant_declarations 严格无 I/O，catalog 仅新声明使用，旧解析/模板不变；selected resolver 检根/内容。

```python
from biucingcli.catalog import load_template
from biucingcli.resources import resolve_resources
from biucingcli.variables import resolve_variables_detailed

# fixture_root contains an experimental template, not a new CLI plugin source.
definition = load_template("fixture", root=fixture_root)
resolved = resolve_variables_detailed(
    definition, {"project_name": "demo", "rendering": "ssg"}
)
resources = resolve_resources(definition, resolved.values)
```

resolver 接解析输入，缺/未知 ValueError，无提示派生渲染复制写。记录路径/层/kind/权限，目录 common 权限胜，精确整覆/stale 拒；变体严格路径/symlink/特殊/case Unicode。输出约束/未渲染 steps 留阶段2，暂不 enforce/Make/占位。旧 inventory symlink 表示不跟踪，非替 copytree，不能接假设全普通文件的执行器。21 resource core fixture，无官方新模板；集成/指纹仍阶段2，fixture 成功不等 CLI 可变体。

<a id="stage-2-implementation-boundary"></a>
## 阶段 2 实施边界

build_plan 选资源/指纹，计数/top/steps/selected_variant 同执行；直接 render_template 同准备发布，不仅 common；历史普通 copytree。提示前 metadata，解析后有效路径/Make/上下文/steps；shadow common/未选内容不参加；validate 全 option 无提示，mode errors 聚合，声明仍原 envelope。

指纹含 Definition/磁盘 metadata/两源层（含 shadow/root）清单权限内容，准备后/暂存前/发布前复查；drift 不重建，非快照/锁。只复制列项、单遍文本/二进制/权限，子项后目录 mode；清理恢复 owner traverse/write。冲突含 dangling、I/O/cancel 保目标清暂存，非任意并发 no-replace。JSON1 两可选字段，普通省，无路径/指纹，info/preview 同 mode；见 [JSON](../../../engineering/json-contract.md#resource-variants)。17 tests，官方/golden 不变；3 才迁移，安装三模式/browser证据仍3–6。

<a id="stage-3-implementation-boundary"></a>
## 阶段 3 实施边界

frontend 只 CSR/default，显式等价；SSG/SSR/未知无写拒；无 CLI flag/分支。common package/锁/workspace/Vite/TS/lint/format/Vitest/document/error/loading/theme/shadcn MIT/welcome/constants/browser；CSR routes/config/Make/Docker/Compose/Nginx/doctor/env/README/browser preset。无 override/merge。旧 src/index 去除，build/client，mock dashboard 换 counter/dialog/routes，无虚构 API。

固定 Node24.19.x/pnpm11.21.0/React19.3.0/Router8.4.0/TS7.0.2/Vite8.3.0/Tailwind4.3.3/Vitest5.0.1/Playwright1.63.0；TS6.0.2 明确 lint API alias，checker 显式 TS7；lint 版本/浮游 Promise 负例；Hooks7.1.1 因7.0.1无 ESLint10，peer无 override；shadcn/Zod workaround不入输出。pnpm11 store 从旧 npmrc 移 workspace 的 storeDir env/default，验证本地/覆盖，Docker scoped volume；命令/隔离不变，dev 每次冻结不信 node_modules 存在。

浏览器 tests 导常量不重复用户字串；声明 prettier-ignore 避长/转义要求手格式，JSX 文本渲染。2026-09-21 macOS 冻结/peer/format/lint负例/TS/route/component/build，Chrome桌面/移动dev与preview通过；下载 Chromium 生产也通过；初始 Headless Shell 取消未默认测试；额外 Escape/focus/deep/nooverflow/noconsole。

同日 Docker29.8.0 Linux arm64 特殊文本新工程 dev构建/安装/peer/verify；生产静态无Node/modules/server，Nginx配置/health；macOS Chrome实际Nginx三测、Linux Chromium同三；Shell下载后默认Make三production/两dev通过。project/端口/store/诊断/connectivity；clean 清test/network/volume，留镜像工程。容器 SPA prerender ::1/127.0.0.1 不匹配，preview.host 固定127.0.0.1/回归，mac/Docker构建通过。未验full-dev/amd64/native Linux/remote/SSG/SSR。

157core+11platform+1Android，四CSR tests；资源感知断言，仅frontend generation/list/required golden变化，其余不变；wheel/sdist解析七配置，尚未安装Node/三模式browser阶段6。

<a id="stage-4-implementation-and-verification-2026-09-21"></a>
## 阶段 4 实施与验证（2026-09-21）

SSG加入，SSR当时仍拒；mode拥有routes/public content/server loaders/origin/meta/prerender/static/preview/验收，无核心分支/schema/依赖/merge，锁仍阶段3。枚举 /、/about、两articles，驱动prerender/sitemap/preview；slug唯一小写段；HTML/.data/builtAt同快照，新内容重建，无任意fallback。

生产 SITE_URL env/builder必需，HTTPS DNS origin语法非连通检查；拒凭据/path/query/fragment/非默认port/loopback/local/坏host；dev可省且无canonical；不从request host推；loader全公开，无CMS/API/auth。Nginx仅client/deep/data/sitemap/robots；未知route/slug/data/assets真实404/noindex，删SPA fallback；无Node/modules/server；全静态目录一版，其他host等效路由非catch-all。

修复root route meta单title（CSR保留），mode preview CSR fallback/SSG各HTML（Vite非生产）；UI prebundle避冷Rolldown chunk；共享useSyncExternalStore在hydration前禁JS counter/dialog，native links/content无JS可用；tests等hydration、window marker不改React DOM。

mac/Docker arm64特殊文本冻结/peer/format/lint负例/TS/route/四unit/build；Chrome四dev/四preview；真实Nginx先六Chrome、最终七Linux Shell，延迟JS/无JS/单title-canonical/sitemap/query独立/client/deep/404；Linux冷/重复四dev。CSR共享修改后全质量、两unit/两dev/两preview。

缺SITE_URL/HTTP localhost/凭据/subpath负构建有清晰错误。159+11+1=171；SSG独立golden/两Python契约，其余不变；分发含SSG/安装wheel外/七config。安装Node/三模式CI仍阶段6，无native Linux/amd64/full-dev/SSR/remote。清容器网络卷，留源镜像，无隐含提交发布。

<a id="stage-5-implementation-and-verification-2026-09-21"></a>
## 阶段 5 实施与验证（2026-09-21）

基于9b94f52，SSR owns routes/request snapshot/React server/Node/preview/deploy/tests。无分支/依赖/锁/override；仅共享TS含server/**/*及Node24 strip用显式.ts，CSR/SSG文件不变。loader有界visitor/UUID/time，重复/过大/control 400；private .server，只显式公开对象，配置失败sanitize500/通用log，unknown404；HTML/data private no-store，fingerprint immutable，其余revalidate；无共享请求缓存/backend/auth/DB/CMS/cloud/RSC。

官方锁定node listener桥Fetch/HTTP，外server public/HEAD/method/path decode-traversal-symlink/health/input timeouts/shutdown；默认忽略forwarded origin，部署仍TLS/host/proxy政策。等待all保status，6秒abort/disconnect取消，不宣称Suspense优化；SIGTERM/INT停接/10秒drain/force，正常0强制1；health非upstream。

Docker冻结builder/prod deps/nonroot node，runtime compiled server/client/source，无app/private env/Vite/TS/dev Router；CONTAINER_PORT同时PORT/映射，3100实际验；worktree不变；preview真handler，built直接Node。

mac/Docker arm64冻结/peer/format/lint负/TSroute/runtime/31unit/build，覆隔离/config/input/HEAD/render/error/deadline/cancel/file/drain。Chrome七Node/四dev/五preview，实际Linux镜像五（特殊文本/12并发/cache/missing/health），healthy/SIGTERM0。Linux Shell七Node、冷/重复四dev、五image/cleanexit。client navigation刷新snapshot不换document。下载慢，精确锁Linux Shell/FFmpeg经host Playwright取复制到本worktree cache、实际Linux执行；初次只跳已准备install前提，不跳build/assert/health/shutdown，随后Linux only-shell正常检查通过；冗余full Chromium取消，不声称完整安装命令完成。

CSR/SSG共享TS后全mac质量、两CSR/四SSG静态browser。161+11+1=173/Ruff，两SSR契约/SSRgolden保护所有权/确定/特殊/执行位，其余不变；分发含private名/三模式外生成/七SSR config/Make；安装Node/browser CI阶段6。无native Linux/amd64/full-dev/remote/load/backend/其他engine，也无隐含提交发布。复现 /private/tmp/biucing-stage5.S6sQOR/ssr-check、ssr-check-aa2ddd01:dev；清test/network/卷，留源/hostbrowser/镜像；缓存可重装非业务数据。

<a id="stage-6-implementation-and-local-verification-2026-09-21"></a>
## 阶段 6 实施与本地验证（2026-09-21）

d53e749之后，payload/内核/锁/JSON/golden不变，增加scripts/tests/CI/docs。[产物验收](../../../guides/frontend-acceptance.md)说明命令/前提/报告/清理/平台。

distribution对325资源在checkout/wheel/sdist比hash/全部执行位，锁环境重建wheel再比；安全解包拒traversal/link/special、新目标、不恢复owner/setuid；Linux Python3.11.2无后续filter API，使用已校验普通提取兼容最低版；两平台core过。

verify-frontend显式wheel新venv验import、清source/external browser override、源树外三模式；原生冻结/peer/format/lint负/TS7/unit/build/dev/builtbrowser；可选实际images/contents/ready/cleanexit，仅清UUID自有容器镜像，失败也清；log/screenshot/SHA JSON保留。十一Python-only测清单/负例/解包/workspace-env/失败超时/cleanup/CI发布。

可复用workflow六jobs=两平台三mode单Python，消费单独已验wheel，Linux加生产镜像。publish同一artifact/release-tag scripts，等待frontend加既有verify/platform；成功失败均upload报告，actionlint1.7.7/contract通过，无Trusted Publisher改。

| 安装 wheel 验证 | macOS arm64 | Docker Linux arm64 |
| --- | --- | --- |
| 三模式冻结/完整质量 | 通过 | 通过 |
| CSR/SSG/SSR unit | 2/4/31 | 2/4/31 |
| dev browser | 2/4/4 Chrome | 2/4/4 Shell |
| built browser/Node | 2/4/7 Chrome | 2/4/7 Shell |
| 实际生产 image | 3/7/5 Chrome→Linux | 由macOS调用验Linux镜像 |

Node24.19.0/pnpm11.21.0/锁不变，两次wheel SHA 24f8c776c0a83ab68307bfbd99334a6e7a9100e851084836eccdcb462223cd15。mac54阶段/Linux27；Linux精确缓存、正常installer/新native deps，非mac modules。实际静态only/nonroot/private sentinel/HTML-data-status/health/exit/cleanup；报告 /private/tmp/biucing-stage6.4fM2Da/macos/reports 与 linux/run/reports，清runner/test，留artifact/project/report/task cache。

最终172core+11platform+1Android=184；Linux3.11.2也172；Ruff/distribution/Make/diff通过，无golden刷新；maturity validated，不升级生产认证。外部gate尚无commit/push/dispatch授权，托管amd64/mac、fresh apt browser deps、原生Linux browser→image组合须远端确认。无PyPI/publication/version bump。
