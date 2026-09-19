"""Generated serialization formats must parse, including special input variants."""

import io
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest

from biucingcli.cli import main
from scripts.config_validation import ConfigurationError, parse_configuration, validate_configurations


class ConfigurationTests(unittest.TestCase):
    def test_all_templates_and_variants_parse(self):
        variants = [
            ("frontend", []),
            ("web-service", ["--module-name", "example.com/demo"]),
            ("worker", ["--module-name", "example.com/demo"]),
            ("android", ["--package-name", "com.example.demo"]),
            ("harmonyos", ["--bundle-name", "com.example.demo"]),
        ]
        variants += [("apple", ["--bundle-identifier", "com.example.demo", "--platform", platform])
                     for platform in ("ios", "macos", "watchos", "tvos")]
        variants += [("microservice", ["--module-name", "example.com/demo", "--proto-package", "demo.v1",
                                       "--dependency-store", store]) for store in ("postgres", "redis")]
        seen = set()
        for template, options in variants:
            with self.subTest(template=template, options=options), tempfile.TemporaryDirectory() as tmp:
                if template in {"frontend", "apple", "android", "harmonyos"}:
                    options = options + ["--display-name", '''R&D "引号" <研发> \\ $HOME''']
                with redirect_stdout(io.StringIO()):
                    main(["create", template, "demo", "--output-dir", tmp, "--non-interactive", *options])
                counts = validate_configurations(Path(tmp) / "demo")
                self.assertGreater(sum(counts.values()), 0)
                seen.update(counts)
        self.assertTrue({".json", ".json5", ".yaml", ".yml", ".toml", ".xml"}.issubset(seen))

    def test_invalid_config_reports_relative_path(self):
        cases = {"bad.json": '{"name": "unescaped "quote""}',
                 "bad.json5": '{ name: "unterminated }',
                 "bad.yaml": 'service: [broken',
                 "bad.toml": 'name = "unterminated',
                 "bad.xml": '<name>R&D</name>',
                 "bad.plist": '<plist><dict>'}
        for name, content in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / name
                path.write_text(content)
                with self.assertRaisesRegex(ConfigurationError, name):
                    validate_configurations(Path(tmp))

    def test_duplicate_keys_and_unsafe_yaml_are_rejected(self):
        cases = [(".json", '{"x": 1, "x": 2}'), (".json", '{"x": NaN}'),
                 (".json5", '{x: 1, x: 2}'), (".yml", 'x: 1\nx: 2'),
                 (".yaml", '!!python/object/apply:os.system ["false"]')]
        for suffix, text in cases:
            with self.subTest(suffix=suffix, text=text), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / ("bad" + suffix)
                path.write_text(text)
                with self.assertRaises(ConfigurationError):
                    validate_configurations(Path(tmp))

    def test_json5_comments_and_yaml_merges_are_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json5"
            path.write_text("{ // comment\n name: 'demo', }")
            self.assertEqual(parse_configuration(path), {"name": "demo"})
            path = Path(tmp) / "config.yaml"
            path.write_text("base: &base {port: 8080}\nservice: {<<: *base, port: 9090}\n")
            self.assertEqual(parse_configuration(path)[0]["service"]["port"], 9090)

    def test_dotfiles_and_plists_are_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".config.toml").write_text('name = "demo"')
            (root / "Info.plist").write_text(
                '<?xml version="1.0"?><plist version="1.0"><dict><key>Name</key><string>Demo</string></dict></plist>')
            self.assertEqual(validate_configurations(root), {".toml": 1, ".plist": 1})


if __name__ == "__main__":
    unittest.main()
