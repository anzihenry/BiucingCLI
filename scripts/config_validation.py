"""Parse generated configuration files; development tooling, not a CLI dependency."""

import json
import plistlib
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.parsers.expat import ExpatError

import json5
import yaml


class ConfigurationError(ValueError):
    """A generated file is not valid in its declared serialization format."""


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f"non-JSON numeric constant: {value}")


class UniqueSafeLoader(yaml.SafeLoader):
    """Safe YAML loading with duplicate mapping keys rejected."""

    def construct_mapping(self, node, deep=False):
        # Validate literal keys before resolving merges so YAML overrides work.
        keys = []
        for key_node, value_node in node.value:
            if key_node.tag != "tag:yaml.org,2002:merge":
                keys.append((self.construct_object(key_node, deep=deep), None))
        unique_object(keys)
        return super().construct_mapping(node, deep=deep)


def parse_configuration(path: Path):
    """Parse a known format without executing tags, includes, or external tools."""
    suffix = path.suffix.lower()
    if suffix in {".plist", ".entitlements"}:
        return plistlib.loads(path.read_bytes())
    text = path.read_text(encoding="utf-8")
    if suffix == ".json":
        return json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid_constant)
    if suffix == ".json5":
        return json5.loads(text, allow_duplicate_keys=False)
    if suffix in {".yaml", ".yml"}:
        return list(yaml.load_all(text, Loader=UniqueSafeLoader))
    if suffix == ".toml":
        return tomllib.loads(text)
    if suffix == ".xml":
        return ET.fromstring(text)
    raise ValueError(f"unsupported configuration suffix: {suffix}")


CONFIG_SUFFIXES = {".json", ".json5", ".yaml", ".yml", ".toml", ".xml", ".plist", ".entitlements"}


def validate_configurations(root: Path) -> dict[str, int]:
    """Check every config in a freshly generated project, including dotfiles."""
    counts = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in CONFIG_SUFFIXES:
            continue
        try:
            parse_configuration(path)
        except (ValueError, TypeError, OSError, yaml.YAMLError, ET.ParseError,
                plistlib.InvalidFileException, ExpatError) as exc:
            raise ConfigurationError(f"{path.relative_to(root)}: {exc}") from exc
        suffix = path.suffix.lower()
        counts[suffix] = counts.get(suffix, 0) + 1
    return counts
