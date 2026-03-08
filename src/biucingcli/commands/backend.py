"""Backend toolchain subcommands."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, cast

import typer
from rich.console import Console
from rich.table import Table

from .common import get_domain_config, render_stack_table

# Template directory path
TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates" / "backend"

app = typer.Typer(help="Curate backend stacks and tooling.")


@app.command("list")
def list_stacks(
    ctx: typer.Context,
    stack: str | None = typer.Option(None, "--stack", "-s", help="Target a specific stack."),
) -> None:
    """List backend stacks."""
    config = get_domain_config(ctx, "backend")
    console: Console = ctx.obj["console"]
    render_stack_table(console, config.get("stacks", {}), stack=stack)


@app.command()
def suggest(
    ctx: typer.Context,
) -> None:
    """Highlight recommended backend stacks."""
    config = get_domain_config(ctx, "backend")
    console: Console = ctx.obj["console"]
    preferred = config.get("preferred", "")
    stacks = config.get("stacks", {})

    if preferred and preferred in stacks:
        console.print(f"[bold green]✨ Recommended Stack: {preferred}[/bold green]\n")
        render_stack_table(console, {preferred: stacks[preferred]}, stack=None)
    else:
        console.print("[yellow]No preferred stack configured.[/yellow]")
        render_stack_table(console, stacks)


@app.command()
def info(
    ctx: typer.Context,
    stack: str = typer.Argument(..., help="Stack name to show details for."),
) -> None:
    """Show detailed information about a specific backend stack."""
    config = get_domain_config(ctx, "backend")
    console: Console = ctx.obj["console"]
    stacks = config.get("stacks", {})

    if stack not in stacks:
        console.print(f"[red]Stack '{stack}' not found.[/red]")
        raise typer.Exit(code=1)

    stack_config = stacks[stack]
    description = stack_config.get("description", "No description available.")
    tools = stack_config.get("tools", [])

    console.print(f"[bold cyan]Stack: {stack}[/bold cyan]")
    console.print(f"[green]Description:[/green] {description}\n")

    table = Table(title="Tools", show_lines=True)
    table.add_column("Name", style="bold cyan")
    table.add_column("Category", style="green")
    table.add_column("Description", style="yellow")
    table.add_column("URL", style="magenta")

    for tool in tools:
        table.add_row(
            tool.get("name", "Unknown"),
            tool.get("category", ""),
            tool.get("description", ""),
            tool.get("url", ""),
        )

    console.print(table)


@app.command()
def init(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Project name."),
    stack: str | None = typer.Option(None, "--stack", "-s", help="Backend stack to use."),
    destination: Path = typer.Argument(..., help="Where to create the project."),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite if destination exists."),
) -> None:
    """Initialize a new Go backend project."""
    config = get_domain_config(ctx, "backend")
    console: Console = ctx.obj["console"]

    # Determine stack
    selected_stack: str = stack if stack else config.get("preferred", "gin-micro")
    if not stack:
        console.print(f"[yellow]No stack specified, using preferred: {selected_stack}[/yellow]")

    stacks = config.get("stacks", {})
    if selected_stack not in stacks:
        console.print(f"[red]Stack '{selected_stack}' not found. Available stacks:[/red]")
        for s in stacks:
            console.print(f"  - {s}")
        raise typer.Exit(code=1)

    # Check destination
    if destination.exists():
        if not force:
            console.print(f"[red]Destination '{destination}' exists. Use --force to overwrite.[/red]")
            raise typer.Exit(code=1)
        shutil.rmtree(destination)

    # Create project structure
    console.print(f"[bold green]Creating Go backend project '{name}' with stack '{selected_stack}'...[/bold green]")
    stack_config: dict[str, Any] = stacks[selected_stack]
    _create_go_project(name, destination, selected_stack, stack_config)
    console.print(f"[bold green]✨ Project created at {destination}[/bold green]")


def _create_go_project(name: str, destination: Path, stack: str, stack_config: dict[str, Any]) -> None:
    """Create Go project structure from template."""
    destination.mkdir(parents=True, exist_ok=True)

    # Determine template directory
    template_name = stack.replace("-", "_") if stack == "gin-micro" else stack.replace("-", "-")
    # Map stack names to template directories
    template_map = {
        "gin-micro": "gin-micro-template",
        "gin-basic": "gin-micro-template",  # Use same template, fewer features
        "grpc-micro": "gin-micro-template",  # Use same template as base
    }
    template_dir_name = template_map.get(stack, "gin-micro-template")
    template_dir = TEMPLATE_DIR / template_dir_name

    if not template_dir.exists():
        # Fallback to code generation if template doesn't exist
        _create_go_project_generated(name, destination, stack, stack_config)
        return

    # Copy template files
    _copy_template(template_dir, destination, name)


def _copy_template(template_dir: Path, destination: Path, project_name: str) -> None:
    """Copy template files to destination with variable substitution."""
    for item in template_dir.rglob("*"):
        if item.is_file():
            # Calculate relative path
            rel_path = item.relative_to(template_dir)
            dest_path = destination / rel_path

            # Create parent directories
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Read and process file content
            content = item.read_text(encoding="utf-8")
            # Replace placeholders
            content = content.replace("{{project_name}}", project_name)

            # Write to destination
            dest_path.write_text(content, encoding="utf-8")


def _create_go_project_generated(name: str, destination: Path, stack: str, stack_config: dict[str, Any]) -> None:
    """Create Go project structure using code generation (fallback)."""
    destination.mkdir(parents=True, exist_ok=True)

    # Create go.mod
    go_mod_content = _generate_go_mod(name, stack_config)
    (destination / "go.mod").write_text(go_mod_content, encoding="utf-8")

    # Create main.go
    main_content = _generate_main_go(name, stack)
    (destination / "main.go").write_text(main_content, encoding="utf-8")

    # Create directory structure
    dirs = [
        "cmd/api",
        "cmd/worker",
        "internal/handlers",
        "internal/services",
        "internal/models",
        "internal/repositories",
        "internal/middleware",
        "internal/config",
        "internal/utils",
        "pkg",
        "migrations",
        "configs",
        "scripts",
        "tests",
        "docs",
    ]
    for d in dirs:
        (destination / d).mkdir(parents=True, exist_ok=True)
        # Add .gitkeep
        (destination / d / ".gitkeep").touch()

    # Create config file
    config_content = _generate_config_yaml(name)
    (destination / "configs" / "config.yaml").write_text(config_content, encoding="utf-8")

    # Create README.md
    readme_content = _generate_readme(name, stack_config)
    (destination / "README.md").write_text(readme_content, encoding="utf-8")

    # Create .gitignore
    gitignore_content = _generate_gitignore()
    (destination / ".gitignore").write_text(gitignore_content, encoding="utf-8")

    # Create Makefile
    makefile_content = _generate_makefile(name)
    (destination / "Makefile").write_text(makefile_content, encoding="utf-8")


def _generate_go_mod(name: str, stack_config: dict[str, Any]) -> str:
    """Generate go.mod content."""
    tools = stack_config.get("tools", [])
    tool_names = [t.get("name", "") for t in tools]

    dependencies = []
    if "Gin" in tool_names:
        dependencies.append("\tgithub.com/gin-gonic/gin v1.10.0")
    if "Go Micro" in tool_names:
        dependencies.append("\tgithub.com/micro/go-micro/v3 v3.10.0")
    if "GORM" in tool_names:
        dependencies.append("\tgorm.io/gorm v1.25.10")
        dependencies.append("\tgorm.io/driver/mysql v1.5.0")
    if "go-redis" in tool_names:
        dependencies.append("\tgithub.com/redis/go-redis/v9 v9.5.0")
    if "Viper" in tool_names:
        dependencies.append("\tgithub.com/spf13/viper v1.19.0")
    if "JWT-Go" in tool_names:
        dependencies.append("\tgithub.com/golang-jwt/jwt/v5 v5.2.0")
    if "Zap" in tool_names:
        dependencies.append("\tgo.uber.org/zap v1.27.0")
    if "Swaggo" in tool_names:
        dependencies.append("\tgithub.com/swaggo/swag v1.16.2")
        dependencies.append("\tgithub.com/swaggo/gin-swagger v1.6.0")
    if "gRPC-Go" in tool_names:
        dependencies.append("\tgoogle.golang.org/grpc v1.62.0")
        dependencies.append("\tgoogle.golang.org/protobuf v1.33.0")

    deps_str = "\n".join(dependencies)
    return f"""module github.com/biucing/{name}

