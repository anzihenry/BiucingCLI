---
title: "HarmonyOS Core, Bytecode Components and Shell Validation"
status: active
owner: project-maintainers
updated: 2026-10-09
---

<a id="harmonyos-核心字节码组件与壳验证"></a>
# HarmonyOS Core, Bytecode Components and Shell Validation

[中文](harmonyos-validation.md) · Translation of the Chinese primary document.

> Initiative material: historical background, design or acceptance for this stage. See the [documentation map](../../../README.en.md) for current usage.

New common-contract evidence: [implementation and validation](cross-platform-validation.en.md). Original-stage evidence below is not automatically a retest of new implementations. Updated: 2026-09-24. Decisions: [HarmonyOS architecture](../../../engineering/native/harmonyos.en.md).

<a id="本地环境"></a>
## Local Environment

macOS arm64; DevEco Node 18.20.1, ohpm 6.1.2.285, hvigor/plugin 6.24.4, SDK 6.1.1.125 (API 24 tools), Native Clang 15.0.4, CMake 3.28.2. Generated compatible/target declarations: 5.0.0(12). Producers/consumers use the same checked toolchain.

<a id="已执行的验收"></a>
## Executed Acceptance

| Check | Result and limits |
| --- | --- |
| Shared source | Sync includes HarmonyOS; C++/C ABI matches Apple/Android |
| C ABI | CMake Release client tests passed: errors, unchanged output, cancellation/isolation |
| Host Node-API | Production bridge.cpp host plugin passed full int64, overflow, invalid input, type tags, cancellation, overlap rejection, close, GC retention |
| ArkTS wrapper/model | SDK TypeScript transpilation of real non-UI source passed host tests for input copies, queues, cancellation, close, isolation and Fake injection |
| Bytecode HAR | contracts/sharedcore/homefeature independently built/published; downstream consumes precompiled contracts |
| Native slices | SharedCore arm64-v8a/x86_64 ELF built/packaged; feature HAR has no native core |
| Symbols | Unstripped libraries; readelf confirms .debug_info/.debug_line |
| Hypium | Three passed: app identity, published HomeFactory Fake injection, unsubscribe/idempotent notifications |
| DI | Component/shell generation; missing/cycle failures correct; actual ArkTS checks calls |
| Direct build gate | Injected missing shell binding fails hvigor; restored build normal |
| Product HAP | verify passed; unsigned HAP has five device declarations, unique two-ABI core and libc++ runtime |
| Device test package | build-device-tests compiles real SharedCore call/close/cancel/isolation tests; not device-executed |
| Single upgrade | HomeFeature 0.1.1 with contracts 0.1.0, explicit lock/install, HAP build passed |
| Override restrictions | Real override rejected by direct hvigor Release/CI; cleared successfully |
| Source-free consumption | Removed components/shared, cleaned; Debug/Release HAP built |
| Python distribution | 472 resources preserve bytes/executable bits across wheel/sdist/rebuilt wheel; seven-template installed generation passed |
| Initialization | components-bootstrap/bootstrap/doctor and frozen third-party lock checks passed |
| Python regression | Ten new component tests; 199 core/eleven platform passed; sandbox Swift cache case retested with temporary cache |

Host transpilation is not ArkTS VM/device execution; cross-compilation is not device execution. Hypium Fake tests verify public contracts, not actual HarmonyOS Node-API.

<a id="可复现入口"></a>
## Reproducible Entrypoints

Configure PATH, DEVECO_SDK_HOME and HOS_SDK_HOME, then generate a fresh project:

```sh
make components-bootstrap
make bootstrap
make core-test
make test-native
make verify-di
make verify
make build-device-tests
```

Use a disposable generated project for source removal: move components/shared outside the product, execute both commands, then restore:

```sh
hvigorw clean assembleHap --mode module -p module=entry@default --no-daemon
hvigorw clean assembleHap --mode module -p module=entry@default -p buildMode=release --no-daemon
```

Retain product/component locks; published SDK resolution/install/verification needs no source. Native device tests: entry/src/ohosTest/ets/test/List.test.ets. Run through DevEco with supported device and valid test signing; no device/signing credentials connected in this round.

Temporary local logs: `/tmp/biucing-harmony-work/`. Manual harmonyos-components.yml needs harmonyos-sdk611 runner; no remote results, so it is not an enabled merge gate.

<a id="明确未完成的外部验收"></a>
## Outstanding External Acceptance

- hdc list targets empty; no simulator/hardware results.
- SDK rejects armeabi-v7a; no support claim for it or lightweight watch application models.
- Watch crown/round screen, TV remote focus, large-screen multiwindow, accessibility, performance/power need product acceptance.
- No real developer signing, market upload, remote artifact/symbol server.
- Core is an architecture example without real database, migrations, cross-device sync or progress callbacks.

hvigor emits duplicate resource declarations during bytecode HAR merging. This round they came from the same component in SDK/generated intermediate tables; compilation/packaging passed. New resources still need name-conflict/device-display checks; this result is not arbitrary resource-combination compatibility.
