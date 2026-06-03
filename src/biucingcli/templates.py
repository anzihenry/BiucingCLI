"""Template loading and rendering for BiucingCLI."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TemplateVariable:
    """A declared template variable."""

    name: str
    required: bool = False
    default: str | None = None
    default_from: str | None = None
    prompt: str | None = None


@dataclass(frozen=True)
class TemplateDefinition:
    """Template metadata and file locations."""

    name: str
    description: str
    stack: list[str]
    variables: list[TemplateVariable]
    next_steps: list[str]
    template_dir: Path


def project_root() -> Path:
    """Return the repository root."""
    return Path(__file__).resolve().parents[2]


def templates_root() -> Path:
    """Return the templates directory."""
    return project_root() / "templates"


def load_template(name: str) -> TemplateDefinition:
    """Load one template definition by name."""
    metadata_path = templates_root() / name / "template.json"
    if not metadata_path.exists():
        raise KeyError(f"Unknown template: {name}")

    with metadata_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    variables = [TemplateVariable(**variable) for variable in data["variables"]]
    return TemplateDefinition(
        name=data["name"],
        description=data["description"],
        stack=data["stack"],
        variables=variables,
        next_steps=data["next_steps"],
        template_dir=metadata_path.parent / "template",
    )


def load_templates() -> list[TemplateDefinition]:
    """Load every available template."""
    definitions: list[TemplateDefinition] = []
    for metadata_path in sorted(templates_root().glob("*/template.json")):
        definitions.append(load_template(metadata_path.parent.name))
    return definitions


def resolve_variables(
    definition: TemplateDefinition,
    provided: dict[str, str | None],
) -> dict[str, str]:
    """Resolve final template variables from provided values and defaults."""
    resolved: dict[str, str] = {}
    for variable in definition.variables:
        value = provided.get(variable.name)
        if value:
            resolved[variable.name] = value
            continue

        if variable.default is not None:
            resolved[variable.name] = variable.default
            continue

        if variable.default_from is not None and variable.default_from in resolved:
            resolved[variable.name] = resolved[variable.default_from]
            continue

        if variable.required:
            prompt = variable.prompt or f"{variable.name}: "
            answer = input(prompt).strip()
            if not answer:
                raise ValueError(f"Missing required value for {variable.name}")
            resolved[variable.name] = answer
            continue

    return resolved


def placeholder_map(values: dict[str, str]) -> dict[str, str]:
    """Map internal variable names to template placeholders."""
    return {
        "{{PROJECT_NAME}}": values.get("project_name", ""),
        "{{DISPLAY_NAME}}": values.get("display_name", ""),
        "{{PACKAGE_NAME}}": values.get("package_name", ""),
        "{{MODULE_NAME}}": values.get("module_name", ""),
        "{{SERVICE_NAME}}": values.get("service_name", ""),
        "{{HTTP_PORT}}": values.get("http_port", ""),
        "{{APPLE_PLATFORM}}": values.get("apple_platform", ""),
        "{{APPLE_PLATFORM_NAME}}": values.get("apple_platform_name", ""),
        "{{BUNDLE_IDENTIFIER}}": values.get("bundle_identifier", ""),
        "{{MINIMUM_OS_VERSION}}": values.get("minimum_os_version", ""),
        "{{DEVELOPMENT_TEAM}}": values.get("development_team", ""),
        "{{ORGANIZATION_NAME}}": values.get("organization_name", ""),
        "{{SWIFT_MODULE_NAME}}": values.get("swift_module_name", ""),
        "{{TUIST_DESTINATIONS}}": values.get("tuist_destinations", ""),
        "{{TUIST_DEPLOYMENT_TARGETS}}": values.get("tuist_deployment_targets", ""),
        "{{XCODEBUILD_DESTINATION}}": values.get("xcodebuild_destination", ""),
        "{{SWIFTPM_SUPPORTED_PLATFORM}}": values.get("swiftpm_supported_platform", ""),
    }


def render_text(text: str, values: dict[str, str]) -> str:
    """Replace placeholders in a text snippet."""
    content = text
    for placeholder, value in placeholder_map(values).items():
        content = content.replace(placeholder, value)
    return content


def render_template(
    definition: TemplateDefinition,
    values: dict[str, str],
    target_dir: Path,
) -> None:
    """Copy and render a template into the target directory."""
    if target_dir.exists():
        raise FileExistsError(f"Target directory already exists: {target_dir}")

    shutil.copytree(definition.template_dir, target_dir)

    for path in target_dir.rglob("*"):
        if not path.is_file():
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        path.write_text(render_text(content, values), encoding="utf-8")
