---
title: "Shared Architecture Decisions and Gaps for Apple, Android and HarmonyOS"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="appleandroidharmonyos-共同架构决策与差距清单"></a>
# Shared Architecture Decisions and Gaps for Apple, Android and HarmonyOS

[中文](cross-platform-decisions.md) · Translation of the Chinese primary document.

Confirmed: 2026-09-24. Status: four decisions accepted; session ownership, DI counterexamples and device interfaces implemented; full device acceptance remains outstanding.

This supplements A01–A20 with common lifecycle, device interaction, acceptance and minimum DI guarantees. These confirmed requirements govern this work. Implementation and partial tests do not establish full acceptance on every device. The platforms share responsibilities, dependency direction, C++20/C ABI and binary delivery rules; directories, shell counts and release units may differ.

<a id="d01会话跟随业务所有者"></a>
## D01: Sessions Follow Business Owners

An explicit business page, window or document owner holds each session. Application objects share factories rather than mutable business sessions by default. View visibility and session lifetime are independent. UI callbacks express events; temporary invisibility does not mean business work has ended.

| Scenario | Common requirement |
| --- | --- |
| Redraw, rotation, layout change | Preserve the living owner's session and state; do not recreate the core |
| Temporary overlays or obstruction | Do not close solely because the view is temporarily hidden |
| Backgrounding | Do not immediately destroy the session; continuation, pause or cancellation follows business policy and system capabilities |
| Explicit business exit, window or document close | Reject new work, request cancellation, wait for actual completion, then release resources; repeated close is safe |
| New independent window or document | Independent session by default; share data through explicit services |
| Restart after process termination | Recreate sessions; restore only supported persisted state, never raw handles or an implied continuation of in-flight tasks |

Async cleanup is not guaranteed when the system terminates a process. Reliable data retention requires persistence. Platform implementations map navigation and window events; completion or failure of close must be observable, beyond merely issuing cancellation.

<a id="d02共享业务按设备设计交互"></a>
## D02: Share Business Logic, Design Interaction for Each Device

| Boundary | Common requirement |
| --- | --- |
| Core | No business branching on device type; outer layers turn device capabilities into explicit inputs or services |
| Feature state | Share applicable use cases, business state and typed output; device UI owns focus and scroll position |
| UI | Phones/tablets support touch and layout; computers keyboard/mouse and windows; watches short flows, round screens and crowns; TVs remote control and focus |
| Composition | Shell/composition selects features, interfaces and platform services; features do not query a global device environment |
| Product scope | Device features and release cadence may differ; state supported, unsupported and inapplicable features |
| Shells/modules | Split by system entrypoints, lifecycle and release requirements; equal shell counts are unnecessary |

HarmonyOS may retain one entry. Watch/TV interfaces may be independent and reuse business models through public factories. Device declarations, font and spacing changes alone do not establish interaction adaptation. Shared state does not imply automatic cross-device synchronization.

<a id="d03支持状态按证据分级"></a>
## D03: Grade Support by Evidence

| Tier | Required evidence | External claim |
| --- | --- | --- |
| V1 Architecture scope | Defined features, component boundaries and platform integration | Included in architecture scope |
| V2 Build verified | Components, apps and test packages build; dependencies/artifacts validated | Build verification completed |
| V3 Runtime verified | Specified simulator/device executes core calls, cancellation, close, isolation and lifecycle scenarios | Runtime verified in the specified environment |
| V4 Device adapted | Main flows, input, layout, accessibility, performance and power pass on target hardware | Target device adaptation completed |
| V5 Release ready | Production signing, installation/upgrade, distribution requirements and release regression pass | Ready for production release |

Record source/artifact version, OS, device/simulator model, CPU architecture, toolchain, build type, scenarios, expected/actual results, log locations and outstanding work. Define product-specific performance/power thresholds in advance; this document invents no universal values. Compilation does not replace execution; host transpilation does not replace ArkTS VM; simulators do not replace hardware; Debug does not replace Release. Record devices, ABIs and build types separately. Partial runtime evidence does not satisfy every V3 scenario. Use common scenario IDs and native test tools; validate device-specific interaction separately.

