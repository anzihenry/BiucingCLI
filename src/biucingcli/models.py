"""Template metadata and variable result models, independent of CLI and I/O."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from collections.abc import Mapping
from types import MappingProxyType


@dataclass(frozen=True)
class TemplateVariable:
    """A declared template variable."""

    name: str
    required: bool = False
    default: str | None = None
    default_from: str | None = None
    prompt: str | None = None
    validator: str = "text"
    choices: list[str] = field(default_factory=list)
    minimum: int | None = None
    maximum: int | None = None
    contexts: list[str] = field(default_factory=list)

    def numeric_bounds(self) -> tuple[int | None, int | None]:
        """Return effective numeric limits, including validator defaults."""
        if self.validator not in {"port", "positive-integer"}:
            return self.minimum, self.maximum
        minimum = self.minimum if self.minimum is not None else 1
        maximum = self.maximum
        if self.validator == "port" and maximum is None:
            maximum = 65535
        return minimum, maximum

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        minimum, maximum = self.numeric_bounds()
        return {
            "name": self.name,
            "required": self.required,
            "default": self.default,
            "default_from": self.default_from,
            "prompt": self.prompt,
            "validator": self.validator,
            "choices": list(self.choices),
            "minimum": minimum,
            "maximum": maximum,
        }


@dataclass(frozen=True)
class ResolvedVariable:
    """A resolved template variable plus its source."""

    name: str
    value: str
    source: str

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class TemplateMaturity:
    """User-facing maturity metadata for a template."""

    level: str
    summary: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class TemplateValidation:
    """User-facing validation metadata for a template."""

    status: str
    verification_tier: str
    evidence: list[str]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class TemplateWorktree:
    """Worktree isolation metadata for a template."""

    support_level: str = ""
    isolation_dimensions: list[str] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)
    cleanup: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class TemplateVariant:
    """One resource layer; paths are relative to template metadata/output."""

    source: str
    required_entries: tuple[str, ...] = ()
    forbidden_entries: tuple[str, ...] = ()
    overrides: tuple[str, ...] = ()
    next_steps: tuple[str, ...] | None = None

    def __post_init__(self):
        for name in ("required_entries", "forbidden_entries", "overrides"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        if self.next_steps is not None:
            object.__setattr__(self, "next_steps", tuple(self.next_steps))


@dataclass(frozen=True)
class TemplateVariants:
    """A single input selector and its immutable option mapping."""

    selector: str
    options: Mapping[str, TemplateVariant]

    def __post_init__(self):
        object.__setattr__(self, "options", MappingProxyType(dict(self.options)))


@dataclass(frozen=True)
class ResourceEntry:
    """A source entry, not a copied/rendered file or filesystem snapshot."""

    source: Path
    output_path: str
    layer: str
    kind: str
    mode: int


@dataclass(frozen=True)
class ResolvedResources:
    """Deterministic resource selection; execution is a separate concern."""

    selector: str | None
    selected_variant: str | None
    entries: tuple[ResourceEntry, ...]
    required_entries: tuple[str, ...]
    forbidden_entries: tuple[str, ...]
    next_steps: tuple[str, ...]

    def __post_init__(self):
        for name in ("entries", "required_entries", "forbidden_entries", "next_steps"):
            object.__setattr__(self, name, tuple(getattr(self, name)))


@dataclass(frozen=True)
class TemplateDefinition:
    """Template metadata and file locations."""

    name: str
    description: str
    stack: list[str]
    category: str
    tags: list[str]
    platforms: list[str]
    maturity: TemplateMaturity
    validation: TemplateValidation
    worktree: TemplateWorktree
    operating_assumptions: list[str]
    workflow_labels: list[str]
    commands: dict[str, str]
    variables: list[TemplateVariable]
    next_steps: list[str]
    template_dir: Path
    contracts: list[str] = field(default_factory=list)
    required_entries: list[str] = field(default_factory=list)
    rule: str | None = None
    derived_outputs: list[str] = field(default_factory=list)
    render_outputs: list[str] = field(default_factory=list)
    variants: TemplateVariants | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "name": self.name,
            "description": self.description,
            "stack": self.stack,
            "category": self.category,
            "tags": self.tags,
            "platforms": self.platforms,
            "maturity": self.maturity.to_dict(),
            "validation": self.validation.to_dict(),
            "worktree": self.worktree.to_dict(),
            "operating_assumptions": self.operating_assumptions,
            "workflow_labels": self.workflow_labels,
            "variables": [variable.to_dict() for variable in self.variables],
            "next_steps": self.next_steps,
        }


@dataclass(frozen=True)
class VariableResolutionResult:
    """Resolved template variables and missing required inputs."""

    values: dict[str, str]
    resolved_variables: list[ResolvedVariable]
    missing_required: list[str]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "values": self.values,
            "resolved_variables": [item.to_dict() for item in self.resolved_variables],
            "missing_required": self.missing_required,
        }


@dataclass(frozen=True)
class CreateRequest:
    """CLI-independent inputs; explicit values retain priority over set values."""

    template: str
    project_name: str
    output_dir: Path = Path(".")
    set_values: Mapping[str, str] = field(default_factory=dict)
    explicit_values: Mapping[str, str | None] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "set_values", MappingProxyType(dict(self.set_values)))
        object.__setattr__(self, "explicit_values", MappingProxyType(dict(self.explicit_values)))


@dataclass(frozen=True)
class GenerationPlan:
    """Resolved generation input, not a snapshot or lock of the filesystem."""

    definition: TemplateDefinition
    project_name: str
    target_dir: Path
    values: Mapping[str, str]
    resolved_variables: tuple[ResolvedVariable, ...]
    derived_values: Mapping[str, str]
    rendered_next_steps: tuple[str, ...]
    template_file_count: int
    template_top_level_entries: tuple[str, ...]

    def __post_init__(self):
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))
        object.__setattr__(self, "derived_values", MappingProxyType(dict(self.derived_values)))

    def to_context(self) -> dict[str, object]:
        """Adapt to the pre-stage-5 formatting context without sharing value maps."""
        return {
            "definition": self.definition,
            "project_name": self.project_name,
            "target_dir": self.target_dir,
            "values": dict(self.values),
            "resolved_variables": [item.to_dict() for item in self.resolved_variables],
            "derived_values": dict(self.derived_values),
            "rendered_next_steps": list(self.rendered_next_steps),
            "template_file_count": self.template_file_count,
            "template_top_level_entries": list(self.template_top_level_entries),
        }
