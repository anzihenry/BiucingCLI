"""Configuration loading helpers for BiucingCLI."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

from . import load_default_config

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "biucingcli" / "config.yaml"


def deep_merge(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge ``override`` into ``base`` and return the mutated ``base``."""
    for key, value in override.items():
        existing = base.get(key)
        if isinstance(value, Mapping) and isinstance(existing, dict):
            deep_merge(cast(dict[str, Any], existing), value)
        else:
            base[key] = value
    return base


def load_user_config(path: Path | None = None, *, strict: bool = False) -> dict[str, Any]:
    """Load a configuration file if it exists, returning an empty dict when absent."""
    target_path = path or DEFAULT_CONFIG_PATH
    if not target_path.exists():
        if strict:
            raise FileNotFoundError(f"Config file not found: {target_path}")
        return {}
    with target_path.open("r", encoding="utf-8") as handle:
        return cast(dict[str, Any], yaml.safe_load(handle) or {})


def build_config(user_path: Path | None = None, *, strict: bool = False) -> dict[str, Any]:
    """Combine built-in defaults with user overrides."""
    defaults = load_default_config()
    overrides = load_user_config(user_path, strict=strict)
    if overrides:
        deep_merge(defaults, overrides)
    return defaults


__all__ = ["DEFAULT_CONFIG_PATH", "build_config", "deep_merge", "load_user_config"]
