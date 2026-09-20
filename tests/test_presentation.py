"""Presentation contracts without command dispatch or terminal writes."""

from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from biucingcli import __version__, cli, presentation
from biucingcli.catalog import load_template, load_templates
from biucingcli.generation import build_generation_plan
from biucingcli.models import CreateRequest


class PresentationTests(unittest.TestCase):
    def test_list_and_info_match_existing_goldens(self):
        golden = Path(__file__).parent / "golden"
        self.assertEqual(presentation.format_template_summary(load_templates()) + "\n",
                         (golden / "list.txt").read_text())
        self.assertEqual(presentation.format_template_info(load_template("web-service")) + "\n",
                         (golden / "info-web-service.txt").read_text())
        for filename, actual in (
            ("list.json", presentation.format_template_summary_json(load_templates())),
            ("info-web-service.json", presentation.format_template_info_json(load_template("web-service"))),
        ):
            expected = json.loads((golden / filename).read_text())
            expected["generator_version"] = __version__
            self.assertEqual(json.loads(actual), expected)

    def test_diagnostics_and_validation_keep_versioned_contract(self):
        self.assertEqual(presentation.format_error(False, "missing_input", "Missing input"),
                         "error: Missing input")
        for details in (None, [], ["broken"]):
            result = json.loads(presentation.format_error(True, "validation_failed", "Invalid", details))
            expected = {"code": "validation_failed", "message": "Invalid"}
            if details is not None:
                expected["details"] = details
            self.assertEqual(result, {"schema_version": 1, "generator_version": __version__,
                                      "ok": False, "error": expected})
        self.assertEqual(presentation.format_validation_report([]), "Template validation passed.")
        self.assertEqual(presentation.format_validation_report(["one", "two"]),
                         "Template validation failed:\n- one\n- two")
        result = json.loads(presentation.format_validation_report_json(["one"]))
        self.assertEqual(result["error_count"], 1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["schema_version"], 1)

    def test_plan_and_legacy_context_format_identically_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = build_generation_plan(CreateRequest("frontend", "demo", Path(tmp)))
            context = plan.to_context()
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                for mode in ("plan", "dry-run", "create"):
                    self.assertEqual(presentation.create_manifest(plan, mode),
                                     presentation.create_manifest(context, mode))
                    self.assertEqual(json.loads(presentation.format_create_json(plan, mode)),
                                     presentation.create_manifest(plan, mode))
                self.assertEqual(presentation.format_create_preview(plan, "plan"),
                                 presentation.format_create_preview(context, "plan"))
                self.assertEqual(presentation.format_create_success(plan),
                                 presentation.format_create_success(context))
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(list(Path(tmp).iterdir()), [])
            self.assertFalse(presentation.create_manifest(plan, "plan")["target_exists"])
            plan.target_dir.mkdir()
            self.assertTrue(presentation.create_manifest(plan, "plan")["target_exists"])

    def test_legacy_formatter_entrypoints_remain_compatible(self):
        for name in ("output_metadata", "create_manifest", "format_create_preview", "format_create_success",
                     "format_validation_report", "format_validation_report_json"):
            self.assertIs(getattr(cli, name), getattr(presentation, name))
        self.assertEqual(cli.JSON_SCHEMA_VERSION, presentation.JSON_SCHEMA_VERSION)
        self.assertEqual(cli.format_template_summary(), presentation.format_template_summary(load_templates()))
        self.assertEqual(cli.format_template_summary_json(), presentation.format_template_summary_json(load_templates()))
        self.assertEqual(cli.format_template_info("frontend"), presentation.format_template_info(load_template("frontend")))
        self.assertEqual(cli.format_template_info_json("frontend"), presentation.format_template_info_json(load_template("frontend")))

    def test_presentation_import_does_not_load_execution_layers(self):
        result = subprocess.run([
            sys.executable, "-c", "import biucingcli.presentation; import sys; "
            "assert not any('biucingcli.' + name in sys.modules for name in "
            "['cli', 'catalog', 'templates', 'generation', 'interaction', 'validation'])",
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
