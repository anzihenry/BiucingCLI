"""Focused validation regression coverage; extracted without changing assertions."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from biucingcli.catalog import load_templates
from biucingcli.validation import validate_templates


from cli_support import CLIHelpers


class TemplateValidationTests(CLIHelpers, unittest.TestCase):
    def test_bundled_template_resources_are_complete(self):
        definitions = load_templates()

        self.assertEqual(len(definitions), 7)
        for definition in definitions:
            with self.subTest(template=definition.name):
                self.assertTrue((definition.template_dir / "README.md").is_file())
                self.assertTrue((definition.template_dir / "Makefile").is_file())
                self.assertTrue((definition.template_dir / ".gitignore").is_file())
        android = next(item for item in definitions if item.name == "android")
        self.assertTrue(
            (android.template_dir / "gradle" / "wrapper" / "gradle-wrapper.jar").is_file()
        )

    def test_validate_reports_new_contract_errors_for_invalid_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_root = Path(tmpdir) / "templates"
            bad_template_dir = templates_root / "broken-service"
            rendered_dir = bad_template_dir / "template"
            rendered_dir.mkdir(parents=True)
            (bad_template_dir / "template.json").write_text(
                json.dumps(
                    {
                        "name": "broken-service",
                        "description": "Broken service template",
                        "category": "backend",
                        "stack": ["Go"],
                        "tags": ["docker", "go", "service"],
                        "platforms": ["linux"],
                        "maturity": {
                            "level": "validated",
                            "summary": "Broken on purpose for validation coverage.",
                        },
                        "validation": {
                            "status": "real-build-verified",
                            "verification_tier": "wrong-tier",
                            "evidence": ["synthetic test fixture"],
                        },
                        "operating_assumptions": ["Synthetic test assumption."],
                        "workflow_labels": ["bootstrap", "wrong-label"],
                        "commands": {"bootstrap": "./bootstrap"},
                        "worktree": {
                            "support_level": "wrong-level",
                            "isolation_dimensions": ["wrong-dimension"],
                            "diagnostics": ["make worktree-info"],
                            "cleanup": ["make clean-worktree"],
                        },
                        "variables": [
                            {
                                "name": "project_name",
                                "required": True,
                                "validator": "wrong-validator",
                            },
                        ],
                        "next_steps": ["make bootstrap"],
                    }
                ),
                encoding="utf-8",
            )
            (rendered_dir / "Makefile").write_text("bootstrap:\n\t@true\n", encoding="utf-8")
            (rendered_dir / ".gitignore").write_text(".cache/\n", encoding="utf-8")
            (rendered_dir / ".dockerignore").write_text(".cache/\n", encoding="utf-8")
            (rendered_dir / "compose.dev.yaml").write_text("services: {}\n", encoding="utf-8")
            (rendered_dir / "go.mod").write_text("module example.com/broken\n", encoding="utf-8")
            (rendered_dir / "go.sum").write_text("", encoding="utf-8")
            (rendered_dir / "cmd").mkdir()
            (rendered_dir / "internal").mkdir()
            (rendered_dir / "configs").mkdir()
            (rendered_dir / "scripts").mkdir()

            with patch("biucingcli.catalog.templates_root", return_value=templates_root):
                errors = validate_templates()

            joined = "\n".join(errors)
            self.assertIn(
                "broken-service: validation.verification_tier must be one of: generated-project, real-build",
                joined,
            )
            self.assertIn(
                "broken-service: workflow_labels contain unsupported values: wrong-label",
                joined,
            )
            self.assertIn(
                "broken-service: worktree.support_level must be one of: partial, planned, worktree-ready",
                joined,
            )
            self.assertIn(
                "broken-service: worktree.isolation_dimensions contain unsupported values: wrong-dimension",
                joined,
            )
            self.assertIn(
                "broken-service: missing required starter entries: README.md, scripts/doctor",
                joined,
            )
            self.assertIn("commands missing required entries", joined)
            self.assertIn(
                "command 'bootstrap' must be exactly 'make bootstrap'",
                joined,
            )
            self.assertIn("uses unsupported validator 'wrong-validator'", joined)


if __name__ == "__main__":
    unittest.main()
