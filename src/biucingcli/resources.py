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


def _entries(root: Path, layer: str, context: str):
    def walk(directory):
        for path in sorted(directory.iterdir()):
            relative = path.relative_to(root).as_posix()
            info = path.lstat()
            if not normalized_path(relative):
                raise InvalidTemplateError(f"{context}: unsafe resource path: {relative!r}")
            if stat.S_ISLNK(info.st_mode):
                raise InvalidTemplateError(f"{context}: symlink resource forbidden: {relative}")
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


def resource_context(definition: TemplateDefinition, selected: str | None) -> str:
    return definition.name if selected is None else f"{definition.name}[{selected}]"


def _select_layers(definition: TemplateDefinition, selected: str | None):
    """Single authority for source layers used by enumeration and fingerprinting."""
    layers = [("common", definition.template_dir)]
    option = None
    if definition.variants is not None:
        if not isinstance(selected, str) or selected not in definition.variants.options:
            raise ValueError(
                f"{definition.name}: invalid resolved value for {definition.variants.selector!r}: {selected!r}"
            )
        option = definition.variants.options[selected]
        layers.append((selected, definition.template_dir.parent / option.source))
    elif selected is not None:
        raise ValueError(f"{definition.name}: ordinary resources cannot select a variant")
    return tuple(layers), option


def resolve_resources(definition: TemplateDefinition, values: Mapping[str, str]) -> ResolvedResources:
    """Compose sources using resolved inputs, without rendering or writing files.

    No defaults/prompts/derivations are applied here. Every layer uses the same
    strict path/type policy. Fingerprinting is separate from enumeration.
    """
    errors = variant_declaration_errors(definition)
    if errors:
        raise InvalidTemplateError("; ".join(errors))
    variants = definition.variants
    selected = values.get(variants.selector) if variants else None
    layers, option = _select_layers(definition, selected)
    context = resource_context(definition, selected)
    output = {}
    canonical = {}
    consumed = set()
    overrides = set(option.overrides) if option else set()
    try:
        for layer, root in layers:
            _check_root(root, definition.template_dir.parent, context)
            for entry in _entries(root, layer, context):
                path = entry.output_path
                key = collision_key(path)
                if key in canonical and canonical[key] != path:
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
    context = resource_context(definition, resources.selected_variant)
    try:
        # Injected definitions need not have a metadata file. Track its absence too.
        if metadata.exists() or metadata.is_symlink():
            metadata_mode = metadata.lstat().st_mode
            record((stat.S_IFMT(metadata_mode), stat.S_IMODE(metadata_mode),
                    str(metadata.readlink()) if metadata.is_symlink() else None))
            record(metadata.read_bytes())
        else:
            record(None)
        layers, _ = _select_layers(definition, resources.selected_variant)
        for layer, root in layers:
            _check_root(root, metadata_dir, context)
            record((layer, stat.S_IMODE(root.stat().st_mode)))
            for entry in _entries(root, layer, context):
                record(entry)
                if entry.kind == "file":
                    record(hashlib.sha256(entry.source.read_bytes()).hexdigest())
    except OSError as exc:
        raise InvalidTemplateError(f"{context}: cannot fingerprint resources: {exc}") from exc
    return digest.hexdigest()
