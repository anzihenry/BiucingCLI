"""Template-scoped single-pass rendering; legacy unscoped helpers remain compatible."""

from __future__ import annotations

import re

from biucingcli import _legacy_rendering
from biucingcli.escaping import CONTEXT_ESCAPERS
from biucingcli.errors import InvalidTemplateError
from biucingcli.models import TemplateDefinition


PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Z0-9_]+\}\}")
NAME_PATTERN = re.compile(r"[a-z][a-z0-9_]*")


def free_text_names(definition: TemplateDefinition) -> set[str]:
    # Infer safety from constraints, never from a hard-coded list of field names.
    return {v.name for v in definition.variables
            if v.validator in {"text", "display-name", "url"}
            or (v.validator == "choice" and (not v.choices or any(
                re.fullmatch(r"[A-Za-z0-9_.-]+", choice) is None for choice in v.choices)))}


def placeholder_bindings(definition: TemplateDefinition) -> dict[str, tuple[str, str | None]]:
    bindings = {}

    def add(name, context=None):
        token = "{{" + name.upper() + ("_" + context if context else "") + "}}"
        if token in bindings:
            raise InvalidTemplateError(f"{definition.name}: duplicate placeholder binding {token}")
        bindings[token] = (name, context)

    inputs = {v.name for v in definition.variables}
    for variable in definition.variables:
        if not isinstance(variable.name, str) or not NAME_PATTERN.fullmatch(variable.name):
            raise InvalidTemplateError(f"{definition.name}: invalid variable name {variable.name!r}")
        add(variable.name)
        for context in variable.contexts:
            if context not in CONTEXT_ESCAPERS:
                raise InvalidTemplateError(f"{definition.name}: unknown escape context {context!r}")
            add(variable.name, context)
    outputs = definition.derived_outputs + definition.render_outputs
    if len(outputs) != len(set(outputs)):
        raise InvalidTemplateError(f"{definition.name}: duplicate derived/render output")
    for name in outputs:
        if not NAME_PATTERN.fullmatch(name):
            raise InvalidTemplateError(f"{definition.name}: invalid output name {name!r}")
        # Legitimate input overwrites are checked against the registered rule.
        if name not in inputs:
            add(name)
    return bindings


def supported_placeholders(definition: TemplateDefinition | None = None) -> set[str]:
    if definition is None:
        return _legacy_rendering.supported_placeholders()
    return set(placeholder_bindings(definition))


def placeholder_map(values: dict[str, str], definition: TemplateDefinition | None = None) -> dict[str, str]:
    if definition is None:
        return _legacy_rendering.placeholder_map(values)
    return {
        token: CONTEXT_ESCAPERS[context](values.get(name, "")) if context else values.get(name, "")
        for token, (name, context) in placeholder_bindings(definition).items()
    }


def render_text(text: str, values: dict[str, str], definition: TemplateDefinition | None = None) -> str:
    placeholders = placeholder_map(values, definition)
    if definition is not None:
        unknown = sorted(set(PLACEHOLDER_PATTERN.findall(text)) - placeholders.keys())
        if unknown:
            raise InvalidTemplateError(f"{definition.name}: unsupported placeholder(s): {', '.join(unknown)}")
    return PLACEHOLDER_PATTERN.sub(lambda match: placeholders.get(match[0], match[0]), text)
