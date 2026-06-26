"""Command entry point for BiucingCLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from biucingcli import __version__
from biucingcli.templates import load_template
from biucingcli.templates import load_templates
from biucingcli.templates import render_template
from biucingcli.templates import render_text
from biucingcli.templates import resolve_variables_detailed
from biucingcli.templates import validate_templates


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


def apple_platform_snippets(values: dict[str, str]) -> dict[str, str]:
    """Return platform-specific Apple template snippets using resolved values."""
    platform = values.get("apple_platform", "ios")
    display_name = values.get("display_name", "App")

    if platform == "macos":
        return {
            "apple_scene_body": "\n".join(
                [
                    f'        WindowGroup("{display_name}") {{',
                    "            HomeView()",
                    "        }",
                    "        .defaultSize(width: 1100, height: 720)",
                ]
            ),
            "apple_home_body": "\n".join(
                [
                    "    var body: some View {",
                    "        NavigationSplitView {",
                    '            List {',
                    '                Section("Workspace") {',
                    '                    Label("Overview", systemImage: "sidebar.left")',
                    '                    Label("Release Checklist", systemImage: "checkmark.circle")',
                    "                }",
                    "            }",
                    "            .navigationSplitViewColumnWidth(min: 220, ideal: 240)",
                    "        } detail: {",
                    "            ScrollView {",
                    "                VStack(alignment: .leading, spacing: 20) {",
                    "                    Text(viewModel.title)",
                    "                        .font(BiucingTheme.titleFont)",
                    "",
                    "                    Text(viewModel.subtitle)",
                    "                        .font(BiucingTheme.bodyFont)",
                    "                        .foregroundStyle(.secondary)",
                    "",
                    '                    GroupBox("Project Summary") {',
                    "                        VStack(alignment: .leading, spacing: 8) {",
                    "                            ForEach(viewModel.facts, id: \\.label) { fact in",
                    '                                Label("\\(fact.label): \\(fact.value)", systemImage: fact.systemImage)',
                    "                            }",
                    "                        }",
                    "                        .font(BiucingTheme.captionFont)",
                    "                    }",
                    "",
                    '                    GroupBox("Release Checklist") {',
                    "                        VStack(alignment: .leading, spacing: 8) {",
                    "                            ForEach(viewModel.releaseChecklist(), id: \\.self) { item in",
                    '                                Label(item, systemImage: "checkmark.circle")',
                    "                            }",
                    "                        }",
                    "                        .font(BiucingTheme.captionFont)",
                    "                    }",
                    "                }",
                    "                .frame(maxWidth: 680, alignment: .leading)",
                    "                .padding(24)",
                    "            }",
                    '            .navigationTitle("Overview")',
                    "        }",
                    "    }",
                ]
            ),
            "apple_platform_output_note": (
                "macOS starters use a split-view workspace with a fixed desktop window size."
            ),
        }

    if platform == "ios":
        return {
            "apple_scene_body": "\n".join(
                [
                    "        WindowGroup {",
                    "            HomeView()",
                    "        }",
                ]
            ),
            "apple_home_body": "\n".join(
                [
                    "    var body: some View {",
                    "        NavigationStack {",
                    "            List {",
                    '                Section("Project Summary") {',
                    "                    ForEach(viewModel.facts, id: \\.label) { fact in",
                    '                        Label("\\(fact.label): \\(fact.value)", systemImage: fact.systemImage)',
                    "                    }",
                    "                }",
                    "",
                    '                Section("Release Checklist") {',
                    "                    ForEach(viewModel.releaseChecklist(), id: \\.self) { item in",
                    '                        Label(item, systemImage: "checkmark.circle")',
                    "                    }",
                    "                }",
                    "            }",
                    "            .listStyle(.insetGrouped)",
                    '            .navigationTitle("Starter Overview")',
                    "        }",
                    "    }",
                ]
            ),
            "apple_platform_output_note": (
                "iOS starters use a stacked overview screen tuned for simulator-first mobile flows."
            ),
        }

    return {
        "apple_scene_body": "\n".join(
            [
                "        WindowGroup {",
                "            HomeView()",
                "        }",
            ]
        ),
        "apple_home_body": "\n".join(
            [
                "    var body: some View {",
                "        NavigationStack {",
                "            VStack(alignment: .leading, spacing: 16) {",
                "                Text(viewModel.title)",
                "                    .font(BiucingTheme.titleFont)",
                "",
                "                Text(viewModel.subtitle)",
                "                    .font(BiucingTheme.bodyFont)",
                "                    .foregroundStyle(.secondary)",
                "",
                "                VStack(alignment: .leading, spacing: 8) {",
                "                    ForEach(viewModel.facts, id: \\.label) { fact in",
                '                        Label("\\(fact.label): \\(fact.value)", systemImage: fact.systemImage)',
                "                    }",
                "                }",
                "                .font(BiucingTheme.captionFont)",
                "",
                "                VStack(alignment: .leading, spacing: 8) {",
                '                    Text("Release Checklist")',
                "                        .font(BiucingTheme.sectionTitleFont)",
                "",
                "                    ForEach(viewModel.releaseChecklist(), id: \\.self) { item in",
                '                        Label(item, systemImage: "checkmark.circle")',
                "                    }",
                "                }",
                "                .font(BiucingTheme.captionFont)",
                "            }",
                "            .padding(24)",
                '            .navigationTitle("Overview")',
                "        }",
                "    }",
            ]
        ),
        "apple_platform_output_note": (
            f"{values.get('apple_platform_name', 'Apple')} starters currently keep the shared overview layout."
        ),
    }


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


def parse_set_values(items: list[str]) -> dict[str, str]:
    """Parse repeated KEY=VALUE pairs from the CLI."""
    values: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid --set value '{item}'. Expected KEY=VALUE.")
        key, value = item.split("=", 1)
        normalized_key = key.strip().replace("-", "_")
        if not normalized_key:
            raise ValueError(f"Invalid --set value '{item}'. Expected KEY=VALUE.")
        values[normalized_key] = value
    return values


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    parser = argparse.ArgumentParser(prog="biucing", description="Project scaffold generator.")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the installed BiucingCLI version.",
    )
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List available templates.")
    list_parser.add_argument(
        "--json",
        action="store_true",
        help="Print template metadata as JSON.",
    )

    info_parser = subparsers.add_parser("info", help="Show details about a template.")
    info_parser.add_argument("template", help="Template name.")
    info_parser.add_argument(
        "--json",
        action="store_true",
        help="Print template metadata as JSON.",
    )

    validate_parser = subparsers.add_parser(
        "validate", help="Validate template metadata and placeholder consistency."
    )
    validate_parser.add_argument(
        "--json",
        action="store_true",
        help="Print validation results as JSON.",
    )

    create_parser = subparsers.add_parser("create", help="Create a new project from a template.")
    create_parser.add_argument("template", help="Template name.")
    create_parser.add_argument("project_name", help="Project directory name.")
    create_parser.add_argument("--output-dir", default=".", help="Base directory for generation.")
    create_parser.add_argument(
        "--set",
        dest="set_values",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Set any template variable via KEY=VALUE. Can be repeated.",
    )
    create_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Fail instead of prompting for missing required values.",
    )
    create_parser.add_argument(
        "--json",
        action="store_true",
        help="Print the create plan or result as JSON.",
    )
    create_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve values and preview the generation result without writing files.",
    )
    create_parser.add_argument(
        "--plan",
        action="store_true",
        help="Print a human-readable generation plan without writing files.",
    )
    create_parser.add_argument("--display-name", help="Display name for frontend projects.")
    create_parser.add_argument("--package-name", help="Package name for frontend projects.")
    create_parser.add_argument("--module-name", help="Go module name for web service projects.")
    create_parser.add_argument("--service-name", help="Service name for web service projects.")
    create_parser.add_argument("--http-port", help="HTTP port for web service projects.")
    create_parser.add_argument("--worker-name", help="Worker process name for worker projects.")
    create_parser.add_argument(
        "--run-mode",
        choices=["scheduled", "oneshot"],
        help="Worker execution mode for worker projects.",
    )
    create_parser.add_argument(
        "--tick-interval-seconds",
        help="Tick interval in seconds for scheduled worker projects.",
    )
    create_parser.add_argument(
        "--shutdown-timeout-seconds",
        help="Shutdown timeout in seconds for worker projects.",
    )
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


def format_template_summary_json() -> str:
    """Return a machine-readable template list."""
    payload = {"templates": [definition.to_dict() for definition in load_templates()]}
    return json.dumps(payload, indent=2)


def format_template_info(template_name: str) -> str:
    """Return a detailed view of one template."""
    definition = load_template(template_name)
    lines = [
        f"Template: {definition.name}",
        f"Description: {definition.description}",
        f"Category: {definition.category}",
        f"Platforms: {', '.join(definition.platforms)}",
        f"Tags: {', '.join(definition.tags)}",
        f"Workflow labels: {', '.join(definition.workflow_labels)}",
        f"Maturity: {definition.maturity.level} - {definition.maturity.summary}",
        f"Validation: {definition.validation.status}",
        f"Verification tier: {definition.validation.verification_tier}",
        f"Stack: {', '.join(definition.stack)}",
        "Operating assumptions:",
    ]
    for assumption in definition.operating_assumptions:
        lines.append(f"- {assumption}")
    lines.append("Variables:")
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


def format_template_info_json(template_name: str) -> str:
    """Return a machine-readable template detail payload."""
    definition = load_template(template_name)
    return json.dumps(definition.to_dict(), indent=2)


def format_validation_report(errors: list[str]) -> str:
    """Return a human-readable validation report."""
    if not errors:
        return "Template validation passed."

    lines = ["Template validation failed:"]
    lines.extend(f"- {error}" for error in errors)
    return "\n".join(lines)


def format_validation_report_json(errors: list[str]) -> str:
    """Return a machine-readable validation report."""
    payload = {
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
    }
    return json.dumps(payload, indent=2)


def count_template_files(template_dir: Path) -> int:
    """Return the number of files in a template directory."""
    return sum(1 for path in template_dir.rglob("*") if path.is_file())


def top_level_template_entries(template_dir: Path) -> list[str]:
    """Return top-level template entries for preview and manifest output."""
    return sorted(path.name for path in template_dir.iterdir())


def build_create_context(args: argparse.Namespace) -> dict[str, object]:
    """Resolve a create request into a reusable context."""
    definition = load_template(args.template)
    set_values = parse_set_values(args.set_values)
    allowed_keys = {variable.name for variable in definition.variables}
    unknown_keys = sorted(key for key in set_values if key not in allowed_keys)
    if unknown_keys:
        unknown_list = ", ".join(unknown_keys)
        raise ValueError(f"Unknown template variable(s) for {args.template}: {unknown_list}")

    requested_service_name = (
        args.service_name or set_values.get("service_name") or args.project_name
    )
    requested_dependency_store = args.dependency_store or set_values.get("dependency_store")
    microservice_values = (
        microservice_dependency_config(requested_dependency_store, requested_service_name)
        if args.template == "microservice"
        else {}
    )
    requested_platform = args.platform or set_values.get("apple_platform")
    requested_minimum_os_version = args.minimum_os_version or set_values.get("minimum_os_version")
    apple_values = (
        apple_platform_config(requested_platform, requested_minimum_os_version)
        if args.template == "apple"
        else {}
    )
    provided_values: dict[str, str | None] = dict(set_values)
    provided_values["project_name"] = args.project_name

    if args.display_name is not None:
        provided_values["display_name"] = args.display_name
    elif "display_name" not in provided_values:
        provided_values["display_name"] = default_display_name(args.project_name)

    if args.package_name is not None:
        provided_values["package_name"] = args.package_name

    explicit_values = {
        "module_name": args.module_name,
        "service_name": args.service_name,
        "http_port": args.http_port,
        "worker_name": args.worker_name,
        "run_mode": args.run_mode,
        "tick_interval_seconds": args.tick_interval_seconds,
        "shutdown_timeout_seconds": args.shutdown_timeout_seconds,
        "grpc_port": args.grpc_port,
        "proto_package": args.proto_package,
        "dependency_store": args.dependency_store,
        "otel_exporter_endpoint": args.otel_exporter_endpoint,
        "apple_platform": requested_platform,
        "apple_platform_name": apple_values.get("apple_platform_name"),
        "bundle_identifier": args.bundle_identifier,
        "minimum_os_version": requested_minimum_os_version,
        "development_team": args.development_team,
        "organization_name": args.organization_name,
        "application_id": args.application_id,
        "compile_sdk": args.compile_sdk,
        "min_sdk": args.min_sdk,
        "target_sdk": args.target_sdk,
        "version_code": args.version_code,
        "version_name": args.version_name,
        "java_version": args.java_version,
        "android_namespace": args.android_namespace,
        "kotlin_module_name": args.kotlin_module_name,
        "swift_module_name": args.swift_module_name,
    }
    for key, value in explicit_values.items():
        if value is not None:
            provided_values[key] = value

    resolution_result = resolve_variables_detailed(
        definition,
        provided_values,
        interactive=not args.non_interactive,
    )
    values = dict(resolution_result.values)
    derived_values: dict[str, str] = {}
    if args.template == "microservice":
        derived_values["service_type_name"] = default_swift_module_name(args.project_name)
    if args.template == "apple":
        derived_values["swift_module_name"] = values.get("swift_module_name") or default_swift_module_name(
            args.project_name
        )
    if args.template == "android":
        derived_values["kotlin_module_name"] = values.get("kotlin_module_name") or default_kotlin_module_name(
            args.project_name
        )
    values.update(
        derived_values
    )
    if args.template == "apple":
        values.update(apple_platform_snippets(values))
    values.update({key: value for key, value in apple_values.items() if value is not None})
    values.update({key: value for key, value in microservice_values.items() if value is not None})

    target_dir = Path(args.output_dir).resolve() / args.project_name
    rendered_next_steps = [render_text(step, values) for step in definition.next_steps]
    system_derived_values = {
        key: values[key]
        for key in sorted(
            {
                *derived_values.keys(),
                *apple_values.keys(),
                *microservice_values.keys(),
            }
        )
        if key in values
    }
    return {
        "definition": definition,
        "project_name": args.project_name,
        "target_dir": target_dir,
        "values": values,
        "resolved_variables": [item.to_dict() for item in resolution_result.resolved_variables],
        "derived_values": system_derived_values,
        "rendered_next_steps": rendered_next_steps,
        "template_file_count": count_template_files(definition.template_dir),
        "template_top_level_entries": top_level_template_entries(definition.template_dir),
    }


def create_manifest(context: dict[str, object], mode: str) -> dict[str, object]:
    """Build a machine-readable preview or generation result."""
    definition = context["definition"]
    assert hasattr(definition, "name")
    return {
        "operation": mode,
        "template": {
            "name": definition.name,
            "description": definition.description,
            "category": definition.category,
            "stack": definition.stack,
            "platforms": definition.platforms,
        },
        "project_name": context["project_name"],
        "output_path": str(context["target_dir"]),
        "target_exists": Path(context["target_dir"]).exists(),
        "resolved_variables": context["resolved_variables"],
        "derived_values": context["derived_values"],
        "next_steps": context["rendered_next_steps"],
        "template_file_count": context["template_file_count"],
        "template_top_level_entries": context["template_top_level_entries"],
    }


def format_create_preview(context: dict[str, object], preview_mode: str) -> str:
    """Return a human-readable create preview."""
    definition = context["definition"]
    target_dir = Path(context["target_dir"])
    lines = [
        f"Create preview ({preview_mode}) for {definition.name}: {context['project_name']}",
        f"Location: {target_dir}",
        f"Target exists: {'yes' if target_dir.exists() else 'no'}",
        f"Stack: {', '.join(definition.stack)}",
        "Resolved variables:",
    ]
    for item in context["resolved_variables"]:
        lines.append(f"  - {item['name']} [{item['source']}]: {item['value']}")
    if context["derived_values"]:
        lines.append("Derived values:")
        for key, value in context["derived_values"].items():
            lines.append(f"  - {key}: {value}")
    lines.extend(
        [
            f"Template file count: {context['template_file_count']}",
            "Top-level template entries:",
        ]
    )
    lines.extend(f"  - {entry}" for entry in context["template_top_level_entries"])
    lines.extend(
        [
            "Next steps:",
            f"  cd {context['project_name']}",
        ]
    )
    lines.extend(f"  {step}" for step in context["rendered_next_steps"])
    lines.append("No files were written.")
    return "\n".join(lines)


def format_create_success(context: dict[str, object]) -> str:
    """Return a human-readable create success summary."""
    definition = context["definition"]
    target_dir = Path(context["target_dir"])
    lines = [
        f"Created {definition.name} project: {context['project_name']}",
        f"Location: {target_dir}",
        f"Stack: {', '.join(definition.stack)}",
        "Resolved variables:",
    ]
    for item in context["resolved_variables"]:
        lines.append(f"  - {item['name']} [{item['source']}]: {item['value']}")
    lines.extend(
        [
            f"Template file count: {context['template_file_count']}",
            "Next steps:",
            f"  cd {context['project_name']}",
        ]
    )
    lines.extend(f"  {step}" for step in context["rendered_next_steps"])
    return "\n".join(lines)


def preview_project(args: argparse.Namespace, preview_mode: str) -> str:
    """Preview a project generation request."""
    context = build_create_context(args)
    if args.json:
        return json.dumps(create_manifest(context, mode=preview_mode), indent=2)
    return format_create_preview(context, preview_mode)


def create_project_output(args: argparse.Namespace) -> str:
    """Create a project and return either text or JSON output."""
    context = build_create_context(args)
    render_template(
        context["definition"],
        context["values"],
        context["target_dir"],
    )
    if args.json:
        return json.dumps(create_manifest(context, mode="create"), indent=2)
    return format_create_success(context)


def main(argv: list[str] | None = None) -> None:
    """Run the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        print(format_template_summary())
        return

    if args.command == "list":
        print(format_template_summary_json() if args.json else format_template_summary())
        return

    if args.command == "info":
        print(format_template_info_json(args.template) if args.json else format_template_info(args.template))
        return

    if args.command == "validate":
        errors = validate_templates()
        if args.json:
            print(format_validation_report_json(errors))
        else:
            print(format_validation_report(errors))
        if errors:
            parser.exit(1)
        return

    if args.command == "create":
        try:
            if args.dry_run or args.plan:
                preview_mode = "dry-run" if args.dry_run else "plan"
                print(preview_project(args, preview_mode))
            else:
                print(create_project_output(args))
        except ValueError as exc:
            parser.exit(2, f"error: {exc}\n")
        return


if __name__ == "__main__":
    main()
