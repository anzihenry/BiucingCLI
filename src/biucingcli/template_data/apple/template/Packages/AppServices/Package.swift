// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "AppServices",
    platforms: [
        {{SWIFTPM_SUPPORTED_PLATFORM}}
    ],
    products: [
        .library(
            name: "AppServices",
            targets: ["AppServices"]
        )
    ],
    targets: [
        .target(
            name: "AppServices"
        )
    ]
)
