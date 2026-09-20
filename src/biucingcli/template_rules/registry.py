"""Explicit built-in rule selection; unassigned templates use generic behavior."""

from collections.abc import Callable
from types import MappingProxyType

from biucingcli.errors import InvalidTemplateError
from biucingcli.models import TemplateDefinition
from biucingcli.template_rules import apple, android, microservice
from biucingcli.template_rules.common import RuleResult


RULES = MappingProxyType({
    "apple": apple.derive,
    "android": android.derive,
    "microservice": microservice.derive,
})
# Built-in release policy and compatibility assignments for the string API.
# The generation path selects the rule from TemplateDefinition metadata.
TEMPLATE_RULES = MappingProxyType({
    "apple": "apple", "android": "android", "microservice": "microservice",
})


def get_rule(name: str) -> Callable[[dict[str, str]], RuleResult]:
    try:
        return RULES[name]
    except KeyError as exc:
        raise InvalidTemplateError(f"unknown built-in template rule '{name}'") from exc


OUTPUTS = MappingProxyType({
    "android": (frozenset({"kotlin_module_name"}), frozenset()),
    "apple": (frozenset({
        "apple_platform", "apple_platform_name", "fastlane_platform", "app_store_platform",
        "minimum_os_version", "tuist_destinations", "tuist_deployment_targets",
        "xcodebuild_destination", "swiftpm_supported_platform", "swift_module_name",
    }), frozenset({"apple_scene_body", "apple_home_body", "apple_platform_output_note"})),
    "microservice": (frozenset({
        "dependency_store", "dependency_store_image", "dependency_store_port",
        "dependency_store_dsn", "dependency_store_container_dsn", "dependency_store_env_block",
        "service_type_name",
    }), frozenset()),
})
OVERWRITES = MappingProxyType({
    "apple": frozenset({"apple_platform", "minimum_os_version", "swift_module_name"}),
    "android": frozenset({"kotlin_module_name"}),
    "microservice": frozenset({"dependency_store"}),
})


def rule_declaration_errors(definition: TemplateDefinition) -> list[str]:
    errors = []
    rule = definition.rule
    mandatory = TEMPLATE_RULES.get(definition.name)
    if mandatory and rule != mandatory:
        errors.append(f"{definition.name}: required built-in rule is {mandatory}")
    if rule is None:
        if definition.derived_outputs or definition.render_outputs:
            errors.append(f"{definition.name}: outputs require a registered rule")
        return errors
    if rule not in RULES or rule not in OUTPUTS:
        return errors + [f"{definition.name}: unknown built-in template rule '{rule}'"]
    derived, snippets = OUTPUTS[rule]
    if set(definition.derived_outputs) != derived or set(definition.render_outputs) != snippets:
        errors.append(f"{definition.name}: output declarations do not match rule '{rule}'")
    collisions = ({v.name for v in definition.variables} & (derived | snippets)) - OVERWRITES[rule]
    if collisions:
        errors.append(f"{definition.name}: rule output conflicts with input: {', '.join(sorted(collisions))}")
    return errors


def derive_template_values(template_name: str | TemplateDefinition, values: dict[str, str]) -> RuleResult:
    if isinstance(template_name, TemplateDefinition):
        errors = rule_declaration_errors(template_name)
        if errors:
            raise InvalidTemplateError("; ".join(errors))
        rule_name = template_name.rule
    else:
        # Compatibility for direct callers of the stage 3 helper.
        rule_name = TEMPLATE_RULES.get(template_name)
    if rule_name is None:
        return RuleResult()
    # Rules receive a copy, never the caller's mutable resolution result.
    result = get_rule(rule_name)(dict(values))
    if isinstance(template_name, TemplateDefinition):
        expected = OUTPUTS[rule_name]
        if (set(result.derived_values), set(result.render_only_values)) != expected:
            raise InvalidTemplateError(f"{template_name.name}: rule returned undeclared or missing outputs")
    return result
