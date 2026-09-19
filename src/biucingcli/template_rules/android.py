"""Android module-name derivation."""

from biucingcli.template_rules.common import RuleResult, default_type_name

default_kotlin_module_name = default_type_name


def derive(values: dict[str, str]) -> RuleResult:
    return RuleResult({"kotlin_module_name": values.get("kotlin_module_name")
                       or default_kotlin_module_name(values["project_name"])})
