"""Main Typer application entrypoint."""

from __future__ import annotations

from pathlib import Path

import typer
import yaml  # type: ignore[import-untyped]
from rich.console import Console
from rich.pretty import Pretty
from rich.syntax import Syntax

from .commands import backend, desktop, devops, frontend, mobile, testing
from .config import DEFAULT_CONFIG_PATH, build_config

console = Console()
app = typer.Typer(help="BiucingCLI • Full-stack toolchain assistant")
config_app = typer.Typer(help="Configuration management commands.")


CONFIG_OPTION = typer.Option(
    None,
    "--config",
    "-c",
    help=f"Override configuration file path (default: {DEFAULT_CONFIG_PATH}).",
)

DESTINATION_ARGUMENT = typer.Argument(
    ..., help="Where to export the merged configuration."
)

FORCE_OPTION = typer.Option(
    False,
    "--force",
    "-f",
    help="Overwrite if the destination exists.",
)


def _resolve_config_path(path: Path | None) -> Path | None:
    if path is None:
        return None
    if path.exists():
        return path
    raise typer.BadParameter(f"Config path does not exist: {path}")


@app.callback()
def main(
    ctx: typer.Context,
    config: Path | None = CONFIG_OPTION,
) -> None:
    """Load configuration before executing subcommands."""
    override_path = _resolve_config_path(config)
    ctx.obj = {
        "config": build_config(override_path),
        "console": console,
        "config_path": override_path or DEFAULT_CONFIG_PATH,
    }


default_domain_apps = {
    "frontend": frontend.app,
    "mobile": mobile.app,
    "desktop": desktop.app,
    "backend": backend.app,
    "testing": testing.app,
    "devops": devops.app,
}

for name, sub_app in default_domain_apps.items():
    app.add_typer(sub_app, name=name)


@app.command()
def domains() -> None:
    """List available toolchain domains."""
    console.print("[bold]Available domains:[/bold]\n" + "\n".join(default_domain_apps))


@config_app.command("show")
def show_config(ctx: typer.Context) -> None:
    """Display the merged configuration used by the CLI."""
    config = ctx.ensure_object(dict)["config"]
    yaml_dump = yaml.safe_dump(config, sort_keys=True)
    syntax = Syntax(yaml_dump, "yaml", theme="monokai", line_numbers=False)
    console.print(syntax)


@config_app.command("path")
def config_path(ctx: typer.Context) -> None:
    """Print the configuration file path in use."""
    console.print(Pretty(ctx.ensure_object(dict)["config_path"]))


@config_app.command("export")
def export_config(
    ctx: typer.Context,
    destination: Path = DESTINATION_ARGUMENT,
    force: bool = FORCE_OPTION,
) -> None:
    """Write the active configuration to the given destination."""
    if destination.exists() and not force:
        raise typer.BadParameter(
            f"Destination exists: {destination}. Use --force to overwrite."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    config = ctx.ensure_object(dict)["config"]
    with destination.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(config, handle, sort_keys=True)
    console.print(f"[green]Exported configuration to {destination}[/green]")


app.add_typer(config_app, name="configure")

__all__ = ["app"]
