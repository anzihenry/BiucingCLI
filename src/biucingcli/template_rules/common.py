"""Pure data returned by built-in template rules."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RuleResult:
    """Manifest-visible derivations and render-only snippets remain distinct."""

    derived_values: dict[str, str] = field(default_factory=dict)
    render_only_values: dict[str, str] = field(default_factory=dict)


def default_type_name(project_name: str) -> str:
    """Return a type name derived from a directory name."""
    parts = [part for part in project_name.replace("_", "-").split("-") if part]
    if not parts:
        return "App"
    return "".join(part[:1].upper() + part[1:] for part in parts)
