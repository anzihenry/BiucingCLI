"""Variant plans, effective validation, CLI contracts and staged publication."""

from contextlib import redirect_stdout, redirect_stderr
from dataclasses import replace
import io
import json
import stat
import unittest
from unittest.mock import patch

from biucingcli import cli, generation, presentation
from biucingcli.errors import GenerationError, GenerationConflictError, InvalidTemplateError
from biucingcli.models import CreateRequest
from biucingcli.template_rules.common import RuleResult
from test_resources import ResourceFixture


class VariantGenerationTests(ResourceFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.output = self.root / "output"
        self.output.mkdir()
        self.put("template/README.md", b"# {{DISPLAY_NAME}}\n")
        self.put("template/.gitignore", b"build/\n")
        commands = list(self.metadata["commands"])
        make = ".PHONY: " + " ".join(commands) + "\n" + "".join(f"{name}:\n\t@true\n" for name in commands)
        self.put("template/Makefile", make.encode())
        for mode in ("csr", "ssg", "ssr"):
            self.metadata["variants"]["options"][mode]["next_steps"] = [f"make build # {mode} {{{{PROJECT_NAME}}}}"]

    def plan(self, mode="csr", name="demo", **kwargs):
        return generation.build_generation_plan(
            CreateRequest("fixture", name, self.output, {"rendering": mode, **kwargs}),
            definition=self.load(),
        )

    def invoke(self, args):
        self.load()
        stdout, stderr = io.StringIO(), io.StringIO()
        status = 0
        with patch("biucingcli.catalog.templates_root", return_value=self.root), \
                patch("biucingcli.cli.terminal_prompt", side_effect=AssertionError("must not prompt")), \
                redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                cli.main(args)
            except SystemExit as exc:
                status = exc.code
        return status, stdout.getvalue(), stderr.getvalue()

    def test_plan_and_execution_share_counts_selection_and_steps(self):
        for mode, expected in (("csr", "client.txt"), ("ssg", "static.txt"), ("ssr", "server.txt")):
            plan = self.plan(mode, name=mode, display_name='A {{UNKNOWN}} & "B"')
            self.assertFalse(plan.target_dir.exists())
            preview = presentation.create_manifest(plan, "plan")
            self.assertEqual(preview["selected_variant"], {"selector": "rendering", "value": mode})
            self.assertEqual(preview["next_steps"], [f"make build # {mode} {mode}"])
            generation.execute_generation_plan(plan)
            actual = {p.relative_to(plan.target_dir).as_posix() for p in plan.target_dir.rglob("*")}
            self.assertEqual(actual, {e.output_path for e in plan.resources.entries})
            self.assertEqual(plan.template_file_count, sum(p.is_file() for p in plan.target_dir.rglob("*")))
            self.assertEqual(plan.template_top_level_entries, tuple(sorted(p.name for p in plan.target_dir.iterdir())))
            self.assertEqual(actual & {"client.txt", "static.txt", "server.txt"}, {expected})
            self.assertEqual((plan.target_dir / ".hidden").read_bytes(), b"\x00\xff\r\n")
            self.assertIn('A {{UNKNOWN}} & "B"', (plan.target_dir / "README.md").read_text())
            self.assertEqual(stat.S_IMODE((plan.target_dir / "scripts/doctor").stat().st_mode), 0o751)
            self.assertTrue((plan.target_dir / "empty").is_dir())

    def test_selected_effective_files_not_common_or_other_modes(self):
        self.put("template/client.txt", b"{{UNSUPPORTED}}")
        self.metadata["variants"]["options"]["csr"]["overrides"] = ["client.txt"]
        self.put("variants/ssr/template/server.txt", b"{{ANOTHER_UNKNOWN}}")
        plan = self.plan()
        generation.execute_generation_plan(plan)
        self.assertEqual((plan.target_dir / "client.txt").read_text(), "csr")
        with self.assertRaisesRegex(InvalidTemplateError, r"fixture\[ssr\].*unsupported placeholder"):
            self.plan("ssr")

    def test_effective_required_forbidden_and_make_checks(self):
        option = self.metadata["variants"]["options"]["csr"]
        option["required_entries"] = ["absent"]
        with self.assertRaisesRegex(InvalidTemplateError, r"fixture\[csr\].*absent"):
            self.plan()
        option["required_entries"] = ["client.txt"]
        option["forbidden_entries"] = ["private"]
        private = self.put("variants/csr/template/private/config", b"secret")
        with self.assertRaisesRegex(InvalidTemplateError, "forbidden entry"):
            self.plan()
        private.unlink()
        private.parent.rmdir()
        self.put("variants/csr/template/Makefile", b"bootstrap:\n\t@true\n")
        option["overrides"] = ["Makefile"]
        with self.assertRaisesRegex(InvalidTemplateError, "command target"):
            self.plan()
        self.assertEqual(list(self.output.iterdir()), [])

    def test_variant_free_text_and_next_step_placeholders(self):
        path = self.put("variants/csr/template/settings.json", b'{"name":"{{DISPLAY_NAME}}"}')
        with self.assertRaisesRegex(InvalidTemplateError, r"fixture\[csr\].*explicit context"):
            self.plan()
        path.write_text('{"name":"{{DISPLAY_NAME_JSON}}"}')
        plan = self.plan(display_name='X " & {{UNKNOWN}}')
        generation.execute_generation_plan(plan)
        self.assertEqual(json.loads((plan.target_dir / "settings.json").read_text())["name"], 'X " & {{UNKNOWN}}')
        self.metadata["variants"]["options"]["csr"]["next_steps"] = ["{{UNKNOWN}}"]
        with self.assertRaisesRegex(InvalidTemplateError, "next_steps"):
            self.plan(name="other")
        self.metadata["variants"]["options"]["csr"]["next_steps"] = []
        self.assertEqual(self.plan(name="empty").rendered_next_steps, ())

    def test_validate_all_modes_without_resolving_required_inputs(self):
        self.metadata["variables"].append({"name": "required_input", "required": True})
        self.put("variants/ssg/template/static.txt", b"{{UNKNOWN}}")
        server = self.home / "variants/ssr/template/server.txt"
        server.unlink()
        server.parent.rmdir()
        status, stdout, stderr = self.invoke(["validate", "--json"])
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        payload = json.loads(stderr)
        self.assertEqual(payload["error"]["code"], "validation_failed")
        self.assertIn("fixture[ssg]", str(payload["error"]["details"]))
        self.assertIn("fixture[ssr]", str(payload["error"]["details"]))
        self.assertNotIn("missing_input", stderr)

    def test_cli_info_list_plan_dry_run_and_create_json(self):
        for args in (["info", "fixture", "--json"], ["list", "--json"]):
            status, stdout, stderr = self.invoke(args)
            self.assertEqual((status, stderr), (0, ""))
            payload = json.loads(stdout)
            summary = payload["variants"] if args[0] == "info" else payload["templates"][0]["variants"]
            self.assertEqual(summary, {"selector": "rendering", "default": "csr", "choices": ["csr", "ssg", "ssr"]})
            self.assertNotIn(str(self.home), stdout)
        self.assertIn("default=csr", self.invoke(["info", "fixture"])[1])
        for flag in ("--plan", "--dry-run"):
            status, stdout, stderr = self.invoke([
                "create", "fixture", "demo", "--output-dir", str(self.output), "--json", flag,
            ])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(json.loads(stdout)["selected_variant"]["value"], "csr")
            self.assertEqual(list(self.output.iterdir()), [])
        status, stdout, stderr = self.invoke([
            "create", "fixture", "demo", "--output-dir", str(self.output), "--set", "rendering=ssr", "--json",
        ])
        self.assertEqual((status, stderr), (0, ""))
        self.assertEqual(json.loads(stdout)["selected_variant"]["value"], "ssr")
        self.assertTrue((self.output / "demo/server.txt").is_file())

    def test_cli_errors_keep_json_envelope_and_no_writes(self):
        base = ["create", "fixture", "demo", "--output-dir", str(self.output), "--json"]
        status, stdout, stderr = self.invoke(base + ["--set", "rendering=bad"])
        self.assertEqual((status, stdout), (2, ""))
        self.assertEqual(json.loads(stderr)["error"]["code"], "invalid_input")
        self.put("variants/csr/template/client.txt", b"{{BAD}}")
        status, stdout, stderr = self.invoke(base)
        self.assertEqual((status, stdout), (1, ""))
        self.assertEqual(json.loads(stderr)["error"]["code"], "invalid_template")
        self.assertEqual(list(self.output.iterdir()), [])

    def test_source_content_inventory_permissions_and_metadata_drift(self):
        for change in ("bytes", "add", "remove", "mode", "metadata", "model", "symlink", "root_mode"):
            with self.subTest(change=change):
                plan = self.plan(name=change)
                path = self.home / "variants/csr/template/client.txt"
                original = path.read_bytes()
                if change == "bytes":
                    path.write_bytes(b"changed")
                elif change == "add":
                    self.put("variants/csr/template/extra")
                elif change == "remove":
                    path.unlink()
                elif change == "mode":
                    path.chmod(0o600)
                elif change == "metadata":
                    (self.home / "template.json").write_text("{}")
                elif change == "model":
                    plan.definition.next_steps.append("changed")
                elif change == "root_mode":
                    path.parent.chmod(0o700)
                else:
                    path.unlink()
                    path.symlink_to(self.common / ".hidden")
                with self.assertRaisesRegex(GenerationError, "changed"):
                    generation.execute_generation_plan(plan)
                self.assertEqual(list(self.output.iterdir()), [])
                if path.is_symlink():
                    path.unlink()
                path.write_bytes(original)
                path.chmod(0o644)
                path.parent.chmod(0o755)
                (path.parent / "extra").unlink(missing_ok=True)

    def test_shadowed_source_drift_is_detected(self):
        common = self.put("template/client.txt", b"old")
        self.metadata["variants"]["options"]["csr"]["overrides"] = ["client.txt"]
        plan = self.plan()
        common.write_bytes(b"new")
        with self.assertRaises(GenerationError):
            generation.execute_generation_plan(plan)

    def test_changes_during_render_do_not_publish(self):
        plan = self.plan()
        def mutate(text, values, definition):
            (self.home / "variants/csr/template/client.txt").write_text("changed")
            return text
        with patch("biucingcli.generation.render_text", side_effect=mutate):
            with self.assertRaises(GenerationError):
                generation.execute_generation_plan(plan)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_failures_and_cancellation_clean_staging(self):
        for boundary in ("shutil.copy2", "render_text", "os.replace"):
            for exception in (OSError("injected"), KeyboardInterrupt()):
                plan = self.plan()
                with self.subTest(boundary=boundary, exception=exception), \
                        patch(f"biucingcli.generation.{boundary}", side_effect=exception):
                    expected = GenerationError if isinstance(exception, OSError) else KeyboardInterrupt
                    with self.assertRaises(expected):
                        generation.execute_generation_plan(plan)
                self.assertEqual(list(self.output.iterdir()), [])

    def test_readonly_directory_permissions_do_not_prevent_failure_cleanup(self):
        source = self.put("template/readonly/file", b"{{PROJECT_NAME}}", 0o444)
        source.parent.chmod(0o500)
        self.addCleanup(source.parent.chmod, 0o755)
        plan = self.plan()
        with patch("biucingcli.generation.os.replace", side_effect=OSError("publish failed")):
            with self.assertRaises(GenerationError):
                generation.execute_generation_plan(plan)
        self.assertEqual(list(self.output.iterdir()), [])
        self.assertEqual(stat.S_IMODE(source.parent.stat().st_mode), 0o500)
        generation.execute_generation_plan(plan)
        generated = plan.target_dir / "readonly/file"
        self.addCleanup(generated.parent.chmod, 0o755)
        self.assertEqual(generated.read_text(), "demo")
        self.assertEqual(stat.S_IMODE(generated.stat().st_mode), 0o444)
        self.assertEqual(stat.S_IMODE(generated.parent.stat().st_mode), 0o500)

    def test_direct_definition_mutation_and_broken_target_symlink(self):
        plan = self.plan()
        plan.target_dir.symlink_to(self.output / "absent")
        with self.assertRaises(GenerationConflictError):
            generation.execute_generation_plan(plan)
        plan.target_dir.unlink()
        changed = replace(plan, definition=replace(plan.definition, variants=None))
        with self.assertRaises(GenerationError):
            generation.execute_generation_plan(changed)

    def test_existing_and_late_target_conflicts(self):
        for late in (False, True):
            plan = self.plan(name=f"target-{int(late)}")
            def occupy(text="", values=None, definition=None):
                plan.target_dir.mkdir(exist_ok=True)
                (plan.target_dir / "sentinel").write_text("user data")
                return text
            if not late:
                occupy()
            with patch("biucingcli.generation.render_text", side_effect=occupy):
                with self.assertRaises(GenerationConflictError):
                    generation.execute_generation_plan(plan)
            self.assertEqual((plan.target_dir / "sentinel").read_text(), "user data")
            self.assertFalse(list(self.output.glob(f".{plan.project_name}.biucing-*")))

    def test_direct_render_and_incomplete_plan(self):
        plan = self.plan()
        with self.assertRaises(GenerationError):
            generation.execute_generation_plan(replace(plan, resources=None))
        generation.render_template(plan.definition, dict(plan.values), plan.target_dir)
        self.assertTrue((plan.target_dir / "client.txt").is_file())

    def test_rule_cannot_overwrite_selector_even_if_same_value(self):
        with patch("biucingcli.generation.derive_template_values", return_value=RuleResult({"rendering": "csr"})):
            with self.assertRaisesRegex(InvalidTemplateError, "overwrite"):
                self.plan()

    def test_legacy_output_omits_variant_fields(self):
        definition = cli.load_template("web-service")
        plan = generation.build_generation_plan(CreateRequest("web-service", "demo", self.output, {"module_name": "example.com/demo"}))
        self.assertIsNone(plan.resources)
        self.assertNotIn("variants", definition.to_dict())
        self.assertNotIn("selected_variant", presentation.create_manifest(plan, "plan"))
