---
title: "初始模板结构"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="initial-template-shapes"></a>
# 初始模板结构

[English](template-shapes.en.md)

初始系统设计的历史 starter 示例，不描述当前目录、变量或平台。已发布目录见 biucing info TEMPLATE 与[当前使用](../../../guides/using.md)，架构见[工程文档](../../../engineering/README.md)。

<a id="first-version-templates"></a>
## 初版模板

<a id="frontend"></a>
### `frontend`

核心变量 project_name、display_name、package_name。建议输出：

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

<a id="web-service"></a>
### `web-service`

核心变量 project_name、module_name、service_name、http_port。建议输出：

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

<a id="apple"></a>
### `apple`

核心变量 project_name、display_name、apple_platform、bundle_identifier、organization_name、development_team、minimum_os_version、swift_module_name。建议输出：

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

<a id="micro-service"></a>
### `micro-service`

核心变量 project_name、module_name、service_name、proto_package、http_port、grpc_port。建议输出：

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

<a id="android"></a>
### `android`

核心变量 project_name、display_name、package_name、application_id、compile_sdk、min_sdk、target_sdk、version_code、version_name、java_version。建议输出：

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

<a id="worker"></a>
### `worker`

核心变量 project_name、module_name、worker_name、run_mode、tick_interval_seconds、shutdown_timeout_seconds。建议输出：

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
