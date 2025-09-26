"""Shared utilities for domain commands."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

import typer
from rich.console import Console
from rich.table import Table


def get_domain_config(ctx: typer.Context, domain: str) -> dict[str, Any]:
    state = cast(dict[str, Any], ctx.ensure_object(dict))
    try:
        config = cast(dict[str, Any], state["config"])
        return cast(dict[str, Any], config[domain])
    except KeyError as err:  # pragma: no cover - defensive branch
        raise typer.BadParameter(f"Unknown domain '{domain}'.") from err


def render_stack_table(console: Console, stacks: dict[str, Any], *, stack: str | None = None) -> None:
    if stack:
        stacks = {stack: stacks[stack]} if stack in stacks else {}
        if not stacks:
            raise typer.BadParameter(f"Stack '{stack}' not found.")

    table = Table(title="Stacks", show_lines=True)
    table.add_column("Stack", style="bold cyan")
    table.add_column("Description", style="green")
    table.add_column("Tools", style="magenta")

    for name, payload in stacks.items():
        tools = _join_tool_lines(payload.get("tools", []))
        table.add_row(name, payload.get("description", ""), tools)

    console.print(table)


def _join_tool_lines(tools: Iterable[dict[str, Any]]) -> str:
    result = []
    for tool in tools:
        label = tool.get("name", "unknown")
        category = tool.get("category", "")
        url = tool.get("url", "")
        result.append(f"{label} [{category}]\n{url}")
    return "\n\n".join(result) if result else "No tools configured"
