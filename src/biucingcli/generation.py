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
from biucingcli.validation import (
    validate_template_placeholders, validate_template_definition, validate_resolved_resources,
)
from biucingcli.models import (
    TemplateDefinition, TemplateVariable, CreateRequest, GenerationPlan, ResolvedResources,
)
from biucingcli.resources import resolve_resources, resource_fingerprint
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
    errors = (validate_template_definition(definition) if definition.variants is not None else
              declaration_errors(definition) + validate_template_placeholders(definition))
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
    if definition.variants is not None:
        selector = definition.variants.selector
        if selector in rule_result.derived_values or selector in rule_result.render_only_values:
            raise InvalidTemplateError(f"{definition.name}: rules must not overwrite the selector")
    values.update(rule_result.derived_values)
    values.update(rule_result.render_only_values)
    errors = validate_resolved_variables(definition, values)
    if errors:
        raise ValueError(f"Invalid input value(s) for {definition.name}: " + "; ".join(errors))
    resources = None
    fingerprint = None
    if definition.variants is not None:
        resources, fingerprint = prepare_resources(definition, values)
    return GenerationPlan(
        definition=definition,
        project_name=values["project_name"],
        target_dir=Path(request.output_dir).resolve() / values["project_name"],
        values=values,
        resolved_variables=tuple(resolution.resolved_variables),
        derived_values={key: values[key] for key in sorted(rule_result.derived_values) if key in values},
        rendered_next_steps=tuple(render_text(step, values, definition) for step in
                                  (resources.next_steps if resources else definition.next_steps)),
        template_file_count=(sum(e.kind == "file" for e in resources.entries) if resources else
                             count_template_files(definition.template_dir)),
        template_top_level_entries=(tuple(sorted({e.output_path.split("/")[0] for e in resources.entries}))
                                    if resources else tuple(top_level_template_entries(definition.template_dir))),
        resources=resources,
        resource_fingerprint=fingerprint,
    )


def execute_generation_plan(plan: GenerationPlan) -> None:
    """Execute a resolved plan; render_template rechecks current target state."""
    if plan.resources is not None:
        publish_resources(plan.definition, dict(plan.values), plan.target_dir,
                          plan.resources, plan.resource_fingerprint)
    elif plan.definition.variants is not None:
        raise GenerationError("variant plan has no resolved resources; build a new plan")
    else:
        render_template(plan.definition, dict(plan.values), plan.target_dir)


def prepare_resources(
    definition: TemplateDefinition, values: dict[str, str],
) -> tuple[ResolvedResources, str]:
    resources = resolve_resources(definition, values)
    before = resource_fingerprint(definition, resources)
    errors = validate_resolved_resources(definition, resources)
    if errors:
        raise InvalidTemplateError("; ".join(errors))
    check_resource_state(definition, values, resources, before)
    return resources, before


def check_resource_state(
    definition: TemplateDefinition, values: dict[str, str],
    resources: ResolvedResources, fingerprint: str | None,
) -> None:
    try:
        current = resolve_resources(definition, values)
        if current == resources and fingerprint == resource_fingerprint(definition, current):
            return
    except (InvalidTemplateError, ValueError, OSError):
        pass
    raise GenerationError("template resources or metadata changed; build a new generation plan")


def publish_resources(
    definition: TemplateDefinition, values: dict[str, str], target_dir: Path,
    resources: ResolvedResources, fingerprint: str | None,
) -> None:
    """Execute exactly the planned selection in a private staging directory."""
    if target_dir.exists() or target_dir.is_symlink():
        raise GenerationConflictError(f"target directory already exists: {target_dir}")
    if not target_dir.parent.is_dir():
        raise GenerationError(f"output directory does not exist or is not a directory: {target_dir.parent}")
    check_resource_state(definition, values, resources, fingerprint)
    staging_root = None
    try:
        staging_root = Path(tempfile.mkdtemp(prefix=f".{target_dir.name}.biucing-", dir=target_dir.parent))
        rendered_dir = staging_root / "project"
        rendered_dir.mkdir()
        for entry in resources.entries:
            destination = rendered_dir / entry.output_path
            if entry.kind == "directory":
                destination.mkdir(exist_ok=True)
            else:
                shutil.copy2(entry.source, destination)
                try:
                    content = destination.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                destination.chmod(entry.mode | stat.S_IWUSR)
                destination.write_text(render_text(content, values, definition), encoding="utf-8")
                executable = destination.name == "gradlew" or "scripts" in destination.relative_to(rendered_dir).parts
                destination.chmod(entry.mode | (stat.S_IXUSR if executable else 0))
        # Keep directories writable until children are populated.
        for entry in reversed(resources.entries):
            if entry.kind == "directory":
                (rendered_dir / entry.output_path).chmod(entry.mode)
        check_resource_state(definition, values, resources, fingerprint)
        if target_dir.exists() or target_dir.is_symlink():
            raise GenerationConflictError(f"target directory already exists: {target_dir}")
        rendered_dir.chmod(stat.S_IMODE(definition.template_dir.stat().st_mode))
        os.replace(rendered_dir, target_dir)
    except BiucingError:
        raise
    except OSError as exc:
        raise GenerationError(f"could not generate project at {target_dir}: {exc}") from exc
    finally:
        if staging_root is not None:
            # Planned directory modes may be read-only. Restore traversal/write
            # only inside our unpublished staging tree, never the user's target.
            try:
                root = staging_root / "project"
                root.chmod(root.stat().st_mode | stat.S_IRWXU)
            except OSError:
                pass
            for entry in resources.entries:
                if entry.kind == "directory":
                    directory = staging_root / "project" / entry.output_path
                    try:
                        directory.chmod(directory.stat().st_mode | stat.S_IRWXU)
                    except OSError:
                        pass
            shutil.rmtree(staging_root, ignore_errors=True)


def render_template(
    definition: TemplateDefinition,
    values: dict[str, str],
    target_dir: Path,
) -> None:
    """Copy and render a template into the target directory."""
    if definition.variants is not None:
        validate_generation_definition(definition)
        resources, fingerprint = prepare_resources(definition, values)
        publish_resources(definition, values, target_dir, resources, fingerprint)
        return
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
