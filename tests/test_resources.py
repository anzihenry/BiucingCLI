"""Standalone resource variants: no generation or shipped template changes."""

from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from biucingcli.catalog import load_template, templates_root
from biucingcli.errors import InvalidTemplateError
from biucingcli.models import TemplateVariant, TemplateVariants
from biucingcli.resources import resolve_resources
from biucingcli.variables import resolve_variables_detailed


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / "fixture"
        self.common = self.home / "template"
        self.common.mkdir(parents=True)
        self.metadata = json.loads((templates_root() / "frontend/template.json").read_text())
        self.metadata.update(name="fixture", contracts=[], required_entries=[])
        self.metadata["variables"].append({
            "name": "rendering", "required": True, "validator": "text",
            "choices": ["csr", "ssg", "ssr"], "default": "csr",
        })
        self.metadata["variants"] = {"selector": "rendering", "options": {
            name: {"source": f"variants/{name}/template"} for name in ("csr", "ssg", "ssr")
        }}
        for name in ("csr", "ssg", "ssr"):
            (self.home / f"variants/{name}/template").mkdir(parents=True)
        self.put("template/.hidden", b"\x00\xff\r\n")
        self.put("template/scripts/doctor", b"{{PROJECT_NAME}}\n", 0o751)
        (self.common / "empty").mkdir()
        self.put("variants/csr/template/client.txt", b"csr")
        self.put("variants/ssg/template/static.txt", b"ssg")
        self.put("variants/ssr/template/server.txt", b"ssr")

    def put(self, path, content=b"test", mode=0o644):
        target = self.home / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        target.chmod(mode)
        return target

    def load(self, metadata=None):
        (self.home / "template.json").write_text(json.dumps(
            self.metadata if metadata is None else metadata
        ))
        return load_template("fixture", root=self.root)

    def resolve(self, mode="csr"):
        return resolve_resources(self.load(), {"rendering": mode})

    def test_load_models_without_exposing_internal_json(self):
        definition = self.load()
        self.assertEqual(definition.variants.selector, "rendering")
        self.assertEqual(definition.variants.options["csr"].source, "variants/csr/template")
        self.assertNotIn("variants", definition.to_dict())
        self.assertIsNone(load_template("frontend").variants)

    def test_new_models_copy_mutable_inputs(self):
        required = ["a"]
        steps = ["make build"]
        option = TemplateVariant("variants/csr/template", required_entries=required, next_steps=steps)
        options = {"csr": option}
        variants = TemplateVariants("rendering", options)
        required.append("b")
        steps.clear()
        options.clear()
        self.assertEqual(option.required_entries, ("a",))
        self.assertEqual(option.next_steps, ("make build",))
        self.assertIn("csr", variants.options)
        with self.assertRaises(TypeError):
            variants.options["ssr"] = option
        with self.assertRaises(FrozenInstanceError):
            option.source = "changed"

    def test_default_uses_existing_variable_resolution(self):
        definition = self.load()
        resolved = resolve_variables_detailed(definition, {"project_name": "demo"})
        resources = resolve_resources(definition, resolved.values)
        self.assertEqual(resources.selected_variant, "csr")
        for values in ({}, {"rendering": "auto"}, {"rendering": " csr "}, {"rendering": None}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                resolve_resources(definition, values)

    def test_deterministic_selection_preserves_bytes_modes_empty_dirs(self):
        definition = self.load()
        before = sorted(p.relative_to(self.home).as_posix() for p in self.home.rglob("*"))
        first = resolve_resources(definition, {"rendering": "csr"})
        self.assertEqual(first, resolve_resources(definition, {"rendering": "csr"}))
        paths = [item.output_path for item in first.entries]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(paths, [".hidden", "client.txt", "empty", "scripts", "scripts/doctor"])
        by_path = {item.output_path: item for item in first.entries}
        self.assertEqual(by_path[".hidden"].source.read_bytes(), b"\x00\xff\r\n")
        self.assertEqual(by_path["scripts/doctor"].source.read_bytes(), b"{{PROJECT_NAME}}\n")
        self.assertEqual(by_path["scripts/doctor"].mode, 0o751)
        self.assertEqual(by_path["empty"].kind, "directory")
        self.assertEqual(by_path["client.txt"].layer, "csr")
        self.assertEqual(before, sorted(p.relative_to(self.home).as_posix() for p in self.home.rglob("*")))
        with self.assertRaises(FrozenInstanceError):
            first.entries[0].mode = 0

    def test_each_mode_is_isolated(self):
        for mode, expected in (("csr", "client.txt"), ("ssg", "static.txt"), ("ssr", "server.txt")):
            with self.subTest(mode=mode):
                paths = {entry.output_path for entry in self.resolve(mode).entries}
                self.assertEqual(paths & {"client.txt", "static.txt", "server.txt"}, {expected})
                self.assertNotIn("template.json", paths)

    def test_explicit_override_and_directory_merge(self):
        self.put("template/client.txt", b"common")
        self.put("variants/csr/template/scripts/build", b"build")
        (self.common / "scripts").chmod(0o750)
        with self.assertRaisesRegex(InvalidTemplateError, "undeclared resource override"):
            self.resolve()
        self.metadata["variants"]["options"]["csr"]["overrides"] = ["client.txt"]
        entries = {e.output_path: e for e in self.resolve().entries}
        self.assertEqual(entries["client.txt"].source.read_bytes(), b"csr")
        self.assertEqual(entries["scripts"].mode, 0o750)
        self.assertEqual(entries["scripts"].layer, "common")
        self.assertIn("scripts/build", entries)

    def test_stale_override_and_file_directory_conflict(self):
        option = self.metadata["variants"]["options"]["csr"]
        for path in ("missing", "client.txt", "empty"):
            option["overrides"] = [path]
            with self.subTest(path=path), self.assertRaisesRegex(InvalidTemplateError, "stale"):
                self.resolve()
        option["overrides"] = ["scripts"]
        self.put("variants/csr/template/scripts")
        with self.assertRaisesRegex(InvalidTemplateError, "file/directory"):
            self.resolve()

    def test_reverse_file_directory_conflict(self):
        self.put("template/assets")
        self.put("variants/csr/template/assets/logo.svg")
        with self.assertRaisesRegex(InvalidTemplateError, "file/directory"):
            self.resolve()

    def test_case_and_unicode_conflicts_across_layers(self):
        # Separate roots work on case-insensitive and normalization-insensitive macOS too.
        for common, variant in (("Asset", "asset"), ("É", "E\u0301"),
                                ("Images/a", "images/b"), ("Straße/a", "STRASSE/b")):
            with self.subTest(common=common):
                a = self.put(f"template/{common}")
                b = self.put(f"variants/csr/template/{variant}")
                with self.assertRaisesRegex(InvalidTemplateError, "case/Unicode"):
                    self.resolve()
                a.unlink()
                b.unlink()
                if "/" in common:
                    a.parent.rmdir()
                    b.parent.rmdir()

    def test_invalid_schema_shapes_are_domain_errors(self):
        for value in (None, [], {}, {"selector": "rendering", "options": {}},
                      {"selector": 1, "options": {"csr": {}}},
                      {"selector": "rendering", "options": {}, "default": "csr"}):
            metadata = deepcopy(self.metadata)
            metadata["variants"] = value
            with self.subTest(value=value), self.assertRaises(InvalidTemplateError):
                self.load(metadata)
        for option in (None, [], {}, {"source": 1}, {"source": "variants/csr/template", "unknown": []}):
            metadata = deepcopy(self.metadata)
            metadata["variants"]["options"]["csr"] = option
            with self.subTest(option=option), self.assertRaises(InvalidTemplateError):
                self.load(metadata)

    def test_option_lists_have_strict_types_and_paths(self):
        for field in ("required_entries", "forbidden_entries", "overrides", "next_steps"):
            for value in (None, "foo", [1]):
                metadata = deepcopy(self.metadata)
                metadata["variants"]["options"]["csr"][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(InvalidTemplateError):
                    self.load(metadata)
        for field in ("required_entries", "forbidden_entries", "overrides"):
            for value in (["x", "x"], ["../x"], ["/x"], ["x//y"], ["x/./y"],
                          ["x\\y"], ["x\x00y"], ["C:/x"], ["*.js"], ["x/"]):
                metadata = deepcopy(self.metadata)
                metadata["variants"]["options"]["csr"][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(InvalidTemplateError):
                    self.load(metadata)

    def test_selector_contract(self):
        for changes in ({"choices": []}, {"choices": ["csr", "ssr"]},
                        {"choices": ["csr", "ssg", "ssr", "csr"]}, {"choices": [1]},
                        {"default": None}, {"default": "auto"}, {"default_from": "project_name"}):
            metadata = deepcopy(self.metadata)
            metadata["variables"][-1].update(changes)
            with self.subTest(changes=changes), self.assertRaises(InvalidTemplateError):
                self.load(metadata)
        for selector in ("missing", "Rendering"):
            metadata = deepcopy(self.metadata)
            metadata["variants"]["selector"] = selector
            with self.subTest(selector=selector), self.assertRaises(InvalidTemplateError):
                self.load(metadata)
        metadata = deepcopy(self.metadata)
        metadata["variables"].append(deepcopy(metadata["variables"][-1]))
        with self.assertRaises(InvalidTemplateError):
            self.load(metadata)
        metadata = deepcopy(self.metadata)
        metadata["derived_outputs"] = ["rendering"]
        with self.assertRaisesRegex(InvalidTemplateError, "overwrite the selector"):
            self.load(metadata)

    def test_source_paths_and_overlapping_roots(self):
        for source in ("variants", "../template", "/tmp", "variants//csr", "variants/./csr",
                       "variants/csr/../ssr", "template", "variants/ssr/template/child",
                       "variants/SSR/template", "variants/ssr", "variants/ssr/template"):
            metadata = deepcopy(self.metadata)
            metadata["variants"]["options"]["csr"]["source"] = source
            with self.subTest(source=source), self.assertRaises(InvalidTemplateError):
                self.load(metadata)

    def test_next_steps_and_additive_contracts(self):
        options = self.metadata["variants"]["options"]
        options["csr"].update(required_entries=["client.txt"], forbidden_entries=["server.txt"])
        inherited = self.resolve()
        self.assertEqual(inherited.next_steps, tuple(self.metadata["next_steps"]))
        self.assertTrue({"README.md", "Makefile", ".gitignore", "scripts/doctor", "client.txt"}
                        <= set(inherited.required_entries))
        self.assertEqual(inherited.forbidden_entries, ("server.txt",))
        options["csr"]["next_steps"] = []
        self.assertEqual(self.resolve().next_steps, ())
        options["csr"]["next_steps"] = ["make build {{PROJECT_NAME}}"]
        self.assertEqual(self.resolve().next_steps, ("make build {{PROJECT_NAME}}",))

    def test_required_forbidden_contradictions_include_common_contracts(self):
        for forbidden in ("scripts", "scripts/doctor", "README.md", "readme.md"):
            metadata = deepcopy(self.metadata)
            metadata["variants"]["options"]["csr"]["forbidden_entries"] = [forbidden]
            with self.subTest(forbidden=forbidden), self.assertRaisesRegex(InvalidTemplateError, "contradiction"):
                self.load(metadata)

    def test_symlinks_in_files_directories_and_root_ancestors(self):
        for relative, target in (("template/link", self.common / ".hidden"),
                                 ("template/link", self.common),
                                 ("template/link", self.home / "absent")):
            link = self.home / relative
            link.symlink_to(target)
            with self.subTest(target=target), self.assertRaisesRegex(InvalidTemplateError, "symlink"):
                self.resolve()
            link.unlink()
        moved = self.home / "moved"
        (self.home / "variants/csr").rename(moved)
        (self.home / "variants/csr").symlink_to(moved, target_is_directory=True)
        with self.assertRaisesRegex(InvalidTemplateError, "real directory"):
            self.resolve()

    def test_special_and_unsafe_resource_files(self):
        fifo = self.common / "pipe"
        os.mkfifo(fifo)
        with self.assertRaisesRegex(InvalidTemplateError, "special resource"):
            self.resolve()
        fifo.unlink()
        self.put("template/bad\\name")
        with self.assertRaisesRegex(InvalidTemplateError, "unsafe resource"):
            self.resolve()

    def test_missing_selected_tree_and_io_errors(self):
        (self.home / "variants/csr/template/client.txt").unlink()
        (self.home / "variants/csr/template").rmdir()
        with self.assertRaisesRegex(InvalidTemplateError, r"fixture\[csr\].*cannot read"):
            self.resolve()
        # Unselected source existence is not a selector/schema check.
        self.assertEqual(self.resolve("ssr").selected_variant, "ssr")
        with patch.object(Path, "iterdir", side_effect=PermissionError("denied")):
            with self.assertRaisesRegex(InvalidTemplateError, "denied"):
                self.resolve("ssr")

    def test_legacy_inventory_does_not_tighten_symlink_policy(self):
        metadata = deepcopy(self.metadata)
        del metadata["variants"]
        (self.common / "link").symlink_to(self.common / ".hidden")
        definition = self.load(metadata)
        resources = resolve_resources(definition, {})
        self.assertIsNone(resources.selector)
        self.assertIsNone(resources.selected_variant)
        link = next(e for e in resources.entries if e.output_path == "link")
        self.assertEqual(link.kind, "symlink")
        self.assertEqual(link.mode, stat.S_IMODE(link.source.lstat().st_mode))

    def test_resolver_revalidates_direct_model_changes(self):
        definition = self.load()
        changed = replace(definition, variants=TemplateVariants("missing", definition.variants.options))
        with self.assertRaises(InvalidTemplateError):
            resolve_resources(changed, {"missing": "csr"})

    def test_module_has_no_cli_rendering_or_generation_dependency(self):
        result = subprocess.run([sys.executable, "-c",
                                 "import biucingcli.resources; import sys; "
                                 "assert not any('biucingcli.' + name in sys.modules "
                                 "for name in ('cli', 'generation', 'rendering', 'templates'))"],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
