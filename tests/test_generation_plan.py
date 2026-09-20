"""Typed planning, injected interaction and execution-time state contracts."""

from contextlib import redirect_stdout, redirect_stderr
from dataclasses import replace
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from biucingcli.catalog import load_template
from biucingcli.cli import build_create_plan, build_parser, create_manifest, CLI_VARIABLE_ARGUMENTS
from biucingcli.errors import GenerationConflictError, GenerationError, MissingInputError
from biucingcli.generation import build_generation_plan, execute_generation_plan
from biucingcli.models import CreateRequest, GenerationPlan, TemplateVariable
from biucingcli.variables import resolve_variables_detailed


class GenerationPlanTests(unittest.TestCase):
    def test_core_plan_and_execution_without_terminal_io(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()
            errors = io.StringIO()
            with patch("builtins.input", side_effect=AssertionError("no terminal")), \
                    redirect_stdout(output), redirect_stderr(errors):
                plan = build_generation_plan(CreateRequest("frontend", "demo", Path(tmp)))
                self.assertIsInstance(plan, GenerationPlan)
                self.assertEqual(list(Path(tmp).iterdir()), [])
                before = create_manifest(plan, "plan")
                self.assertFalse(before["target_exists"])
                execute_generation_plan(plan)
                after = create_manifest(plan, "create")
                self.assertTrue(after["target_exists"])
                self.assertTrue((plan.target_dir / "package.json").is_file())
                before.update(operation="create", target_exists=True)
                self.assertEqual(before, after)
            self.assertEqual(output.getvalue(), "")
            self.assertEqual(errors.getvalue(), "")

    def test_prompt_callback_and_source_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompts = []

            def prompt(variable):
                prompts.append(variable.name)
                return " example.com/demo "

            plan = build_generation_plan(CreateRequest("web-service", "demo", Path(tmp)), prompt=prompt)
            self.assertEqual(prompts, ["module_name"])
            self.assertEqual(plan.values["module_name"], "example.com/demo")
            item = next(v for v in plan.resolved_variables if v.name == "module_name")
            self.assertEqual(item.source, "prompted")
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_no_prompt_aggregates_missing_inputs_without_terminal(self):
        definition = replace(load_template("frontend"), variables=[
            TemplateVariable("first", required=True), TemplateVariable("second", required=True),
        ])
        with patch("builtins.input", side_effect=AssertionError("no terminal")):
            with self.assertRaisesRegex(MissingInputError, "first, second"):
                resolve_variables_detailed(definition, {})
        with self.assertRaisesRegex(MissingInputError, "Missing required value for first"):
            resolve_variables_detailed(definition, {}, prompt=lambda variable: "  ")

    def test_callback_cancellation_never_creates_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            for error in (EOFError(), KeyboardInterrupt()):
                with self.subTest(error=type(error).__name__):
                    with self.assertRaises(type(error)):
                        build_generation_plan(CreateRequest("web-service", "demo", Path(tmp)),
                                              prompt=unittest.mock.Mock(side_effect=error))
                    self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_execution_rechecks_existing_target_and_missing_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = build_generation_plan(CreateRequest("frontend", "demo", root))
            plan.target_dir.mkdir()
            sentinel = plan.target_dir / "sentinel"
            sentinel.write_text("keep")
            with self.assertRaises(GenerationConflictError):
                execute_generation_plan(plan)
            self.assertEqual(sentinel.read_text(), "keep")
            self.assertEqual(list(plan.target_dir.iterdir()), [sentinel])
            missing = root / "missing"
            plan = build_generation_plan(CreateRequest("frontend", "demo", missing))
            self.assertFalse(missing.exists())
            with self.assertRaises(GenerationError):
                execute_generation_plan(plan)
            self.assertFalse(missing.exists())

    def test_request_and_plan_maps_are_detached_and_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            supplied = {"display_name": "First"}
            explicit = {"display_name": "Explicit"}
            request = CreateRequest("frontend", "demo", Path(tmp), supplied, explicit)
            supplied["display_name"] = "mutated"
            explicit["display_name"] = "mutated"
            plan = build_generation_plan(request)
            self.assertEqual(plan.values["display_name"], "Explicit")
            with self.assertRaises(TypeError):
                plan.values["display_name"] = "mutated"
            with self.assertRaises(TypeError):
                request.set_values["display_name"] = "mutated"
            context = plan.to_context()
            context["values"]["display_name"] = "mutated"
            context["resolved_variables"][0]["value"] = "mutated"
            self.assertEqual(plan.values["display_name"], "Explicit")
            self.assertEqual(plan.resolved_variables[0].value, "demo")

    def test_cli_alias_map_and_core_priority(self):
        args = build_parser().parse_args(["create", "frontend", "demo"])
        self.assertEqual(CLI_VARIABLE_ARGUMENTS["apple_platform"], "platform")
        self.assertEqual(len(set(CLI_VARIABLE_ARGUMENTS.values())), len(CLI_VARIABLE_ARGUMENTS))
        operational = {"command", "template", "project_name", "output_dir", "set_values",
                       "non_interactive", "json", "dry_run", "plan"}
        self.assertEqual(set(vars(args)) - operational, set(CLI_VARIABLE_ARGUMENTS.values()))
        with tempfile.TemporaryDirectory() as tmp:
            request = CreateRequest("frontend", " demo ", Path(tmp),
                                    {"project_name": "ignored", "display_name": "set"},
                                    {"display_name": " explicit "})
            plan = build_generation_plan(request)
            self.assertEqual(plan.project_name, "demo")
            self.assertEqual(plan.values["display_name"], "explicit")
            cli_args = build_parser().parse_args([
                "create", "frontend", " demo ", "--output-dir", tmp, "--non-interactive",
                "--set", "project_name=ignored", "--set", "display_name=set", "--display-name", " explicit ",
            ])
            self.assertEqual(plan, build_create_plan(cli_args))

    def test_core_imports_do_not_load_cli_or_terminal_adapter(self):
        result = subprocess.run([
            sys.executable, "-c", "from biucingcli.generation import build_generation_plan; import sys; "
            "assert 'biucingcli.cli' not in sys.modules; "
            "assert 'biucingcli.interaction' not in sys.modules; "
            "assert 'biucingcli.templates' not in sys.modules",
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
