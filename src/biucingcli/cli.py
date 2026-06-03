"""Command entry point for BiucingCLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from biucingcli.templates import load_template
from biucingcli.templates import load_templates
from biucingcli.templates import render_template
from biucingcli.templates import render_text
from biucingcli.templates import resolve_variables


def default_display_name(project_name: str) -> str:
    """Return a human-friendly display name from a directory name."""
    return project_name.replace("-", " ").replace("_", " ").title()


def default_swift_module_name(project_name: str) -> str:
    """Return a Swift-safe module name derived from a directory name."""
    parts = [part for part in project_name.replace("_", "-").split("-") if part]
    if not parts:
        return "App"
    return "".join(part[:1].upper() + part[1:] for part in parts)


def apple_platform_config(platform: str | None, minimum_os_version: str | None) -> dict[str, str]:
    """Return derived Apple platform values for template rendering."""
    requested = (platform or "ios").lower()
    supported = {
        "ios": {
            "apple_platform": "ios",
            "apple_platform_name": "iOS",
            "minimum_os_version": "17.0",
            "tuist_destinations": ".iOS",
            "tuist_deployment_targets": '.iOS("{{MINIMUM_OS_VERSION}}")',
            "xcodebuild_destination": "platform=iOS Simulator,name=iPhone 16",
        },
        "macos": {
            "apple_platform": "macos",
            "apple_platform_name": "macOS",
            "minimum_os_version": "14.0",
            "tuist_destinations": ".macOS",
            "tuist_deployment_targets": '.macOS("{{MINIMUM_OS_VERSION}}")',
            "xcodebuild_destination": "platform=macOS",
        },
        "watchos": {
            "apple_platform": "watchos",
            "apple_platform_name": "watchOS",
            "minimum_os_version": "10.0",
            "tuist_destinations": ".watchOS",
            "tuist_deployment_targets": '.watchOS("{{MINIMUM_OS_VERSION}}")',
            "xcodebuild_destination": "platform=watchOS Simulator,name=Apple Watch Series 10 (46mm)",
        },
        "tvos": {
            "apple_platform": "tvos",
            "apple_platform_name": "tvOS",
            "minimum_os_version": "17.0",
            "tuist_destinations": ".tvOS",
            "tuist_deployment_targets": '.tvOS("{{MINIMUM_OS_VERSION}}")',
            "xcodebuild_destination": "platform=tvOS Simulator,name=Apple TV",
        },
    }
    if requested not in supported:
        raise ValueError(
            "Unsupported Apple platform. Expected one of: ios, macos, watchos, tvos"
        )

    resolved = dict(supported[requested])
    resolved["minimum_os_version"] = minimum_os_version or resolved["minimum_os_version"]
    resolved["tuist_deployment_targets"] = resolved["tuist_deployment_targets"].replace(
        "{{MINIMUM_OS_VERSION}}", resolved["minimum_os_version"]
    )
    return resolved


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
    create_parser.add_argument(
        "--platform",
        choices=["ios", "macos", "watchos", "tvos"],
        help="Apple platform for the apple template.",
    )
    create_parser.add_argument("--bundle-identifier", help="Apple app bundle identifier.")
    create_parser.add_argument("--minimum-os-version", help="Minimum Apple OS version.")
    create_parser.add_argument("--development-team", help="Apple development team ID.")
    create_parser.add_argument("--organization-name", help="Organization or team name.")
    create_parser.add_argument("--swift-module-name", help="Swift module name for app targets.")
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
    apple_values = (
        apple_platform_config(args.platform, args.minimum_os_version)
        if args.template == "apple"
        else {}
    )
    values = resolve_variables(
        definition,
        {
            "project_name": args.project_name,
            "display_name": args.display_name or default_display_name(args.project_name),
            "package_name": args.package_name or args.project_name,
            "module_name": args.module_name,
            "service_name": args.service_name,
            "http_port": args.http_port,
            "apple_platform": apple_values.get("apple_platform"),
            "apple_platform_name": apple_values.get("apple_platform_name"),
            "bundle_identifier": args.bundle_identifier,
            "minimum_os_version": apple_values.get("minimum_os_version"),
            "development_team": args.development_team,
            "organization_name": args.organization_name,
            "swift_module_name": args.swift_module_name
            or default_swift_module_name(args.project_name),
            "tuist_destinations": apple_values.get("tuist_destinations"),
            "tuist_deployment_targets": apple_values.get("tuist_deployment_targets"),
            "xcodebuild_destination": apple_values.get("xcodebuild_destination"),
        },
    )
    values.update({key: value for key, value in apple_values.items() if value is not None})

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
