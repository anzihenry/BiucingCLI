"""Template loading and rendering for BiucingCLI."""

from __future__ import annotations

import json
import re
import stat
import shutil
from dataclasses import asdict
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

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class ResolvedVariable:
    """A resolved template variable plus its source."""

    name: str
    value: str
    source: str

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class TemplateMaturity:
    """User-facing maturity metadata for a template."""

    level: str
    summary: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class TemplateValidation:
    """User-facing validation metadata for a template."""

    status: str
    evidence: list[str]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class TemplateDefinition:
    """Template metadata and file locations."""

    name: str
    description: str
    stack: list[str]
    category: str
    tags: list[str]
    platforms: list[str]
    maturity: TemplateMaturity
    validation: TemplateValidation
    variables: list[TemplateVariable]
    next_steps: list[str]
    template_dir: Path

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "name": self.name,
            "description": self.description,
            "stack": self.stack,
            "category": self.category,
            "tags": self.tags,
            "platforms": self.platforms,
            "maturity": self.maturity.to_dict(),
            "validation": self.validation.to_dict(),
            "variables": [variable.to_dict() for variable in self.variables],
            "next_steps": self.next_steps,
        }


@dataclass(frozen=True)
class VariableResolutionResult:
    """Resolved template variables and missing required inputs."""

    values: dict[str, str]
    resolved_variables: list[ResolvedVariable]
    missing_required: list[str]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "values": self.values,
            "resolved_variables": [item.to_dict() for item in self.resolved_variables],
            "missing_required": self.missing_required,
        }


PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Z0-9_]+\}\}")


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
    maturity = TemplateMaturity(**data["maturity"])
    validation = TemplateValidation(**data["validation"])
    return TemplateDefinition(
        name=data["name"],
        description=data["description"],
        stack=data["stack"],
        category=data["category"],
        tags=data["tags"],
        platforms=data["platforms"],
        maturity=maturity,
        validation=validation,
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


def supported_placeholders() -> set[str]:
    """Return every placeholder the renderer knows how to replace."""
    return set(placeholder_map({}).keys())


def validate_template_definition(definition: TemplateDefinition) -> list[str]:
    """Return validation errors for one template definition."""
    errors: list[str] = []

    if definition.template_dir.name != "template":
        errors.append(f"{definition.name}: template_dir must end in /template")

    if not definition.template_dir.exists():
        errors.append(f"{definition.name}: template directory is missing")

    if not definition.category:
        errors.append(f"{definition.name}: category must not be empty")

    if not definition.stack:
        errors.append(f"{definition.name}: stack must contain at least one entry")

    if not definition.tags:
        errors.append(f"{definition.name}: tags must contain at least one entry")

    if not definition.platforms:
        errors.append(f"{definition.name}: platforms must contain at least one entry")

    if not definition.next_steps:
        errors.append(f"{definition.name}: next_steps must contain at least one entry")

    if not definition.maturity.level or not definition.maturity.summary:
        errors.append(f"{definition.name}: maturity.level and maturity.summary must be set")

    if not definition.validation.status:
        errors.append(f"{definition.name}: validation.status must not be empty")

    if not definition.validation.evidence:
        errors.append(f"{definition.name}: validation.evidence must contain at least one entry")

    variable_names = [variable.name for variable in definition.variables]
    duplicate_names = sorted({name for name in variable_names if variable_names.count(name) > 1})
    if duplicate_names:
        errors.append(
            f"{definition.name}: duplicate variable names: {', '.join(duplicate_names)}"
        )

    supported = supported_placeholders()
    for variable in definition.variables:
        placeholder = "{{" + variable.name.upper() + "}}"
        if placeholder not in supported:
            errors.append(
                f"{definition.name}: variable '{variable.name}' has no supported placeholder mapping"
            )
        if variable.default_from and variable.default_from not in variable_names:
            errors.append(
                f"{definition.name}: variable '{variable.name}' default_from unknown variable '{variable.default_from}'"
            )

    return errors


def validate_template_placeholders(definition: TemplateDefinition) -> list[str]:
    """Return placeholder validation errors for a template directory."""
    errors: list[str] = []
    supported = supported_placeholders()

    if not definition.template_dir.exists():
        return [f"{definition.name}: template directory is missing"]

    for path in definition.template_dir.rglob("*"):
        if not path.is_file():
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        placeholders = sorted(set(PLACEHOLDER_PATTERN.findall(content)))
        unsupported = [placeholder for placeholder in placeholders if placeholder not in supported]
        if unsupported:
            relative_path = path.relative_to(project_root()).as_posix()
            errors.append(
                f"{definition.name}: unsupported placeholder(s) in {relative_path}: {', '.join(unsupported)}"
            )

    for step in definition.next_steps:
        placeholders = sorted(set(PLACEHOLDER_PATTERN.findall(step)))
        unsupported = [placeholder for placeholder in placeholders if placeholder not in supported]
        if unsupported:
            errors.append(
                f"{definition.name}: unsupported placeholder(s) in next_steps: {', '.join(unsupported)}"
            )

    return errors


def validate_templates() -> list[str]:
    """Return every template validation error in the repository."""
    errors: list[str] = []
    definitions = load_templates()
    known_names = {definition.name for definition in definitions}

    for definition in definitions:
        errors.extend(validate_template_definition(definition))
        errors.extend(validate_template_placeholders(definition))

    for metadata_path in sorted(templates_root().glob("*/template.json")):
        folder_name = metadata_path.parent.name
        definition_name = json.loads(metadata_path.read_text(encoding="utf-8"))["name"]
        if definition_name != folder_name:
            errors.append(
                f"{folder_name}: template name '{definition_name}' must match folder name"
            )

    if not known_names:
        errors.append("no templates found under templates/")

    return errors


def resolve_variables(
    definition: TemplateDefinition,
    provided: dict[str, str | None],
    interactive: bool = True,
) -> dict[str, str]:
    """Resolve final template variables from provided values and defaults."""
    return resolve_variables_detailed(definition, provided, interactive=interactive).values


def resolve_variables_detailed(
    definition: TemplateDefinition,
    provided: dict[str, str | None],
    interactive: bool = True,
) -> VariableResolutionResult:
    """Resolve final template variables along with source metadata."""
    resolved: dict[str, str] = {}
    resolution_sources: dict[str, str] = {}
    missing_required: list[str] = []
    for variable in definition.variables:
        value = provided.get(variable.name)
        if value:
            resolved[variable.name] = value
            resolution_sources[variable.name] = "provided"
            continue

        if variable.default is not None:
            resolved[variable.name] = variable.default
            resolution_sources[variable.name] = "default"
            continue

        if variable.default_from is not None and variable.default_from in resolved:
            resolved[variable.name] = resolved[variable.default_from]
            resolution_sources[variable.name] = f"default_from:{variable.default_from}"
            continue

        if variable.required:
            if not interactive:
                missing_required.append(variable.name)
                continue
            prompt = variable.prompt or f"{variable.name}: "
            answer = input(prompt).strip()
            if not answer:
                raise ValueError(f"Missing required value for {variable.name}")
            resolved[variable.name] = answer
            resolution_sources[variable.name] = "prompted"

    if missing_required:
        missing_list = ", ".join(missing_required)
        raise ValueError(
            f"Missing required values in non-interactive mode: {missing_list}"
        )

    resolved_variables = [
        ResolvedVariable(
            name=variable.name,
            value=resolved[variable.name],
            source=resolution_sources[variable.name],
        )
        for variable in definition.variables
        if variable.name in resolved and variable.name in resolution_sources
    ]
    return VariableResolutionResult(
        values=resolved,
        resolved_variables=resolved_variables,
        missing_required=missing_required,
    )


def placeholder_map(values: dict[str, str]) -> dict[str, str]:
    """Map internal variable names to template placeholders."""
    return {
        "{{PROJECT_NAME}}": values.get("project_name", ""),
        "{{DISPLAY_NAME}}": values.get("display_name", ""),
        "{{PACKAGE_NAME}}": values.get("package_name", ""),
        "{{MODULE_NAME}}": values.get("module_name", ""),
        "{{SERVICE_NAME}}": values.get("service_name", ""),
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
        "{{APPLE_SCENE_BODY}}": values.get("apple_scene_body", ""),
        "{{APPLE_HOME_BODY}}": values.get("apple_home_body", ""),
        "{{APPLE_PLATFORM_OUTPUT_NOTE}}": values.get("apple_platform_output_note", ""),
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
        if path.name == "gradlew" or "scripts" in path.parts:
            current_mode = path.stat().st_mode
            path.chmod(current_mode | stat.S_IXUSR)