<a id="d04统一-di-最低保证允许工具不同"></a>
## D04: Common Minimum DI Guarantees, Different Tools Allowed

- Inject through explicit constructors or public factories; business code never accesses a global service container.
- Check internal graphs before component publication; shells check visible dependencies without scanning hidden binary SDK sources.
- Missing dependencies, duplicate bindings, invalid cycles and type mismatches must block builds.
- Define application, business-session and feature-instance owners; prevent long-lived objects from retaining short-lived sessions.
- Business owners perform cancellation, waiting and close; container destruction alone is insufficient.
- Public SDK APIs stay independent of DI tools; document static-check gaps and cover them with focused tests.

Distinguish compile-time checks, build-time tests and device behavior tests; passing tests is not a full compile-time proof. Apple retains SafeDI; Android retains Dagger; HarmonyOS retains explicit construction and its small graph generator. Do not introduce TheRouter/ArkDI now or turn the generator into a general runtime container.

<a id="harmonyos-第三方选型依据"></a>
### HarmonyOS Third-Party Selection Evidence

Inspected source versions in this investigation, rather than claims about all versions:

| Project | Inspected version | Finding |
| --- | --- | --- |
| TheRouter Harmony | `d90329c6ffc8ccdf37f424336ba89dcb48c3134a`, package `1.0.3-rc3` | Named service lookup, caching and duplicate-name checks within module scans; full construction-graph/session-scope checks unconfirmed. Not the current DI replacement; remains a routing candidate |
| ArkDI | `f48ddd98f0a9d556af866d9d46997a0c26a7deea`, package `1.0.0` | Minimal host cases from transpiled non-UI source exposed nested resolution, cycle detection and same-name token cache issues; not adopted |

ArkDI cases: A→B→A overflows the stack; within one scope, B's factory resolves A through a resolver, obtaining a different A from direct scope lookup that is excluded from scope disposal; distinct class tokens sharing a name collide as singletons. `close(): void` also cannot await async disposal. These are host logic reproductions, not HarmonyOS hardware results. Neither candidate completed source-free bytecode HAR consumption, Release/obfuscation or device integration acceptance; this does not establish that HAR is unsupported.

