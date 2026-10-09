---
title: "Android Shared Core, Binary Components and Shell Validation"
status: active
owner: project-maintainers
updated: 2026-10-09
---

<a id="android-共享核心二进制组件与壳验证"></a>
# Android Shared Core, Binary Components and Shell Validation

[中文](android-validation.md) · Translation of the Chinese primary document.

> Initiative material: historical background, design or acceptance for this stage. See the [documentation map](../../../README.en.md) for current usage.

New common-contract evidence appears in [implementation and validation](cross-platform-validation.en.md). Evidence below is from the original stage and is not automatically a retest of new implementations.

Updated: 2026-09-23. Responsibilities/decisions: [Android architecture](../../../engineering/native/android.en.md). Environment: macOS arm64, JDK 17, Gradle 8.10.2, AGP 8.7.3, Kotlin 2.0.21. Dagger 2.52 uses Java annotation processing. NDK 28.2.13676358/CMake 3.22.1 build arm64-v8a/x86_64 C++20 libraries. Android API 35 simulator; no Android hardware execution recorded.

<a id="2026-09-23-手机壳基线验收"></a>
## 2026-09-23 Phone Shell Baseline Acceptance

| Check | Result |
| --- | --- |
| Initial publication | All seven AARs built/published/exactly locked; SharedCore includes both ABI JNI libraries and matching unstripped symbols |
| Shared C ABI | CMake Release C-client tests passed: errors, cancellation, overflow, unchanged output, session isolation |
| Host JVM/JNI | Four tests passed: values/overflow/isolation, concurrency/close, cancellation-close race, no commit from cancelled coroutine |
| Home component | Two Fake tests passed: real public factory injection and error-state mapping |
| Dagger | SDK/shell generation passed; four missing-binding/cycle counterexamples failed as expected |
| Product shell | Debug, R8 Release, JVM tests and Android lint passed |
| Debug simulator | Two instrumentation tests passed: binary service/session; resources/UI calculation/navigation/Activity recreation |
| Minified Release runtime | Local default test-key signing; installed/launched APK; UIAutomator confirmed 42 and injected beta environment on settings |
| Source-free consumption | Removed components/core/feature/shared, cleaned and rebuilt Debug/Release successfully |
| Independent upgrade | Home 0.1.1 published alone, other SDKs 0.1.0; explicit lock update and shell build passed |
| Artifact/lock regression | Six Python tests passed: tampering, manifest replacement, overrides, dependency consistency, independent upgrade, native ownership/shared source consistency |
| Template regression | 188 Python core tests and Android AAPT2 special-text resource compilation passed |
| Platform regression | Eleven passed; one Swift cache sandbox case passed after cache writes were allowed |
| Distribution | Wheel, sdist, rebuilt wheel and generation for all seven templates passed |

Validate locked manifest digests before artifact digests. Shared-core synchronization ensures Apple/Android C++/C ABI derive from root shared/core, with no independent template drift. NDK ELF LOAD segments use 16 KB alignment; execution on 16 KB systems needs device acceptance.

<a id="可复现入口"></a>
## Reproducible Entrypoints

Fresh generated project with pinned NDK/CMake installed:

```sh
make components-bootstrap
make core-test
./scripts/test-native
./scripts/verify-di
./gradlew :app:assembleDebug :app:assembleRelease :app:testDebugUnitTest :app:lint
make test-ui
```

components-bootstrap creates initial locks without silently replacing existing ones. Third-party Gradle locks ship with templates; product locks separately manage coordinates/content. Upgrades explicitly change declarations, run scripts/components lock and resolve, and update Gradle locks as needed.

Temporary local projects/logs: `/private/tmp/biucing-android-architecture/`, principally android-arch/android-final. These do not ship with templates/releases.

<a id="边界与已发现的验证限制"></a>
## Boundaries and Verification Limitations

- Debug instrumentation and direct minified Release execution are separate evidence. An additional AndroidJUnitRunner attempt under minified Release crashed before tests due to missing androidx.tracing.Trace. It was not counted as passing, and product obfuscation was not weakened. Debug instrumentation remains; Release uses the actual minified APK independently.
- Test signing is local installation only; no production signing, AAB upload or store review acceptance.
- Teams configure external Maven hosting/authentication/symbol services; default is immutable local directories.
- CI workflows exist but were not remotely executed; host JNI tests do not replace device ABI acceptance.
- Real databases/file migrations, synchronization, background work and long-task progress are product extensions.

<a id="2026-09-24-wear-os--tv-补齐"></a>
## 2026-09-24 Wear OS / TV Completion

Same toolchain; product expands to app/wear/tv, SDKs to ten AARs, SharedCore adds armeabi-v7a. New runtime evidence uses official API 34 ARM64 images.

- All ten SDK Release builds and shared Home state tests passed.
- Three apps passed Debug, R8 Release and lint (no errors; version catalog suggestions and other warnings retained).
- Round-screen Wear: two instrumentation tests passed, including crown MotionEvent scrolling, JNI result 42, navigation and Activity recreation state retention.
- TV: one instrumentation test passed, including direction/confirm keys, focus restoration, JNI calculation and Activity recreation.
- Dagger: eight missing/cycle counterexamples across homestate and three shells rejected; restored graphs compiled.
- After removing components/core/feature/shared and cleaning, three apps rebuilt Debug/R8 Release; phone JVM tests passed.
- 189 core, eleven platform, AAPT2 special-text, wheel/sdist and seven-template install/generation checks passed.

Temporary logs/projects: `/private/tmp/biucing-android-devices/`. Sessions are independent; no phone/watch companion synchronization. ARMv7 ELF/symbol delivery compiled but has no device execution. Wear/TV minified Release compiled; runtime evidence is Debug instrumentation. Hardware, production signing/store acceptance remain outstanding. CI has phone/Wear/TV matrices but no remote results; TV uses API 36 x86_64 because older TV x86 images are outside template ABIs.
