"""Filesystem generation with staging, publication and cleanup."""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
from pathlib import Path

from biucingcli.errors import BiucingError, GenerationConflictError, GenerationError
from biucingcli.models import TemplateDefinition
from biucingcli.rendering import render_text


def render_template(
    definition: TemplateDefinition,
    values: dict[str, str],
    target_dir: Path,
) -> None:
    """Copy and render a template into the target directory."""
    if target_dir.exists():
        raise GenerationConflictError(f"target directory already exists: {target_dir}")
    if not target_dir.parent.exists():
        raise GenerationError(f"output directory does not exist: {target_dir.parent}")
    if not target_dir.parent.is_dir():
        raise GenerationError(f"output path is not a directory: {target_dir.parent}")

    staging_root: Path | None = None
    try:
        staging_root = Path(
            tempfile.mkdtemp(prefix=f".{target_dir.name}.biucing-", dir=target_dir.parent)
        )
        rendered_dir = staging_root / "project"
        shutil.copytree(definition.template_dir, rendered_dir)

        for path in rendered_dir.rglob("*"):
            if not path.is_file():
                continue

            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            path.write_text(render_text(content, values), encoding="utf-8")
            if path.name == "gradlew" or "scripts" in path.parts:
                current_mode = path.stat().st_mode
                path.chmod(current_mode | stat.S_IXUSR)

        if target_dir.exists():
            raise GenerationConflictError(f"target directory already exists: {target_dir}")
        os.replace(rendered_dir, target_dir)
    except BiucingError:
        raise
    except OSError as exc:
        raise GenerationError(f"could not generate project at {target_dir}: {exc}") from exc
    finally:
        if staging_root is not None:
            shutil.rmtree(staging_root, ignore_errors=True)
