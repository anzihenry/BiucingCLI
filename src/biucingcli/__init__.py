"""BiucingCLI package."""

from importlib import resources
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

__all__ = ["__version__", "load_default_config"]

__version__ = "0.2.0"


def load_default_config() -> dict[str, Any]:
    """Load the built-in YAML configuration shipped with the package."""
    with resources.files("biucingcli.data").joinpath("defaults.yaml").open(
        "r", encoding="utf-8"
    ) as handle:
        return cast(dict[str, Any], yaml.safe_load(handle) or {})
