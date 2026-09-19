"""Public JSON metadata must describe the actual validation contract."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from biucingcli import __version__
from biucingcli.templates import TemplateVariable, load_templates, variable_validation_error


class JSONContractTests(unittest.TestCase):
    def invoke(self, *args):
        result = subprocess.run([sys.executable, "-m", "biucingcli.cli", *args, "--json"],
                                capture_output=True, text=True, timeout=30)
        payload = json.loads(result.stderr if result.returncode else result.stdout)
        self.assertEqual(payload["schema_version"], 1)
        self.assertIs(type(payload["schema_version"]), int)
        self.assertEqual(payload["generator_version"], __version__)
        return result, payload

    def test_every_public_output_has_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            commands = [
                ["list"], ["info", "frontend"], ["validate"],
                ["create", "frontend", "demo", "--output-dir", tmp, "--dry-run"],
                ["create", "frontend", "demo", "--output-dir", tmp, "--plan"],
                ["create", "frontend", "demo", "--output-dir", tmp],
            ]
            for command in commands:
                with self.subTest(command=command):
                    result, _ = self.invoke(*command)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
            for command in (["info", "missing"], ["info"],
                            ["create", "web-service", "demo"]):
                with self.subTest(command=command):
                    result, payload = self.invoke(*command)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(payload["ok"])

    def test_list_and_info_constraints_match_source_definitions(self):
        _, listing = self.invoke("list")
        by_name = {item["name"]: item for item in listing["templates"]}
        for definition in load_templates():
            _, info = self.invoke("info", definition.name)
            self.assertEqual(info["variables"], by_name[definition.name]["variables"])
            for variable, metadata in zip(definition.variables, info["variables"], strict=True):
                self.assertEqual(metadata["name"], variable.name)
                self.assertEqual(metadata["validator"], variable.validator)
                self.assertEqual(metadata["choices"], variable.choices)
                for key in ("required", "default", "default_from", "prompt"):
                    self.assertEqual(metadata[key], getattr(variable, key))
                for key in ("minimum", "maximum"):
                    self.assertIn(key, metadata)

    def test_effective_ranges_agree_with_boundary_validation(self):
        cases = [
            (TemplateVariable("port", validator="port"), 1, 65535),
            (TemplateVariable("count", validator="positive-integer"), 1, None),
            (TemplateVariable("count", validator="positive-integer", minimum=0, maximum=4), 0, 4),
            (TemplateVariable("port", validator="port", minimum=100, maximum=200), 100, 200),
        ]
        for variable, minimum, maximum in cases:
            with self.subTest(variable=variable):
                metadata = variable.to_dict()
                self.assertEqual(metadata["minimum"], minimum)
                self.assertEqual(metadata["maximum"], maximum)
                self.assertIsNone(variable_validation_error(variable, str(minimum)))
                self.assertIsNotNone(variable_validation_error(variable, str(minimum - 1)))
                if maximum is not None:
                    self.assertIsNone(variable_validation_error(variable, str(maximum)))
                    self.assertIsNotNone(variable_validation_error(variable, str(maximum + 1)))
        text = TemplateVariable("text").to_dict()
        self.assertEqual(text["validator"], "text")
        self.assertEqual(text["choices"], [])
        self.assertIsNone(text["minimum"])
        self.assertIsNone(text["maximum"])

    def test_choices_are_enforced_and_exported_as_a_copy(self):
        variable = TemplateVariable("mode", choices=["scheduled", "oneshot"])
        metadata = variable.to_dict()
        for choice in metadata["choices"]:
            self.assertIsNone(variable_validation_error(variable, choice))
        self.assertIsNotNone(variable_validation_error(variable, "other"))
        metadata["choices"].append("other")
        self.assertNotIn("other", variable.choices)

    def test_json_golden_contracts(self):
        for name, args in (("list.json", ["list"]),
                           ("info-web-service.json", ["info", "web-service"])):
            with self.subTest(name=name):
                _, payload = self.invoke(*args)
                expected = json.loads((Path(__file__).parent / "golden" / name).read_text())
                # Release version changes do not change the JSON contract.
                expected["generator_version"] = __version__
                self.assertEqual(payload, expected)


if __name__ == "__main__":
    unittest.main()
