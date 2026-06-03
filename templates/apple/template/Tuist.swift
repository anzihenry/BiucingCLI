import ProjectDescription

let config = Config(
    fullHandle: "{{ORGANIZATION_SLUG}}/{{PROJECT_NAME}}",
    project: .tuist(
        compatibleXcodeVersions: .all,
        swiftVersion: "6.0"
    )
)
