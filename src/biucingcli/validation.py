"""Template metadata, file, Make and placeholder validation."""

from __future__ import annotations

import json
import re

from biucingcli import catalog
from biucingcli.catalog import load_templates
from biucingcli.models import TemplateDefinition
from biucingcli.variables import ALLOWED_VARIABLE_VALIDATORS, variable_validation_error
from biucingcli.rendering import PLACEHOLDER_PATTERN, supported_placeholders
from biucingcli.escaping import FREE_TEXT_KEYS


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
        raw_free_text = {"{{" + key.upper() + "}}" for key in FREE_TEXT_KEYS}
        unescaped = sorted(raw_free_text.intersection(placeholders))
        if unescaped and path.suffix != ".md":
            errors.append(
                f"{definition.name}: free-text placeholder(s) require an explicit context "
                f"in {path.relative_to(definition.template_dir)}: {', '.join(unescaped)}"
            )
        unsupported = [placeholder for placeholder in placeholders if placeholder not in supported]
        if unsupported:
            relative_path = path.relative_to(catalog.templates_root()).as_posix()
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

    for metadata_path in sorted(catalog.templates_root().glob("*/template.json")):
        folder_name = metadata_path.parent.name
        definition_name = json.loads(metadata_path.read_text(encoding="utf-8"))["name"]
        if definition_name != folder_name:
            errors.append(
                f"{folder_name}: template name '{definition_name}' must match folder name"
            )

    if not known_names:
        errors.append("no templates found under templates/")

    return errors
