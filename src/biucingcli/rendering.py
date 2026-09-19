"""Pure single-pass text rendering; no filesystem operations."""

from __future__ import annotations

import re

from biucingcli.escaping import CONTEXT_ESCAPERS, FREE_TEXT_KEYS


PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Z0-9_]+\}\}")
def supported_placeholders() -> set[str]:
    """Return every placeholder the renderer knows how to replace."""
    return set(placeholder_map({}).keys())


def placeholder_map(values: dict[str, str]) -> dict[str, str]:
    """Map internal variable names to template placeholders."""
    placeholders = {
        "{{PROJECT_NAME}}": values.get("project_name", ""),
        "{{DISPLAY_NAME}}": values.get("display_name", ""),
        "{{PACKAGE_NAME}}": values.get("package_name", ""),
        "{{MODULE_NAME}}": values.get("module_name", ""),
        "{{SERVICE_NAME}}": values.get("service_name", ""),
        "{{WORKER_NAME}}": values.get("worker_name", ""),
        "{{RUN_MODE}}": values.get("run_mode", ""),
        "{{TICK_INTERVAL_SECONDS}}": values.get("tick_interval_seconds", ""),
        "{{SHUTDOWN_TIMEOUT_SECONDS}}": values.get("shutdown_timeout_seconds", ""),
        "{{SERVICE_TYPE_NAME}}": values.get("service_type_name", ""),
        "{{HTTP_PORT}}": values.get("http_port", ""),
        "{{GRPC_PORT}}": values.get("grpc_port", ""),
        "{{PROTO_PACKAGE}}": values.get("proto_package", ""),
        "{{DEPENDENCY_STORE}}": values.get("dependency_store", ""),
        "{{DEPENDENCY_STORE_IMAGE}}": values.get("dependency_store_image", ""),
        "{{DEPENDENCY_STORE_PORT}}": values.get("dependency_store_port", ""),
        "{{DEPENDENCY_STORE_DSN}}": values.get("dependency_store_dsn", ""),
        "{{DEPENDENCY_STORE_CONTAINER_DSN}}": values.get("dependency_store_container_dsn", ""),
        "{{DEPENDENCY_STORE_ENV_BLOCK}}": values.get("dependency_store_env_block", ""),
        "{{OTEL_EXPORTER_ENDPOINT}}": values.get("otel_exporter_endpoint", ""),
        "{{APPLICATION_ID}}": values.get("application_id", ""),
        "{{ANDROID_NAMESPACE}}": values.get("android_namespace", ""),
        "{{COMPILE_SDK}}": values.get("compile_sdk", ""),
        "{{MIN_SDK}}": values.get("min_sdk", ""),
        "{{TARGET_SDK}}": values.get("target_sdk", ""),
        "{{VERSION_CODE}}": values.get("version_code", ""),
        "{{VERSION_NAME}}": values.get("version_name", ""),
        "{{JAVA_VERSION}}": values.get("java_version", ""),
        "{{KOTLIN_MODULE_NAME}}": values.get("kotlin_module_name", ""),
        "{{BUNDLE_NAME}}": values.get("bundle_name", ""),
        "{{HARMONY_MODULE_NAME}}": values.get("harmony_module_name", ""),
        "{{ABILITY_NAME}}": values.get("ability_name", ""),
        "{{COMPATIBLE_SDK_VERSION}}": values.get("compatible_sdk_version", ""),
        "{{TARGET_SDK_VERSION}}": values.get("target_sdk_version", ""),
        "{{MIN_API_VERSION}}": values.get("min_api_version", ""),
        "{{HARMONY_VERSION_CODE}}": values.get("harmony_version_code", ""),
        "{{HARMONY_VERSION_NAME}}": values.get("harmony_version_name", ""),
        "{{APPLE_PLATFORM}}": values.get("apple_platform", ""),
        "{{APPLE_PLATFORM_NAME}}": values.get("apple_platform_name", ""),
        "{{FASTLANE_PLATFORM}}": values.get("fastlane_platform", ""),
        "{{APP_STORE_PLATFORM}}": values.get("app_store_platform", ""),
        "{{BUNDLE_IDENTIFIER}}": values.get("bundle_identifier", ""),
        "{{MINIMUM_OS_VERSION}}": values.get("minimum_os_version", ""),
        "{{DEVELOPMENT_TEAM}}": values.get("development_team", ""),
        "{{ORGANIZATION_NAME}}": values.get("organization_name", ""),
        "{{SWIFT_MODULE_NAME}}": values.get("swift_module_name", ""),
        "{{TUIST_DESTINATIONS}}": values.get("tuist_destinations", ""),
        "{{TUIST_DEPLOYMENT_TARGETS}}": values.get("tuist_deployment_targets", ""),
        "{{XCODEBUILD_DESTINATION}}": values.get("xcodebuild_destination", ""),
        "{{SWIFTPM_SUPPORTED_PLATFORM}}": values.get("swiftpm_supported_platform", ""),
        "{{APPLE_SCENE_BODY}}": values.get("apple_scene_body", ""),
        "{{APPLE_HOME_BODY}}": values.get("apple_home_body", ""),
        "{{APPLE_PLATFORM_OUTPUT_NOTE}}": values.get("apple_platform_output_note", ""),
    }
    for key in FREE_TEXT_KEYS:
        for context, escape in CONTEXT_ESCAPERS.items():
            placeholders["{{" + key.upper() + "_" + context + "}}"] = escape(values.get(key, ""))
    return placeholders


def render_text(text: str, values: dict[str, str]) -> str:
    """Replace placeholders in a text snippet."""
    placeholders = placeholder_map(values)
    # Replace only tokens from the template, never tokens inside inserted data.
    return PLACEHOLDER_PATTERN.sub(lambda match: placeholders.get(match[0], match[0]), text)
