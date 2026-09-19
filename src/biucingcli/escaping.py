"""Escapes for explicit template insertion contexts (without surrounding quotes)."""

import html
import json


def json_string(value: str) -> str:
    """JSON and double-quoted JS/TS/Go string contents."""
    return (json.dumps(value, ensure_ascii=False)[1:-1]
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def swift_string(value: str) -> str:
    """Swift string contents, including protection against interpolation."""
    return "".join(
        "\\" + char if char in ('\\', '"')
        else f"\\u{{{ord(char):x}}}" if ord(char) < 32 or char in "\u2028\u2029"
        else char
        for char in value
    )


def android_string(value: str) -> str:
    """Android resource quoting followed by XML escaping."""
    content = value.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'")
    # Quotes preserve internal whitespace and prevent leading @/? references.
    return html.escape('"' + content + '"', quote=True)


def docker_string(value: str) -> str:
    """Double-quoted Dockerfile ENV contents; prevent environment expansion."""
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$")


CONTEXT_ESCAPERS = {
    "JSON": json_string,
    "XML": lambda value: html.escape(value, quote=True),
    "SWIFT": swift_string,
    "KOTLIN": lambda value: json_string(value).replace("$", "\\$"),
    "JS_SINGLE": lambda value: json_string(value).replace("'", "\\'"),
    "ANDROID": android_string,
    "DOCKER": docker_string,
}

FREE_TEXT_KEYS = ("display_name", "organization_name", "otel_exporter_endpoint")
