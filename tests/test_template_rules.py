"""Pure built-in derivations and registry contracts, independent of CLI I/O."""

import subprocess
import sys
import unittest
from unittest.mock import patch

from biucingcli import cli
from biucingcli.errors import InvalidTemplateError
from biucingcli.template_rules import apple, android, microservice, registry
from biucingcli.template_rules.common import RuleResult


class TemplateRuleTests(unittest.TestCase):
    def test_apple_platforms_and_render_only_snippets(self):
        for platform, destination in (("ios", ".iOS"), ("macos", ".macOS"),
                                      ("watchos", ".watchOS"), ("tvos", ".tvOS")):
            with self.subTest(platform=platform):
                values = {"project_name": "my-app", "apple_platform": platform,
                          "minimum_os_version": "27.1", "display_name": 'A "quoted" name'}
                before = dict(values)
                result = apple.derive(values)
                self.assertEqual(values, before)
                self.assertEqual(result.derived_values["swift_module_name"], "MyApp")
                self.assertEqual(result.derived_values["tuist_destinations"], destination)
                self.assertEqual(result.derived_values["tuist_deployment_targets"], f'{destination}("27.1")')
                self.assertEqual(set(result.render_only_values),
                                 {"apple_scene_body", "apple_home_body", "apple_platform_output_note"})
                self.assertFalse(set(result.derived_values) & set(result.render_only_values))
                if platform == "macos":
                    self.assertIn('A \\"quoted\\" name', result.render_only_values["apple_scene_body"])
        default = apple.derive({"project_name": "demo", "swift_module_name": "Custom"})
        self.assertEqual(default.derived_values["apple_platform"], "ios")
        self.assertEqual(default.derived_values["minimum_os_version"], "26.0")
        self.assertEqual(default.derived_values["swift_module_name"], "Custom")

    def test_android_explicit_and_default_module_names(self):
        for explicit, expected in ((None, "MyApp"), ("", "MyApp"), ("Custom", "Custom")):
            values = {"project_name": "my_app"}
            if explicit is not None:
                values["kotlin_module_name"] = explicit
            before = dict(values)
            result = android.derive(values)
            self.assertEqual(result.derived_values, {"kotlin_module_name": expected})
            self.assertEqual(result.render_only_values, {})
            self.assertEqual(values, before)

    def test_microservice_components_are_independent(self):
        for database in ("none", "postgres"):
            for cache in ("none", "redis"):
                values = {"project_name": "my-service", "service_name": "database-name", "database": database, "cache": cache}
                before = dict(values)
                result = microservice.derive(values)
                self.assertEqual(result.derived_values["service_type_name"], "MyService")
                self.assertEqual(bool(result.derived_values["database_dsn"]), database == "postgres")
                self.assertEqual(bool(result.derived_values["cache_dsn"]), cache == "redis")
                self.assertEqual(values, before)
                if database == "postgres":
                    self.assertIn("/database-name?", result.derived_values["database_dsn"])
        default = microservice.derive({"project_name": "demo"})
        self.assertEqual(default.derived_values["database_dsn"], "")
        self.assertEqual(default.derived_values["cache_dsn"], "")

    def test_invalid_selections_preserve_errors(self):
        with self.assertRaisesRegex(ValueError, "Unsupported Apple platform"):
            apple.derive({"project_name": "demo", "apple_platform": "invalid"})
        with self.assertRaisesRegex(ValueError, "Unsupported database"):
            microservice.derive({"project_name": "demo", "database": "invalid"})
        with self.assertRaisesRegex(InvalidTemplateError, "unknown built-in template rule"):
            registry.get_rule("missing")

    def test_generic_fallback_and_missing_assigned_rule(self):
        for template in ("frontend", "worker", "harmonyos", "future-template"):
            self.assertEqual(registry.derive_template_values(template, {"project_name": "demo"}), RuleResult())
        with patch.object(registry, "TEMPLATE_RULES", {"fixture": "missing"}):
            with self.assertRaises(InvalidTemplateError):
                registry.derive_template_values("fixture", {})
        for name, rule_name, derive in (("apple", "apple", apple.derive),
                                        ("android", "android", android.derive),
                                        ("micro-service", "microservice", microservice.derive)):
            self.assertIs(registry.get_rule(rule_name), derive)
            values = {"project_name": "demo"}
            self.assertEqual(registry.derive_template_values(name, values), derive(values))

    def test_registry_protects_input_and_results_are_fresh(self):
        def mutating_fixture(values):
            values["project_name"] = "changed"
            return RuleResult(values)

        original = {"project_name": "demo"}
        with patch.object(registry, "RULES", {"android": mutating_fixture}):
            registry.derive_template_values("android", original)
        self.assertEqual(original, {"project_name": "demo"})
        first = registry.derive_template_values("apple", original)
        first.derived_values["swift_module_name"] = "changed"
        self.assertEqual(registry.derive_template_values("apple", original).derived_values["swift_module_name"], "Demo")

    def test_legacy_helpers_and_independent_imports(self):
        for name in ("default_swift_module_name", "apple_platform_config", "apple_platform_snippets"):
            self.assertIs(getattr(cli, name), getattr(apple, name))
        self.assertIs(cli.default_kotlin_module_name, android.default_kotlin_module_name)
        for module in ("apple", "android", "microservice", "registry"):
            with self.subTest(module=module):
                result = subprocess.run([
                    sys.executable, "-c", f"import biucingcli.template_rules.{module}; import sys; "
                    "assert 'biucingcli.cli' not in sys.modules; "
                    "assert 'biucingcli.templates' not in sys.modules; "
                    "assert 'biucingcli.generation' not in sys.modules",
                ], capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
