"""Filesystem generation with staging, publication and cleanup."""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
from pathlib import Path
from collections.abc import Callable

from biucingcli.errors import BiucingError, GenerationConflictError, GenerationError, InvalidTemplateError
from biucingcli.declarations import declaration_errors
from biucingcli.validation import validate_template_placeholders
from biucingcli.models import TemplateDefinition, TemplateVariable, CreateRequest, GenerationPlan
from biucingcli.catalog import load_template
from biucingcli.variables import resolve_variables_detailed, validate_resolved_variables
from biucingcli.template_rules.registry import derive_template_values
from biucingcli.rendering import render_text


def default_display_name(project_name: str) -> str:
    """Return the historical generated display-name default."""
    return project_name.replace("-", " ").replace("_", " ").title()


def count_template_files(template_dir: Path) -> int:
    return sum(1 for path in template_dir.rglob("*") if path.is_file())


def top_level_template_entries(template_dir: Path) -> list[str]:
    return sorted(path.name for path in template_dir.iterdir())


def validate_generation_definition(definition: TemplateDefinition) -> None:
    errors = declaration_errors(definition) + validate_template_placeholders(definition)
    if errors:
        raise InvalidTemplateError("; ".join(errors))


def build_generation_plan(
    request: CreateRequest, *, definition: TemplateDefinition | None = None,
    prompt: Callable[[TemplateVariable], str] | None = None,
) -> GenerationPlan:
    """Read/resolve a request without creating directories or writing files."""
    definition = load_template(request.template) if definition is None else definition
    validate_generation_definition(definition)
    allowed_keys = {variable.name for variable in definition.variables}
    unknown = sorted(key for key in request.set_values if key not in allowed_keys)
    if unknown:
        raise ValueError(f"Unknown template variable(s) for {request.template}: {', '.join(unknown)}")
    unsupported = sorted(key for key, value in request.explicit_values.items()
                         if value is not None and key not in allowed_keys)
    if unsupported:
        raise ValueError(f"Unsupported option(s) for {request.template}: {', '.join(unsupported)}")
    project_name = request.project_name.strip()
    provided = dict(request.set_values)
    provided["project_name"] = project_name
    if "display_name" not in provided:
        provided["display_name"] = default_display_name(project_name)
    provided.update({key: value for key, value in request.explicit_values.items() if value is not None})
    # Positional identity is authoritative, including for non-CLI callers.
    provided["project_name"] = project_name
    resolution = resolve_variables_detailed(definition, provided, prompt=prompt)
    values = dict(resolution.values)
    rule_result = derive_template_values(definition, values)
    values.update(rule_result.derived_values)
    values.update(rule_result.render_only_values)
    errors = validate_resolved_variables(definition, values)
    if errors:
        raise ValueError(f"Invalid input value(s) for {definition.name}: " + "; ".join(errors))
    return GenerationPlan(
        definition=definition,
        project_name=values["project_name"],
        target_dir=Path(request.output_dir).resolve() / values["project_name"],
        values=values,
        resolved_variables=tuple(resolution.resolved_variables),
        derived_values={key: values[key] for key in sorted(rule_result.derived_values) if key in values},
        rendered_next_steps=tuple(render_text(step, values, definition) for step in definition.next_steps),
        template_file_count=count_template_files(definition.template_dir),
        template_top_level_entries=tuple(top_level_template_entries(definition.template_dir)),
    )


def execute_generation_plan(plan: GenerationPlan) -> None:
    """Execute a resolved plan; render_template rechecks current target state."""
    render_template(plan.definition, dict(plan.values), plan.target_dir)


def render_template(
    definition: TemplateDefinition,
    values: dict[str, str],
    target_dir: Path,
) -> None:
    """Copy and render a template into the target directory."""
    if target_dir.exists():
        raise GenerationConflictError(f"target directory already exists: {target_dir}")
    if not target_dir.parent.exists():
        raise GenerationError(f"output directory does not exist: {target_dir.parent}")
    if not target_dir.parent.is_dir():
        raise GenerationError(f"output path is not a directory: {target_dir.parent}")

    errors = declaration_errors(definition) + validate_template_placeholders(definition)
    if errors:
        raise InvalidTemplateError("; ".join(errors))

    staging_root: Path | None = None
    try:
        staging_root = Path(
            tempfile.mkdtemp(prefix=f".{target_dir.name}.biucing-", dir=target_dir.parent)
        )
        rendered_dir = staging_root / "project"
        shutil.copytree(definition.template_dir, rendered_dir)

        for path in rendered_dir.rglob("*"):
            if not path.is_file():
                continue

            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            path.write_text(render_text(content, values, definition), encoding="utf-8")
            if path.name == "gradlew" or "scripts" in path.parts:
                current_mode = path.stat().st_mode
                path.chmod(current_mode | stat.S_IXUSR)

        if target_dir.exists():
            raise GenerationConflictError(f"target directory already exists: {target_dir}")
        os.replace(rendered_dir, target_dir)
    except BiucingError:
        raise
    except OSError as exc:
        raise GenerationError(f"could not generate project at {target_dir}: {exc}") from exc
    finally:
        if staging_root is not None:
            shutil.rmtree(staging_root, ignore_errors=True)
