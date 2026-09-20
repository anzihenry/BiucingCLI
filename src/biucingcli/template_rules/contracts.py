"""Project-owned reusable file contracts, independent of display categories."""

from types import MappingProxyType


CONTRACTS = MappingProxyType({
    "base": frozenset({"README.md", "Makefile", ".gitignore", "scripts/doctor"}),
    "docker-compose": frozenset({".dockerignore", "compose.dev.yaml"}),
    "go-backend": frozenset({"go.mod", "go.sum", "cmd", "internal", "configs", "scripts"}),
    "native-tools": frozenset({".mise.toml", "scripts"}),
})
# Release policy: removing a built-in's declaration must not disable its gate.
BUILTIN_CONTRACTS = MappingProxyType({
    "frontend": frozenset({"docker-compose"}),
    "web-service": frozenset({"docker-compose", "go-backend"}),
    "worker": frozenset({"docker-compose", "go-backend"}),
    "microservice": frozenset({"docker-compose", "go-backend"}),
    "apple": frozenset({"native-tools"}),
    "android": frozenset({"native-tools"}),
    "harmonyos": frozenset({"native-tools"}),
})


def required_entries(definition):
    entries = set(CONTRACTS["base"])
    for name in set(definition.contracts) | BUILTIN_CONTRACTS.get(definition.name, frozenset()):
        entries.update(CONTRACTS.get(name, ()))
    entries.update(definition.required_entries)
    return entries
