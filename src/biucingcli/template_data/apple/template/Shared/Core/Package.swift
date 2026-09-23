// swift-tools-version: 6.4
import PackageDescription

let package = Package(
    name: "SharedCore",
    products: [
        .library(name: "SharedCore", targets: ["SharedCore"])
    ],
    targets: [
        .target(name: "CoreNative", publicHeadersPath: "include"),
        .target(name: "SharedCore", dependencies: ["CoreNative"]),
        .testTarget(name: "SharedCoreTests", dependencies: ["SharedCore"])
    ],
    cxxLanguageStandard: .cxx20
)
