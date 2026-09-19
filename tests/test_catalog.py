"""Stage 1 module boundaries and package resource loading contracts."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from biucingcli import catalog, errors, models, templates


class CatalogTests(unittest.TestCase):
    def test_foundation_modules_import_without_cli_or_compatibility_module(self):
        for module in ("errors", "models", "catalog"):
            with self.subTest(module=module):
                result = subprocess.run([
                    sys.executable, "-c",
                    f"import biucingcli.{module}; import sys; "
                    "assert 'biucingcli.cli' not in sys.modules; "
                    "assert 'biucingcli.templates' not in sys.modules",
                ], capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_legacy_exports_are_identical_objects(self):
        groups = [
            (errors, ("BiucingError", "UnknownTemplateError", "InvalidTemplateError",
                      "GenerationError", "GenerationConflictError", "MissingInputError", "InputEndedError")),
            (models, ("TemplateVariable", "ResolvedVariable", "TemplateMaturity", "TemplateValidation",
                      "TemplateWorktree", "TemplateDefinition", "VariableResolutionResult")),
            (catalog, ("templates_root", "load_template", "load_templates")),
        ]
        for module, names in groups:
            for name in names:
                with self.subTest(name=name):
                    self.assertIs(getattr(templates, name), getattr(module, name))
        self.assertTrue(issubclass(errors.GenerationConflictError, errors.GenerationError))
        self.assertTrue(issubclass(errors.GenerationError, errors.BiucingError))
        self.assertTrue(issubclass(errors.MissingInputError, ValueError))
        self.assertFalse(issubclass(errors.MissingInputError, errors.BiucingError))

    def test_bundled_catalog_is_sorted_and_independent_of_cwd(self):
        definitions = catalog.load_templates()
        names = [item.name for item in definitions]
        self.assertEqual(names, sorted(["frontend", "web-service", "microservice", "worker",
                                       "apple", "android", "harmonyos"]))
        for definition in definitions:
            self.assertIsInstance(definition, models.TemplateDefinition)
            self.assertTrue(definition.template_dir.is_dir())
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([
                sys.executable, "-c",
                "import json; from biucingcli.catalog import load_templates; "
                "print(json.dumps([x.name for x in load_templates()]))",
            ], cwd=tmp, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), names)

    def test_explicit_fixture_root_without_global_patch(self):
        original = catalog.load_template("frontend")
        source = (catalog.templates_root() / "frontend/template.json").read_text()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(catalog.load_templates(root=root), [])
            target = root / "frontend"
            target.mkdir()
            (target / "template.json").write_text(source)
            (target / "template").mkdir()
            loaded = catalog.load_template("frontend", root=root)
            self.assertEqual(loaded.to_dict(), original.to_dict())
            self.assertEqual(loaded.template_dir, target / "template")
            self.assertEqual(catalog.load_templates(root=root), [loaded])
            self.assertNotEqual(catalog.load_template("frontend").template_dir, loaded.template_dir)

    def test_missing_and_malformed_metadata_keep_domain_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(errors.UnknownTemplateError, "unknown template 'absent'"):
                catalog.load_template("absent", root=root)
            target = root / "bad"
            target.mkdir()
            for content in (b"{invalid", b"{}", b"\xff", b'{"variables": [null]}'):
                with self.subTest(content=content):
                    (target / "template.json").write_bytes(content)
                    with self.assertRaisesRegex(errors.InvalidTemplateError, "invalid metadata for template 'bad'"):
                        catalog.load_template("bad", root=root)
                    with self.assertRaises(errors.InvalidTemplateError):
                        catalog.load_templates(root=root)
