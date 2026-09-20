"""Read-only resource selection; independent of CLI, rendering and generation."""

import stat
import hashlib
from collections.abc import Mapping
from pathlib import Path

from biucingcli.errors import InvalidTemplateError
from biucingcli.models import ResourceEntry, ResolvedResources, TemplateDefinition
from biucingcli.template_rules.contracts import required_entries
from biucingcli.variant_declarations import (
    collision_key, normalized_path, variant_declaration_errors,
)


def _check_root(root: Path, metadata_dir: Path, context: str) -> None:
    """Reject symlinks in every resource-root component below metadata_dir."""
    relative = root.relative_to(metadata_dir)
    current = metadata_dir
    for component in relative.parts:
        current = current / component
        mode = current.lstat().st_mode
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise InvalidTemplateError(f"{context}: resource root must be a real directory: {current}")


def _entries(root: Path, layer: str, context: str, *, strict: bool):
    def walk(directory):
        for path in sorted(directory.iterdir()):
            relative = path.relative_to(root).as_posix()
            info = path.lstat()
            if strict and not normalized_path(relative):
                raise InvalidTemplateError(f"{context}: unsafe resource path: {relative!r}")
            if stat.S_ISLNK(info.st_mode):
                if strict:
                    raise InvalidTemplateError(f"{context}: symlink resource forbidden: {relative}")
                kind = "symlink"
            elif stat.S_ISDIR(info.st_mode):
                kind = "directory"
            elif stat.S_ISREG(info.st_mode):
                kind = "file"
            else:
                raise InvalidTemplateError(f"{context}: special resource forbidden: {relative}")
            yield ResourceEntry(path, relative, layer, kind, stat.S_IMODE(info.st_mode))
            if kind == "directory":
                yield from walk(path)
    yield from walk(root)


def resolve_resources(definition: TemplateDefinition, values: Mapping[str, str]) -> ResolvedResources:
    """Compose sources using resolved inputs, without rendering or writing files.

    No defaults/prompts/derivations are applied here. Legacy symlinks are retained
    as inventory entries, not followed; legacy generation remains on its existing
    copytree path. Fingerprinting is explicit and separate from enumeration.
    """
    errors = variant_declaration_errors(definition)
    if errors:
        raise InvalidTemplateError("; ".join(errors))
    variants = definition.variants
    selected = None
    option = None
    context = definition.name
    if variants is not None:
        selected = values.get(variants.selector)
        if not isinstance(selected, str) or selected not in variants.options:
            raise ValueError(f"{definition.name}: invalid resolved value for {variants.selector!r}: {selected!r}")
        option = variants.options[selected]
        context = f"{definition.name}[{selected}]"
    layers = [("common", definition.template_dir)]
    if option is not None:
        layers.append((selected, definition.template_dir.parent / option.source))
    output = {}
    canonical = {}
    consumed = set()
    overrides = set(option.overrides) if option else set()
    try:
        for layer, root in layers:
            if variants is not None:
                _check_root(root, definition.template_dir.parent, context)
            for entry in _entries(root, layer, context, strict=variants is not None):
                path = entry.output_path
                key = collision_key(path)
                if variants is not None and key in canonical and canonical[key] != path:
                    raise InvalidTemplateError(
                        f"{context}: case/Unicode resource collision: {canonical[key]!r} and {path!r}"
                    )
                canonical[key] = path
                previous = output.get(path)
                if previous is not None:
                    if previous.kind == entry.kind == "directory":
                        continue  # Common directory permissions win deterministically.
                    if previous.kind != "file" or entry.kind != "file":
                        raise InvalidTemplateError(f"{context}: file/directory resource collision: {path}")
                    if path not in overrides:
                        raise InvalidTemplateError(f"{context}: undeclared resource override: {path}")
                    consumed.add(path)
                output[path] = entry
    except OSError as exc:
        raise InvalidTemplateError(f"{context}: cannot read resource tree: {exc}") from exc
    stale = overrides - consumed
    if stale:
        raise InvalidTemplateError(f"{context}: stale resource overrides: {', '.join(sorted(stale))}")
    return ResolvedResources(
        selector=variants.selector if variants else None,
        selected_variant=selected,
        entries=tuple(output[path] for path in sorted(output)),
        required_entries=tuple(sorted(required_entries(definition) | set(option.required_entries if option else ()))),
        forbidden_entries=option.forbidden_entries if option else (),
        next_steps=(option.next_steps if option and option.next_steps is not None else tuple(definition.next_steps)),
    )


def resource_fingerprint(definition: TemplateDefinition, resources: ResolvedResources) -> str:
    """Detect selected source/metadata drift, including shadowed common files.

    This is a consistency check, not a lock or persistent filesystem snapshot.
    Never follows resource symlinks; captures directory and file permission bits.
    """
    digest = hashlib.sha256()

    def record(value):
        encoded = repr(value).encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)

    record(definition)
    record(resources)
    metadata_dir = definition.template_dir.parent
    metadata = metadata_dir / "template.json"
    context = f"{definition.name}[{resources.selected_variant}]"
    try:
        # Injected definitions need not have a metadata file. Track its absence too.
        if metadata.exists() or metadata.is_symlink():
            metadata_mode = metadata.lstat().st_mode
            record((stat.S_IFMT(metadata_mode), stat.S_IMODE(metadata_mode),
                    str(metadata.readlink()) if metadata.is_symlink() else None))
            record(metadata.read_bytes())
        else:
            record(None)
        option = definition.variants.options[resources.selected_variant]
        for layer, root in (("common", definition.template_dir),
                            (resources.selected_variant, metadata_dir / option.source)):
            _check_root(root, metadata_dir, context)
            record((layer, stat.S_IMODE(root.stat().st_mode)))
            for entry in _entries(root, layer, context, strict=True):
                record(entry)
                if entry.kind == "file":
                    record(hashlib.sha256(entry.source.read_bytes()).hexdigest())
    except OSError as exc:
        raise InvalidTemplateError(f"{context}: cannot fingerprint resources: {exc}") from exc
    return digest.hexdigest()
