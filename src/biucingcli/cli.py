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


def default_kotlin_module_name(project_name: str) -> str:
    """Return a Kotlin-safe module name derived from a directory name."""
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
            "minimum_os_version": "26.0",
            "tuist_destinations": ".iOS",
            "tuist_deployment_targets": '.iOS("{{MINIMUM_OS_VERSION}}")',
            "xcodebuild_destination": "generic/platform=iOS Simulator",
            "swiftpm_supported_platform": '.iOS("{{MINIMUM_OS_VERSION}}")',
        },
        "macos": {
            "apple_platform": "macos",
            "apple_platform_name": "macOS",
            "minimum_os_version": "26.0",
            "tuist_destinations": ".macOS",
            "tuist_deployment_targets": '.macOS("{{MINIMUM_OS_VERSION}}")',
            "xcodebuild_destination": "platform=macOS",
            "swiftpm_supported_platform": '.macOS("{{MINIMUM_OS_VERSION}}")',
        },
        "watchos": {
            "apple_platform": "watchos",
            "apple_platform_name": "watchOS",
            "minimum_os_version": "26.0",
            "tuist_destinations": ".watchOS",
            "tuist_deployment_targets": '.watchOS("{{MINIMUM_OS_VERSION}}")',
            "xcodebuild_destination": "generic/platform=watchOS Simulator",
            "swiftpm_supported_platform": '.watchOS("{{MINIMUM_OS_VERSION}}")',
        },
        "tvos": {
            "apple_platform": "tvos",
            "apple_platform_name": "tvOS",
            "minimum_os_version": "26.0",
            "tuist_destinations": ".tvOS",
            "tuist_deployment_targets": '.tvOS("{{MINIMUM_OS_VERSION}}")',
            "xcodebuild_destination": "generic/platform=tvOS Simulator",
            "swiftpm_supported_platform": '.tvOS("{{MINIMUM_OS_VERSION}}")',
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
    resolved["swiftpm_supported_platform"] = resolved["swiftpm_supported_platform"].replace(
        "{{MINIMUM_OS_VERSION}}", resolved["minimum_os_version"]
    )
    return resolved


def microservice_dependency_config(store: str | None, service_name: str) -> dict[str, str]:
    """Return derived local dependency values for the microservice template."""
    selected = (store or "postgres").lower()
    supported = {
        "postgres": {
            "dependency_store": "postgres",
            "dependency_store_image": "postgres:16-alpine",
            "dependency_store_port": "5432",
            "dependency_store_dsn": f"postgres://postgres:postgres@localhost:5432/{service_name}?sslmode=disable",
            "dependency_store_container_dsn": (
                f"postgres://postgres:postgres@postgres:5432/{service_name}?sslmode=disable"
            ),
            "dependency_store_env_block": "\n".join(
                [
                    "    environment:",
                    f"      POSTGRES_DB: {service_name}",
                    "      POSTGRES_USER: postgres",
                    "      POSTGRES_PASSWORD: postgres",
                ]
            ),
        },
        "redis": {
            "dependency_store": "redis",
            "dependency_store_image": "redis:7-alpine",
            "dependency_store_port": "6379",
            "dependency_store_dsn": "redis://localhost:6379/0",
            "dependency_store_container_dsn": "redis://redis:6379/0",
            "dependency_store_env_block": "",
        },
    }
    if selected not in supported:
        raise ValueError("Unsupported dependency store. Expected one of: postgres, redis")
    return dict(supported[selected])


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
    create_parser.add_argument("--module-name", help="Go module name for web service projects.")
    create_parser.add_argument("--service-name", help="Service name for web service projects.")
    create_parser.add_argument("--http-port", help="HTTP port for web service projects.")
    create_parser.add_argument("--grpc-port", help="gRPC port for microservice projects.")
    create_parser.add_argument("--proto-package", help="Proto package for microservice projects.")
    create_parser.add_argument(
        "--dependency-store",
        choices=["postgres", "redis"],
        help="Local dependency store for microservice projects.",
    )
    create_parser.add_argument(
        "--otel-exporter-endpoint",
        help="OpenTelemetry exporter endpoint for microservice projects.",
    )
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
    create_parser.add_argument("--application-id", help="Android application ID.")
    create_parser.add_argument("--compile-sdk", help="Android compile SDK version.")
    create_parser.add_argument("--min-sdk", help="Android minimum SDK version.")
    create_parser.add_argument("--target-sdk", help="Android target SDK version.")
    create_parser.add_argument("--version-code", help="Android version code.")
    create_parser.add_argument("--version-name", help="Android version name.")
    create_parser.add_argument("--java-version", help="Java version for Android builds.")
    create_parser.add_argument("--android-namespace", help="Android namespace.")
    create_parser.add_argument("--kotlin-module-name", help="Kotlin module name for Android code.")
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
    microservice_values = (
        microservice_dependency_config(args.dependency_store, args.service_name or args.project_name)
        if args.template == "microservice"
        else {}
    )
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
            "package_name": args.package_name
            or (args.project_name if args.template == "frontend" else None),
            "module_name": args.module_name,
            "service_name": args.service_name,
            "service_type_name": default_swift_module_name(args.project_name),
            "http_port": args.http_port,
            "grpc_port": args.grpc_port,
            "proto_package": args.proto_package,
            "dependency_store": microservice_values.get("dependency_store"),
            "dependency_store_image": microservice_values.get("dependency_store_image"),
            "dependency_store_port": microservice_values.get("dependency_store_port"),
            "dependency_store_dsn": microservice_values.get("dependency_store_dsn"),
            "dependency_store_container_dsn": microservice_values.get(
                "dependency_store_container_dsn"
            ),
            "dependency_store_env_block": microservice_values.get("dependency_store_env_block"),
            "otel_exporter_endpoint": args.otel_exporter_endpoint
            or "http://localhost:4318",
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
            "swiftpm_supported_platform": apple_values.get("swiftpm_supported_platform"),
            "application_id": args.application_id,
            "compile_sdk": args.compile_sdk,
            "min_sdk": args.min_sdk,
            "target_sdk": args.target_sdk,
            "version_code": args.version_code,
            "version_name": args.version_name,
            "java_version": args.java_version,
            "android_namespace": args.android_namespace,
            "kotlin_module_name": args.kotlin_module_name
            or default_kotlin_module_name(args.project_name),
        },
    )
    values.update(
        {
            "service_type_name": default_swift_module_name(args.project_name),
        }
    )
    values.update({key: value for key, value in apple_values.items() if value is not None})
    values.update({key: value for key, value in microservice_values.items() if value is not None})

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
