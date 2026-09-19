"""Direct contracts for the extracted rendering and filesystem boundaries."""

from dataclasses import replace
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from biucingcli import generation, rendering, templates, validation, variables
from biucingcli.catalog import load_template
from biucingcli.errors import GenerationConflictError, GenerationError


class GenerationTests(unittest.TestCase):
    def fixture(self, root):
        source = root / "source"
        source.mkdir()
        (source / "empty").mkdir()
        (source / "scripts").mkdir()
        (source / "scripts/run").write_text("{{PROJECT_NAME}}")
        (source / "scripts/run").chmod(0o640)
        (source / "binary").write_bytes(b"\xff\x00{{PROJECT_NAME}}")
        (source / "binary").chmod(0o600)
        return replace(load_template("frontend"), template_dir=source)

    def test_direct_render_preserves_binary_modes_and_single_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            definition = self.fixture(root)
            target = root / "output"
            generation.render_template(definition, {"project_name": "{{DISPLAY_NAME}}"}, target)
            self.assertEqual((target / "scripts/run").read_text(), "{{DISPLAY_NAME}}")
            self.assertEqual((target / "scripts/run").stat().st_mode & 0o777, 0o740)
            self.assertEqual((target / "binary").read_bytes(), b"\xff\x00{{PROJECT_NAME}}")
            self.assertEqual((target / "binary").stat().st_mode & 0o777, 0o600)
            self.assertTrue((target / "empty").is_dir())
            self.assertEqual((definition.template_dir / "scripts/run").read_text(), "{{PROJECT_NAME}}")
            self.assertEqual({p.name for p in root.iterdir()}, {"source", "output"})

    def test_failure_and_cancellation_cleanup_at_multiple_stages(self):
        for boundary in ("shutil.copytree", "render_text", "os.replace"):
            for exception in (OSError("injected"), KeyboardInterrupt()):
                with self.subTest(boundary=boundary, exception=type(exception).__name__), \
                        tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    definition = self.fixture(root)
                    expected = GenerationError if isinstance(exception, OSError) else KeyboardInterrupt
                    with patch(f"biucingcli.generation.{boundary}", side_effect=exception):
                        with self.assertRaises(expected):
                            generation.render_template(definition, {}, root / "output")
                    self.assertEqual({p.name for p in root.iterdir()}, {"source"})

    def test_existing_and_late_conflicts_preserve_target(self):
        for late in (False, True):
            with self.subTest(late=late), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                definition = self.fixture(root)
                target = root / "output"

                def occupy(text="", values=None):
                    target.mkdir(exist_ok=True)
                    (target / "sentinel").write_bytes(b"user data")
                    return text

                if not late:
                    occupy()
                with patch("biucingcli.generation.render_text", side_effect=occupy):
                    with self.assertRaises(GenerationConflictError):
                        generation.render_template(definition, {}, target)
                self.assertEqual((target / "sentinel").read_bytes(), b"user data")
                self.assertEqual({p.name for p in target.iterdir()}, {"sentinel"})
                self.assertEqual({p.name for p in root.iterdir()}, {"source", "output"})

    def test_moved_exports_keep_identity(self):
        for module, names in (
            (generation, ["render_template"]),
            (rendering, ["placeholder_map", "render_text", "supported_placeholders", "PLACEHOLDER_PATTERN"]),
            (variables, ["variable_validation_error", "validate_resolved_variables", "ALLOWED_VARIABLE_VALIDATORS"]),
            (validation, ["validate_templates", "validate_template_definition", "validate_template_required_files",
                          "validate_template_command_contract", "validate_template_placeholders", "REQUIRED_COMMAND_CONTRACT"]),
        ):
            for name in names:
                with self.subTest(name=name):
                    self.assertIs(getattr(templates, name), getattr(module, name))

    def test_extracted_modules_do_not_import_legacy_or_cli(self):
        for module in ("variables", "validation", "rendering", "generation"):
            with self.subTest(module=module):
                result = subprocess.run([
                    sys.executable, "-c", f"import biucingcli.{module}; import sys; "
                    "assert 'biucingcli.templates' not in sys.modules; "
                    "assert 'biucingcli.cli' not in sys.modules",
                ], capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
