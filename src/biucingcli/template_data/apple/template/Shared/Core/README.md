# Portable C++20 core

`Sources/CoreNative` contains platform-neutral C++20 and a C-compatible ABI.
`Sources/SharedCore` provides the Swift 6.4+ facade. CMake and SwiftPM support
standalone development; Apple shells consume the published static SharedCore SDK.
The SDK groups CoreNative and SharedCore XCFrameworks; no feature SDK bundles its
own copy of the native implementation.

## Contracts

- ABI version 1; fixed-width status codes, integers, and explicit element counts.
- Input buffers are borrowed only until the synchronous C call returns.
- Stateful sessions and cancellation tokens are opaque, allocated and freed by C++.
- Stateless `bc_sum` may run concurrently. Session access is serial; token cancellation
  is the explicit thread-safe exception. Do not destroy handles while calls are live.
- C++ catches allocation and internal exceptions. Outputs and completed-operation
  count remain unchanged on failure. Diagnostics are optional caller-owned buffers.
- `bc_session_analyze` checks at most 1,000,000 values, with checked intermediate
  sums; cancellation is cooperative and idempotent. Success commits once, with no
  partial result. Retrying a successful operation counts as another completion.
- There are no progress callbacks in this bounded example. New long operations
  must specify callback executor, throttling, post-completion suppression and reentry.

`CoreSession` copies Swift inputs into the accepted task's lifetime, schedules native
work on its own serial DispatchQueue, and forwards Swift task cancellation through
an atomic token. Admission and close are ordered under a lock. `close()` stops new
work, cancels accepted operations, waits asynchronously, then releases the session.
Repeated close is safe; in-flight operations retain their owner until completion.
C++ owns the authoritative completed-operation state; platform UI state stays outside.

```swift
import SharedCore

let session = try CoreSession()
let value = try await session.analyze([20, -3, 25]) // 42
await session.close()
```

## Development verification

From the product root: `make core-test core-swift-test`.
The native test compiles as C and verifies ABI behavior even in Release builds.
Swift tests cover result/error conversion, pre-cancellation, repeated close and
concurrent admission/close. Four shell tests separately verify the shipped binaries.

For macOS, Windows or Linux with CMake 3.20+ and a C++20 compiler:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBIUCING_CORE_BUILD_TESTS=ON
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```

Embedding applications use `add_subdirectory(path/to/Core core-build)` and link
`Biucing::Core`. The position-independent static target does not require Swift,
Xcode or the product's Apple-specific Makefile. Cross-compilation disables host
tests with `-DBIUCING_CORE_BUILD_TESTS=OFF`.

## Reserved adapters

| Platform | Adapter boundary | Build |
| --- | --- | --- |
| Android | JNI/Kotlin: values, errors, lifetime and cancellation | Android NDK/CMake |
| HarmonyOS | Node-API/ArkTS: values, errors, lifetime and cancellation | DevEco native CMake |
| Windows/Linux | Direct C/C++ facade or language wrapper | Host CMake toolchain |

These adapters and desktop UI applications are not generated. Keep JNI/Node-API
headers outside this directory. Compile separately for each OS/CPU/SDK;
Apple XCFrameworks are not reusable as Android, HarmonyOS or Windows binaries.
