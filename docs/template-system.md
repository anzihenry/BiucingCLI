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
  web/
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
  "name": "web",
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

### `web`

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
