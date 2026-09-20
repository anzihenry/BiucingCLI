"""Terminal adapter used by the CLI and legacy interactive resolver entrypoints."""

import sys

from biucingcli.errors import InputEndedError
from biucingcli.models import TemplateVariable


def terminal_prompt(variable: TemplateVariable) -> str:
    print(variable.prompt or f"{variable.name}: ", end="", file=sys.stderr, flush=True)
    try:
        return input()
    except EOFError as exc:
        print(file=sys.stderr)
        raise InputEndedError(
            f"Input ended while reading {variable.name}; supply it with a flag or --set."
        ) from exc
    except KeyboardInterrupt:
        print(file=sys.stderr)
        raise
