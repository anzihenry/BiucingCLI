"""Command entry point for BiucingCLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from biucingcli import __version__, presentation
from biucingcli.presentation import (
    JSON_SCHEMA_VERSION as JSON_SCHEMA_VERSION,
    output_metadata as output_metadata,
    create_manifest as create_manifest,
    format_create_preview as format_create_preview,
    format_create_success as format_create_success,
    format_validation_report as format_validation_report,
    format_validation_report_json as format_validation_report_json,
)
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


class CLIUsageError(ValueError):
    """Argument parsing failure handled by the common CLI error boundary."""


class CLIParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)

    def error(self, message):
        raise CLIUsageError(message)


def exit_with_error(parser, json_mode, code, message, status, details=None):
    """Keep stream selection and exit status at the CLI boundary."""
    parser.exit(status, presentation.format_error(json_mode, code, message, details) + "\n")


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
    """Compatibility adapter retaining the original loading entrypoint."""
    return presentation.format_template_summary(load_templates())


def format_template_summary_json() -> str:
    return presentation.format_template_summary_json(load_templates())


def format_template_info(template_name: str) -> str:
    return presentation.format_template_info(load_template(template_name))


def format_template_info_json(template_name: str) -> str:
    return presentation.format_template_info_json(load_template(template_name))


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


def preview_project(args: argparse.Namespace, preview_mode: str) -> str:
    """Preview a project generation request."""
    context = build_create_plan(args)
    if args.json:
        return presentation.format_create_json(context, mode=preview_mode)
    return format_create_preview(context, preview_mode)


def create_project_output(args: argparse.Namespace) -> str:
    """Create a project and return either text or JSON output."""
    context = build_create_plan(args)
    execute_generation_plan(context)
    if args.json:
        return presentation.format_create_json(context, mode="create")
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
