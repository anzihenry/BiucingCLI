"""Expected domain failures shared by the CLI and generation core."""

class BiucingError(Exception):
    """Base class for expected, user-facing CLI failures."""


class UnknownTemplateError(BiucingError):
    """Raised when a requested template does not exist."""


class InvalidTemplateError(BiucingError):
    """Raised when bundled template metadata cannot be loaded."""


class GenerationError(BiucingError):
    """Raised when a project cannot be generated safely."""


class GenerationConflictError(GenerationError):
    """Raised when generation would overwrite an existing path."""


class MissingInputError(ValueError):
    """Required variables were not supplied."""


class InputEndedError(BiucingError):
    """Interactive input ended before a required value was supplied."""
