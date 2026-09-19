"""Regression checks for user text in generated language/resource contexts."""

import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from html.parser import HTMLParser
from pathlib import Path
from dataclasses import replace
from suite_support import android_test, platform_test

from biucingcli.cli import main
from biucingcli.escaping import swift_string
from biucingcli.templates import load_template, render_text, validate_template_placeholders, validate_templates


SAMPLES = [
    "R&D",
    '''O'Reilly "Studio" <研发> & friends''',
    r'Path\name $HOME ${1+1} \(1+1) /.*[test]',
    "@string/other  ?attribute  100% %s %d",
    "?attr/theme",
    "你好 🚀 {{PROJECT_NAME}} {{DISPLAY_NAME_JSON}}",
    "literal \\u2028 and separator \u2028 end\u2029!",
]
JS_STRING = r'"(?:\\.|[^"\\])*"'


class TextCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


class EscapingTests(unittest.TestCase):
    def generate(self, template, value, root):
        options = {
            "frontend": [],
            "android": ["--package-name", "com.example.demo", "--organization-name", value],
            "apple": ["--bundle-identifier", "com.example.demo", "--platform", "macos",
                      "--organization-name", value],
            "harmonyos": ["--bundle-name", "com.example.demo", "--organization-name", value],
        }
        with redirect_stdout(io.StringIO()):
            main(["create", template, "demo", "--output-dir", str(root),
                  "--non-interactive", "--display-name", value, *options[template]])
        return Path(root) / "demo"

    def test_single_pass_does_not_expand_user_placeholders(self):
        value = "{{PROJECT_NAME}} {{DISPLAY_NAME_JSON}}"
        self.assertEqual(render_text("{{DISPLAY_NAME}}", {
            "display_name": value, "project_name": "unexpected",
        }), value)
        self.assertEqual(json.loads('"' + render_text("{{DISPLAY_NAME_JSON}}", {
            "display_name": value, "project_name": "unexpected",
        }) + '"'), value)

    def test_all_context_placeholders_validate(self):
        self.assertEqual(validate_templates(), [])

    def test_validation_rejects_unescaped_free_text_in_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Fixture file, not a generated production source.
            path = Path(tmp) / "unsafe.ts"
            path.write_text('const title = "{{DISPLAY_NAME}}";')
            definition = replace(load_template("frontend"), template_dir=Path(tmp))
            errors = validate_template_placeholders(definition)
            self.assertTrue(any("require an explicit context" in error for error in errors))

    @android_test
    @unittest.skipUnless(os.environ.get("AAPT2"), "Set AAPT2 to validate native Android resources")
    def test_android_resources_compile_with_aapt2(self):
        for value in SAMPLES:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                project = self.generate("android", value, tmp)
                subprocess.run([os.environ["AAPT2"], "compile", "--dir",
                                str(project / "app/src/main/res"),
                                "-o", str(Path(tmp) / "resources.zip")],
                               capture_output=True, text=True, check=True)

    def test_android_xml_and_resource_rules(self):
        for value in SAMPLES:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                project = self.generate("android", value, tmp)
                for file in project.rglob("*.xml"):
                    ET.parse(file)
                app = ET.parse(project / "app/src/main/AndroidManifest.xml").find("application")
                self.assertEqual(app.get("{http://schemas.android.com/apk/res/android}label"),
                                 "@string/app_name")
                resource = ET.parse(project / "app/src/main/res/values/strings.xml").find("string")
                self.assertEqual(resource.get("formatted"), "false")
                self.assertTrue(resource.text.startswith('"') and resource.text.endswith('"'))
                self.assertEqual(re.sub(r"\\(.)", r"\1", resource.text[1:-1]), value)
                kotlin = (project / "feature/home/src/main/java/home/HomeRoute.kt").read_text()
                literal = re.search(r"title = (" + JS_STRING + ")", kotlin)[1]
                self.assertNotRegex(literal, r"(?<!\\)\$")
                self.assertEqual(json.loads(literal.replace(r"\$", "$")), value)

    def test_harmony_json_and_json5_round_trip(self):
        for value in SAMPLES:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                project = self.generate("harmonyos", value, tmp)
                metadata = json.loads((project / "AppScope/app.json5").read_text())
                self.assertEqual(metadata["app"]["vendor"], value)
                for relative in ("oh-package.json5", "entry/oh-package.json5"):
                    data = json.loads((project / relative).read_text())
                    self.assertEqual(data["author"], value)
                    self.assertTrue(data["description"].startswith(value))
                data = json.loads((project / "AppScope/resources/base/element/string.json").read_text())
                self.assertEqual(data["string"][0]["value"], value)

    @platform_test
    @unittest.skipUnless(shutil.which("node"), "Node required for JS string evaluation")
    def test_frontend_and_arkts_literals_evaluate_to_original_text(self):
        for value in SAMPLES:
            for template in ("frontend", "harmonyos"):
                with self.subTest(value=value, template=template), tempfile.TemporaryDirectory() as tmp:
                    project = self.generate(template, value, tmp)
                    if template == "frontend":
                        html = (project / "index.html").read_text()
                        title = re.search(r"<title>(.*?)</title>", html, re.S)[1]
                        parser = TextCollector()
                        parser.feed(title)
                        self.assertEqual("".join(parser.parts), value)
                        source = (project / "src/pages/HomePage.tsx").read_text()
                        literals = [re.search(r"<h1>\{(" + JS_STRING + r")\}</h1>", source)[1]]
                        source = (project / "src/services/projectOverview.ts").read_text()
                        literals.append(re.search(r"title: (" + JS_STRING + ")", source)[1])
                        for name in ("browser-smoke", "production-browser-smoke"):
                            source = (project / f"tests/{name}.spec.ts").read_text()
                            literals.append(re.search(r"toHaveTitle\((" + JS_STRING + r")\)", source)[1])
                    else:
                        source = (project / "entry/src/main/ets/core/config/AppConfig.ets").read_text()
                        literals = [re.search(r"displayName: string = ('(?:\\.|[^'\\])*')", source)[1]]
                    result = subprocess.run(["node", "-e", "console.log(JSON.stringify([" +
                                             ",".join(literals) + "]))"],
                                            capture_output=True, text=True, check=True)
                    self.assertEqual(json.loads(result.stdout), [value] * len(literals))

    @platform_test
    @unittest.skipUnless(shutil.which("swift"), "Swift required for literal evaluation")
    def test_swift_literals_and_generated_window_title(self):
        literals = []
        for value in SAMPLES:
            with tempfile.TemporaryDirectory() as tmp:
                project = self.generate("apple", value, tmp)
                source = (project / "App/Project.swift").read_text()
                self.assertIn('organizationName: "' + swift_string(value) + '"', source)
                app_sources = project / "App/Targets/App/Sources"
                source = "\n".join(file.read_text() for file in app_sources.rglob("*.swift"))
                literals.append(re.search(r"WindowGroup\((" + JS_STRING + r")\)", source)[1])
        code = ('import Foundation\nlet values = [' + ','.join(literals) + ']\n'
                'let data = try! JSONSerialization.data(withJSONObject: values)\n'
                'print(String(data: data, encoding: .utf8)!)')
        result = subprocess.run(["swift", "-e", code], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout), SAMPLES)

    def test_endpoint_is_quoted_and_preserved_in_yaml_and_go(self):
        value = r'https://example.com/a"b\c?q=$HOME&x=1#frag'
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            main(["create", "microservice", "demo", "--output-dir", tmp,
                  "--module-name", "example.com/demo", "--proto-package", "demo.v1",
                  "--otel-exporter-endpoint", value, "--non-interactive"])
            project = Path(tmp) / "demo"
            yaml = (project / "configs/config.yaml").read_text()
            literal = re.search(r"otlp_http_endpoint: (" + JS_STRING + ")", yaml)[1]
            self.assertEqual(json.loads(literal), value)
            go = (project / "internal/config/config.go").read_text()
            literal = re.search(r"cfg.Telemetry.OTLPHTTPEndpoint = (" + JS_STRING + ")", go)[1]
            self.assertEqual(json.loads(literal), value)
            docker = (project / "Dockerfile").read_text()
            self.assertIn(r"\$HOME", docker)


if __name__ == "__main__":
    unittest.main()