Sources: [TheRouter repository](https://github.com/HuolalaTech/hll-wp-therouter-harmony), [TheRouter version notes](https://therouter.cn/docs/2022/09/06/01), [ArkDI repository](https://gitcode.com/chenjz0369/arkdi). Temporary reproductions are not durable CI evidence. Pin versions and retain reproducible cases/logs when reconsidering selection.

<a id="当前实现与差距"></a>
## Current Implementation and Gaps

This table reflects this implementation round; builds, tests and uncovered scope appear in the [validation record](../../initiatives/feature/native-components/cross-platform-validation.en.md). “Pending verification” means missing evidence, not a proven implementation defect.

| Item | Apple | Android | HarmonyOS |
| --- | --- | --- | --- |
| Shells/devices | Four shells: iOS/macOS/watchOS/tvOS | Three shells: phone/tablet, Wear, TV | One entry declaring phone/tablet/2in1/wearable/tv |
| Lifecycle | Four shells use StateObject for SessionOwner/model; explicit close awaits completion, disposal has fallback cleanup | ViewModel retains session/business work; clearing stops model and closes native; completion/errors observable | WindowStage owns SessionOwner and injects models through local storage; closes on stage/ability destruction |
| Device interaction | Four shells do not establish full interaction acceptance | Independent Wear/TV UI with simulator crown/focus evidence | Mobile/Desktop/Watch/TV separated; keyboard/mouse, crown and remote await device validation; no in-app new-window entrypoint |
| DI | SafeDI missing/duplicate/cycle cases and real Swift type counterexamples; owner behavior tests | Four Dagger graph layers each test four failure classes; model stop, close waiting and ownership tests | Graph failures and real ArkTS shell constructor type failures; host scope/close tests, no full static scope proof |
| Runtime evidence | macOS hardware and other three simulators have core/session/resource tests; complete new D01 scenarios unaccepted | Three shells have builds/simulator evidence including Activity recreation; complete common scenarios need mapping | Core host tests, HAR/HAP and device test package builds recorded; no HarmonyOS device execution |
| Support claims | Describe existing scenarios; do not assert full V3/V4/V5 | Same; ARMv7 compilation is not execution; Wear/TV Debug does not replace Release | Five device categories in scope with existing build verification; no claim all five ran successfully |

Source entrypoints:

- Apple: `Apps/{ios,macos,watchos,tvos}/Sources/ShellRoot.swift`, `Composition/Sources/AppComposition.swift`.
- Android: `composition/src/main/java/composition/SessionOwner.kt`.
- HarmonyOS: `components/homefeature/src/main/ets/HomeView.ets`, `composition/di.json`, `scripts/di`.

Paths are relative to `src/biucingcli/template_data/{apple,android,harmonyos}/template/`. The shared core example has no real database, migrations, cross-device synchronization or long-task progress; these are not implemented common capabilities.

<a id="实施状态与验收条件"></a>
## Implementation Status and Acceptance Conditions

G01 owner implementation/behavior tests, G02 DI failure cases, G03 device interfaces/scope matrix and G04 evidence templates are implemented. The table retains full completion conditions. Incomplete lifecycle and interaction evidence prevents marking the entire items accepted.

| ID/order | Scope and remaining work | Completion condition |
| --- | --- | --- |
| G01 Priority | Decouple Apple/HarmonyOS ownership from view visibility callbacks; verify Android owner boundaries | L01–L05 pass; no remaining core work after exit; close observable |
| G02 Priority | List static DI guarantees/gaps and add nested dependency/scope counterexamples on all platforms | Platform evidence for I01–I04, check phase identified, uncovered items visible |
| G03 Later | Device-specific HarmonyOS interactions; feature/capability matrices on all platforms | Scope recorded per device; M01 on target devices; unverified items remain incomplete |
| G04 Throughout | Device/version/build-specific acceptance records | Complete V01; HarmonyOS obtains actual platform execution before V4/V5 |

| Scenario | Acceptance assertion |
| --- | --- |
| L01 Retention | Same business session across redraw/configuration changes/temporary overlays; no lost results or duplicate core |
| L02 Background | Explicit background policy; invisibility alone never destroys a valid session |
| L03 Exit | Reject new work, cancel active work, release after actual completion; repeated close safe, errors observable, old callbacks cannot contaminate new pages |
| L04 Isolation | Independent owners have distinct sessions/state; closing one leaves the other intact; application factory may be shared |
| L05 Restart | New session on process restart; no handle reuse; restore only declared persistence, mark inapplicable when absent |
| I01 Build failure | Missing/duplicate bindings, invalid cycles and incorrect constructor types each block component/shell builds for the expected reason |
| I02 Nested scope | Direct/nested dependencies resolve the same managed instance within a session; different across sessions; long-lived objects never capture ended sessions |
| I03 Disposal | Closing with in-flight work waits for actual completion; each resource released once, including nested dependencies |
| I04 Delivery | Published source-free components compose; public APIs contain no DI types; mismatches between declarations and real interfaces block builds |
| M01 Interaction | Device-specific touch/layout, keyboard/mouse/windows, round screens/crowns or remotes/focus plus accessibility; record inapplicable checks |
| V01 Evidence | Record environment, versions, results and remaining work by V1–V5; historical partial tests cannot imply full new-contract acceptance |

<a id="平台实现与历史验证依据"></a>
## Platform Implementations and Historical Evidence

- [Apple architecture](apple.en.md) · [Apple core/component validation](../../initiatives/feature/native-components/apple-validation.en.md)
- [Android architecture](android.en.md) · [Android component validation](../../initiatives/feature/native-components/android-validation.en.md)
- [HarmonyOS architecture](harmonyos.en.md) · [HarmonyOS component validation](../../initiatives/feature/native-components/harmonyos-validation.en.md)
