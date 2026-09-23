# Component source development

This package is a component-development host, not a source dependency of the apps.
From the product root, `make component-test` generates the internal SafeDI graph
and runs the package's tests. Previews use deterministic injected services.

Publish all SDKs initially with `make components-bootstrap`; publish a single SDK
with `./scripts/components build --component HomeFeature --version 0.1.1`.
That command compiles against the declared FoundationKit binary, not an unpublished
local FoundationKit source edit. Update the declaration/lock explicitly afterward,
or set a local binary override for personal testing.

The starter's release units and module boundaries live in `scripts/components`.
When adding components, extend the module/dependency declarations, product lock,
Tuist references and corresponding tests together. The script is the starter's
small release tool, not a general-purpose package manager.

For an independent component repository:

1. Move the component package, its tests, DI input and resources together.
2. Run the pinned SafeDITool 2.0.0 before compilation:
   `SafeDITool generate --include DI --combined-output Sources/HomeFeature/DependencyTree.swift`.
3. Run `swift test`. When extracting a single feature instead of this whole source
   package, replace its foundational source targets with the declared binary SDK
   dependencies; retain the same public module names.
4. Adapt the publication entry point to the new source root. Publish the same
   `SDK/version/manifest.json`, static XCFrameworks and Resources layout.
5. Product repositories consume that immutable artifact and never scan this repository.

Both generators consume declarations only. Compiling the generated Swift against
real types is mandatory: graph descriptions are not a substitute for type checking.
