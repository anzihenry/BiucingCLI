---
title: "Initial template shapes"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

# Initial template shapes

[中文](template-shapes.md) · Translation of the Chinese primary document.

Historical starter examples from the initial template-system design. They do not describe current generated trees, variable sets or platform capabilities. Use `biucing info TEMPLATE` and [current usage](../../../guides/using.en.md) for the shipped catalog, and [engineering](../../../engineering/README.en.md) for current architecture.

## First Version Templates

### `frontend`

Core variables:

- `project_name`
- `display_name`
- `package_name`

Suggested output:

```text
my-app/
  .dockerignore
  README.md
  Dockerfile
  Dockerfile.dev
  Makefile
  compose.dev.yaml
  index.html
  nginx.conf
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
  .air.toml
  README.md
  Dockerfile
  Dockerfile.dev
  Makefile
  compose.dev.yaml
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

### `micro-service`

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
  .air.toml
  .dockerignore
  README.md
  Brewfile
  .mise.toml
  Makefile
  Dockerfile
  Dockerfile.dev
  compose.dev.yaml
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

### `worker`

Core variables:

- `project_name`
- `module_name`
- `worker_name`
- `run_mode`
- `tick_interval_seconds`
- `shutdown_timeout_seconds`

Suggested output:

```text
email-worker/
  .dockerignore
  README.md
  Dockerfile
  Dockerfile.dev
  Makefile
  compose.dev.yaml
  go.mod
  go.sum
  cmd/
    worker/
      main.go
  internal/
    config/
    runtime/
    task/
  configs/
    config.json
  scripts/
    bootstrap
    doctor
  tests/
```
