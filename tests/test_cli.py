import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from biucingcli.cli import main


class CLITestCase(unittest.TestCase):
    def run_cli(self, argv, stdin_values=None):
        output = io.StringIO()
        with redirect_stdout(output):
            if stdin_values is None:
                main(argv)
            else:
                with patch("builtins.input", side_effect=stdin_values):
                    main(argv)
        return output.getvalue()

    def test_main_defaults_to_template_summary(self):
        output = self.run_cli([])

        self.assertIn("Available templates:", output)
        self.assertIn("frontend", output)
        self.assertIn("web", output)

    def test_info_prints_template_details(self):
        output = self.run_cli(["info", "web"])

        self.assertIn("Template: web", output)
        self.assertIn("Go, Gin", output)
        self.assertIn("module_name", output)

    def test_create_frontend_renders_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                ["create", "frontend", "demo-app", "--output-dir", tmpdir]
            )
            project_dir = Path(tmpdir) / "demo-app"

            self.assertTrue(project_dir.exists())
            self.assertTrue((project_dir / "package.json").exists())
            self.assertIn("Created frontend project: demo-app", output)
            self.assertIn("npm install", output)
            self.assertIn("demo-app", (project_dir / "package.json").read_text(encoding="utf-8"))

    def test_create_web_prompts_for_module_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                ["create", "web", "user-service", "--output-dir", tmpdir],
                stdin_values=["github.com/example/user-service"],
            )
            project_dir = Path(tmpdir) / "user-service"
            main_go = (project_dir / "cmd" / "server" / "main.go").read_text(encoding="utf-8")

            self.assertTrue(project_dir.exists())
            self.assertIn("Created web project: user-service", output)
            self.assertIn("go mod tidy", output)
            self.assertIn("github.com/example/user-service", main_go)


if __name__ == "__main__":
    unittest.main()
