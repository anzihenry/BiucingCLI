"""Template loading and rendering for BiucingCLI."""

from __future__ import annotations

import json
import re
import stat
import shutil
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class TemplateVariable:
    """A declared template variable."""

    name: str
    required: bool = False
    default: str | None = None
    default_from: str | None = None
    prompt: str | None = None
    validator: str = "text"
    choices: list[str] = field(default_factory=list)
    minimum: int | None = None
    maximum: int | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "name": self.name,
            "required": self.required,
            "default": self.default,
            "default_from": self.default_from,
            "prompt": self.prompt,
        }


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
    verification_tier: str
    evidence: list[str]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class TemplateWorktree:
    """Worktree isolation metadata for a template."""

    support_level: str = ""
    isolation_dimensions: list[str] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)
    cleanup: list[str] = field(default_factory=list)

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
    worktree: TemplateWorktree
    operating_assumptions: list[str]
    workflow_labels: list[str]
    commands: dict[str, str]
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
            "worktree": self.worktree.to_dict(),
            "operating_assumptions": self.operating_assumptions,
            "workflow_labels": self.workflow_labels,
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
ALLOWED_VERIFICATION_TIERS = {
    "generated-project",
    "real-build",
}
ALLOWED_WORKFLOW_LABELS = {
    "bootstrap",
    "doctor",
    "dev",
    "test",
    "verify",
    "build",
    "runtime",
    "generate",
    "format",
    "release",
    "ui-test",
    "open",
    "lint",
}
ALLOWED_WORKTREE_SUPPORT_LEVELS = {
    "planned",
    "partial",
    "worktree-ready",
}
ALLOWED_WORKTREE_ISOLATION_DIMENSIONS = {
    "runtime-names",
    "ports",
    "dependency-stores",
    "caches",
    "generated-output",
    "local-config",
    "installed-app-identity",
    "cleanup",
    "diagnostics",
}
ALLOWED_VARIABLE_VALIDATORS = {
    "apple-version",
    "bundle-identifier",
    "choice",
    "display-name",
    "go-module",
    "harmony-sdk-version",
    "identifier",
    "java-package",
    "npm-package",
    "port",
    "positive-integer",
    "project-name",
    "protobuf-package",
    "semantic-version",
    "slug",
    "team-id",
    "text",
    "url",
}
REQUIRED_COMMAND_CONTRACT = (
    "bootstrap",
    "doctor",
    "lint",
    "test",
    "verify",
    "build",
    "clean",
    "help",
)
MAKE_TARGET_PATTERN = re.compile(
    r"^([A-Za-z0-9_.-]+(?:[ \t]+[A-Za-z0-9_.-]+)*):(?:[ \t]|$)",
    re.MULTILINE,
)


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
    worktree = TemplateWorktree(**data.get("worktree", {}))
    return TemplateDefinition(
        name=data["name"],
        description=data["description"],
        stack=data["stack"],
        category=data["category"],
        tags=data["tags"],
        platforms=data["platforms"],
        maturity=maturity,
        validation=validation,
        worktree=worktree,
        operating_assumptions=data["operating_assumptions"],
        workflow_labels=data["workflow_labels"],
        commands=data.get("commands", {}),
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


def variable_validation_error(variable: TemplateVariable, value: str) -> str | None:
    """Return a concise validation error for one resolved template value."""
    if value != value.strip():
        return "must not start or end with whitespace"
    if not value:
        return "must not be empty"
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        return "must not contain control characters"
    if variable.choices and value not in variable.choices:
        return f"must be one of: {', '.join(variable.choices)}"

    validator = variable.validator
    patterns = {
        "apple-version": (
            r"^\d+(?:\.\d+){1,2}$",
            "must be a numeric Apple OS version such as 17.0",
        ),
        "bundle-identifier": (
            r"^[A-Za-z0-9][A-Za-z0-9-]*(?:\.[A-Za-z0-9][A-Za-z0-9-]*)+$",
            "must be a reverse-DNS identifier such as com.example.app",
        ),
        "go-module": (
            r"^[A-Za-z0-9][A-Za-z0-9.+~-]*(?:[./][A-Za-z0-9][A-Za-z0-9._+~-]*)+$",
            "must be a Go module path such as github.com/example/service",
        ),
        "harmony-sdk-version": (
            r"^\d+\.\d+\.\d+\(\d+\)$",
            "must use HarmonyOS SDK notation such as 5.0.0(12)",
        ),
        "identifier": (
            r"^[A-Za-z_][A-Za-z0-9_]*$",
            "must be a valid language identifier",
        ),
        "java-package": (
            r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$",
            "must be a dotted Java package such as com.example.app",
        ),
        "npm-package": (
            r"^(?:@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*$",
            "must be a lowercase npm package name",
        ),
        "protobuf-package": (
            r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$",
            "must be a dotted lowercase Protobuf package such as service.v1",
        ),
        "semantic-version": (
            r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$",
            "must be a semantic version such as 1.2.3",
        ),
        "slug": (
            r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
            "must be a lowercase hyphenated slug",
        ),
        "team-id": (
            r"^(?:[A-Z0-9]{10}|DEVELOPMENT_TEAM_ID)$",
            "must be a 10-character Apple team ID or DEVELOPMENT_TEAM_ID",
        ),
    }
    if validator in patterns:
        pattern, message = patterns[validator]
        if re.fullmatch(pattern, value) is None:
            return message

    if validator == "project-name":
        if value in {".", ".."} or len(value) > 80 or re.fullmatch(
            r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?", value
        ) is None:
            return (
                "must be a safe directory name using letters, numbers, dots, "
                "underscores, or hyphens"
            )
    elif validator == "display-name" and len(value) > 120:
        return "must contain at most 120 characters"
    elif validator == "npm-package" and len(value) > 214:
        return "must contain at most 214 characters"
    elif validator == "slug" and len(value) > 63:
        return "must contain at most 63 characters"
    elif validator in {"port", "positive-integer"}:
        if re.fullmatch(r"\d+", value) is None:
            return "must be an integer"
        numeric_value = int(value)
        minimum = variable.minimum if variable.minimum is not None else 1
        maximum = variable.maximum
        if validator == "port" and maximum is None:
            maximum = 65535
        if numeric_value < minimum or (maximum is not None and numeric_value > maximum):
            upper = str(maximum) if maximum is not None else "unbounded"
            return f"must be between {minimum} and {upper}"
    elif validator == "url":
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return "must be an absolute http or https URL"

    return None


def validate_resolved_variables(
    definition: TemplateDefinition, values: dict[str, str]
) -> list[str]:
    """Validate every resolved input according to its template metadata."""
    errors: list[str] = []
    for variable in definition.variables:
        value = values.get(variable.name)
        if value is None:
            continue
        reason = variable_validation_error(variable, value)
        if reason:
            errors.append(f"{variable.name}: {reason} (received {value!r})")
    return errors


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
    if not definition.operating_assumptions:
        errors.append(f"{definition.name}: operating_assumptions must contain at least one entry")
    if not definition.workflow_labels:
        errors.append(f"{definition.name}: workflow_labels must contain at least one entry")

    if not definition.maturity.level or not definition.maturity.summary:
        errors.append(f"{definition.name}: maturity.level and maturity.summary must be set")

    if not definition.validation.status:
        errors.append(f"{definition.name}: validation.status must not be empty")
    if definition.validation.verification_tier not in ALLOWED_VERIFICATION_TIERS:
        allowed_tiers = ", ".join(sorted(ALLOWED_VERIFICATION_TIERS))
        errors.append(
            f"{definition.name}: validation.verification_tier must be one of: {allowed_tiers}"
        )

    if not definition.validation.evidence:
        errors.append(f"{definition.name}: validation.evidence must contain at least one entry")

    if definition.worktree.support_level not in ALLOWED_WORKTREE_SUPPORT_LEVELS:
        allowed_levels = ", ".join(sorted(ALLOWED_WORKTREE_SUPPORT_LEVELS))
        errors.append(
            f"{definition.name}: worktree.support_level must be one of: {allowed_levels}"
        )

    if not definition.worktree.isolation_dimensions:
        errors.append(
            f"{definition.name}: worktree.isolation_dimensions must contain at least one entry"
        )
    if not definition.worktree.diagnostics:
        errors.append(f"{definition.name}: worktree.diagnostics must contain at least one entry")
    if not definition.worktree.cleanup:
        errors.append(f"{definition.name}: worktree.cleanup must contain at least one entry")

    invalid_worktree_dimensions = sorted(
        dimension
        for dimension in definition.worktree.isolation_dimensions
        if dimension not in ALLOWED_WORKTREE_ISOLATION_DIMENSIONS
    )
    if invalid_worktree_dimensions:
        allowed_dimensions = ", ".join(sorted(ALLOWED_WORKTREE_ISOLATION_DIMENSIONS))
        invalid_dimensions = ", ".join(invalid_worktree_dimensions)
        errors.append(
            f"{definition.name}: worktree.isolation_dimensions contain unsupported values: "
            f"{invalid_dimensions}; expected one of: {allowed_dimensions}"
        )

    if len(definition.worktree.isolation_dimensions) != len(
        set(definition.worktree.isolation_dimensions)
    ):
        errors.append(
            f"{definition.name}: worktree.isolation_dimensions must not contain duplicates"
        )
    if len(definition.worktree.diagnostics) != len(set(definition.worktree.diagnostics)):
        errors.append(f"{definition.name}: worktree.diagnostics must not contain duplicates")
    if len(definition.worktree.cleanup) != len(set(definition.worktree.cleanup)):
        errors.append(f"{definition.name}: worktree.cleanup must not contain duplicates")

    invalid_workflow_labels = sorted(
        label for label in definition.workflow_labels if label not in ALLOWED_WORKFLOW_LABELS
    )
    if invalid_workflow_labels:
        errors.append(
            f"{definition.name}: workflow_labels contain unsupported values: {', '.join(invalid_workflow_labels)}"
        )

    if len(definition.workflow_labels) != len(set(definition.workflow_labels)):
        errors.append(f"{definition.name}: workflow_labels must not contain duplicates")

    missing_commands = sorted(set(REQUIRED_COMMAND_CONTRACT) - set(definition.commands))
    if missing_commands:
        errors.append(
            f"{definition.name}: commands missing required entries: {', '.join(missing_commands)}"
        )
    for command_name, command in sorted(definition.commands.items()):
        if command != f"make {command_name}":
            errors.append(
                f"{definition.name}: command '{command_name}' must be exactly 'make {command_name}'"
            )

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
        if variable.validator not in ALLOWED_VARIABLE_VALIDATORS:
            errors.append(
                f"{definition.name}: variable '{variable.name}' uses unsupported validator '{variable.validator}'"
            )
        if variable.validator == "choice" and not variable.choices:
            errors.append(
                f"{definition.name}: variable '{variable.name}' choice validator requires choices"
            )
        if variable.minimum is not None and variable.maximum is not None:
            if variable.minimum > variable.maximum:
                errors.append(
                    f"{definition.name}: variable '{variable.name}' minimum must not exceed maximum"
                )
        if variable.default is not None:
            reason = variable_validation_error(variable, variable.default)
            if reason:
                errors.append(
                    f"{definition.name}: default for variable '{variable.name}' {reason}"
                )

    return errors


def validate_template_command_contract(definition: TemplateDefinition) -> list[str]:
    """Validate metadata commands against concrete phony Make targets."""
    makefile_path = definition.template_dir / "Makefile"
    if not makefile_path.is_file():
        return [f"{definition.name}: Makefile is missing for command contract validation"]

    content = makefile_path.read_text(encoding="utf-8")
    targets: set[str] = set()
    phony_targets: set[str] = set()
    for match in MAKE_TARGET_PATTERN.finditer(content):
        names = match.group(1).split()
        if names == [".PHONY"]:
            line_end = content.find("\n", match.end())
            if line_end < 0:
                line_end = len(content)
            phony_targets.update(content[match.end():line_end].split())
        else:
            targets.update(names)

    errors: list[str] = []
    for command_name in sorted(definition.commands):
        if command_name not in targets:
            errors.append(
                f"{definition.name}: command target '{command_name}' is missing from Makefile"
            )
        elif command_name not in phony_targets:
            errors.append(
                f"{definition.name}: command target '{command_name}' must be declared .PHONY"
            )
    return errors


def validate_template_required_files(definition: TemplateDefinition) -> list[str]:
    """Return family-level required file errors for a template."""
    errors: list[str] = []

    if not definition.template_dir.exists():
        return [f"{definition.name}: template directory is missing"]

    relative_entries = {
        path.relative_to(definition.template_dir).as_posix()
        for path in definition.template_dir.rglob("*")
    }

    required_entries = {"README.md", "Makefile", ".gitignore", "scripts/doctor"}
    if "docker" in definition.tags:
        required_entries.update({".dockerignore", "compose.dev.yaml"})
    if definition.category == "backend":
        required_entries.update({"go.mod", "go.sum", "cmd", "internal", "configs", "scripts"})
    if definition.category == "native":
        required_entries.update({".mise.toml", "scripts"})
    if definition.name == "apple":
        required_entries.update(
            {
                "Tuist.swift",
                "Workspace.swift",
                "fastlane/Fastfile",
                "scripts/verify-release-identity",
            }
        )
    if definition.name == "android":
        required_entries.update({"gradlew", "gradlew.bat", "scripts"})
    if definition.name == "microservice":
        required_entries.update(
            {
                "api/buf.gen.yaml",
                "api/buf.yaml",
                "api/proto/service/v1/service.proto",
                "internal/transport/grpc.go",
                "internal/transport/ping.go",
                "internal/runtime/server.go",
                "internal/runtime/server_test.go",
                "tests/server_test.go",
            }
        )
    if definition.name == "web-service":
        required_entries.update(
            {
                "internal/runtime/server.go",
                "internal/runtime/server_test.go",
            }
        )
    if definition.name == "worker":
        required_entries.update(
            {
                "internal/runtime/runner.go",
                "internal/runtime/runner_test.go",
            }
        )
    if definition.name == "frontend":
        required_entries.update(
            {
                "pnpm-lock.yaml",
                "playwright.production.config.ts",
                "scripts/browser-smoke-production",
                "tests/production-browser-smoke.spec.ts",
            }
        )

    missing_entries = sorted(entry for entry in required_entries if entry not in relative_entries)
    if missing_entries:
        errors.append(
            f"{definition.name}: missing required starter entries: {', '.join(missing_entries)}"
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
        errors.extend(validate_template_required_files(definition))
        errors.extend(validate_template_command_contract(definition))

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
        normalized_value = value.strip() if value is not None else ""
        if normalized_value:
            resolved[variable.name] = normalized_value
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
