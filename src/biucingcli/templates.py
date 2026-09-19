"""Compatibility exports and variable resolution pending later extraction."""

from __future__ import annotations

import sys

from biucingcli.catalog import (
    templates_root as templates_root,
    load_template as load_template,
    load_templates as load_templates,
)
from biucingcli.errors import (
    BiucingError as BiucingError,
    UnknownTemplateError as UnknownTemplateError,
    InvalidTemplateError as InvalidTemplateError,
    GenerationError as GenerationError,
    GenerationConflictError as GenerationConflictError,
    MissingInputError as MissingInputError,
    InputEndedError as InputEndedError,
)
from biucingcli.models import (
    TemplateVariable as TemplateVariable,
    ResolvedVariable as ResolvedVariable,
    TemplateMaturity as TemplateMaturity,
    TemplateValidation as TemplateValidation,
    TemplateWorktree as TemplateWorktree,
    TemplateDefinition as TemplateDefinition,
    VariableResolutionResult as VariableResolutionResult,
)

from biucingcli.variables import (
    ALLOWED_VARIABLE_VALIDATORS as ALLOWED_VARIABLE_VALIDATORS,
    variable_validation_error as variable_validation_error,
    validate_resolved_variables as validate_resolved_variables,
)
from biucingcli.validation import (
    ALLOWED_VERIFICATION_TIERS as ALLOWED_VERIFICATION_TIERS,
    ALLOWED_WORKFLOW_LABELS as ALLOWED_WORKFLOW_LABELS,
    ALLOWED_WORKTREE_SUPPORT_LEVELS as ALLOWED_WORKTREE_SUPPORT_LEVELS,
    ALLOWED_WORKTREE_ISOLATION_DIMENSIONS as ALLOWED_WORKTREE_ISOLATION_DIMENSIONS,
    REQUIRED_COMMAND_CONTRACT as REQUIRED_COMMAND_CONTRACT,
    MAKE_TARGET_PATTERN as MAKE_TARGET_PATTERN,
    validate_template_definition as validate_template_definition,
    validate_template_command_contract as validate_template_command_contract,
    validate_template_required_files as validate_template_required_files,
    validate_template_placeholders as validate_template_placeholders,
    validate_templates as validate_templates,
)
from biucingcli.rendering import (
    PLACEHOLDER_PATTERN as PLACEHOLDER_PATTERN,
    supported_placeholders as supported_placeholders,
    placeholder_map as placeholder_map,
    render_text as render_text,
)
from biucingcli.generation import (
    render_template as render_template,
)


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
            print(prompt, end="", file=sys.stderr, flush=True)
            try:
                answer = input().strip()
            except EOFError as exc:
                print(file=sys.stderr)
                raise InputEndedError(
                    f"Input ended while reading {variable.name}; supply it with a flag or --set."
                ) from exc
            except KeyboardInterrupt:
                print(file=sys.stderr)
                raise
            if not answer:
                raise MissingInputError(f"Missing required value for {variable.name}")
            resolved[variable.name] = answer
            resolution_sources[variable.name] = "prompted"

    if missing_required:
        missing_list = ", ".join(missing_required)
        raise MissingInputError(
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
