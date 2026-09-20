"""Focused cli regression coverage; extracted without changing assertions."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

from biucingcli.cli import main


from cli_support import CLIHelpers


class CLITestCase(CLIHelpers, unittest.TestCase):
    def test_main_defaults_to_template_summary(self):
        output = self.run_cli([])

        self.assert_matches_golden("list.txt", output)

    def test_info_prints_template_details(self):
        output = self.run_cli(["info", "web-service"])

        self.assertIn("Template: web-service", output)
        self.assertIn("Workflow labels: bootstrap, dev, verify, build, runtime", output)
        self.assertIn("Verification tier: real-build", output)
        self.assertIn("Worktree support: worktree-ready", output)
        self.assertIn(
            "Worktree isolation: runtime-names, ports, caches, "
            "generated-output, cleanup, diagnostics",
            output,
        )
        self.assertIn("Worktree diagnostics:", output)
        self.assertIn("- make worktree-info", output)
        self.assertIn("Worktree cleanup:", output)
        self.assertIn("- make clean-worktree", output)
        self.assertIn("Operating assumptions:", output)
        self.assertIn(
            "- The starter is optimized for Go service development with Docker-based dev and runtime flows.",
            output,
        )

    def test_info_prints_android_template_details(self):
        output = self.run_cli(["info", "android"])

        self.assertIn("Template: android", output)
        self.assertIn("Kotlin, Android, Gradle, Jetpack Compose, fastlane", output)
        self.assertIn("package_name", output)
        self.assertIn("compile_sdk", output)

    def test_info_prints_harmonyos_template_details(self):
        output = self.run_cli(["info", "harmonyos"])

        self.assertIn("Template: harmonyos", output)
        self.assertIn("ArkTS, ArkUI, HarmonyOS, DevEco Studio, hvigor, ohpm", output)
        self.assertIn("bundle_name", output)
        self.assertIn("compatible_sdk_version", output)

    def test_info_prints_microservice_template_details(self):
        output = self.run_cli(["info", "microservice"])

        self.assertIn("Template: microservice", output)
        self.assertIn("Go, Gin, Protobuf, Buf, Docker Compose, OpenTelemetry", output)
        self.assertIn("proto_package", output)
        self.assertIn("grpc_port", output)

    def test_info_prints_worker_template_details(self):
        output = self.run_cli(["info", "worker"])

        self.assertIn("Template: worker", output)
        self.assertIn("Go, Docker", output)
        self.assertIn("worker_name", output)
        self.assertIn("run_mode", output)
        self.assertIn("tick_interval_seconds", output)

    def test_list_json_prints_machine_readable_templates(self):
        output = self.run_cli(["list", "--json"])

        payload = json.loads(output)
        self.assertEqual(len(payload["templates"]), 7)
        web_service = next(
            template for template in payload["templates"] if template["name"] == "web-service"
        )
        self.assertEqual(web_service["validation"]["verification_tier"], "real-build")
        self.assertEqual(
            web_service["workflow_labels"],
            ["bootstrap", "dev", "verify", "build", "runtime"],
        )
        self.assertEqual(web_service["worktree"]["support_level"], "worktree-ready")
        self.assertIn("runtime-names", web_service["worktree"]["isolation_dimensions"])
        self.assertIn("make worktree-info", web_service["worktree"]["diagnostics"])
        self.assertIn("make clean-worktree", web_service["worktree"]["cleanup"])
        self.assertTrue(web_service["operating_assumptions"])

    def test_info_json_prints_machine_readable_template_detail(self):
        output = self.run_cli(["info", "web-service", "--json"])

        payload = json.loads(output)
        self.assertEqual(payload["name"], "web-service")
        self.assertEqual(payload["validation"]["verification_tier"], "real-build")
        self.assertEqual(
            payload["workflow_labels"],
            ["bootstrap", "dev", "verify", "build", "runtime"],
        )
        self.assertEqual(payload["worktree"]["support_level"], "worktree-ready")
        self.assertIn("ports", payload["worktree"]["isolation_dimensions"])
        self.assertEqual(
            payload["worktree"]["diagnostics"],
            ["make worktree-info", "make worktree-doctor"],
        )
        self.assertEqual(payload["worktree"]["cleanup"], ["make clean-worktree"])
        self.assertIn("Go service development", payload["operating_assumptions"][0])

    def test_validate_passes_for_repo_templates(self):
        output = self.run_cli(["validate"])

        self.assertEqual(output, "Template validation passed.\n")

    def test_validate_json_passes_for_repo_templates(self):
        output = self.run_cli(["validate", "--json"])

        payload = json.loads(output)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["error_count"], 0)
        self.assertEqual(payload["errors"], [])

    def test_unknown_template_errors_are_user_facing(self):
        cases = [
            ["info", "does-not-exist"],
            ["create", "does-not-exist", "demo", "--non-interactive"],
        ]

        for argv in cases:
            with self.subTest(argv=argv):
                code, stdout, stderr = self.run_cli_failure(argv)
                self.assertEqual(code, 2)
                self.assertEqual(stdout, "")
                self.assertEqual(stderr, "error: unknown template 'does-not-exist'\n")
                self.assertNotIn("Traceback", stderr)

    def test_invalid_template_metadata_is_user_facing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_root = Path(tmpdir)
            broken_dir = templates_root / "broken"
            broken_dir.mkdir()
            (broken_dir / "template.json").write_text("{not-json", encoding="utf-8")

            with patch("biucingcli.catalog.templates_root", return_value=templates_root):
                code, stdout, stderr = self.run_cli_failure(["info", "broken"])

        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("error: invalid metadata for template 'broken'", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_create_reports_target_conflict_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "demo").mkdir()
            code, stdout, stderr = self.run_cli_failure(
                ["create", "frontend", "demo", "--output-dir", tmpdir]
            )

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("error: target directory already exists:", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_create_reports_missing_output_directory_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_output = Path(tmpdir) / "missing"
            code, stdout, stderr = self.run_cli_failure(
                ["create", "frontend", "demo", "--output-dir", str(missing_output)]
            )

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("error: output directory does not exist:", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_create_cleans_staging_directory_after_io_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "biucingcli.generation.shutil.copytree",
                side_effect=OSError("synthetic copy failure"),
            ):
                code, stdout, stderr = self.run_cli_failure(
                    ["create", "frontend", "demo", "--output-dir", tmpdir]
                )

            self.assertEqual(list(Path(tmpdir).iterdir()), [])

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("synthetic copy failure", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_microservice_derivations_use_normalized_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "microservice",
                    "demo",
                    "--output-dir",
                    tmpdir,
                    "--module-name",
                    "github.com/example/demo",
                    "--proto-package",
                    "demo.v1",
                    "--service-name",
                    "  api  ",
                    "--set",
                    "dependency_store= redis ",
                    "--non-interactive",
                    "--plan",
                    "--json",
                ]
            )

        payload = json.loads(output)
        service_name = next(
            item for item in payload["resolved_variables"] if item["name"] == "service_name"
        )
        self.assertEqual(service_name["value"], "api")
        self.assertEqual(payload["derived_values"]["dependency_store"], "redis")
        self.assertEqual(
            payload["derived_values"]["dependency_store_dsn"],
            "redis://localhost:6379/0",
        )

    def test_apple_derivations_use_normalized_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "apple",
                    "demo",
                    "--output-dir",
                    tmpdir,
                    "--bundle-identifier",
                    "com.example.demo",
                    "--set",
                    "apple_platform= macos ",
                    "--set",
                    "minimum_os_version= 26.1 ",
                    "--non-interactive",
                    "--plan",
                    "--json",
                ]
            )

        payload = json.loads(output)
        self.assertEqual(payload["derived_values"]["apple_platform"], "macos")
        self.assertEqual(payload["derived_values"]["apple_platform_name"], "macOS")
        self.assertEqual(payload["derived_values"]["minimum_os_version"], "26.1")

    def test_create_rejects_invalid_template_inputs_before_writing(self):
        cases = [
            (
                ["create", "frontend", "bad/name", "--non-interactive"],
                "project_name: must be a safe directory name",
            ),
            (
                [
                    "create",
                    "web-service",
                    "bad-port",
                    "--module-name",
                    "github.com/example/bad-port",
                    "--http-port",
                    "70000",
                    "--non-interactive",
                ],
                "http_port: must be between 1 and 65535",
            ),
            (
                [
                    "create",
                    "microservice",
                    "bad-proto",
                    "--module-name",
                    "github.com/example/bad-proto",
                    "--proto-package",
                    "Bad-Package",
                    "--non-interactive",
                ],
                "proto_package: must be a dotted lowercase Protobuf package",
            ),
            (
                [
                    "create",
                    "worker",
                    "bad-worker",
                    "--module-name",
                    "github.com/example/bad-worker",
                    "--set",
                    "run_mode=forever",
                    "--non-interactive",
                ],
                "run_mode: must be one of: scheduled, oneshot",
            ),
            (
                [
                    "create",
                    "apple",
                    "bad-apple",
                    "--bundle-identifier",
                    "not-a-bundle-id",
                    "--non-interactive",
                ],
                "bundle_identifier: must be a reverse-DNS identifier",
            ),
            (
                [
                    "create",
                    "android",
                    "bad-android",
                    "--package-name",
                    "com.example.badandroid",
                    "--application-id",
                    "invalid-id",
                    "--non-interactive",
                ],
                "application_id: must be a dotted Java package",
            ),
            (
                [
                    "create",
                    "harmonyos",
                    "bad-harmony",
                    "--bundle-name",
                    "com.example.badharmony",
                    "--compatible-sdk-version",
                    "5.0",
                    "--non-interactive",
                ],
                "compatible_sdk_version: must use HarmonyOS SDK notation",
            ),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            for argv, expected_error in cases:
                with self.subTest(template=argv[1]):
                    code, stdout, stderr = self.run_cli_failure(
                        [*argv, "--output-dir", tmpdir]
                    )
                    self.assertEqual(code, 2)
                    self.assertEqual(stdout, "")
                    self.assertIn(expected_error, stderr)
                    self.assertFalse((Path(tmpdir) / argv[2]).exists())

    def test_create_normalizes_cli_and_set_values_before_validation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "web-service",
                    "  normalized-service  ",
                    "--module-name",
                    "  github.com/example/normalized-service  ",
                    "--set",
                    "http_port= 8181 ",
                    "--output-dir",
                    tmpdir,
                    "--non-interactive",
                ]
            )
            project_dir = Path(tmpdir) / "normalized-service"
            config = (project_dir / "configs" / "config.yaml").read_text(encoding="utf-8")
            go_mod = (project_dir / "go.mod").read_text(encoding="utf-8")

            self.assertIn("Created web-service project: normalized-service", output)
            self.assertIn("port: 8181", config)
            self.assertIn("module github.com/example/normalized-service", go_mod)

    def test_create_rejects_options_owned_by_another_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code, stdout, stderr = self.run_cli_failure(
                [
                    "create",
                    "frontend",
                    "wrong-option-app",
                    "--http-port",
                    "8081",
                    "--output-dir",
                    tmpdir,
                ]
            )

            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("Unsupported option(s) for frontend: http_port", stderr)
            self.assertFalse((Path(tmpdir) / "wrong-option-app").exists())

    def test_version_prints_cli_version(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        with self.assertRaises(SystemExit) as excinfo:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                main(["--version"])

        self.assertEqual(excinfo.exception.code, 0)
        self.assertEqual(stdout.getvalue(), "biucing 0.9.1\n")
        self.assertEqual(stderr.getvalue(), "")

    def test_create_android_prompts_for_package_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                ["create", "android", "prompt-android", "--output-dir", tmpdir],
                stdin_values=["com.example.promptandroid"],
            )
            project_dir = Path(tmpdir) / "prompt-android"
            app_build = (project_dir / "app" / "build.gradle.kts").read_text(encoding="utf-8")

            self.assertIn("Created android project: prompt-android", output)
            self.assertIn('namespace = "com.example.promptandroid"', app_build)

    def test_create_harmonyos_prompts_for_bundle_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                ["create", "harmonyos", "prompt-harmony", "--output-dir", tmpdir],
                stdin_values=["com.example.promptharmony"],
            )
            project_dir = Path(tmpdir) / "prompt-harmony"
            app_json = (project_dir / "AppScope" / "app.json5").read_text(encoding="utf-8")

            self.assertIn("Created harmonyos project: prompt-harmony", output)
            self.assertIn('"bundleName": "com.example.promptharmony"', app_json)

    def test_create_frontend_supports_set_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "frontend",
                    "scripted-app",
                    "--output-dir",
                    tmpdir,
                    "--set",
                    "display_name=Scripted Frontend",
                    "--set",
                    "package_name=scripted.frontend",
                ]
            )
            project_dir = Path(tmpdir) / "scripted-app"
            package_json = (project_dir / "package.json").read_text(encoding="utf-8")
            index_html = (project_dir / "index.html").read_text(encoding="utf-8")

            self.assertIn("Created frontend project: scripted-app", output)
            self.assertIn('"name": "scripted.frontend"', package_json)
            self.assertIn("<title>Scripted Frontend</title>", index_html)

    def test_create_microservice_prompts_for_proto_package(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "microservice",
                    "prompt-service",
                    "--output-dir",
                    tmpdir,
                    "--module-name",
                    "github.com/example/prompt-service",
                ],
                stdin_values=["prompt.v1"],
            )
            project_dir = Path(tmpdir) / "prompt-service"
            proto_file = (
                project_dir / "api" / "proto" / "service" / "v1" / "service.proto"
            ).read_text(encoding="utf-8")
            compose_yaml = (project_dir / "deploy" / "compose.yaml").read_text(encoding="utf-8")

            self.assertIn("Created microservice project: prompt-service", output)
            self.assertIn("package prompt.v1;", proto_file)
            self.assertIn("POSTGRES_DB: prompt-service", compose_yaml)

    def test_create_microservice_non_interactive_fails_fast(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code, stdout, stderr = self.run_cli_failure(
                [
                    "create",
                    "microservice",
                    "non-interactive-service",
                    "--output-dir",
                    tmpdir,
                    "--module-name",
                    "github.com/example/non-interactive-service",
                    "--non-interactive",
                ]
            )

            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn(
                "Missing required values in non-interactive mode: proto_package",
                stderr,
            )

    def test_create_microservice_non_interactive_reports_all_missing_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code, stdout, stderr = self.run_cli_failure(
                [
                    "create",
                    "microservice",
                    "needs-values",
                    "--output-dir",
                    tmpdir,
                    "--non-interactive",
                ]
            )

            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn(
                "Missing required values in non-interactive mode: module_name, proto_package",
                stderr,
            )

    def test_create_frontend_dry_run_preview_does_not_write_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "frontend",
                    "preview-app",
                    "--output-dir",
                    tmpdir,
                    "--dry-run",
                    "--set",
                    "display_name=Preview App",
                ]
            )
            project_dir = Path(tmpdir) / "preview-app"

            self.assertFalse(project_dir.exists())
            self.assertIn("Create preview (dry-run) for frontend: preview-app", output)
            self.assertIn("Resolved variables:", output)
            self.assertIn("display_name [provided]: Preview App", output)
            self.assertIn("package_name [default_from:project_name]: preview-app", output)
            self.assertIn("No files were written.", output)

    def test_create_web_plan_json_returns_manifest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "web-service",
                    "plan-web-service",
                    "--output-dir",
                    tmpdir,
                    "--module-name",
                    "github.com/example/plan-web-service",
                    "--plan",
                    "--json",
                ]
            )
            project_dir = Path(tmpdir) / "plan-web-service"
            payload = json.loads(output)

            self.assertFalse(project_dir.exists())
            self.assertEqual(payload["operation"], "plan")
            self.assertEqual(payload["template"]["name"], "web-service")
            self.assertEqual(payload["project_name"], "plan-web-service")
            self.assertEqual(payload["target_exists"], False)
            self.assertEqual(payload["resolved_variables"][1]["name"], "module_name")
            self.assertEqual(payload["resolved_variables"][1]["source"], "provided")
            self.assertIn("make verify", payload["next_steps"])

    def test_create_frontend_json_returns_manifest_after_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "frontend",
                    "json-app",
                    "--output-dir",
                    tmpdir,
                    "--json",
                ]
            )
            project_dir = Path(tmpdir) / "json-app"
            payload = json.loads(output)

            self.assertTrue(project_dir.exists())
            self.assertEqual(payload["operation"], "create")
            self.assertEqual(payload["template"]["name"], "frontend")
            self.assertEqual(payload["project_name"], "json-app")
            self.assertEqual(payload["target_exists"], True)
            self.assertGreater(payload["template_file_count"], 0)
            self.assertIn("README.md", payload["template_top_level_entries"])
            self.assertIn("make docker-run", payload["next_steps"])

    def test_create_web_set_values_can_replace_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "web-service",
                    "set-web-service",
                    "--output-dir",
                    tmpdir,
                    "--set",
                    "module_name=github.com/example/set-web-service",
                    "--set",
                    "service_name=set-service",
                    "--set",
                    "http_port=9191",
                ]
            )
            project_dir = Path(tmpdir) / "set-web-service"
            main_go = (project_dir / "cmd" / "server" / "main.go").read_text(encoding="utf-8")
            config_yaml = (project_dir / "configs" / "config.yaml").read_text(encoding="utf-8")

            self.assertIn("Created web-service project: set-web-service", output)
            self.assertIn("github.com/example/set-web-service", main_go)
            self.assertIn("name: set-service", config_yaml)
            self.assertIn("port: 9191", config_yaml)

    def test_create_web_explicit_flag_overrides_set_value(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "web-service",
                    "override-web-service",
                    "--output-dir",
                    tmpdir,
                    "--set",
                    "module_name=github.com/example/wrong-web-service",
                    "--module-name",
                    "github.com/example/right-web-service",
                ]
            )
            project_dir = Path(tmpdir) / "override-web-service"
            main_go = (project_dir / "cmd" / "server" / "main.go").read_text(encoding="utf-8")

            self.assertIn("Created web-service project: override-web-service", output)
            self.assertIn("github.com/example/right-web-service", main_go)
            self.assertNotIn("github.com/example/wrong-web-service", main_go)

    def test_create_web_prompts_for_module_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                ["create", "web-service", "user-service", "--output-dir", tmpdir],
                stdin_values=["github.com/example/user-service"],
            )
            project_dir = Path(tmpdir) / "user-service"
            main_go = (project_dir / "cmd" / "server" / "main.go").read_text(encoding="utf-8")
            dockerfile = (project_dir / "Dockerfile").read_text(encoding="utf-8")
            compose_yaml = (project_dir / "compose.yaml").read_text(encoding="utf-8")
            makefile = (project_dir / "Makefile").read_text(encoding="utf-8")
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            dockerfile_dev = (project_dir / "Dockerfile.dev").read_text(encoding="utf-8")
            compose_dev = (project_dir / "compose.dev.yaml").read_text(encoding="utf-8")
            air_toml = (project_dir / ".air.toml").read_text(encoding="utf-8")
            dockerignore = (project_dir / ".dockerignore").read_text(encoding="utf-8")
            brewfile = (project_dir / "Brewfile").read_text(encoding="utf-8")
            mise_toml = (project_dir / ".mise.toml").read_text(encoding="utf-8")
            go_sum = (project_dir / "go.sum").read_text(encoding="utf-8")
            config_go = (project_dir / "internal" / "config" / "config.go").read_text(
                encoding="utf-8"
            )
            config_test = (
                project_dir / "internal" / "config" / "config_test.go"
            ).read_text(encoding="utf-8")
            runtime_go = (
                project_dir / "internal" / "runtime" / "server.go"
            ).read_text(encoding="utf-8")
            runtime_test = (
                project_dir / "internal" / "runtime" / "server_test.go"
            ).read_text(encoding="utf-8")
            config_yaml = (project_dir / "configs" / "config.yaml").read_text(
                encoding="utf-8"
            )
            test_file = (project_dir / "tests" / "server_test.go").read_text(encoding="utf-8")
            bootstrap = (project_dir / "scripts" / "bootstrap").read_text(encoding="utf-8")
            doctor = (project_dir / "scripts" / "doctor").read_text(encoding="utf-8")
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
            self.assertIn("Created web-service project: user-service", output)
            self.assertIn("make bootstrap", output)
            self.assertIn("make dev", output)
            self.assertIn("make verify", output)
            self.assertIn("make docker-build", output)
            self.assertIn("make docker-run", output)
            self.assertIn("github.com/example/user-service", main_go)
            self.assertIn("ARG BUILDER_IMAGE=golang:1.26-alpine", dockerfile)
            self.assertIn("ARG RUNTIME_IMAGE=alpine:3.20", dockerfile)
            self.assertIn("GOOS=linux GOARCH=${TARGETARCH:-amd64}", dockerfile)
            self.assertIn("EXPOSE 8080", dockerfile)
            self.assertIn("HEALTHCHECK", dockerfile)
            self.assertIn("http://127.0.0.1:8080/healthz", dockerfile)
            self.assertIn('["/app/server", "healthcheck"', dockerfile)
            self.assertIn("BUILDER_IMAGE: ${BUILDER_IMAGE:-golang:1.26-alpine}", compose_yaml)
            self.assertIn("RUNTIME_IMAGE: ${RUNTIME_IMAGE:-alpine:3.20}", compose_yaml)
            self.assertIn("image: ${IMAGE:-user-service}:${TAG:-latest}", compose_yaml)
            self.assertIn('- "${HOST_PORT:-8080}:8080"', compose_yaml)
            self.assertIn("stop_grace_period: 15s", compose_yaml)
            self.assertIn("DOCKER_VARIANT ?=alpine", makefile)
            self.assertIn("DOCKER_PLATFORM ?=linux/arm64", makefile)
            self.assertIn("GOPROXY ?=https://proxy.golang.org,direct", makefile)
            self.assertIn("GOSUMDB ?=sum.golang.org", makefile)
            self.assertIn("GOMODCACHE ?= $(CURDIR)/.cache/go-mod", makefile)
            self.assertIn("Go module cache: $(GOMODCACHE)", makefile)
            self.assertIn("GOMODCACHE should stay inside this worktree", makefile)
            self.assertIn("DEV_COMPOSE_FILE ?=compose.dev.yaml", makefile)
            self.assertIn("COMPOSE_PROJECT_NAME ?=$(WORKTREE_SLUG)", makefile)
            self.assertIn("WORKTREE_LABEL ?=$(shell basename", makefile)
            self.assertIn("worktree-info:", makefile)
            self.assertIn("worktree-compose-config:", makefile)
            self.assertIn("clean-worktree:", makefile)
            self.assertIn("Warning: HOST_PORT $(HOST_PORT) is already in use.", makefile)
            self.assertIn("Suggested override: HOST_PORT=$$(( $(HOST_PORT) + 10000 )) make dev", makefile)
            self.assertIn("$(COMPOSE) -f $(DEV_COMPOSE_FILE) config", makefile)
            self.assertIn("GOPROXY=$(GOPROXY) GOSUMDB=$(GOSUMDB) $(COMPOSE) -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE)", makefile)
            self.assertIn("public.ecr.aws/docker/library/golang:1.26", makefile)
            self.assertIn("public.ecr.aws/docker/library/ubuntu:26.04", makefile)
            self.assertIn("IMAGE ?=$(WORKTREE_SLUG)", makefile)
            self.assertIn("--build-arg BUILDER_IMAGE=$(BUILDER_IMAGE)", makefile)
            self.assertIn("--build-arg RUNTIME_IMAGE=$(RUNTIME_IMAGE)", makefile)
            self.assertIn("--build-arg GOPROXY=$(GOPROXY)", makefile)
            self.assertIn("--build-arg GOSUMDB=$(GOSUMDB)", makefile)
            self.assertIn("docker run --rm -p $(HOST_PORT):$(CONTAINER_PORT) $(IMAGE_REF)", makefile)
            self.assertIn("docker push $(IMAGE_REF)", makefile)
            self.assertIn("ARG AIR_VERSION=1.65.3", dockerfile_dev)
            self.assertIn("ARG GOLANGCI_LINT_VERSION=2.12.2", dockerfile_dev)
            self.assertIn("ARG GOPROXY=https://proxy.golang.org,direct", dockerfile_dev)
            self.assertIn("ARG GOSUMDB=sum.golang.org", dockerfile_dev)
            self.assertIn("air_${AIR_VERSION}_linux_${air_arch}.tar.gz", dockerfile_dev)
            self.assertIn("golangci-lint-${GOLANGCI_LINT_VERSION}-linux-${golangci_arch}.tar.gz", dockerfile_dev)
            self.assertIn("COPY go.mod go.sum ./", dockerfile_dev)
            self.assertIn("until go mod download; do", dockerfile_dev)
            self.assertIn("app-dev", compose_dev)
            self.assertIn("GOPROXY: ${GOPROXY:-https://proxy.golang.org,direct}", compose_dev)
            self.assertIn("GOSUMDB: ${GOSUMDB:-sum.golang.org}", compose_dev)
            self.assertIn("GOMODCACHE: /workspace/.cache/go-mod", compose_dev)
            self.assertIn("web-service-go-mod:/workspace/.cache/go-mod", compose_dev)
            self.assertIn("command: air -c .air.toml", compose_dev)
            self.assertIn("stop_grace_period: 15s", compose_dev)
            self.assertIn('cmd = "go build -o ./tmp/server ./cmd/server"', air_toml)
            self.assertIn(".cache/", dockerignore)
            self.assertIn("make bootstrap", readme)
            self.assertIn("make dev", readme)
            self.assertIn("make dev-shell", readme)
            self.assertIn("make lint", readme)
            self.assertIn("make verify", readme)
            self.assertIn("make docker-run", readme)
            self.assertIn("make docker-build DOCKER_VARIANT=ubuntu", readme)
            self.assertIn("make docker-build DOCKER_VARIANT=ubuntu IMAGE=user-service-ubuntu TAG=dev", readme)
            self.assertIn("make docker-run IMAGE=user-service-ubuntu TAG=dev HOST_PORT=8080", readme)
            self.assertIn("starts whatever image tag you last built", readme)
            self.assertIn("prewarms `go mod download`", readme)
            self.assertIn("GOPROXY", readme)
            self.assertIn("GOSUMDB", readme)
            self.assertIn("DOCKER_VARIANT=ubuntu", readme)
            self.assertIn("public.ecr.aws/docker/library/golang:1.26", readme)
            self.assertIn("make docker-push IMAGE=registry.example.com/user-service TAG=0.1.0", readme)
            self.assertIn("make dev", readme)
            self.assertIn("scripts/bootstrap", readme)
            self.assertIn('brew "golangci-lint"', brewfile)
            self.assertIn('go = "1.26.0"', mise_toml)
            self.assertIn("go 1.26.0", (project_dir / "go.mod").read_text(encoding="utf-8"))
            self.assertIn("github.com/gin-gonic/gin v1.10.0", go_sum)
            self.assertIn("yaml.Unmarshal", config_go)
            self.assertIn("ShutdownTimeoutSeconds", config_go)
            self.assertIn("shutdown_timeout_seconds: 10", config_yaml)
            self.assertIn("TestLoadDefaultConfig", config_test)
            self.assertIn("TestLoadUsesConfigFileOverride", config_test)
            self.assertIn("TestLoadRejectsNegativeTimeout", config_test)
            self.assertIn("signal.NotifyContext", main_go)
            self.assertIn("serverruntime.Serve", main_go)
            self.assertIn("ReadHeaderTimeout", runtime_go)
            self.assertIn("func CheckHealth", runtime_go)
            self.assertIn("server.Shutdown(shutdownCtx)", runtime_go)
            self.assertIn("server.Close()", runtime_go)
            self.assertIn("TestServeDrainsInFlightRequest", runtime_test)
            self.assertIn("TestServeEnforcesShutdownTimeout", runtime_test)
            self.assertIn("SIGINT", readme)
            self.assertIn("server.shutdown_timeout_seconds", readme)
            self.assertIn("TestHealthz", test_file)
            self.assertIn("TestPing", test_file)
            self.assertIn("TestListUsers", test_file)
            self.assertIn("TestGetUser", test_file)
            self.assertIn("go mod tidy", bootstrap)
            self.assertIn("./scripts/doctor", bootstrap)
            self.assertIn("go.sum is missing", doctor)
            self.assertIn("service.port must be between 1 and 65535", doctor)
            self.assertIn("go test ./internal/config -run TestLoadDefaultConfig", doctor)
            self.assertIn("golangci-lint: not installed", doctor)
            self.assertIn("Environment looks ready.", doctor)
            self.assertIn('group.GET("/ping"', ping_handler)
            self.assertIn('Message: "pong"', ping_service)
            self.assertIn('group.GET("/users"', user_handler)
            self.assertIn("ListUsers() []model.User", user_service)
            self.assertIn("Ada Lovelace", user_repository)
            self.assertIn("type User struct", user_model)
            self.assertTrue(os.access(project_dir / "scripts" / "bootstrap", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "doctor", os.X_OK))


if __name__ == "__main__":
    unittest.main()
