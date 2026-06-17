import ProjectDescription

let appName = "{{SWIFT_MODULE_NAME}}"

let project = Project(
    name: appName,
    organizationName: "{{ORGANIZATION_NAME}}",
    packages: [
        .local(path: "../Packages/AppServices"),
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
            destinations: {{TUIST_DESTINATIONS}},
            product: .app,
            bundleId: "{{BUNDLE_IDENTIFIER}}",
            deploymentTargets: {{TUIST_DEPLOYMENT_TARGETS}},
            infoPlist: .extendingDefault(
                with: [
                    "UILaunchScreen": [:],
                    "CFBundleDisplayName": "{{DISPLAY_NAME}}"
                ]
            ),
            sources: ["Targets/App/Sources/**"],
            resources: ["Targets/App/Resources/**"],
            dependencies: [
                .package(product: "AppServices"),
                .package(product: "DesignSystem")
            ]
        ),
        .target(
            name: "\(appName)Tests",
            destinations: {{TUIST_DESTINATIONS}},
            product: .unitTests,
            bundleId: "{{BUNDLE_IDENTIFIER}}.tests",
            infoPlist: .default,
            sources: ["Targets/AppTests/Sources/**"],
            dependencies: [
                .package(product: "AppServices"),
                .target(name: appName)
            ]
        )
    ],
    schemes: [
        .scheme(
            name: appName,
            shared: true,
            buildAction: .buildAction(targets: [.target(appName)]),
            testAction: .targets(
                [
                    .testableTarget(target: .target("\(appName)Tests"))
                ],
                options: .options(coverage: true)
            ),
            runAction: .runAction(executable: .target(appName))
        )
    ]
)
