# Template System

## Goal

BiucingCLI should use a small internal template system that is easy to read, easy to extend, and good enough for variable replacement.

The first version does not need a complex template engine. It needs predictable metadata and straightforward file generation.

## Directory Shape

```text
templates/
  frontend/
    template.json
    template/
      ...
  web-service/
    template.json
    template/
      ...
```

## Template Metadata

Each template should contain a `template.json` file with:

- template name;
- description;
- stack;
- variable definitions;
- next steps.

Suggested shape:

```json
{
  "name": "web-service",
  "description": "Go + Gin web service starter",
  "stack": ["Go", "Gin"],
  "variables": [
    { "name": "project_name", "required": true },
    { "name": "module_name", "required": true },
    { "name": "service_name", "required": false, "default_from": "project_name" },
    { "name": "http_port", "required": false, "default": "8080" }
  ],
  "next_steps": [
    "go mod tidy",
    "go run ./cmd/server"
  ]
}
```

## Variable Replacement

The first version should support simple placeholder replacement only.

Suggested placeholders:

- `{{PROJECT_NAME}}`
- `{{DISPLAY_NAME}}`
- `{{PACKAGE_NAME}}`
- `{{MODULE_NAME}}`
- `{{SERVICE_NAME}}`
- `{{HTTP_PORT}}`
- `{{APPLICATION_ID}}`
- `{{ANDROID_NAMESPACE}}`
- `{{COMPILE_SDK}}`
- `{{MIN_SDK}}`
- `{{TARGET_SDK}}`
- `{{VERSION_CODE}}`
- `{{VERSION_NAME}}`
- `{{JAVA_VERSION}}`
- `{{KOTLIN_MODULE_NAME}}`
- `{{BUNDLE_IDENTIFIER}}`
- `{{MINIMUM_OS_VERSION}}`
- `{{DEVELOPMENT_TEAM}}`
- `{{ORGANIZATION_NAME}}`
- `{{SWIFT_MODULE_NAME}}`
- `{{APPLE_PLATFORM}}`
- `{{APPLE_PLATFORM_NAME}}`
- `{{TUIST_DESTINATIONS}}`
- `{{TUIST_DEPLOYMENT_TARGETS}}`
- `{{XCODEBUILD_DESTINATION}}`

This keeps template files readable and avoids introducing a heavy rendering layer too early.

## First Version Templates

### `frontend`

Core variables:

- `project_name`
- `display_name`
- `package_name`

Suggested output:

```text
my-app/
  README.md
  index.html
  package.json
  tsconfig.json
  vite.config.ts
  .gitignore
  public/
  src/
    main.tsx
    App.tsx
    index.css
    types/
    components/
    pages/
    hooks/
    services/
```

### `web-service`

Core variables:

- `project_name`
- `module_name`
- `service_name`
- `http_port`

Suggested output:

```text
user-service/
  .dockerignore
  README.md
  Dockerfile
  Makefile
  go.mod
  .gitignore
  cmd/
    server/
      main.go
  internal/
    config/
    handler/
    model/
    repository/
    router/
    service/
  configs/
    config.yaml
  tests/
```

### `apple`

Core variables:

- `project_name`
- `display_name`
- `apple_platform`
- `bundle_identifier`
- `organization_name`
- `development_team`
- `minimum_os_version`
- `swift_module_name`

Suggested output:

```text
my-apple-app/
  README.md
  Brewfile
  .mise.toml
  Makefile
  Tuist.swift
  Workspace.swift
  App/
    Project.swift
    Config/
      XCConfig/
      ProjectDescriptionHelpers/
    Targets/
      App/
        Sources/
        Resources/
      AppTests/
        Sources/
  Packages/
    DesignSystem/
      Package.swift
      Sources/
  fastlane/
    Fastfile
    Appfile
  scripts/
    bootstrap
    doctor
    setup-xcode
```

### `microservice`

Core variables:

- `project_name`
- `module_name`
- `service_name`
- `proto_package`
- `http_port`
- `grpc_port`

Suggested output:

```text
my-microservice/
  README.md
  Brewfile
  .mise.toml
  Makefile
  Dockerfile
  cmd/
    server/
  internal/
    config/
    handler/
    service/
    repository/
    transport/
    telemetry/
  api/
    proto/
    buf.yaml
    buf.gen.yaml
    gen/
  configs/
    config.yaml
  deploy/
    compose.yaml
    otel-collector.yaml
  scripts/
    bootstrap
    doctor
```

### `android`

Core variables:

- `project_name`
- `display_name`
- `package_name`
- `application_id`
- `compile_sdk`
- `min_sdk`
- `target_sdk`
- `version_code`
- `version_name`
- `java_version`

Suggested output:

```text
my-android-app/
  README.md
  Brewfile
  .mise.toml
  Makefile
  settings.gradle.kts
  build.gradle.kts
  gradle.properties
  app/
    build.gradle.kts
    src/
      main/
        AndroidManifest.xml
        java/
        res/
      test/
      androidTest/
  core/
    designsystem/
      build.gradle.kts
      src/
    model/
      build.gradle.kts
      src/
  feature/
    home/
      build.gradle.kts
      src/
  fastlane/
    Fastfile
    Appfile
  gradle/
    libs.versions.toml
    wrapper/
  scripts/
    bootstrap
    doctor
    setup-android-sdk
```

## CLI Behavior

`biucing create <template> <project-name>` should:

1. Load template metadata.
2. Resolve defaults.
3. Ask for missing high-value variables only.
4. Copy the template tree into the target directory.
5. Replace placeholders in text files.
6. Print next steps.

## Non-Goals

- No remote template registry.
- No plugin system in the first version.
- No complicated conditional rendering.
- No support for dozens of stacks before the first two templates feel good.
