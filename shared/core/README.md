# Portable core source authority

Edit C++ and C ABI sources here. Run `python3 scripts/sync-shared-core` from the
repository root to materialize identical source files into the Apple and Android
template payloads. `--check` rejects drift in tests. Platform wrappers remain in
their platform templates; no Swift, Kotlin or JNI dependencies enter this core.

The committed materializations keep generated products and installed Python wheels
self-contained without runtime downloads or cross-template filesystem dependencies.
The two platforms share source and ABI contracts, not compiled binaries.