go 1.21

require (
{deps_str}
)
"""


def _generate_main_go(name: str, stack: str) -> str:
    """Generate main.go content."""
    if stack == "gin-micro":
        return f'''package main

import (
\t"log"
\t"os"

\t"github.com/gin-gonic/gin"
\t"github.com/spf13/viper"
\t"go.uber.org/zap"
)

func main() {{
\t// Initialize config
\tif err := initConfig(); err != nil {{
\t\tlog.Fatalf("Failed to load config: %v", err)
\t}}

\t// Initialize logger
\tlogger, _ := zap.NewProduction()
\tdefer logger.Sync()

\t// Initialize Gin router
\tgin.SetMode(viper.GetString("server.mode"))
\tr := gin.Default()

\t// Register routes
\tregisterRoutes(r)

\t// Start server
\tport := viper.GetString("server.port")
\tlogger.Info("Starting server", zap.String("port", port))
\tif err := r.Run(":" + port); err != nil {{
\t\tlog.Fatalf("Failed to start server: %v", err)
\t}}
}}

func initConfig() error {{
\tviper.SetConfigFile("configs/config.yaml")
\tviper.AutomaticEnv()
\treturn viper.ReadInConfig()
}}

func registerRoutes(r *gin.Engine) {{
\tr.GET("/health", func(c *gin.Context) {{
\t\tc.JSON(200, gin.H{{"status": "ok"}})
\t}})
}}
'''
    elif stack == "grpc-micro":
        return f'''package main

import (
\t"log"

\t"github.com/micro/go-micro/v3"
\t"go.uber.org/zap"
)

func main() {{
\t// Initialize logger
\tlogger, _ := zap.NewProduction()
\tdefer logger.Sync()

\t// Create service
\tservice := micro.NewService(
\t\tmicro.Name("github.com/biucing/{name}"),
\t\tmicro.Version("latest"),
\t)

\t// Initialize service
\tservice.Init()

\t// Register handler
\t// RegisterHandler(service.Server(), &Handler{{}})

\t// Run service
\tlogger.Info("Starting service")
\tif err := service.Run(); err != nil {{
\t\tlog.Fatalf("Failed to start service: %v", err)
\t}}
}}
'''
    else:  # gin-basic
        return f'''package main

import (
\t"log"

\t"github.com/gin-gonic/gin"
)

func main() {{
\tr := gin.Default()

\t// Register routes
\tr.GET("/health", func(c *gin.Context) {{
\t\tc.JSON(200, gin.H{{"status": "ok"}})
\t}})

\t// Start server
\tif err := r.Run(":8080"); err != nil {{
\t\tlog.Fatalf("Failed to start server: %v", err)
\t}}
}}
'''


def _generate_config_yaml(name: str) -> str:
    """Generate config.yaml content."""
    return f"""# Server configuration
