"""Mobile toolchain subcommands."""

from __future__ import annotations

import typer
from rich.console import Console

from .common import get_domain_config, render_stack_table

app = typer.Typer(help="Curate mobile stacks and tooling.")


@app.command("list")
def list_stacks(
    ctx: typer.Context,
    stack: str | None = typer.Option(None, "--stack", "-s", help="Target a specific stack."),
) -> None:
    """List mobile stacks."""
    config = get_domain_config(ctx, "mobile")
    console: Console = ctx.obj["console"]
    render_stack_table(console, config.get("stacks", {}), stack=stack)


@app.command()
def suggest(
    ctx: typer.Context,
    stack: str | None = typer.Option(None, "--stack", "-s", help="Target a specific stack."),
) -> None:
    """Highlight recommended mobile stacks."""
    config = get_domain_config(ctx, "mobile")
    console: Console = ctx.obj["console"]
    render_stack_table(console, config.get("stacks", {}), stack=stack)
