"""Shared generation contracts for ordinary and layered templates."""

from dataclasses import replace
import stat
import unittest
from unittest.mock import patch

from biucingcli import generation, presentation
from biucingcli.errors import GenerationError
from biucingcli.models import CreateRequest
from test_resources import ResourceFixture


class UnifiedGenerationTests(ResourceFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.output = self.root / "output"
        self.output.mkdir()
        self.put("template/README.md", b"{{DISPLAY_NAME}}\n")
        self.put("template/.gitignore", b"build/\n")
        commands = self.metadata["commands"]
        make = ".PHONY: " + " ".join(commands) + "\n"
        make += "".join(f"{name}:\n\t@true\n" for name in commands)
        self.put("template/Makefile", make.encode())

    def definition(self, layered):
        definition = self.load()
        return definition if layered else replace(definition, variants=None)

    def plan(self, layered, name):
        return generation.build_generation_plan(
            CreateRequest("fixture", name, self.output,
                          {"display_name": "Literal {{UNKNOWN}}"}),
            definition=self.definition(layered),
        )

    def test_shared_output_contract(self):
        for layered in (False, True):
            with self.subTest(layered=layered):
                plan = self.plan(layered, f"demo-{int(layered)}")
                self.assertFalse(plan.target_dir.exists())
                manifest = presentation.create_manifest(plan, "plan")
                self.assertEqual("selected_variant" in manifest, layered)
                generation.execute_generation_plan(plan)
                self.assertEqual((plan.target_dir / "README.md").read_text(),
                                 "Literal {{UNKNOWN}}\n")
                self.assertEqual((plan.target_dir / ".hidden").read_bytes(), b"\x00\xff\r\n")
                self.assertTrue((plan.target_dir / "empty").is_dir())
                self.assertEqual(stat.S_IMODE((plan.target_dir / "scripts/doctor").stat().st_mode), 0o751)
                self.assertEqual(plan.template_file_count,
                                 sum(p.is_file() for p in plan.target_dir.rglob("*")))
                self.assertEqual((plan.target_dir / "client.txt").exists(), layered)
                self.assertEqual((self.common / "README.md").read_text(), "{{DISPLAY_NAME}}\n")

    def test_shared_failure_cleanup_contract(self):
        for layered in (False, True):
            for boundary in ("render_text", "os.replace"):
                for error in (OSError("injected"), KeyboardInterrupt()):
                    with self.subTest(layered=layered, boundary=boundary, error=type(error)):
                        plan = self.plan(layered, "failure")
                        expected = GenerationError if isinstance(error, OSError) else KeyboardInterrupt
                        with patch(f"biucingcli.generation.{boundary}", side_effect=error):
                            with self.assertRaises(expected):
                                generation.execute_generation_plan(plan)
                        self.assertEqual(list(self.output.iterdir()), [])
