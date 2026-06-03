"""Command entry point for BiucingCLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from biucingcli.templates import load_template
from biucingcli.templates import load_templates
from biucingcli.templates import render_template
from biucingcli.templates import render_text
from biucingcli.templates import resolve_variables


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    parser = argparse.ArgumentParser(prog="biucing", description="Project scaffold generator.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List available templates.")

    info_parser = subparsers.add_parser("info", help="Show details about a template.")
    info_parser.add_argument("template", help="Template name.")

    create_parser = subparsers.add_parser("create", help="Create a new project from a template.")
    create_parser.add_argument("template", help="Template name.")
    create_parser.add_argument("project_name", help="Project directory name.")
    create_parser.add_argument("--output-dir", default=".", help="Base directory for generation.")
    create_parser.add_argument("--display-name", help="Display name for frontend projects.")
    create_parser.add_argument("--package-name", help="Package name for frontend projects.")
    create_parser.add_argument("--module-name", help="Go module name for web projects.")
    create_parser.add_argument("--service-name", help="Service name for web projects.")
    create_parser.add_argument("--http-port", help="HTTP port for web projects.")
    return parser


def format_template_summary() -> str:
    """Return a concise summary of available templates."""
    lines = ["Available templates:"]
    for definition in load_templates():
        lines.append(f"- {definition.name}: {definition.description}")
    return "\n".join(lines)


def format_template_info(template_name: str) -> str:
    """Return a detailed view of one template."""
    definition = load_template(template_name)
    lines = [
        f"Template: {definition.name}",
        f"Description: {definition.description}",
        f"Stack: {', '.join(definition.stack)}",
        "Variables:",
    ]
    for variable in definition.variables:
        required = "required" if variable.required else "optional"
        details = [required]
        if variable.default is not None:
            details.append(f"default={variable.default}")
        if variable.default_from is not None:
            details.append(f"default_from={variable.default_from}")
        lines.append(f"- {variable.name} ({', '.join(details)})")
    lines.append("Next steps:")
    for step in definition.next_steps:
        lines.append(f"- {step}")
    return "\n".join(lines)


def create_project(args: argparse.Namespace) -> str:
    """Generate a project and return the output message."""
    definition = load_template(args.template)
    values = resolve_variables(
        definition,
        {
            "project_name": args.project_name,
            "display_name": args.display_name or args.project_name.replace("-", " ").title(),
            "package_name": args.package_name or args.project_name,
            "module_name": args.module_name,
            "service_name": args.service_name,
            "http_port": args.http_port,
        },
    )

    target_dir = Path(args.output_dir).resolve() / args.project_name
    render_template(definition, values, target_dir)

    lines = [
        f"Created {definition.name} project: {args.project_name}",
        f"Location: {target_dir}",
        f"Stack: {', '.join(definition.stack)}",
        "Next steps:",
        f"  cd {args.project_name}",
    ]
    lines.extend(f"  {render_text(step, values)}" for step in definition.next_steps)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    """Run the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        print(format_template_summary())
        return

    if args.command == "list":
        print(format_template_summary())
        return

    if args.command == "info":
        print(format_template_info(args.template))
        return

    if args.command == "create":
        print(create_project(args))
        return


if __name__ == "__main__":
    main()
