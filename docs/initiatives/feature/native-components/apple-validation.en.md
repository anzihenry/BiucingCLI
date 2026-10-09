---
title: "Apple Core, Static Components and Four-Platform Validation"
status: active
owner: project-maintainers
updated: 2026-10-09
---

<a id="apple-核心静态组件与四平台验证"></a>
# Apple Core, Static Components and Four-Platform Validation

[中文](apple-validation.md) · Translation of the Chinese primary document.

> Initiative material: historical background, design or acceptance for this stage. See the [documentation map](../../../README.en.md) for current usage.

New common-contract evidence appears in [implementation and validation](cross-platform-validation.en.md); original-stage results below do not automatically retest new implementations. Updated: 2026-09-23. Baseline/responsibilities: [architecture](../../../engineering/native/apple.en.md).

Templates generate iOS/macOS/watchOS/tvOS shells together. Swift 6.4+ uses Swift 6 language mode; core is C++20. SwiftPM/CMake develop source; shells consume independently published static XCFrameworks.

| Release unit | Modules | Dependencies |
| --- | --- | --- |
| FoundationKit | ProductContracts, DesignSystem | None |
| SharedCore | CoreNative, SharedCore | None |
| HomeFeature | HomeFeature | Exact FoundationKit version |

Platform adapters inject SharedCore into HomeFeature. Application scope shares a factory; windows/pages own sessions. C++ provides opaque handles, operation commit state, cooperative cancellation, fixed-width errors/diagnostics; Swift wrappers provide background serial scheduling, task retention and async close.

Official SafeDI 2.0.0 CLI has a pinned download digest and separately generates internal/shell-public construction. SDKs expose no SafeDI types. Generated Swift compilation validates descriptions against real interfaces. Shell reads Composition/DI only, without component source scans.

<a id="本地验收"></a>
## Local Acceptance

Xcode 27.0 (27A266a), Apple Swift 6.4, Apple Clang 21, Tuist 4.209.0. Template Tuist pin matches this verification. All app builds use CODE_SIGNING_ALLOWED=NO. Fresh project:

```sh
make components-bootstrap generate
make verify XCODEBUILD='xcodebuild -derivedDataPath DerivedData/final CODE_SIGNING_ALLOWED=NO'
```

| Check | Result |
| --- | --- |
| Static SDKs | Five modules packaged as XCFrameworks for macOS and iOS/watchOS/tvOS device/simulator slices |
| C ABI / CMake Release | One C-client test passed: values, overflow, unchanged output, diagnostics, cancellation, independent session state |
| Swift core | Five tests passed: error mapping, pre-cancellation, repeat close, concurrent commit/close |
| Feature | One state test with deterministic injected service passed |
| SafeDI | Valid graph generated; missing/cyclic dependencies failed for expected reasons |
| iOS Simulator | Build and three shell tests passed |
| macOS hardware | Build and three shell tests passed |
| watchOS Simulator | Build and three shell tests passed |
| tvOS Simulator | Build and three shell tests passed |
| SwiftLint | 27 Swift files, zero violations |
| Independent upgrade | HomeFeature 0.1.1 with FoundationKit 0.1.0; shell validation passed |
| Source-free consumption | Removed Components/Shared; all four shells rebuilt |
| Direct Xcode build | Injected MissingFactory rejected by SafeDI build phase; restored four shells built |

Three shell tests per platform cover real binary calls/close, factory-created independent sessions and resource bundles. Source-component tests are not counted as binary-consumer verification. SDK manifests record slice platforms/architectures, static archive type, source digests, toolchain/dependencies/resources, Swift interface/ABI and symbols. Static objects contain DWARF; app archives produce dSYM. Versions are immutable; product locks bind complete combinations/manifest digests.

Python regression covers manifest replacement, artifact tampering, missing-lock rejection without source fallback, missing resources/slices, independent upgrade, override dependency consistency, CI/Release override rejection, and FAT dynamic libraries masquerading as static archives. Temporary local logs: `/tmp/biucing-architecture-final/`, not distributed.

<a id="尚未验证或不属于本次实现"></a>
## Unverified or Outside This Implementation

- Device SDK slice compilation passed; iOS/watchOS/tvOS hardware execution unverified.
- No production developer signing, macOS notarization or store upload.
- Windows/Linux CMake CI configured, no remote results from this round.
- Four-platform CI provided, requires apple-swift64 macOS runner setup.
- Android Kotlin/JNI/binary baseline: [Android validation](android-validation.en.md); Apple does not generate Android shells. HarmonyOS/Node-API joins core/component baseline: [HarmonyOS validation](harmonyos-validation.en.md). Windows/Linux UI/adapters remain pending.
- Teams configure external hosting/authentication; default immutable local registry and explicit directory/manifest contract.
- No real business database/migrations/long-task progress; future components must follow their contracts.

Automated tests do not replace full interaction, accessibility or performance acceptance per platform.
