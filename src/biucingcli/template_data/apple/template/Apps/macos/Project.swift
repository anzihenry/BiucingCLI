import ProjectDescription

let appName = "{{SWIFT_MODULE_NAME}}_macos"
let debugBundleSuffix = Environment.debugBundleSuffix.getString(default: "")
let binaryDependencies: [TargetDependency] = [
    .xcframework(path: "../../.build/components/FoundationKit/ProductContracts.xcframework"),
    .xcframework(path: "../../.build/components/FoundationKit/DesignSystem.xcframework"),
    .xcframework(path: "../../.build/components/SharedCore/CoreNative.xcframework"),
    .xcframework(path: "../../.build/components/SharedCore/SharedCore.xcframework"),
    .xcframework(path: "../../.build/components/HomeFeature/HomeFeature.xcframework")
]

let project = Project(
    name: appName,
    organizationName: "{{ORGANIZATION_NAME_SWIFT}}",
    settings: .settings(base: [
        "DEVELOPMENT_TEAM": "{{DEVELOPMENT_TEAM}}",
        "SWIFT_VERSION": "6.0",
        "ENABLE_USER_SCRIPT_SANDBOXING": "NO"
    ]),
    targets: [
        .target(
            name: appName,
            destinations: [.mac],
            product: .app,
            bundleId: "{{BUNDLE_IDENTIFIER}}.macos\(debugBundleSuffix)",
            deploymentTargets: .macOS("{{MINIMUM_OS_VERSION}}"),
            infoPlist: .extendingDefault(with: [
                "UILaunchScreen": [:],
                "CFBundleDisplayName": "{{DISPLAY_NAME_SWIFT}}"
            ]),
            sources: ["Sources/**", "../../Composition/Sources/**", "../../Composition/Generated/**"],
            resources: ["../../.build/components/HomeFeature/Resources/**"],
            scripts: [.pre(
                script: """
                set -e
                python3 "$SRCROOT/../../scripts/components" verify-resolved
                python3 "$SRCROOT/../../scripts/components" di
                """,
                name: "Verify SDKs and generate SafeDI",
                basedOnDependencyAnalysis: false
            )],
            dependencies: binaryDependencies
        ),
        .target(
            name: "\(appName)Tests",
            destinations: [.mac],
            product: .unitTests,
            bundleId: "{{BUNDLE_IDENTIFIER}}.macos\(debugBundleSuffix).tests",
            deploymentTargets: .macOS("{{MINIMUM_OS_VERSION}}"),
            infoPlist: .default,
            sources: ["Tests/**"],
            dependencies: [.target(name: appName)] + binaryDependencies
        )
    ],
    schemes: [
        .scheme(
            name: appName,
            shared: true,
            buildAction: .buildAction(targets: [.target(appName)]),
            testAction: .targets([.testableTarget(target: .target("\(appName)Tests"))]),
            runAction: .runAction(executable: .target(appName))
        )
    ]
)
