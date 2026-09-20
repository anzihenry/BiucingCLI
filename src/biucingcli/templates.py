"""Compatibility exports, including the historical interactive resolver API."""

from __future__ import annotations

from biucingcli import variables
from biucingcli.interaction import terminal_prompt

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


def resolve_variables(definition: TemplateDefinition, provided: dict[str, str | None],
                      interactive: bool = True) -> dict[str, str]:
    return resolve_variables_detailed(definition, provided, interactive=interactive).values


def resolve_variables_detailed(definition: TemplateDefinition, provided: dict[str, str | None],
                               interactive: bool = True) -> VariableResolutionResult:
    return variables.resolve_variables_detailed(
        definition, provided, prompt=terminal_prompt if interactive else None,
    )
