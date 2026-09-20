"""Command entry point for BiucingCLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from biucingcli import __version__
from biucingcli.catalog import load_template, load_templates
from biucingcli.errors import (
    BiucingError,
    InvalidTemplateError,
    GenerationConflictError,
    GenerationError,
    InputEndedError,
    MissingInputError,
    UnknownTemplateError,
)
from biucingcli.generation import (
    build_generation_plan, execute_generation_plan, validate_generation_definition,
    count_template_files as count_template_files,
    top_level_template_entries as top_level_template_entries,
    default_display_name as default_display_name,
    render_template as render_template,
)
from biucingcli.models import CreateRequest, GenerationPlan
from biucingcli.interaction import terminal_prompt
from biucingcli.validation import validate_templates
from biucingcli.template_rules.apple import (
    default_swift_module_name as default_swift_module_name,
    apple_platform_config as apple_platform_config,
    apple_platform_snippets as apple_platform_snippets,
)
from biucingcli.template_rules.android import default_kotlin_module_name as default_kotlin_module_name
from biucingcli.template_rules.microservice import microservice_dependency_config as microservice_dependency_config


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


JSON_SCHEMA_VERSION = 1


def output_metadata() -> dict[str, object]:
    """Version the JSON contract independently of the generator release."""
    return {"schema_version": JSON_SCHEMA_VERSION, "generator_version": __version__}


class CLIUsageError(ValueError):
    """Argument parsing failure handled by the common CLI error boundary."""


class CLIParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)

    def error(self, message):
        raise CLIUsageError(message)


def exit_with_error(parser, json_mode, code, message, status, details=None):
    """Emit exactly one diagnostic on stderr, leaving stdout for successful results."""
    if json_mode:
        error = {"code": code, "message": message}
        if details is not None:
            error["details"] = details
        diagnostic = json.dumps({**output_metadata(), "ok": False, "error": error})
    else:
        diagnostic = f"error: {message}"
    parser.exit(status, diagnostic + "\n")


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    parser = CLIParser(prog="biucing", description="Project scaffold generator.")
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
    create_parser.add_argument("--bundle-name", help="HarmonyOS bundle name.")
    create_parser.add_argument("--harmony-module-name", help="HarmonyOS module name.")
    create_parser.add_argument("--ability-name", help="HarmonyOS entry ability name.")
    create_parser.add_argument("--compatible-sdk-version", help="HarmonyOS compatible SDK version.")
    create_parser.add_argument("--target-sdk-version", help="HarmonyOS target SDK version.")
    create_parser.add_argument("--min-api-version", help="HarmonyOS minimum API version.")
    create_parser.add_argument("--harmony-version-code", help="HarmonyOS version code.")
    create_parser.add_argument("--harmony-version-name", help="HarmonyOS version name.")
    return parser


def format_template_summary() -> str:
    """Return a concise summary of available templates."""
    lines = ["Available templates:"]
    for definition in load_templates():
        lines.append(f"- {definition.name}: {definition.description}")
    return "\n".join(lines)


def format_template_summary_json() -> str:
    """Return a machine-readable template list."""
    payload = {**output_metadata(), "templates": [definition.to_dict() for definition in load_templates()]}
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
        f"Worktree support: {definition.worktree.support_level}",
        f"Worktree isolation: {', '.join(definition.worktree.isolation_dimensions)}",
        f"Stack: {', '.join(definition.stack)}",
        "Operating assumptions:",
    ]
    for assumption in definition.operating_assumptions:
        lines.append(f"- {assumption}")
    lines.append("Worktree diagnostics:")
    for diagnostic in definition.worktree.diagnostics:
        lines.append(f"- {diagnostic}")
    lines.append("Worktree cleanup:")
    for cleanup in definition.worktree.cleanup:
        lines.append(f"- {cleanup}")
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
    return json.dumps({**output_metadata(), **definition.to_dict()}, indent=2)


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
        **output_metadata(),
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
    }
    return json.dumps(payload, indent=2)


# Single mapping for existing convenience flags; new fields use --set.
CLI_VARIABLE_ARGUMENTS = {
    "display_name": "display_name",
    "package_name": "package_name",
    "module_name": "module_name",
    "service_name": "service_name",
    "http_port": "http_port",
    "worker_name": "worker_name",
    "run_mode": "run_mode",
    "tick_interval_seconds": "tick_interval_seconds",
    "shutdown_timeout_seconds": "shutdown_timeout_seconds",
    "grpc_port": "grpc_port",
    "proto_package": "proto_package",
    "dependency_store": "dependency_store",
    "otel_exporter_endpoint": "otel_exporter_endpoint",
    "apple_platform": "platform",
    "bundle_identifier": "bundle_identifier",
    "minimum_os_version": "minimum_os_version",
    "development_team": "development_team",
    "organization_name": "organization_name",
    "swift_module_name": "swift_module_name",
    "application_id": "application_id",
    "compile_sdk": "compile_sdk",
    "min_sdk": "min_sdk",
    "target_sdk": "target_sdk",
    "version_code": "version_code",
    "version_name": "version_name",
    "java_version": "java_version",
    "android_namespace": "android_namespace",
    "kotlin_module_name": "kotlin_module_name",
    "bundle_name": "bundle_name",
    "harmony_module_name": "harmony_module_name",
    "ability_name": "ability_name",
    "compatible_sdk_version": "compatible_sdk_version",
    "target_sdk_version": "target_sdk_version",
    "min_api_version": "min_api_version",
    "harmony_version_code": "harmony_version_code",
    "harmony_version_name": "harmony_version_name",
}


def build_create_plan(args: argparse.Namespace) -> GenerationPlan:
    definition = load_template(args.template)
    # Keep metadata errors ahead of --set parsing errors, as before.
    validate_generation_definition(definition)
    request = CreateRequest(
        template=args.template,
        project_name=args.project_name,
        output_dir=Path(args.output_dir),
        set_values=parse_set_values(args.set_values),
        explicit_values={key: getattr(args, attr) for key, attr in CLI_VARIABLE_ARGUMENTS.items()},
    )
    prompt = terminal_prompt if not (args.non_interactive or args.json) and sys.stdin.isatty() else None
    return build_generation_plan(request, definition=definition, prompt=prompt)


def build_create_context(args: argparse.Namespace) -> dict[str, object]:
    """Compatibility adapter; active preview/create paths use GenerationPlan."""
    return build_create_plan(args).to_context()


def create_manifest(context: GenerationPlan | dict[str, object], mode: str) -> dict[str, object]:
    """Build a machine-readable preview or generation result."""
    if isinstance(context, GenerationPlan):
        context = context.to_context()
    definition = context["definition"]
    assert hasattr(definition, "name")
    return {
        **output_metadata(),
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


def format_create_preview(context: GenerationPlan | dict[str, object], preview_mode: str) -> str:
    """Return a human-readable create preview."""
    if isinstance(context, GenerationPlan):
        context = context.to_context()
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


def format_create_success(context: GenerationPlan | dict[str, object]) -> str:
    """Return a human-readable create success summary."""
    if isinstance(context, GenerationPlan):
        context = context.to_context()
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
    context = build_create_plan(args)
    if args.json:
        return json.dumps(create_manifest(context, mode=preview_mode), indent=2)
    return format_create_preview(context, preview_mode)


def create_project_output(args: argparse.Namespace) -> str:
    """Create a project and return either text or JSON output."""
    context = build_create_plan(args)
    execute_generation_plan(context)
    if args.json:
        return json.dumps(create_manifest(context, mode="create"), indent=2)
    return format_create_success(context)


def main(argv: list[str] | None = None) -> None:
    """Run the CLI."""
    parser = build_parser()
    arguments = list(sys.argv[1:] if argv is None else argv)
    option_arguments = arguments[:arguments.index("--")] if "--" in arguments else arguments
    json_mode = "--json" in option_arguments

    try:
        args = parser.parse_args(arguments)
        if args.command is None:
            print(format_template_summary())
            return

        if args.command == "list":
            print(format_template_summary_json() if args.json else format_template_summary())
            return

        if args.command == "info":
            output = (
                format_template_info_json(args.template)
                if args.json
                else format_template_info(args.template)
            )
            print(output)
            return

        if args.command == "validate":
            errors = validate_templates()
            if errors and args.json:
                exit_with_error(parser, True, "validation_failed", "Template validation failed.",
                                1, details=errors)
            if args.json:
                print(format_validation_report_json(errors))
            else:
                print(format_validation_report(errors))
            if errors:
                parser.exit(1)
            return

        if args.command == "create":
            if args.dry_run or args.plan:
                preview_mode = "dry-run" if args.dry_run else "plan"
                print(preview_project(args, preview_mode))
            else:
                print(create_project_output(args))
            return
    except KeyboardInterrupt:
        exit_with_error(parser, json_mode, "cancelled", "Operation cancelled.", 130)
    except (InputEndedError, EOFError) as exc:
        exit_with_error(parser, json_mode, "input_ended", str(exc) or "Input ended.", 2)
    except (BiucingError, ValueError, OSError) as exc:
        categories = (
            (CLIUsageError, "usage_error", 2),
            (InvalidTemplateError, "invalid_template", 1),
            (UnknownTemplateError, "unknown_template", 2),
            (GenerationConflictError, "target_conflict", 2),
            (GenerationError, "generation_failed", 2),
            (MissingInputError, "missing_input", 2),
            (OSError, "io_error", 1),
        )
        code, status = next(((code, status) for kind, code, status in categories
                             if isinstance(exc, kind)), ("invalid_input", 2))
        exit_with_error(parser, json_mode, code, str(exc), status)


if __name__ == "__main__":
    main()
