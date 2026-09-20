"""Text and JSON presentation, independent of CLI, loading and generation."""

from __future__ import annotations

import json
from pathlib import Path

from biucingcli import __version__
from biucingcli.models import GenerationPlan, TemplateDefinition


JSON_SCHEMA_VERSION = 1


def output_metadata() -> dict[str, object]:
    """Version the JSON contract independently of the generator release."""
    return {"schema_version": JSON_SCHEMA_VERSION, "generator_version": __version__}


def format_error(json_mode: bool, code: str, message: str, details=None) -> str:
    """Format a diagnostic without selecting streams, exit codes or terminating."""
    if json_mode:
        error = {"code": code, "message": message}
        if details is not None:
            error["details"] = details
        return json.dumps({**output_metadata(), "ok": False, "error": error})
    return f"error: {message}"


def format_template_summary(definitions: list[TemplateDefinition]) -> str:
    """Return a concise summary of available templates."""
    lines = ["Available templates:"]
    for definition in definitions:
        lines.append(f"- {definition.name}: {definition.description}")
    return "\n".join(lines)


def format_template_summary_json(definitions: list[TemplateDefinition]) -> str:
    """Return a machine-readable template list."""
    payload = {**output_metadata(), "templates": [definition.to_dict() for definition in definitions]}
    return json.dumps(payload, indent=2)


def format_template_info(definition: TemplateDefinition) -> str:
    """Return a detailed view of one template."""
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


def format_template_info_json(definition: TemplateDefinition) -> str:
    """Return a machine-readable template detail payload."""
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


def format_create_json(context: GenerationPlan | dict[str, object], mode: str) -> str:
    return json.dumps(create_manifest(context, mode), indent=2)