server:
  port: "8080"
  mode: "debug"  # debug, release, test

# Database configuration
database:
  driver: "mysql"
  host: "localhost"
  port: "3306"
  user: "root"
  password: "password"
  dbname: "{name}"
  max_idle_conns: 10
  max_open_conns: 100

# Redis configuration
redis:
  addr: "localhost:6379"
  password: ""
  db: 0
  pool_size: 100

# JWT configuration
jwt:
  secret: "your-secret-key-change-in-production"
  expire_hours: 24

# Logging configuration
logging:
  level: "debug"  # debug, info, warn, error
  format: "json"  # json, console
"""


def _generate_readme(name: str, stack_config: dict[str, Any]) -> str:
    """Generate README.md content."""
    tools = stack_config.get("tools", [])
    tool_list = "\n".join([f"- {t.get('name')}: {t.get('url', '')}" for t in tools])

    return f"""# {name}

A Go backend service built with modern microservice architecture.

## Tech Stack

{tool_list}

## Project Structure

```
{name}/
├── cmd/                    # Application entry points
│   ├── api/               # API service
│   └── worker/            # Background worker
├── internal/              # Private application code
│   ├── handlers/          # HTTP handlers
│   ├── services/          # Business logic
│   ├── models/            # Data models
│   ├── repositories/      # Data access layer
│   ├── middleware/        # HTTP middleware
│   ├── config/            # Configuration
│   └── utils/             # Utility functions
├── pkg/                   # Public library code
├── migrations/            # Database migrations
├── configs/               # Configuration files
├── scripts/               # Utility scripts
├── tests/                 # Test files
└── docs/                  # API documentation
```

## Getting Started

### Prerequisites

- Go 1.21+
- MySQL (or your preferred database)
- Redis (if using caching)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd {name}

# Install dependencies
go mod download

# Run the application
go run main.go
```

### Configuration

Edit `configs/config.yaml` to configure the application.

### Running Tests

```bash
go test ./...
```

### Building

```bash
go build -o bin/{name} main.go
```

## API Documentation

After running the application, access Swagger UI at:
http://localhost:8080/swagger/index.html

## License

MIT
"""


def _generate_gitignore() -> str:
    """Generate .gitignore content."""
    return """# Binaries
*.exe
*.exe~
*.dll
*.so
*.dylib
bin/
dist/

# Test binary
*.test

# Output of the go coverage tool
*.out

# Dependency directories
vendor/

# Go workspace file
go.work

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Config overrides
configs/config.local.yaml

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
"""


def _generate_makefile(name: str) -> str:
    """Generate Makefile content."""
    return f"""# Makefile for {name}

.PHONY: build run test clean lint fmt deps docs

# Build the application
build:
\tgo build -o bin/{name} main.go

# Run the application
run:
\tgo run main.go

# Run tests
test:
\tgo test -v ./...

# Run tests with coverage
test-coverage:
\tgo test -cover -coverprofile=coverage.out ./...
\tgo tool cover -html=coverage.out -o coverage.html

# Clean build artifacts
clean:
\trm -rf bin/
\trm -f coverage.out coverage.html

# Lint the code
lint:
\tgolangci-lint run

# Format the code
fmt:
\tgo fmt ./...

# Install dependencies
deps:
\tgo mod download
\tgo mod tidy

# Generate API documentation
docs:
\tswag init -g main.go -o ./docs

# Build and run
dev: deps fmt build run
"""
