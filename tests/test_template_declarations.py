"""New-template onboarding and negative declaration boundaries."""

from dataclasses import replace
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from biucingcli.catalog import load_template, load_templates, templates_root
from biucingcli.cli import main
from biucingcli.declarations import declaration_errors
from biucingcli.errors import InvalidTemplateError
from biucingcli.generation import render_template
from biucingcli.models import TemplateVariable
from biucingcli.rendering import render_text, supported_placeholders
from biucingcli.template_rules.contracts import required_entries
from biucingcli.template_rules.registry import derive_template_values
from biucingcli.template_rules.common import RuleResult
from biucingcli.validation import (REQUIRED_COMMAND_CONTRACT, validate_templates,
                                   validate_template_placeholders, validate_template_required_files)


class DeclarationTests(unittest.TestCase):
    def test_built_in_required_entries_preserve_pre_migration_checks(self):
        expected = json.loads((Path(__file__).parent / "golden/required-entries.json").read_text())
        actual = {d.name: sorted(required_entries(d)) for d in load_templates()}
        self.assertEqual(actual, expected)

    def fixture(self, root):
        data = json.loads((templates_root() / "frontend/template.json").read_text())
        data.update(name="python-api", category="backend", stack=["Python"], tags=["python"],
                    contracts=[], required_entries=["pyproject.toml"], rule=None,
                    derived_outputs=[], render_outputs=[], next_steps=["cd {{PROJECT_NAME}}", "make test"])
        data["variables"] = [
            {"name": "project_name", "required": True, "validator": "project-name"},
            {"name": "greeting", "required": True, "validator": "text", "contexts": ["JSON"]},
        ]
        directory = root / "python-api"
        source = directory / "template"
        (source / "scripts").mkdir(parents=True)
        (directory / "template.json").write_text(json.dumps(data))
        (source / "README.md").write_text("# {{PROJECT_NAME}}\n{{GREETING}}\n")
        (source / ".gitignore").write_text(".venv/\n")
        (source / "scripts/doctor").write_text("#!/bin/sh\nexit 0\n")
        (source / "pyproject.toml").write_text('[project]\nname = "{{PROJECT_NAME}}"\nversion = "0.1.0"\n')
        (source / "settings.json").write_text('{"greeting":"{{GREETING_JSON}}"}\n')
        (source / "Makefile").write_text(".PHONY: " + " ".join(REQUIRED_COMMAND_CONTRACT) + "\n" +
                                        "".join(f"{cmd}:\n\t@true\n" for cmd in REQUIRED_COMMAND_CONTRACT))
        return load_template("python-api", root=root)

    def test_new_python_template_load_validate_preview_generate_without_registry_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "catalog"
            definition = self.fixture(root)
            output = Path(tmp) / "output"
            output.mkdir()
            value = '你好 "quoted" \\ $HOME {{PROJECT_NAME}}'
            args = ["create", "python-api", "demo", "--output-dir", str(output),
                    "--set", "greeting=" + value, "--non-interactive", "--json"]
            with patch("biucingcli.catalog.templates_root", return_value=root):
                self.assertEqual(validate_templates(), [])
                self.assertNotIn("go.mod", required_entries(definition))
                self.assertEqual(derive_template_values(definition, {"project_name": "demo"}), RuleResult())
                preview = io.StringIO()
                with redirect_stdout(preview):
                    main([*args, "--plan"])
                self.assertEqual(list(output.iterdir()), [])
                self.assertEqual(json.loads(preview.getvalue())["derived_values"], {})
                created = io.StringIO()
                with redirect_stdout(created):
                    main(args)
                self.assertEqual(json.loads((output / "demo/settings.json").read_text())["greeting"], value)
                self.assertTrue(json.loads(created.getvalue())["target_exists"])
                self.assertFalse((output / "demo/go.mod").exists())

    def test_template_scope_does_not_leak_other_template_variables(self):
        definition = load_template("frontend")
        self.assertNotIn("{{BUNDLE_IDENTIFIER}}", supported_placeholders(definition))
        with self.assertRaisesRegex(InvalidTemplateError, "unsupported placeholder"):
            render_text("{{BUNDLE_IDENTIFIER}}", {"bundle_identifier": "com.example.demo"}, definition)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            (source / "file.txt").write_text("{{BUNDLE_IDENTIFIER}}")
            fixture = replace(definition, template_dir=source)
            self.assertTrue(validate_template_placeholders(fixture))
            with self.assertRaises(InvalidTemplateError):
                render_template(fixture, {}, Path(tmp) / "result")
            self.assertFalse((Path(tmp) / "result").exists())
            self.assertEqual(list(Path(tmp).iterdir()), [source])

    def test_bad_names_contexts_and_binding_collisions(self):
        definition = replace(load_template("frontend"), name="fixture", contracts=[], required_entries=[])
        cases = [
            [TemplateVariable("bad-name")],
            [TemplateVariable("UPPER")],
            [TemplateVariable("title", contexts=["UNKNOWN"])],
            [TemplateVariable("title", contexts=["JSON", "JSON"])],
            [TemplateVariable("title"), TemplateVariable("title")],
            [TemplateVariable("title", contexts=["JSON"]), TemplateVariable("title_json")],
            [TemplateVariable("title", validator="undeclared-custom-validator")],
        ]
        for variables in cases:
            with self.subTest(variables=variables):
                self.assertTrue(declaration_errors(replace(definition, variables=variables)))

    def test_new_free_text_is_not_allowed_raw_in_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            definition = self.fixture(Path(tmp))
            (definition.template_dir / "settings.json").write_text('{"label":"{{GREETING}}"}')
            self.assertTrue(any("explicit context" in e for e in validate_template_placeholders(definition)))
            with self.assertRaises(InvalidTemplateError):
                render_template(definition, {"project_name": "demo", "greeting": '"'}, Path(tmp) / "result")
            (definition.template_dir / "settings.json").write_text('{"label":"{{GREETING_XML}}"}')
            self.assertTrue(any("unsupported placeholder" in e for e in validate_template_placeholders(definition)))

    def test_contract_removal_unknown_contract_and_unsafe_paths(self):
        self.assertTrue(declaration_errors(replace(load_template("worker"), contracts=[])))
        definition = replace(load_template("frontend"), name="fixture", contracts=[])
        for contracts, entries in [(["unknown"], []), (["base", "base"], []),
                                   ([], ["../escape"]), ([], ["/absolute"]), ([], ["a\\b"]),
                                   ([], ["a//b"]), ([], ["."]), ([], ["same", "same"])]:
            with self.subTest(contracts=contracts, entries=entries):
                self.assertTrue(declaration_errors(replace(definition, contracts=contracts, required_entries=entries)))

    def test_rule_and_output_declarations_are_checked(self):
        apple = load_template("apple")
        for fixture in (replace(apple, rule=None), replace(apple, rule="missing"),
                        replace(apple, derived_outputs=[]),
                        replace(apple, render_outputs=apple.render_outputs + ["extra"]),
                        replace(apple, derived_outputs=apple.derived_outputs * 2),
                        replace(apple, variables=apple.variables + [TemplateVariable("apple_scene_body")])):
            with self.subTest(fixture=fixture.rule):
                self.assertTrue(declaration_errors(fixture))
        with patch("biucingcli.template_rules.registry.RULES", {"apple": lambda values: RuleResult()}):
            with self.assertRaisesRegex(InvalidTemplateError, "undeclared or missing"):
                derive_template_values(apple, {"project_name": "demo"})

    def test_invalid_declaration_fails_cli_before_prompt_or_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            definition = self.fixture(root)
            path = definition.template_dir.parent / "template.json"
            data = json.loads(path.read_text())
            data["variables"][1]["contexts"] = ["INVALID"]
            path.write_text(json.dumps(data))
            stderr = io.StringIO()
            with patch("biucingcli.catalog.templates_root", return_value=root), \
                    patch("builtins.input", side_effect=AssertionError("must not prompt")), \
                    redirect_stderr(stderr), redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    main(["create", "python-api", "demo", "--output-dir", tmp, "--json"])
            self.assertEqual(error.exception.code, 1)
            self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "invalid_template")
            self.assertFalse((root / "demo").exists())

    def test_metadata_extension_types_fail_as_domain_errors(self):
        for field, value in (("contracts", "go-backend"), ("required_entries", [1]),
                             ("derived_outputs", {}), ("render_outputs", None), ("rule", [])):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                definition = self.fixture(Path(tmp))
                path = definition.template_dir.parent / "template.json"
                data = json.loads(path.read_text())
                data[field] = value
                path.write_text(json.dumps(data))
                with self.assertRaises(InvalidTemplateError):
                    load_template("python-api", root=Path(tmp))

    def test_base_and_declared_required_entries_remain_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            definition = self.fixture(Path(tmp))
            (definition.template_dir / "README.md").unlink()
            (definition.template_dir / "pyproject.toml").unlink()
            message = " ".join(validate_template_required_files(definition))
            self.assertIn("README.md", message)
            self.assertIn("pyproject.toml", message)
