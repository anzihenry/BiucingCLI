"""Explicit built-in rule selection; unassigned templates use generic behavior."""

from collections.abc import Callable
from types import MappingProxyType

from biucingcli.errors import InvalidTemplateError
from biucingcli.template_rules import apple, android, microservice
from biucingcli.template_rules.common import RuleResult


RULES = MappingProxyType({
    "apple": apple.derive,
    "android": android.derive,
    "microservice": microservice.derive,
})
# Missing registered implementations must not silently use generic generation.
# Metadata declarations are a later-stage change.
TEMPLATE_RULES = MappingProxyType({
    "apple": "apple", "android": "android", "microservice": "microservice",
})


def get_rule(name: str) -> Callable[[dict[str, str]], RuleResult]:
    try:
        return RULES[name]
    except KeyError as exc:
        raise InvalidTemplateError(f"unknown built-in template rule '{name}'") from exc


def derive_template_values(template_name: str, values: dict[str, str]) -> RuleResult:
    rule_name = TEMPLATE_RULES.get(template_name)
    if rule_name is None:
        return RuleResult()
    # Rules receive a copy, never the caller's mutable resolution result.
    return get_rule(rule_name)(dict(values))
