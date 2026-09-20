"""Variable constraints and resolution with an optional injected prompt callback."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from collections.abc import Callable

from biucingcli.errors import MissingInputError
from biucingcli.models import TemplateDefinition, TemplateVariable, ResolvedVariable, VariableResolutionResult


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
        minimum, maximum = variable.numeric_bounds()
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


def resolve_variables_detailed(
    definition: TemplateDefinition,
    provided: dict[str, str | None],
    *,
    prompt: Callable[[TemplateVariable], str] | None = None,
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
            if prompt is None:
                missing_required.append(variable.name)
                continue
            answer = prompt(variable).strip()
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


def resolve_variables(definition: TemplateDefinition, provided: dict[str, str | None], *,
                      prompt: Callable[[TemplateVariable], str] | None = None) -> dict[str, str]:
    return resolve_variables_detailed(definition, provided, prompt=prompt).values
