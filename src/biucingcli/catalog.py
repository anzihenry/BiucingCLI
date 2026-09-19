"""Load package-owned template resources; callers may inject a fixture root."""

from __future__ import annotations

import json
from pathlib import Path

from biucingcli.errors import InvalidTemplateError, UnknownTemplateError
from biucingcli.models import (
    TemplateDefinition, TemplateVariable, TemplateMaturity, TemplateValidation, TemplateWorktree,
)


def templates_root() -> Path:
    """Return the templates bundled inside the installed package."""
    return Path(__file__).resolve().parent / "template_data"


def load_template(name: str, *, root: Path | None = None) -> TemplateDefinition:
    """Load one template definition by name."""
    metadata_path = (templates_root() if root is None else root) / name / "template.json"
    if not metadata_path.exists():
        raise UnknownTemplateError(f"unknown template '{name}'")

    try:
        with metadata_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        variables = [TemplateVariable(**variable) for variable in data["variables"]]
        maturity = TemplateMaturity(**data["maturity"])
        validation = TemplateValidation(**data["validation"])
        worktree = TemplateWorktree(**data.get("worktree", {}))
        return TemplateDefinition(
            name=data["name"],
            description=data["description"],
            stack=data["stack"],
            category=data["category"],
            tags=data["tags"],
            platforms=data["platforms"],
            maturity=maturity,
            validation=validation,
            worktree=worktree,
            operating_assumptions=data["operating_assumptions"],
            workflow_labels=data["workflow_labels"],
            commands=data.get("commands", {}),
            variables=variables,
            next_steps=data["next_steps"],
            template_dir=metadata_path.parent / "template",
        )
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise InvalidTemplateError(
            f"invalid metadata for template '{name}': {exc}"
        ) from exc


def load_templates(*, root: Path | None = None) -> list[TemplateDefinition]:
    """Load every available template."""
    definitions: list[TemplateDefinition] = []
    root = templates_root() if root is None else root
    for metadata_path in sorted(root.glob("*/template.json")):
        definitions.append(load_template(metadata_path.parent.name, root=root))
    return definitions
