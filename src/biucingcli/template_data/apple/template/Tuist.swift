import ProjectDescription

let config = Config(
    project: .tuist(
        compatibleXcodeVersions: .all,
        // Swift language mode; the toolchain minimum is Swift 6.4.
        swiftVersion: "6.0"
    )
)
