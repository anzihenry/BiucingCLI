"""Shared generation contracts for ordinary and layered templates."""

from dataclasses import replace
import stat
import unittest
from unittest.mock import patch

from biucingcli import generation, presentation
from biucingcli.errors import GenerationError, GenerationConflictError, InvalidTemplateError
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
            for boundary in ("shutil.copy2", "render_text", "os.replace"):
                for error in (OSError("injected"), KeyboardInterrupt()):
                    with self.subTest(layered=layered, boundary=boundary, error=type(error)):
                        plan = self.plan(layered, "failure")
                        expected = GenerationError if isinstance(error, OSError) else KeyboardInterrupt
                        with patch(f"biucingcli.generation.{boundary}", side_effect=error):
                            with self.assertRaises(expected):
                                generation.execute_generation_plan(plan)
                        self.assertEqual(list(self.output.iterdir()), [])

    def test_shared_source_drift_rejects_before_staging(self):
        source = self.common / "README.md"
        for layered in (False, True):
            for change in ("bytes", "add", "remove", "mode", "root_mode", "metadata", "model"):
                with self.subTest(layered=layered, change=change):
                    plan = self.plan(layered, "drift")
                    content, mode = source.read_bytes(), stat.S_IMODE(source.stat().st_mode)
                    root_mode = stat.S_IMODE(self.common.stat().st_mode)
                    try:
                        if change == "bytes":
                            source.write_text("changed")
                        elif change == "add":
                            self.put("template/extra.txt")
                        elif change == "remove":
                            source.unlink()
                        elif change == "mode":
                            source.chmod(0o600)
                        elif change == "root_mode":
                            self.common.chmod(0o700)
                        elif change == "metadata":
                            (self.home / "template.json").write_text("{}")
                        else:
                            plan.definition.next_steps.append("changed")
                        with self.assertRaisesRegex(GenerationError, "changed"):
                            generation.execute_generation_plan(plan)
                        self.assertEqual(list(self.output.iterdir()), [])
                    finally:
                        source.write_bytes(content)
                        source.chmod(mode)
                        self.common.chmod(root_mode)
                        (self.common / "extra.txt").unlink(missing_ok=True)

    def test_shared_render_time_drift_cleans_staging(self):
        original = generation.render_text
        source = self.common / "README.md"
        content = source.read_bytes()
        for layered in (False, True):
            plan = self.plan(layered, "during-render")
            def mutate(text, values, definition):
                source.write_text("changed")
                return original(text, values, definition)
            try:
                with patch("biucingcli.generation.render_text", side_effect=mutate):
                    with self.assertRaisesRegex(GenerationError, "changed"):
                        generation.execute_generation_plan(plan)
                self.assertEqual(list(self.output.iterdir()), [])
            finally:
                source.write_bytes(content)

    def test_shared_readonly_modes_and_failure_cleanup(self):
        source = self.put("template/readonly/file", b"{{PROJECT_NAME}}", 0o444)
        source.parent.chmod(0o500)
        self.addCleanup(source.parent.chmod, 0o755)
        for layered in (False, True):
            plan = self.plan(layered, f"readonly-{int(layered)}")
            for error in (OSError("publish failed"), KeyboardInterrupt()):
                with self.subTest(layered=layered, error=type(error)):
                    expected = GenerationError if isinstance(error, OSError) else KeyboardInterrupt
                    with patch("biucingcli.generation.os.replace", side_effect=error):
                        with self.assertRaises(expected):
                            generation.execute_generation_plan(plan)
                    self.assertFalse(list(self.output.glob(".*.biucing-*")))
                    self.assertFalse(plan.target_dir.exists())
            generation.execute_generation_plan(plan)
            generated = plan.target_dir / "readonly/file"
            self.addCleanup(generated.parent.chmod, 0o755)
            self.assertEqual(generated.read_text(), plan.project_name)
            self.assertEqual(stat.S_IMODE(generated.stat().st_mode), 0o444)
            self.assertEqual(stat.S_IMODE(generated.parent.stat().st_mode), 0o500)
            self.assertEqual(source.read_text(), "{{PROJECT_NAME}}")

    def test_output_ancestors_do_not_control_executable_bits(self):
        self.output = self.output / "scripts"
        self.output.mkdir()
        self.put("template/plain.txt", b"text", 0o640)
        self.put("template/scripts/run", b"run", 0o640)
        self.put("template/gradlew", b"wrapper", 0o640)
        for layered in (False, True):
            plan = self.plan(layered, f"mode-{int(layered)}")
            generation.execute_generation_plan(plan)
            for name, expected in (("plain.txt", 0o640), ("scripts/run", 0o740), ("gradlew", 0o740)):
                self.assertEqual(stat.S_IMODE((plan.target_dir / name).stat().st_mode), expected)

    def test_shared_conflicts_preserve_target(self):
        for layered in (False, True):
            for kind in ("directory", "dangling", "late"):
                with self.subTest(layered=layered, kind=kind):
                    plan = self.plan(layered, f"conflict-{int(layered)}-{kind}")
                    def occupy(text="", values=None, definition=None):
                        plan.target_dir.mkdir(exist_ok=True)
                        (plan.target_dir / "sentinel").write_text("keep")
                        return text
                    if kind == "directory":
                        occupy()
                    elif kind == "dangling":
                        plan.target_dir.symlink_to(self.output / "missing")
                    with patch("biucingcli.generation.render_text", side_effect=occupy):
                        with self.assertRaises(GenerationConflictError):
                            generation.execute_generation_plan(plan)
                    if kind == "dangling":
                        self.assertTrue(plan.target_dir.is_symlink())
                    else:
                        self.assertEqual((plan.target_dir / "sentinel").read_text(), "keep")
                    self.assertFalse(list(self.output.glob(".*.biucing-*")))

    def test_shared_effective_validation_before_writes(self):
        for layered in (False, True):
            for name in ("README.md", "Makefile"):
                source = self.common / name
                content = source.read_bytes()
                try:
                    source.unlink()
                    with self.assertRaisesRegex(InvalidTemplateError, "missing"):
                        self.plan(layered, "invalid")
                    self.assertEqual(list(self.output.iterdir()), [])
                finally:
                    source.write_bytes(content)
            makefile = self.common / "Makefile"
            content = makefile.read_bytes()
            try:
                makefile.write_text("bootstrap:\n\t@true\n")
                with self.assertRaisesRegex(InvalidTemplateError, "command target"):
                    self.plan(layered, "invalid")
            finally:
                makefile.write_bytes(content)

    def test_shared_symlink_policy(self):
        link = self.common / "link"
        for layered in (False, True):
            for target in (self.common / ".hidden", self.common, self.home / "absent"):
                try:
                    link.symlink_to(target)
                    with self.assertRaisesRegex(InvalidTemplateError, "symlink"):
                        self.plan(layered, "symlink")
                    self.assertEqual(list(self.output.iterdir()), [])
                finally:
                    link.unlink()

    def test_shared_direct_entrypoint_and_incomplete_plans(self):
        def inventory(root):
            return {p.relative_to(root).as_posix():
                    (p.read_bytes() if p.is_file() else None, stat.S_IMODE(p.stat().st_mode))
                    for p in root.rglob("*")}
        for layered in (False, True):
            plan = self.plan(layered, f"entry-{int(layered)}")
            for changes in ({"resources": None}, {"resource_fingerprint": None}):
                with self.assertRaisesRegex(GenerationError, "build a new plan"):
                    generation.execute_generation_plan(replace(plan, **changes))
            generation.execute_generation_plan(plan)
            target = self.output / f"direct-{int(layered)}"
            with patch("biucingcli.generation.resolve_variables_detailed", side_effect=AssertionError("no resolution")), \
                    patch("biucingcli.generation.derive_template_values", side_effect=AssertionError("no derivation")):
                generation.render_template(plan.definition, dict(plan.values), target)
            self.assertEqual(inventory(plan.target_dir), inventory(target))
