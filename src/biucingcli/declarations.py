"""Validation of template-owned extension declarations, without filesystem I/O."""

from pathlib import PurePosixPath

from biucingcli.errors import InvalidTemplateError
from biucingcli.rendering import placeholder_bindings
from biucingcli.template_rules.contracts import CONTRACTS, BUILTIN_CONTRACTS
from biucingcli.template_rules.registry import rule_declaration_errors
from biucingcli.variables import ALLOWED_VARIABLE_VALIDATORS


def declaration_errors(definition) -> list[str]:
    errors = rule_declaration_errors(definition)
    for variable in definition.variables:
        if variable.validator not in ALLOWED_VARIABLE_VALIDATORS:
            errors.append(f"{definition.name}: variable '{variable.name}' uses unsupported validator '{variable.validator}'")
    for field in ("contracts", "required_entries", "derived_outputs", "render_outputs"):
        values = getattr(definition, field)
        if len(values) != len(set(values)):
            errors.append(f"{definition.name}: {field} must not contain duplicates")
    unknown = sorted(set(definition.contracts) - CONTRACTS.keys())
    if unknown:
        errors.append(f"{definition.name}: unknown contracts: {', '.join(unknown)}")
    missing = BUILTIN_CONTRACTS.get(definition.name, frozenset()) - set(definition.contracts)
    if missing:
        errors.append(f"{definition.name}: missing required contracts: {', '.join(sorted(missing))}")
    for entry in definition.required_entries:
        path = PurePosixPath(entry)
        if (not entry or path.is_absolute() or ".." in path.parts or "\\" in entry
                or ":" in entry or entry != path.as_posix() or entry == "."):
            errors.append(f"{definition.name}: required entry must be a normalized relative path: {entry!r}")
    try:
        placeholder_bindings(definition)
    except InvalidTemplateError as exc:
        errors.append(str(exc))
    return errors
