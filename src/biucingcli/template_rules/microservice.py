"""Micro-service components and protocol type derivation."""
from biucingcli.template_rules.backend import components
from biucingcli.template_rules.common import RuleResult, default_type_name


def derive(values: dict[str, str]) -> RuleResult:
    result = components(values)
    return RuleResult({**result.derived_values, "service_type_name": default_type_name(values["project_name"])},
                      result.render_only_values)
