"""Template metadata and variable result models, independent of CLI and I/O."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path


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
