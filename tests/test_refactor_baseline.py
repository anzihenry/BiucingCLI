"""Characterization tests: preserve current behavior during kernel extraction."""

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from biucingcli.cli import build_create_context, build_parser
from biucingcli.templates import TemplateVariable, load_template, resolve_variables_detailed
from generation_baseline import CASES, collect_case, inventory


class RefactorBaselineTests(unittest.TestCase):
    def test_frontend_resource_layers_have_no_local_build_artifacts(self):
        # Include empty and ignored directories: Git and wheel file inventories
        # cannot reveal these, but the resource resolver copies directories too.
        root = Path(__file__).resolve().parents[1] / "src/biucingcli/template_data/frontend"
        forbidden = {".pnpm-store", "node_modules", ".react-router", "build",
                     "dist", "coverage", "test-results", "playwright-report"}
        polluted = sorted(path.relative_to(root).as_posix() for path in root.rglob("*")
                          if path.name in forbidden)
        self.assertEqual(polluted, [], f"Remove local artifacts from template layers: {polluted}")

    def test_generated_projects_match_baseline(self):
        expected = json.loads((Path(__file__).parent / "golden/generation-baseline.json").read_text())
        self.assertEqual(set(expected), set(CASES))
        for name in CASES:
            with self.subTest(case=name):
                actual = collect_case(name)
                self.assertEqual(actual["manifest"], expected[name]["manifest"])
                self.assertEqual(set(actual["entries"]), set(expected[name]["entries"]))
                for path, entry in actual["entries"].items():
                    with self.subTest(path=path):
                        self.assertEqual(entry, expected[name]["entries"][path])

    def test_generation_is_independent_of_temporary_root(self):
        for name in CASES:
            with self.subTest(case=name):
                self.assertEqual(collect_case(name), collect_case(name))

    def test_inventory_detects_bytes_permissions_and_empty_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file = root / "binary"
            file.write_bytes(b"\x00\xff\r\n")
            before = inventory(root)
            file.write_bytes(b"\x00\xff\n")
            self.assertNotEqual(before, inventory(root))
            before = inventory(root)
            file.chmod(file.stat().st_mode ^ 0o100)
            self.assertNotEqual(before, inventory(root))
            before = inventory(root)
            (root / "empty").mkdir()
            self.assertNotEqual(before, inventory(root))

    def test_cli_priority_and_context_do_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = build_parser().parse_args([
                "create", "frontend", " demo ", "--output-dir", tmp, "--non-interactive",
                "--set", "project_name=ignored", "--set", "display_name=first",
                "--set", "display_name=second", "--display-name", " Explicit ",
            ])
            context = build_create_context(args)
            self.assertEqual(context["values"]["project_name"], "demo")
            self.assertEqual(context["values"]["display_name"], "Explicit")
            args.display_name = None
            self.assertEqual(build_create_context(args)["values"]["display_name"], "second")
            args.set_values = []
            context = build_create_context(args)
            self.assertEqual(context["values"]["display_name"], "Demo")
            source = {item["name"]: item["source"] for item in context["resolved_variables"]}
            self.assertEqual(source["display_name"], "provided")
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_resolution_defaults_and_declaration_order(self):
        definition = replace(load_template("frontend"), variables=[
            TemplateVariable("first", default=" fallback "),
            TemplateVariable("copy", default_from="first"),
            TemplateVariable("early", default_from="later"),
            TemplateVariable("later", default="last"),
        ])
        result = resolve_variables_detailed(definition, {"first": "  "}, interactive=False)
        self.assertEqual(result.values, {"first": " fallback ", "copy": " fallback ", "later": "last"})
        self.assertEqual([item.source for item in result.resolved_variables],
                         ["default", "default_from:first", "default"])
        result = resolve_variables_detailed(definition, {"first": " supplied "}, interactive=False)
        self.assertEqual(result.values["copy"], "supplied")
        self.assertEqual(result.resolved_variables[0].source, "provided")
