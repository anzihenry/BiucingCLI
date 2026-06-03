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
        self.assertIn("apple", output)
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
            package_json = (project_dir / "package.json").read_text(encoding="utf-8")
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            index_html = (project_dir / "index.html").read_text(encoding="utf-8")
            home_page = (project_dir / "src" / "pages" / "HomePage.tsx").read_text(
                encoding="utf-8"
            )
            overview_service = (
                project_dir / "src" / "services" / "projectOverview.ts"
            ).read_text(encoding="utf-8")
            overview_type = (
                project_dir / "src" / "types" / "projectOverview.ts"
            ).read_text(encoding="utf-8")

            self.assertTrue(project_dir.exists())
            self.assertTrue((project_dir / "package.json").exists())
            self.assertIn("Created frontend project: demo-app", output)
            self.assertIn("npm install", output)
            self.assertIn("demo-app", package_json)
            self.assertIn('"typecheck": "tsc --noEmit"', package_json)
            self.assertIn("Project Layout", readme)
            self.assertIn("<title>Demo App</title>", index_html)
            self.assertIn("useProjectOverview", home_page)
            self.assertIn('title: "Demo App"', overview_service)
            self.assertIn("export type ProjectOverview", overview_type)

    def test_create_web_prompts_for_module_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                ["create", "web", "user-service", "--output-dir", tmpdir],
                stdin_values=["github.com/example/user-service"],
            )
            project_dir = Path(tmpdir) / "user-service"
            main_go = (project_dir / "cmd" / "server" / "main.go").read_text(encoding="utf-8")
            dockerfile = (project_dir / "Dockerfile").read_text(encoding="utf-8")
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            config_go = (project_dir / "internal" / "config" / "config.go").read_text(
                encoding="utf-8"
            )
            test_file = (project_dir / "tests" / "server_test.go").read_text(encoding="utf-8")
            ping_handler = (project_dir / "internal" / "handler" / "ping.go").read_text(
                encoding="utf-8"
            )
            ping_service = (project_dir / "internal" / "service" / "ping.go").read_text(
                encoding="utf-8"
            )
            user_handler = (project_dir / "internal" / "handler" / "user.go").read_text(
                encoding="utf-8"
            )
            user_service = (project_dir / "internal" / "service" / "user.go").read_text(
                encoding="utf-8"
            )
            user_repository = (
                project_dir / "internal" / "repository" / "user.go"
            ).read_text(encoding="utf-8")
            user_model = (project_dir / "internal" / "model" / "user.go").read_text(
                encoding="utf-8"
            )

            self.assertTrue(project_dir.exists())
            self.assertIn("Created web project: user-service", output)
            self.assertIn("go mod tidy", output)
            self.assertIn("docker build -t user-service .", output)
            self.assertIn("github.com/example/user-service", main_go)
            self.assertIn("EXPOSE 8080", dockerfile)
            self.assertIn("Docker", readme)
            self.assertIn("yaml.Unmarshal", config_go)
            self.assertIn("TestHealthz", test_file)
            self.assertIn("TestPing", test_file)
            self.assertIn("TestListUsers", test_file)
            self.assertIn("TestGetUser", test_file)
            self.assertIn('group.GET("/ping"', ping_handler)
            self.assertIn('Message: "pong"', ping_service)
            self.assertIn('group.GET("/users"', user_handler)
            self.assertIn("ListUsers() []model.User", user_service)
            self.assertIn("Ada Lovelace", user_repository)
            self.assertIn("type User struct", user_model)

    def test_create_apple_renders_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "apple",
                    "pulse-mac",
                    "--output-dir",
                    tmpdir,
                    "--platform",
                    "macos",
                    "--bundle-identifier",
                    "com.example.pulsemac",
                    "--organization-name",
                    "Example Labs",
                    "--development-team",
                    "ABCDE12345",
                ]
            )
            project_dir = Path(tmpdir) / "pulse-mac"
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            makefile = (project_dir / "Makefile").read_text(encoding="utf-8")
            tuist_config = (project_dir / "Tuist.swift").read_text(encoding="utf-8")
            project_swift = (project_dir / "App" / "Project.swift").read_text(
                encoding="utf-8"
            )
            bootstrap = (project_dir / "scripts" / "bootstrap").read_text(encoding="utf-8")
            design_system = (
                project_dir
                / "Packages"
                / "DesignSystem"
                / "Package.swift"
            ).read_text(encoding="utf-8")
            design_system_theme = (
                project_dir
                / "Packages"
                / "DesignSystem"
                / "Sources"
                / "DesignSystem"
                / "Theme.swift"
            ).read_text(encoding="utf-8")
            app_tests = (
                project_dir / "App" / "Targets" / "AppTests" / "Sources" / "AppTests.swift"
            ).read_text(encoding="utf-8")

            self.assertTrue(project_dir.exists())
            self.assertIn("Created apple project: pulse-mac", output)
            self.assertIn("make bootstrap", output)
            self.assertIn("Tuist", readme)
            self.assertIn("Target platform: `macOS`", readme)
            self.assertIn("generate:", makefile)
            self.assertIn("tuist generate --no-open", makefile)
            self.assertIn("platform=macOS", makefile)
            self.assertIn("let config = Config(", tuist_config)
            self.assertNotIn("fullHandle:", tuist_config)
            self.assertIn('bundleId: "com.example.pulsemac"', project_swift)
            self.assertIn("destinations: .macOS", project_swift)
            self.assertIn('deploymentTargets: .macOS("26.0")', project_swift)
            self.assertIn("brew bundle", bootstrap)
            self.assertIn('.macOS("26.0")', design_system)
            self.assertIn("enum BiucingTheme", design_system_theme)
            self.assertIn("@testable import PulseMac", app_tests)


if __name__ == "__main__":
    unittest.main()
