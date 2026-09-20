"""Pure parsing and validation for optional resource variants (no filesystem I/O)."""

import re
import unicodedata

from biucingcli.models import TemplateVariant, TemplateVariants
from biucingcli.template_rules.contracts import required_entries


IDENTIFIER = re.compile(r"[a-z][a-z0-9_]*\Z")


def normalized_path(value: str) -> bool:
    """Accept literal, portable relative POSIX paths, never glob expressions."""
    return (isinstance(value, str) and bool(value)
            and not any(char in value for char in "\\\x00:*?[]")
            and all(part not in {"", ".", ".."} for part in value.split("/")))


def collision_key(path: str) -> str:
    return unicodedata.normalize("NFC", unicodedata.normalize("NFC", path).casefold())


def at_or_below(path: str, parent: str) -> bool:
    return path == parent or path.startswith(parent + "/")


def _string_list(data, key):
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"variants {key} must be a list of strings")
    return tuple(value)


def parse_variants(data) -> TemplateVariants:
    """Parse only the new strict schema; legacy metadata policy is unchanged."""
    if not isinstance(data, dict) or set(data) != {"selector", "options"}:
        raise TypeError("variants must contain exactly selector and options")
    if not isinstance(data["selector"], str):
        raise TypeError("variants selector must be a string")
    options = data["options"]
    if not isinstance(options, dict) or not options:
        raise TypeError("variants options must be a nonempty object")
    parsed = {}
    allowed = {"source", "required_entries", "forbidden_entries", "overrides", "next_steps"}
    for name, option in options.items():
        if not isinstance(option, dict) or "source" not in option or set(option) - allowed:
            raise TypeError(f"variants option {name!r} has missing/unknown fields")
        if not isinstance(option["source"], str):
            raise TypeError(f"variants option {name!r} source must be a string")
        parsed[name] = TemplateVariant(
            source=option["source"],
            required_entries=_string_list(option, "required_entries"),
            forbidden_entries=_string_list(option, "forbidden_entries"),
            overrides=_string_list(option, "overrides"),
            next_steps=_string_list(option, "next_steps") if "next_steps" in option else None,
        )
    return TemplateVariants(data["selector"], parsed)


def variant_declaration_errors(definition) -> list[str]:
    variants = definition.variants
    if variants is None:
        return []
    errors = []
    prefix = f"{definition.name}: variants"
    if not IDENTIFIER.fullmatch(variants.selector):
        errors.append(f"{prefix}: invalid selector identifier")
    variables = [v for v in definition.variables if v.name == variants.selector]
    if len(variables) != 1:
        errors.append(f"{prefix}: selector must reference exactly one declared input")
    else:
        variable = variables[0]
        choices = variable.choices
        if (not isinstance(choices, (list, tuple)) or not choices
                or not all(isinstance(v, str) and IDENTIFIER.fullmatch(v) for v in choices)):
            errors.append(f"{prefix}: selector requires nonempty identifier choices")
        elif len(set(choices)) != len(choices) or set(choices) != set(variants.options):
            errors.append(f"{prefix}: choices and options must match exactly without duplicates")
        if (not isinstance(variable.default, str) or not isinstance(choices, (list, tuple))
                or variable.default not in choices or variable.default_from is not None):
            errors.append(f"{prefix}: selector requires a literal default in choices, no default_from")
    if variants.selector in set(definition.derived_outputs) | set(definition.render_outputs):
        errors.append(f"{prefix}: rules must not overwrite the selector")
    if not variants.options:
        errors.append(f"{prefix}: options must not be empty")
    roots = []
    for name, option in sorted(variants.options.items()):
        context = f"{definition.name}[{name}]"
        if not IDENTIFIER.fullmatch(name):
            errors.append(f"{context}: invalid option identifier")
        source = option.source
        if not normalized_path(source) or not source.startswith("variants/"):
            errors.append(f"{context}: source must be a normalized path beneath variants/")
        else:
            key = collision_key(source)
            common = collision_key(definition.template_dir.name)
            if at_or_below(key, common) or at_or_below(common, key):
                errors.append(f"{context}: source overlaps common root")
            for previous, other in roots:
                if at_or_below(key, other) or at_or_below(other, key):
                    errors.append(f"{context}: source overlaps option {previous!r}")
            roots.append((name, key))
        for field in ("required_entries", "forbidden_entries", "overrides"):
            paths = getattr(option, field)
            if len(set(paths)) != len(paths):
                errors.append(f"{context}: {field} must not contain duplicates")
            for path in paths:
                if not normalized_path(path):
                    errors.append(f"{context}: {field} requires normalized relative paths: {path!r}")
        for path in sorted(required_entries(definition) | set(option.required_entries)):
            for forbidden in option.forbidden_entries:
                if at_or_below(collision_key(path), collision_key(forbidden)):
                    errors.append(f"{context}: required/forbidden contradiction: {path!r}")
    return errors
