---
title: "Shared Architecture Contract Implementation and Validation"
status: active
owner: project-maintainers
updated: 2026-10-09
---

<a id="共同架构契约实现与验证记录"></a>
# Shared Architecture Contract Implementation and Validation

[中文](cross-platform-validation.md) · Translation of the Chinese primary document.

> Initiative material: historical background, design or acceptance for this stage. See the [documentation map](../../../README.en.md) for current usage.

Implements [D01–D04](../../../engineering/native/cross-platform-decisions.en.md). Verified 2026-09-24 against workspace changes after e0d8cd9; add final commit at commit time, never use the parent to identify new work. Local evidence does not establish remote CI, full V3 or hardware V4/V5 acceptance.

<a id="实现范围"></a>
## Implementation Scope

- Apple: four shells use StateObject for SessionOwner/stable models; overlays preserve them, explicit close awaits, owner disposal provides fallback close.
- Android: ViewModel scope owns business work; owner clearing stops model/closes native; close completion/errors observable; cancelling a waiter does not cancel shared completion.
- HarmonyOS: WindowStage owns SessionOwner, injects via local LocalStorage; destruction closes/rejects work/drains tasks; phone/computer/watch/TV interfaces share business state.
- All platforms add DI failure cases, acceptance checklist and JSON record example. New generated records start not_run, without inheriting repository success.

<a id="环境与产物"></a>
## Environment and Artifacts

Host: macOS 27.0 (26A428), arm64. Temporary projects/logs: `/tmp/biucing-session-contracts/`, neither distributed nor permanent CI archives.

| Platform | Toolchain and consumer versions | Execution environment |
| --- | --- | --- |
| Apple | Xcode 27.0, Swift 6.4, SafeDI 2.0.0; FoundationKit/SharedCore/HomeFeature 0.1.0, HomeFeature rebuilt | Local macOS; iPhone 18 Pro/iOS 27.0, Watch Series 12 46mm/watchOS 27.0, TV 4K third generation/tvOS 27.0, latter three arm64 simulators |
| Android | JDK 17, Gradle 8.10.2, NDK 28.2.13676358; sharedcore 0.1.1, others 0.1.0; changed state/UI rebuilt | Host JVM/JNI, Biucing_API_35 Android 15 phone simulator |
| HarmonyOS | SDK 6.1.1.125, hvigor 6.24.4, ohpm 6.1.2.285, Node 18.20.1; all three components 0.1.0 rebuilt; host native Node 24.19.0 | Host tests/real SDK compilation; no hdc target |

Temporary component version changes avoid immutable artifact replacement; template initial-version policy unchanged.

<a id="本轮结果"></a>
## Results for This Round

| Check | Result | Log relative to temporary directory |
| --- | --- | --- |
| Apple four Debug shells | Five each, twenty passed: stable model, independent owners, repeat close, post-close rejection, owner release | apple-{macos,ios,watchos,tvos}.log |
| Apple DI | Missing/duplicate/cyclic and real Swift signature drift failed correctly | apple-di-final.log |
| Android three shells | Six phone/Wear/TV Debug/Release builds passed | android-shell-final.log |
| Android state | Three tests including discarded late post-close results | android-state-final.log, device-demo/core/homestate/build/test-results/ |
| Android host JNI | Five with explicitly enabled host library, including cancelled close waiter and cancellation/release race | android-jni-final.log, device-demo/core/sharedcore/build/test-results/ |
| Android phone instrumentation | Three: recreation, settings return retention, ViewModelStore clearing/independent close | android-device.log |
| Android DI | Four errors across four graph layers, sixteen correct failures | android-di.log |
| HarmonyOS host bridge/models | Production bridge, queue/cancel/close/isolation, injection, stable owner, late results/failure cleanup passed | harmony-native.log |
| HarmonyOS DI | Missing/duplicate/cycle checks; actual shell type failure rejected, restored rebuild passed | harmony-di.log |
| HarmonyOS unit/device packages | test succeeded with four Hypium cases; three ohosTest cases compiled, not device-executed | harmony-tests.log |
| HarmonyOS source-free | Removed sources/cleaned, unsigned Debug/Release HAP built; sources restored | harmony-no-source-{debug,release}.log |
| CLI/distribution | 199 core, eleven platform; wheel/sdist/seven-template distribution passed | python-core-final.log, python-platform-final.log, distribution-final.log |

Default Gradle excludes CoreSessionTest; ordinary testReleaseUnitTest success cannot establish JNI tests. This round separately built the host library and ran -PhostNativePath=<host-library-directory>; XML reports five, zero skipped/failed. HarmonyOS host tests use identity decorators for @Observed and cannot prove ArkUI reactivity; Hypium success cannot replace production bridge execution on devices.

<a id="仍须按设备验收"></a>
## Remaining Device Acceptance

L01/L03/L04 and I01–I04 have partial automated evidence; units do not replace system window/navigation events. All platforms need device-specific L02 background, actual business exit/window destruction, restart, M01 input/accessibility. Persistence restoration is absent, so that L05 portion is inapplicable; native handles/in-flight work are never promised to resume.

Wear/TV instrumentation was not rerun this round; historical results are in platform records. Six builds do not add new interaction evidence. Apple shell tests are Debug, not four-platform hardware Release acceptance. HarmonyOS still has no ArkTS VM/real bridge device evidence; crown, remote, windows and observation updates need testing. Its type-drift failure covers shell graphs; component real signatures compile at publication, but each component lacks injected type-error cases. No production signing, installation/upgrades, publication, performance/power acceptance; no new database, cross-device sync or continuous background execution.

Generated docs/architecture-acceptance.md provides reproduction/feature matrices; docs/verification-record.example.json records further source/artifact/device/build results.
