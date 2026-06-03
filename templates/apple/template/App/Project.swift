import ProjectDescription

let appName = "{{SWIFT_MODULE_NAME}}"

let project = Project(
    name: appName,
    organizationName: "{{ORGANIZATION_NAME}}",
    packages: [
        .local(path: "../Packages/DesignSystem")
    ],
    settings: .settings(
        base: [
            "DEVELOPMENT_TEAM": "{{DEVELOPMENT_TEAM}}",
            "SWIFT_VERSION": "6.0"
        ]
    ),
    targets: [
        .target(
            name: appName,
            destinations: .iOS,
            product: .app,
            bundleId: "{{BUNDLE_IDENTIFIER}}",
            deploymentTargets: .iOS("{{IOS_MINIMUM_VERSION}}"),
            infoPlist: .extendingDefault(
                with: [
                    "UILaunchScreen": [:],
                    "CFBundleDisplayName": "{{DISPLAY_NAME}}"
                ]
            ),
            sources: ["Targets/App/Sources/**"],
            resources: ["Targets/App/Resources/**"],
            dependencies: [
                .package(product: "DesignSystem")
            ]
        ),
        .target(
            name: "\(appName)Tests",
            destinations: .iOS,
            product: .unitTests,
            bundleId: "{{BUNDLE_IDENTIFIER}}.tests",
            infoPlist: .default,
            sources: ["Targets/AppTests/Sources/**"],
            dependencies: [
                .target(name: appName)
            ]
        )
    ],
    schemes: [
        .scheme(
            name: appName,
            shared: true,
            buildAction: .buildAction(targets: [appName]),
            testAction: .targets(
                [
                    "\(appName)Tests"
                ],
                options: .options(coverage: true)
            ),
            runAction: .runAction(executable: appName)
        )
    ]
)
