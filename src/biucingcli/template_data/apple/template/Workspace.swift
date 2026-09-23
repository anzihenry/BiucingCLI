import ProjectDescription

let workspace = Workspace(
    name: "{{PROJECT_NAME}}",
    projects: ["Apps/ios", "Apps/macos", "Apps/watchos", "Apps/tvos"],
    additionalFiles: ["README.md", "Dependencies/**", "Shared/Core/README.md"]
)
