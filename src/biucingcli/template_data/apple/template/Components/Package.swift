// swift-tools-version: 6.4
import PackageDescription

let package = Package(
    name: "ProductComponents",
    platforms: [
        .macOS("{{MINIMUM_OS_VERSION}}"),
        .iOS("{{MINIMUM_OS_VERSION}}"),
        .watchOS("{{MINIMUM_OS_VERSION}}"),
        .tvOS("{{MINIMUM_OS_VERSION}}")
    ],
    products: [
        .library(name: "ProductContracts", targets: ["ProductContracts"]),
        .library(name: "DesignSystem", targets: ["DesignSystem"]),
        .library(name: "HomeFeature", targets: ["HomeFeature"])
    ],
    targets: [
        .target(name: "ProductContracts"),
        .target(name: "DesignSystem"),
        .target(name: "HomeFeature", dependencies: ["ProductContracts", "DesignSystem"]),
        .testTarget(name: "HomeFeatureTests", dependencies: ["HomeFeature", "ProductContracts"])
    ]
)
