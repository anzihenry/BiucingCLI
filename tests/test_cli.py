import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from biucingcli.cli import default_kotlin_module_name
from biucingcli.cli import main
from biucingcli.templates import render_text
from biucingcli.templates import validate_templates


class CLITestCase(unittest.TestCase):
    def golden_path(self, name):
        return Path(__file__).resolve().parent / "golden" / name

    def assert_matches_golden(self, name, actual):
        expected = self.golden_path(name).read_text(encoding="utf-8")
        self.assertEqual(actual, expected)

    def run_cli(self, argv, stdin_values=None):
        output = io.StringIO()
        with redirect_stdout(output):
            if stdin_values is None:
                main(argv)
            else:
                with patch("builtins.input", side_effect=stdin_values):
                    main(argv)
        return output.getvalue()

    def run_cli_failure(self, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with self.assertRaises(SystemExit) as excinfo:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                main(argv)
        return excinfo.exception.code, stdout.getvalue(), stderr.getvalue()

    def test_main_defaults_to_template_summary(self):
        output = self.run_cli([])

        self.assert_matches_golden("list.txt", output)

    def test_info_prints_template_details(self):
        output = self.run_cli(["info", "web-service"])

        self.assertIn("Template: web-service", output)
        self.assertIn("Workflow labels: bootstrap, dev, verify, build, runtime", output)
        self.assertIn("Verification tier: real-build", output)
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
        self.assertEqual(len(payload["templates"]), 6)
        web_service = next(
            template for template in payload["templates"] if template["name"] == "web-service"
        )
        self.assertEqual(web_service["validation"]["verification_tier"], "real-build")
        self.assertEqual(
            web_service["workflow_labels"],
            ["bootstrap", "dev", "verify", "build", "runtime"],
        )
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

    def test_validate_reports_new_contract_errors_for_invalid_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_root = Path(tmpdir) / "templates"
            bad_template_dir = templates_root / "broken-service"
            rendered_dir = bad_template_dir / "template"
            rendered_dir.mkdir(parents=True)
            (bad_template_dir / "template.json").write_text(
                json.dumps(
                    {
                        "name": "broken-service",
                        "description": "Broken service template",
                        "category": "backend",
                        "stack": ["Go"],
                        "tags": ["docker", "go", "service"],
                        "platforms": ["linux"],
                        "maturity": {
                            "level": "validated",
                            "summary": "Broken on purpose for validation coverage.",
                        },
                        "validation": {
                            "status": "real-build-verified",
                            "verification_tier": "wrong-tier",
                            "evidence": ["synthetic test fixture"],
                        },
                        "operating_assumptions": ["Synthetic test assumption."],
                        "workflow_labels": ["bootstrap", "wrong-label"],
                        "variables": [
                            {"name": "project_name", "required": True},
                        ],
                        "next_steps": ["make bootstrap"],
                    }
                ),
                encoding="utf-8",
            )
            (rendered_dir / "Makefile").write_text("bootstrap:\n\t@true\n", encoding="utf-8")
            (rendered_dir / ".gitignore").write_text(".cache/\n", encoding="utf-8")
            (rendered_dir / ".dockerignore").write_text(".cache/\n", encoding="utf-8")
            (rendered_dir / "compose.dev.yaml").write_text("services: {}\n", encoding="utf-8")
            (rendered_dir / "go.mod").write_text("module example.com/broken\n", encoding="utf-8")
            (rendered_dir / "go.sum").write_text("", encoding="utf-8")
            (rendered_dir / "cmd").mkdir()
            (rendered_dir / "internal").mkdir()
            (rendered_dir / "configs").mkdir()
            (rendered_dir / "scripts").mkdir()

            with patch("biucingcli.templates.templates_root", return_value=templates_root):
                errors = validate_templates()

            joined = "\n".join(errors)
            self.assertIn(
                "broken-service: validation.verification_tier must be one of: generated-project, real-build",
                joined,
            )
            self.assertIn(
                "broken-service: workflow_labels contain unsupported values: wrong-label",
                joined,
            )
            self.assertIn(
                "broken-service: missing required starter entries: README.md",
                joined,
            )

    def test_version_prints_cli_version(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        with self.assertRaises(SystemExit) as excinfo:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                main(["--version"])

        self.assertEqual(excinfo.exception.code, 0)
        self.assertEqual(stdout.getvalue(), "biucing 0.4.0\n")
        self.assertEqual(stderr.getvalue(), "")

    def test_create_android_renders_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "android",
                    "demo-android",
                    "--output-dir",
                    tmpdir,
                    "--package-name",
                    "com.example.demoandroid",
                    "--application-id",
                    "com.example.demoandroid.app",
                    "--compile-sdk",
                    "35",
                    "--min-sdk",
                    "26",
                    "--target-sdk",
                    "35",
                    "--version-code",
                    "7",
                    "--version-name",
                    "1.2.3",
                    "--java-version",
                    "17",
                    "--android-namespace",
                    "com.example.demoandroid",
                    "--kotlin-module-name",
                    "DemoAndroid",
                ]
            )
            project_dir = Path(tmpdir) / "demo-android"
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            settings_gradle = (project_dir / "settings.gradle.kts").read_text(encoding="utf-8")
            app_build = (project_dir / "app" / "build.gradle.kts").read_text(encoding="utf-8")
            manifest = (
                project_dir / "app" / "src" / "main" / "AndroidManifest.xml"
            ).read_text(encoding="utf-8")
            main_activity = (
                project_dir / "app" / "src" / "main" / "java" / "app" / "MainActivity.kt"
            ).read_text(encoding="utf-8")
            app_smoke_test = (
                project_dir / "app" / "src" / "test" / "java" / "app" / "AppSmokeTest.kt"
            ).read_text(encoding="utf-8")
            home_route_ui_test = (
                project_dir / "app" / "src" / "androidTest" / "java" / "app" / "HomeRouteUiTest.kt"
            ).read_text(encoding="utf-8")
            home_route = (
                project_dir / "feature" / "home" / "src" / "main" / "java" / "home" / "HomeRoute.kt"
            ).read_text(encoding="utf-8")
            settings_route = (
                project_dir / "feature" / "settings" / "src" / "main" / "java" / "settings" / "SettingsRoute.kt"
            ).read_text(encoding="utf-8")
            app_environment = (
                project_dir / "core" / "network" / "src" / "main" / "java" / "network" / "AppEnvironment.kt"
            ).read_text(encoding="utf-8")
            fake_environment_provider = (
                project_dir / "core" / "testing" / "src" / "main" / "java" / "testing" / "FakeAppEnvironmentProvider.kt"
            ).read_text(encoding="utf-8")
            theme = (
                project_dir
                / "core"
                / "designsystem"
                / "src"
                / "main"
                / "java"
                / "designsystem"
                / "Theme.kt"
            ).read_text(encoding="utf-8")
            design_tokens = (
                project_dir
                / "core"
                / "designsystem"
                / "src"
                / "main"
                / "java"
                / "designsystem"
                / "DesignTokens.kt"
            ).read_text(encoding="utf-8")
            components = (
                project_dir
                / "core"
                / "designsystem"
                / "src"
                / "main"
                / "java"
                / "designsystem"
                / "Components.kt"
            ).read_text(encoding="utf-8")
            appfile = (project_dir / "fastlane" / "Appfile").read_text(encoding="utf-8")
            fastfile = (project_dir / "fastlane" / "Fastfile").read_text(encoding="utf-8")
            bootstrap = (project_dir / "scripts" / "bootstrap").read_text(encoding="utf-8")
            doctor = (project_dir / "scripts" / "doctor").read_text(encoding="utf-8")
            sync_wrapper = (
                project_dir / "scripts" / "sync-gradle-wrapper"
            ).read_text(encoding="utf-8")
            release_signing_example = (
                project_dir / "docs" / "release-signing.properties.example"
            ).read_text(encoding="utf-8")
            gradlew = (project_dir / "gradlew").read_text(encoding="utf-8")
            generated_files = {
                path.relative_to(project_dir).as_posix()
                for path in project_dir.rglob("*")
                if path.is_file()
            }
            expected_files = {
                ".editorconfig",
                ".gitignore",
                ".mise.toml",
                "Brewfile",
                "Makefile",
                "README.md",
                "app/build.gradle.kts",
                "app/proguard-rules.pro",
                "app/src/main/AndroidManifest.xml",
                "app/src/main/java/app/MainActivity.kt",
                "app/src/main/res/values/strings.xml",
                "app/src/main/res/values/themes.xml",
                "app/src/androidTest/java/app/HomeRouteUiTest.kt",
                "app/src/test/java/app/AppSmokeTest.kt",
                "build.gradle.kts",
                "core/designsystem/build.gradle.kts",
                "core/designsystem/src/main/java/designsystem/Components.kt",
                "core/designsystem/src/main/java/designsystem/DesignTokens.kt",
                "core/designsystem/src/main/java/designsystem/Theme.kt",
                "core/model/build.gradle.kts",
                "core/model/src/main/java/model/Greeting.kt",
                "core/model/src/test/java/model/GreetingTest.kt",
                "core/network/build.gradle.kts",
                "core/network/src/main/java/network/AppEnvironment.kt",
                "core/testing/build.gradle.kts",
                "core/testing/src/main/java/testing/FakeAppEnvironmentProvider.kt",
                "docs/release-signing.properties.example",
                "fastlane/Appfile",
                "fastlane/Fastfile",
                "feature/home/build.gradle.kts",
                "feature/home/src/main/java/home/HomeRoute.kt",
                "feature/settings/build.gradle.kts",
                "feature/settings/src/main/java/settings/SettingsRoute.kt",
                "gradle.properties",
                "gradle/libs.versions.toml",
                "gradle/wrapper/gradle-wrapper.properties",
                "gradlew",
                "gradlew.bat",
                "scripts/bootstrap",
                "scripts/doctor",
                "scripts/setup-android-sdk",
                "scripts/sync-gradle-wrapper",
                "settings.gradle.kts",
            }

            self.assertTrue(project_dir.exists())
            self.assertIn("Created android project: demo-android", output)
            self.assertIn("make bootstrap", output)
            self.assertIn("make doctor", output)
            self.assertIn("make format", output)
            self.assertIn("make test-ui", output)
            self.assertIn('open -a "Android Studio" .', output)
            self.assertIn("Application ID: `com.example.demoandroid.app`", readme)
            self.assertIn("make doctor", readme)
            self.assertIn("make format", readme)
            self.assertIn("make test-ui", readme)
            self.assertIn("./gradlew assembleRelease", readme)
            self.assertIn("debug`: default local development build", readme)
            self.assertIn("Release signing is optional", readme)
            self.assertIn("BIUCING_RELEASE_STORE_FILE", readme)
            self.assertIn("make release", readme)
            self.assertIn("cmdline-tools/latest", readme)
            self.assertIn("emulator/AVD visibility", readme)
            self.assertIn("connectedDebugAndroidTest", readme)
            self.assertIn("adb devices", readme)
            self.assertIn("unauthorized", readme)
            self.assertIn("`home` and `settings`", readme)
            self.assertIn("network config", readme)
            self.assertIn("shared fake environment provider", readme)
            self.assertIn("starter theme tokens", readme)
            self.assertIn("section cards and status badges", readme)
            self.assertIn("Dark mode is part of the starter theme contract", readme)
            self.assertIn('rootProject.name = "demo-android"', settings_gradle)
            self.assertIn('alias(libs.plugins.spotless)', (project_dir / "build.gradle.kts").read_text(encoding="utf-8"))
            self.assertIn('ktlint = "1.8.0"', (project_dir / "gradle" / "libs.versions.toml").read_text(encoding="utf-8"))
            self.assertIn('spotless = "8.7.0"', (project_dir / "gradle" / "libs.versions.toml").read_text(encoding="utf-8"))
            self.assertIn('androidx-test-ext = "1.2.1"', (project_dir / "gradle" / "libs.versions.toml").read_text(encoding="utf-8"))
            self.assertIn('androidx-compose-ui-test-junit4 = { module = "androidx.compose.ui:ui-test-junit4" }', (project_dir / "gradle" / "libs.versions.toml").read_text(encoding="utf-8"))
            self.assertIn("ktlint(libs.versions.ktlint.get())", (project_dir / "build.gradle.kts").read_text(encoding="utf-8"))
            self.assertIn('include(":core:network")', settings_gradle)
            self.assertIn('include(":core:testing")', settings_gradle)
            self.assertIn('include(":feature:home")', settings_gradle)
            self.assertIn('include(":feature:settings")', settings_gradle)
            self.assertIn('namespace = "com.example.demoandroid"', app_build)
            self.assertIn('applicationId = "com.example.demoandroid.app"', app_build)
            self.assertIn('versionCode = 7', app_build)
            self.assertIn('versionName = "1.2.3"', app_build)
            self.assertIn('applicationIdSuffix = ".debug"', app_build)
            self.assertIn('versionNameSuffix = "-debug"', app_build)
            self.assertIn('create("release")', app_build)
            self.assertIn('signingConfig = signingConfigs.getByName("release")', app_build)
            self.assertIn('biucing.release.storeFile', app_build)
            self.assertIn('BIUCING_RELEASE_STORE_FILE', app_build)
            self.assertIn('hasCompleteReleaseSigning', app_build)
            self.assertIn('implementation(project(":core:network"))', app_build)
            self.assertIn('implementation(project(":feature:settings"))', app_build)
            self.assertIn('testImplementation(project(":core:testing"))', app_build)
            self.assertIn('android:label="Demo Android"', manifest)
            self.assertIn('android:theme="@style/Theme.DemoAndroid"', manifest)
            self.assertIn("package com.example.demoandroid", main_activity)
            self.assertIn("BiucingTheme", main_activity)
            self.assertIn("SettingsRoute()", main_activity)
            self.assertIn("BiucingSpacing.large", main_activity)
            self.assertIn("fakeEnvironmentProviderExposesPredictableReleaseChannel", app_smoke_test)
            self.assertIn("createAndroidComposeRule<MainActivity>()", home_route_ui_test)
            self.assertIn('onNodeWithText("Demo Android", substring = true).assertIsDisplayed()', home_route_ui_test)
            self.assertIn('onNodeWithText("Generated by BiucingCLI", substring = true).assertIsDisplayed()', home_route_ui_test)
            self.assertIn("package com.example.demoandroid.feature.home", home_route)
            self.assertIn('title = "Demo Android"', home_route)
            self.assertIn("AppSectionCard(", home_route)
            self.assertIn('StatusBadge(text = "Compose baseline ready")', home_route)
            self.assertIn("package com.example.demoandroid.feature.settings", settings_route)
            self.assertIn('StatusBadge(text = "Release channel: ${environment.releaseChannel}")', settings_route)
            self.assertIn('text = "API base URL: ${environment.apiBaseUrl}"', settings_route)
            self.assertIn("interface AppEnvironmentProvider", app_environment)
            self.assertIn("class DefaultAppEnvironmentProvider", app_environment)
            self.assertIn("class FakeAppEnvironmentProvider", fake_environment_provider)
            self.assertIn("fun BiucingTheme", theme)
            self.assertIn("private val LightColors = lightColorScheme(", theme)
            self.assertIn("private val DarkColors = darkColorScheme(", theme)
            self.assertIn("private val BiucingTypography = Typography(", theme)
            self.assertIn("BiucingColors.Brand", theme)
            self.assertIn("object BiucingColors", design_tokens)
            self.assertIn("object BiucingSpacing", design_tokens)
            self.assertIn("val SurfaceWarm", design_tokens)
            self.assertIn("fun AppSectionCard(", components)
            self.assertIn("fun StatusBadge(", components)
            self.assertIn('package_name("com.example.demoandroid.app")', appfile)
            self.assertIn("assembleRelease", fastfile)
            self.assertIn("BIUCING_RELEASE_*", fastfile)
            self.assertIn("./scripts/setup-android-sdk", bootstrap)
            self.assertNotIn("./scripts/sync-gradle-wrapper", bootstrap)
            self.assertIn("Android environment doctor", doctor)
            self.assertIn("JAVA_HOME is set to", doctor)
            self.assertIn("cmdline-tools/latest", doctor)
            self.assertIn("adb is available", doctor)
            self.assertIn("Emulator command is available", doctor)
            self.assertIn("gradle-wrapper.jar is missing", doctor)
            self.assertIn("Doctor found", doctor)
            self.assertIn("biucing.release.storeFile=signing/release.keystore", release_signing_example)
            self.assertIn("BIUCING_RELEASE_KEY_ALIAS", release_signing_example)
            self.assertIn("./gradlew spotlessApply", (project_dir / "Makefile").read_text(encoding="utf-8"))
            self.assertIn("./gradlew connectedDebugAndroidTest", (project_dir / "Makefile").read_text(encoding="utf-8"))
            self.assertIn("androidTestImplementation(libs.androidx.compose.ui.test.junit4)", app_build)
            self.assertIn("debugImplementation(libs.androidx.compose.ui.test.manifest)", app_build)
            self.assertIn("gradle wrapper --gradle-version 8.10.2", sync_wrapper)
            self.assertIn('-jar "$APP_HOME/gradle/wrapper/gradle-wrapper.jar"', gradlew)
            self.assertTrue(expected_files.issubset(generated_files))
            self.assertIn("gradle/wrapper/gradle-wrapper.jar", generated_files)
            self.assertTrue(os.access(project_dir / "gradlew", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "bootstrap", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "doctor", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "sync-gradle-wrapper", os.X_OK))

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

    def test_default_kotlin_module_name_derives_pascal_case(self):
        self.assertEqual(default_kotlin_module_name("demo-android_app"), "DemoAndroidApp")
        self.assertEqual(default_kotlin_module_name(""), "App")

    def test_render_text_replaces_android_placeholders(self):
        rendered = render_text(
            "\n".join(
                [
                    "applicationId = {{APPLICATION_ID}}",
                    "namespace = {{ANDROID_NAMESPACE}}",
                    "compileSdk = {{COMPILE_SDK}}",
                    "minSdk = {{MIN_SDK}}",
                    "targetSdk = {{TARGET_SDK}}",
                    "versionCode = {{VERSION_CODE}}",
                    "versionName = {{VERSION_NAME}}",
                    "javaVersion = {{JAVA_VERSION}}",
                    "moduleName = {{KOTLIN_MODULE_NAME}}",
                ]
            ),
            {
                "application_id": "com.example.demoandroid",
                "android_namespace": "com.example.demoandroid",
                "compile_sdk": "35",
                "min_sdk": "26",
                "target_sdk": "35",
                "version_code": "1",
                "version_name": "1.0.0",
                "java_version": "17",
                "kotlin_module_name": "DemoAndroid",
            },
        )

        self.assertIn("applicationId = com.example.demoandroid", rendered)
        self.assertIn("namespace = com.example.demoandroid", rendered)
        self.assertIn("compileSdk = 35", rendered)
        self.assertIn("minSdk = 26", rendered)
        self.assertIn("targetSdk = 35", rendered)
        self.assertIn("versionCode = 1", rendered)
        self.assertIn("versionName = 1.0.0", rendered)
        self.assertIn("javaVersion = 17", rendered)
        self.assertIn("moduleName = DemoAndroid", rendered)

    def test_render_text_replaces_microservice_placeholders(self):
        rendered = render_text(
            "\n".join(
                [
                    "grpcPort = {{GRPC_PORT}}",
                    "protoPackage = {{PROTO_PACKAGE}}",
                    "store = {{DEPENDENCY_STORE}}",
                    "image = {{DEPENDENCY_STORE_IMAGE}}",
                    "dsn = {{DEPENDENCY_STORE_DSN}}",
                    "collector = {{OTEL_EXPORTER_ENDPOINT}}",
                ]
            ),
            {
                "grpc_port": "9090",
                "proto_package": "user.v1",
                "dependency_store": "postgres",
                "dependency_store_image": "postgres:16-alpine",
                "dependency_store_dsn": "postgres://postgres:postgres@localhost:5432/user-service?sslmode=disable",
                "otel_exporter_endpoint": "http://localhost:4318",
            },
        )

        self.assertIn("grpcPort = 9090", rendered)
        self.assertIn("protoPackage = user.v1", rendered)
        self.assertIn("store = postgres", rendered)
        self.assertIn("image = postgres:16-alpine", rendered)
        self.assertIn(
            "dsn = postgres://postgres:postgres@localhost:5432/user-service?sslmode=disable",
            rendered,
        )
        self.assertIn("collector = http://localhost:4318", rendered)

    def test_create_frontend_renders_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                ["create", "frontend", "demo-app", "--output-dir", tmpdir]
            )
            project_dir = Path(tmpdir) / "demo-app"
            package_json = (project_dir / "package.json").read_text(encoding="utf-8")
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            index_html = (project_dir / "index.html").read_text(encoding="utf-8")
            eslint_config = (project_dir / "eslint.config.js").read_text(encoding="utf-8")
            prettier_config = (project_dir / ".prettierrc.json").read_text(encoding="utf-8")
            env_example = (project_dir / ".env.example").read_text(encoding="utf-8")
            vite_config = (project_dir / "vite.config.ts").read_text(encoding="utf-8")
            makefile = (project_dir / "Makefile").read_text(encoding="utf-8")
            dockerfile = (project_dir / "Dockerfile").read_text(encoding="utf-8")
            dockerfile_dev = (project_dir / "Dockerfile.dev").read_text(encoding="utf-8")
            dockerfile_dev_full = (
                project_dir / "Dockerfile.dev.full"
            ).read_text(encoding="utf-8")
            compose_dev = (project_dir / "compose.dev.yaml").read_text(encoding="utf-8")
            nginx_conf = (project_dir / "nginx.conf").read_text(encoding="utf-8")
            dockerignore = (project_dir / ".dockerignore").read_text(encoding="utf-8")
            app_test = (project_dir / "src" / "App.test.tsx").read_text(encoding="utf-8")
            app_file = (project_dir / "src" / "App.tsx").read_text(encoding="utf-8")
            env_config = (project_dir / "src" / "config" / "env.ts").read_text(encoding="utf-8")
            playwright_config = (
                project_dir / "playwright.smoke.config.ts"
            ).read_text(encoding="utf-8")
            browser_smoke_test = (
                project_dir / "tests" / "browser-smoke.spec.ts"
            ).read_text(encoding="utf-8")
            app_router = (
                project_dir / "src" / "router" / "AppRouter.tsx"
            ).read_text(encoding="utf-8")
            api_client = (
                project_dir / "src" / "services" / "api" / "client.ts"
            ).read_text(encoding="utf-8")
            test_setup = (
                project_dir / "src" / "test" / "setup.ts"
            ).read_text(encoding="utf-8")
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
            self.assertIn("make dev", output)
            self.assertIn("make test", output)
            self.assertIn("make docker-build", output)
            self.assertIn("make docker-run", output)
            self.assertIn("demo-app", package_json)
            self.assertIn('"packageManager": "pnpm@9.9.0"', package_json)
            self.assertIn('"node": ">=20.0.0"', package_json)
            self.assertIn("react-router-dom", package_json)
            self.assertIn('"lint": "eslint ."', package_json)
            self.assertIn('"typecheck": "tsc --noEmit"', package_json)
            self.assertIn('"test": "vitest run"', package_json)
            self.assertIn('"test:watch": "vitest"', package_json)
            self.assertIn('"browser:install": "playwright install chromium"', package_json)
            self.assertIn('"browser:smoke": "playwright test -c playwright.smoke.config.ts"', package_json)
            self.assertIn('"format": "prettier --write ."', package_json)
            self.assertIn("Docker Workflow", readme)
            self.assertIn("Available Commands", readme)
            self.assertIn("Quality Checks", readme)
            self.assertIn("Runtime Configuration", readme)
            self.assertIn("Docker Files", readme)
            self.assertIn("Package Manager", readme)
            self.assertIn("make dev", readme)
            self.assertIn("make browser-smoke", readme)
            self.assertIn("The default development image stays relatively light", readme)
            self.assertIn("make bootstrap-full", readme)
            self.assertIn("DEV_DOCKERFILE=Dockerfile.dev.full make dev", readme)
            self.assertIn("<title>Demo App</title>", index_html)
            self.assertIn("DEV_DOCKERFILE ?=Dockerfile.dev", makefile)
            self.assertIn(
                "DEV_DOCKERFILE=$(DEV_DOCKERFILE) docker compose -f $(DEV_COMPOSE_FILE) build $(DEV_SERVICE)",
                makefile,
            )
            self.assertIn(
                "DEV_DOCKERFILE=Dockerfile.dev.full docker compose -f $(DEV_COMPOSE_FILE) build $(DEV_SERVICE)",
                makefile,
            )
            self.assertIn(
                "DEV_DOCKERFILE=$(DEV_DOCKERFILE) docker compose -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE)",
                makefile,
            )
            self.assertIn(
                "DEV_DOCKERFILE=$(DEV_DOCKERFILE) docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm browser:install",
                makefile,
            )
            self.assertIn(
                "DEV_DOCKERFILE=$(DEV_DOCKERFILE) docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm browser:smoke",
                makefile,
            )
            self.assertIn("docker build -t $(IMAGE_REF) .", makefile)
            self.assertIn("FROM node:20-alpine AS builder", dockerfile)
            self.assertIn("FROM nginx:1.27-alpine", dockerfile)
            self.assertIn("COPY --from=builder /app/dist /usr/share/nginx/html", dockerfile)
            self.assertIn("FROM node:20-bookworm", dockerfile_dev)
            self.assertIn("PNPM_STORE_DIR=/pnpm-store", dockerfile_dev)
            self.assertIn("PLAYWRIGHT_BROWSERS_PATH=/ms-playwright", dockerfile_dev)
            self.assertIn(
                'CMD ["bash", "-lc", "if [ ! -d node_modules/.pnpm ]; then pnpm install; fi; pnpm dev --host 0.0.0.0 --port 5173"]',
                dockerfile_dev,
            )
            self.assertIn("FROM node:20-bookworm", dockerfile_dev_full)
            self.assertIn("COPY package.json ./", dockerfile_dev_full)
            self.assertIn("pnpm install --no-frozen-lockfile", dockerfile_dev_full)
            self.assertIn("pnpm exec playwright install chromium", dockerfile_dev_full)
            self.assertIn("frontend-dev", compose_dev)
            self.assertIn("dockerfile: ${DEV_DOCKERFILE:-Dockerfile.dev}", compose_dev)
            self.assertIn(
                'command: bash -lc "if [ ! -d node_modules/.pnpm ]; then pnpm install; fi; pnpm dev --host 0.0.0.0 --port 5173 --strictPort"',
                compose_dev,
            )
            self.assertIn("frontend-node-modules", compose_dev)
            self.assertIn("frontend-pnpm-store", compose_dev)
            self.assertIn("frontend-playwright-cache", compose_dev)
            self.assertIn("try_files $uri $uri/ /index.html;", nginx_conf)
            self.assertIn("node_modules/", dockerignore)
            self.assertIn("dist/", dockerignore)
            self.assertIn("react-refresh/only-export-components", eslint_config)
            self.assertIn('"trailingComma": "all"', prettier_config)
            self.assertIn("VITE_API_BASE_URL=http://localhost:8080", env_example)
            self.assertIn('environment: "jsdom"', vite_config)
            self.assertIn('include: ["src/**/*.test.{ts,tsx}"]', vite_config)
            self.assertIn("await getProjectOverview()", app_test)
            self.assertIn('from "vitest"', app_test)
            self.assertIn("toBeInTheDocument", app_test)
            self.assertIn("AppRouter", app_file)
            self.assertIn("apiBaseUrl", env_config)
            self.assertIn("pnpm exec vite", playwright_config)
            self.assertIn('baseURL: "http://127.0.0.1:4173"', playwright_config)
            self.assertIn('name: "Demo App"', browser_smoke_test)
            self.assertIn("browser-smoke-homepage.png", browser_smoke_test)
            self.assertIn("createBrowserRouter", app_router)
            self.assertIn("v7_startTransition", app_router)
            self.assertIn("VITE_API_BASE_URL is not configured", api_client)
            self.assertIn("@testing-library/jest-dom/vitest", test_setup)
            self.assertIn("useProjectOverview", home_page)
            self.assertIn('title: "Demo App"', overview_service)
            self.assertIn("getProjectOverviewFallback", overview_service)
            self.assertIn("export type ProjectOverview", overview_type)

    def test_create_microservice_renders_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "microservice",
                    "user-service",
                    "--output-dir",
                    tmpdir,
                    "--module-name",
                    "github.com/example/user-service",
                    "--proto-package",
                    "user.v1",
                    "--grpc-port",
                    "9191",
                    "--dependency-store",
                    "redis",
                    "--otel-exporter-endpoint",
                    "http://localhost:14318",
                ]
            )
            project_dir = Path(tmpdir) / "user-service"
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            makefile = (project_dir / "Makefile").read_text(encoding="utf-8")
            dockerfile = (project_dir / "Dockerfile").read_text(encoding="utf-8")
            dockerfile_dev = (project_dir / "Dockerfile.dev").read_text(encoding="utf-8")
            compose_dev = (project_dir / "compose.dev.yaml").read_text(encoding="utf-8")
            air_toml = (project_dir / ".air.toml").read_text(encoding="utf-8")
            dockerignore = (project_dir / ".dockerignore").read_text(encoding="utf-8")
            compose_yaml = (project_dir / "deploy" / "compose.yaml").read_text(encoding="utf-8")
            config_yaml = (project_dir / "configs" / "config.yaml").read_text(encoding="utf-8")
            proto_file = (
                project_dir / "api" / "proto" / "service" / "v1" / "service.proto"
            ).read_text(encoding="utf-8")
            buf_yaml = (project_dir / "api" / "buf.yaml").read_text(encoding="utf-8")
            buf_gen = (project_dir / "api" / "buf.gen.yaml").read_text(encoding="utf-8")
            go_sum = (project_dir / "go.sum").read_text(encoding="utf-8")
            mise_toml = (project_dir / ".mise.toml").read_text(encoding="utf-8")
            go_mod = (project_dir / "go.mod").read_text(encoding="utf-8")
            main_go = (project_dir / "cmd" / "server" / "main.go").read_text(encoding="utf-8")
            telemetry_go = (
                project_dir / "internal" / "telemetry" / "telemetry.go"
            ).read_text(encoding="utf-8")
            grpc_transport = (
                project_dir / "internal" / "transport" / "grpc.go"
            ).read_text(encoding="utf-8")
            config_go = (project_dir / "internal" / "config" / "config.go").read_text(
                encoding="utf-8"
            )
            config_test = (
                project_dir / "internal" / "config" / "config_test.go"
            ).read_text(encoding="utf-8")
            doctor = (project_dir / "scripts" / "doctor").read_text(encoding="utf-8")
            bootstrap = (project_dir / "scripts" / "bootstrap").read_text(encoding="utf-8")
            server_test = (project_dir / "tests" / "server_test.go").read_text(
                encoding="utf-8"
            )

            self.assertTrue(project_dir.exists())
            self.assertIn("Created microservice project: user-service", output)
            self.assertIn("make dev", output)
            self.assertIn("make verify", output)
            self.assertIn("make up", output)
            self.assertIn("OpenTelemetry", readme)
            self.assertIn("Docker Workflow", readme)
            self.assertIn("make dev-shell", readme)
            self.assertIn("Proto package: `user.v1`", readme)
            self.assertIn("Local dependency store: `redis`", readme)
            self.assertIn("make verify", readme)
            self.assertIn(
                "the first `make proto` may still fetch remote Buf plugin artifacts",
                readme,
            )
            self.assertIn("GOPROXY", readme)
            self.assertIn("GOSUMDB", readme)
            self.assertIn("docker compose -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE) redis otel-collector", makefile)
            self.assertIn("docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) buf generate ./api", makefile)
            self.assertIn('bash -lc "buf lint ./api && golangci-lint run', makefile)
            self.assertIn("HOST_GRPC_PORT ?=9191", makefile)
            self.assertIn("BUILDER_IMAGE ?= golang:1.26-alpine", makefile)
            self.assertIn("EXPOSE 9191", dockerfile)
            self.assertIn("ARG BUILDER_IMAGE=golang:1.26-alpine", dockerfile)
            self.assertIn("ARG BUF_VERSION=1.70.0", dockerfile_dev)
            self.assertIn("ARG GOLANGCI_LINT_VERSION=2.12.2", dockerfile_dev)
            self.assertIn("ARG GOPROXY=https://proxy.golang.org,direct", dockerfile_dev)
            self.assertIn("ARG GOSUMDB=sum.golang.org", dockerfile_dev)
            self.assertIn("buf-Linux-${buf_arch}.tar.gz", dockerfile_dev)
            self.assertIn("golangci-lint-${GOLANGCI_LINT_VERSION}-linux-${golangci_arch}.tar.gz", dockerfile_dev)
            self.assertIn("COPY go.mod go.sum ./", dockerfile_dev)
            self.assertIn("until go mod download; do", dockerfile_dev)
            self.assertIn('CMD ["air", "-c", ".air.toml"]', dockerfile_dev)
            self.assertIn("app-dev", compose_dev)
            self.assertIn("GOPROXY: ${GOPROXY:-https://proxy.golang.org,direct}", compose_dev)
            self.assertIn("GOSUMDB: ${GOSUMDB:-sum.golang.org}", compose_dev)
            self.assertIn("otel/opentelemetry-collector-contrib:0.126.0", compose_dev)
            self.assertIn("STORE_DSN: redis://redis:6379/0", compose_dev)
            self.assertIn('cmd = "go build -o ./tmp/server ./cmd/server"', air_toml)
            self.assertIn("include_ext = [\"go\", \"yaml\", \"proto\"]", air_toml)
            self.assertIn(".cache/", dockerignore)
            self.assertIn('image: user-service:latest', compose_yaml)
            self.assertIn('- "9191:9191"', compose_yaml)
            self.assertIn("BUILDER_IMAGE: ${BUILDER_IMAGE:-golang:1.26-alpine}", compose_yaml)
            self.assertIn("STORE_DSN: redis://redis:6379/0", compose_yaml)
            self.assertIn("image: redis:7-alpine", compose_yaml)
            self.assertNotIn("POSTGRES_PASSWORD", compose_yaml)
            self.assertIn("driver: redis", config_yaml)
            self.assertIn("dsn: redis://localhost:6379/0", config_yaml)
            self.assertIn("otlp_http_endpoint: http://localhost:14318", config_yaml)
            self.assertIn("package user.v1;", proto_file)
            self.assertIn('option go_package = "github.com/example/user-service/api/gen/go/service/v1;servicev1";', proto_file)
            self.assertIn("service UserServiceService", proto_file)
            self.assertIn("version: v2", buf_yaml)
            self.assertIn("remote: buf.build/protocolbuffers/go", buf_gen)
            self.assertIn("remote: buf.build/grpc/go", buf_gen)
            self.assertIn('go = "1.26.0"', mise_toml)
            self.assertIn("go 1.26.0", go_mod)
            self.assertIn("go.opentelemetry.io/otel v1.43.0", go_sum)
            self.assertIn("telemetry.Setup", main_go)
            self.assertIn('log.Printf("starting %s gRPC server on :%s"', main_go)
            self.assertIn("otlptracehttp.New", telemetry_go)
            self.assertIn("semconv.ServiceName(serviceName)", telemetry_go)
            self.assertIn("grpc.NewServer()", grpc_transport)
            self.assertIn("healthpb.RegisterHealthServer", grpc_transport)
            self.assertIn('cfg.Store.Driver = "redis"', config_go)
            self.assertIn('cfg.Telemetry.OTLPHTTPEndpoint = "http://localhost:14318"', config_go)
            self.assertIn("TestLoadUsesEnvironmentOverrides", config_test)
            self.assertIn("buf is not installed or not on PATH.", doctor)
            self.assertIn("service.grpc_port must be between 1 and 65535", doctor)
            self.assertIn("go mod tidy", bootstrap)
            self.assertIn("buf is not available on PATH.", bootstrap)
            self.assertIn("TestHealthz", server_test)
            self.assertIn("TestPing", server_test)
            self.assertTrue(os.access(project_dir / "scripts" / "bootstrap", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "doctor", os.X_OK))

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
            self.assertIn("BUILDER_IMAGE: ${BUILDER_IMAGE:-golang:1.26-alpine}", compose_yaml)
            self.assertIn("RUNTIME_IMAGE: ${RUNTIME_IMAGE:-alpine:3.20}", compose_yaml)
            self.assertIn("image: user-service:latest", compose_yaml)
            self.assertIn('- "8080:8080"', compose_yaml)
            self.assertIn("DOCKER_VARIANT ?=alpine", makefile)
            self.assertIn("DOCKER_PLATFORM ?=linux/arm64", makefile)
            self.assertIn("GOPROXY ?=https://proxy.golang.org,direct", makefile)
            self.assertIn("GOSUMDB ?=sum.golang.org", makefile)
            self.assertIn("DEV_COMPOSE_FILE ?=compose.dev.yaml", makefile)
            self.assertIn("GOPROXY=$(GOPROXY) GOSUMDB=$(GOSUMDB) docker compose -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE)", makefile)
            self.assertIn("public.ecr.aws/docker/library/golang:1.26", makefile)
            self.assertIn("public.ecr.aws/docker/library/ubuntu:26.04", makefile)
            self.assertIn("IMAGE ?=$(APP_NAME)", makefile)
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
            self.assertIn("command: air -c .air.toml", compose_dev)
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
            self.assertIn("TestLoadDefaultConfig", config_test)
            self.assertIn("TestLoadUsesConfigFileOverride", config_test)
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

    def test_create_worker_renders_template_and_generated_tests_pass(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "worker",
                    "email-worker",
                    "--output-dir",
                    tmpdir,
                    "--module-name",
                    "github.com/example/email-worker",
                    "--worker-name",
                    "mailer-worker",
                    "--run-mode",
                    "oneshot",
                    "--tick-interval-seconds",
                    "15",
                    "--shutdown-timeout-seconds",
                    "5",
                ]
            )
            project_dir = Path(tmpdir) / "email-worker"
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            makefile = (project_dir / "Makefile").read_text(encoding="utf-8")
            dockerfile = (project_dir / "Dockerfile").read_text(encoding="utf-8")
            dockerfile_dev = (project_dir / "Dockerfile.dev").read_text(encoding="utf-8")
            compose_dev = (project_dir / "compose.dev.yaml").read_text(encoding="utf-8")
            config_json = (project_dir / "configs" / "config.json").read_text(encoding="utf-8")
            main_go = (project_dir / "cmd" / "worker" / "main.go").read_text(encoding="utf-8")
            config_go = (project_dir / "internal" / "config" / "config.go").read_text(
                encoding="utf-8"
            )
            runner_go = (project_dir / "internal" / "runtime" / "runner.go").read_text(
                encoding="utf-8"
            )
            heartbeat_go = (project_dir / "internal" / "task" / "heartbeat.go").read_text(
                encoding="utf-8"
            )
            doctor = (project_dir / "scripts" / "doctor").read_text(encoding="utf-8")
            bootstrap = (project_dir / "scripts" / "bootstrap").read_text(encoding="utf-8")
            worker_test = (project_dir / "tests" / "worker_test.go").read_text(encoding="utf-8")

            self.assertTrue(project_dir.exists())
            self.assertIn("Created worker project: email-worker", output)
            self.assertIn("make bootstrap", output)
            self.assertIn("make verify", output)
            self.assertIn("make docker-run", output)
            self.assertIn("background execution rather than a public HTTP API", readme)
            self.assertIn("scheduled` and `oneshot` execution modes", readme)
            self.assertIn("WORKER_RUN_MODE=oneshot make run", readme)
            self.assertIn("go test ./...", readme)
            self.assertIn("APP_NAME=mailer-worker", makefile)
            self.assertIn("WORKER_RUN_MODE ?=oneshot", makefile)
            self.assertIn("WORKER_TICK_INTERVAL_SECONDS ?=15", makefile)
            self.assertIn("WORKER_SHUTDOWN_TIMEOUT_SECONDS ?=5", makefile)
            self.assertIn("docker run --rm -e WORKER_RUN_MODE=$(WORKER_RUN_MODE)", makefile)
            self.assertIn("ARG BUILDER_IMAGE=golang:1.26-alpine", dockerfile)
            self.assertIn('CMD ["/usr/local/bin/worker"]', dockerfile)
            self.assertIn('CMD ["sh", "-lc", "go run ./cmd/worker"]', dockerfile_dev)
            self.assertIn('WORKER_RUN_MODE: ${WORKER_RUN_MODE:-oneshot}', compose_dev)
            self.assertIn('"name": "mailer-worker"', config_json)
            self.assertIn('"run_mode": "oneshot"', config_json)
            self.assertIn('"tick_interval_seconds": 15', config_json)
            self.assertIn('"shutdown_timeout_seconds": 5', config_json)
            self.assertIn("signal.NotifyContext", main_go)
            self.assertIn("task.NewHeartbeatTask", main_go)
            self.assertIn('cfg.Worker.RunMode != "scheduled" && cfg.Worker.RunMode != "oneshot"', config_go)
            self.assertIn("runScheduled", runner_go)
            self.assertIn("heartbeat completed", heartbeat_go)
            self.assertIn("Worker environment doctor", doctor)
            self.assertIn("go mod tidy", bootstrap)
            self.assertIn('cfg.Worker.Name != "mailer-worker"', worker_test)
            self.assertTrue(os.access(project_dir / "scripts" / "bootstrap", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "doctor", os.X_OK))

            env = os.environ.copy()
            env["GOCACHE"] = str(project_dir / ".cache" / "go-build")
            env["GOTMPDIR"] = str(project_dir / ".cache" / "go-tmp")
            os.makedirs(env["GOCACHE"], exist_ok=True)
            os.makedirs(env["GOTMPDIR"], exist_ok=True)
            result = subprocess.run(
                ["go", "test", "./..."],
                cwd=project_dir,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                result.returncode,
                0,
                msg=f"go test failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
            )

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
            swiftlint_config = (project_dir / ".swiftlint.yml").read_text(
                encoding="utf-8"
            )
            swiftformat_config = (project_dir / ".swiftformat").read_text(
                encoding="utf-8"
            )
            project_swift = (project_dir / "App" / "Project.swift").read_text(
                encoding="utf-8"
            )
            home_view = (
                project_dir / "App" / "Targets" / "App" / "Sources" / "HomeView.swift"
            ).read_text(encoding="utf-8")
            home_view_model = (
                project_dir / "App" / "Targets" / "App" / "Sources" / "HomeViewModel.swift"
            ).read_text(encoding="utf-8")
            bootstrap = (project_dir / "scripts" / "bootstrap").read_text(encoding="utf-8")
            doctor = (project_dir / "scripts" / "doctor").read_text(encoding="utf-8")
            design_system = (
                project_dir
                / "Packages"
                / "DesignSystem"
                / "Package.swift"
            ).read_text(encoding="utf-8")
            app_services_package = (
                project_dir
                / "Packages"
                / "AppServices"
                / "Package.swift"
            ).read_text(encoding="utf-8")
            app_services_source = (
                project_dir
                / "Packages"
                / "AppServices"
                / "Sources"
                / "AppServices"
                / "StarterMetadata.swift"
            ).read_text(encoding="utf-8")
            design_system_theme = (
                project_dir
                / "Packages"
                / "DesignSystem"
                / "Sources"
                / "DesignSystem"
                / "Theme.swift"
            ).read_text(encoding="utf-8")
            appfile = (project_dir / "fastlane" / "Appfile").read_text(encoding="utf-8")
            fastfile = (project_dir / "fastlane" / "Fastfile").read_text(encoding="utf-8")
            app_tests = (
                project_dir / "App" / "Targets" / "AppTests" / "Sources" / "AppTests.swift"
            ).read_text(encoding="utf-8")

            self.assertTrue(project_dir.exists())
            self.assertIn("Created apple project: pulse-mac", output)
            self.assertIn("make bootstrap", output)
            self.assertIn("make doctor", output)
            self.assertIn("make lint", output)
            self.assertIn("Tuist", readme)
            self.assertIn("Target platform: `macOS`", readme)
            self.assertIn("make doctor", readme)
            self.assertIn("make lint", readme)
            self.assertIn("make format", readme)
            self.assertIn("make release", readme)
            self.assertIn("simulator/runtime visibility", readme)
            self.assertIn("warning-only signal for macOS starters", readme)
            self.assertIn("split-view workspace", readme)
            self.assertIn("small view-model test", readme)
            self.assertIn("mocked service dependency", readme)
            self.assertIn("`Packages/AppServices` holds starter metadata", readme)
            self.assertIn("keep UI-focused primitives in `DesignSystem`", readme)
            self.assertIn("`development_team` is written into `App/Project.swift`", readme)
            self.assertIn("`bundle_identifier` is used for the main app target", readme)
            self.assertIn("`{{BUNDLE_IDENTIFIER}}.tests`".replace("{{BUNDLE_IDENTIFIER}}", "com.example.pulsemac"), readme)
            self.assertIn("fastlane match", readme)
            self.assertIn("App Store Connect API key auth", readme)
            self.assertIn("lightweight validation lane", readme)
            self.assertIn("production-oriented lane", readme)
            self.assertIn("generate:", makefile)
            self.assertIn("tuist generate --no-open", makefile)
            self.assertIn("platform=macOS", makefile)
            self.assertIn("swiftlint lint --cache-path .swiftlint-cache", makefile)
            self.assertIn("swiftformat . --cache .swiftformat.cache", makefile)
            self.assertIn("included:", swiftlint_config)
            self.assertIn("modifier_order", swiftlint_config)
            self.assertIn("--swiftversion 6", swiftformat_config)
            self.assertIn("--disable trailingCommas", swiftformat_config)
            self.assertIn("--maxwidth 120", swiftformat_config)
            self.assertIn("let config = Config(", tuist_config)
            self.assertNotIn("fullHandle:", tuist_config)
            self.assertIn('bundleId: "com.example.pulsemac"', project_swift)
            self.assertIn('.local(path: "../Packages/AppServices")', project_swift)
            self.assertIn("destinations: .macOS", project_swift)
            self.assertIn('deploymentTargets: .macOS("26.0")', project_swift)
            self.assertIn('.package(product: "AppServices")', project_swift)
            self.assertIn('WindowGroup("Pulse Mac")', (project_dir / "App" / "Targets" / "App" / "Sources" / "AppEntry.swift").read_text(encoding="utf-8"))
            self.assertIn(".defaultSize(width: 1100, height: 720)", (project_dir / "App" / "Targets" / "App" / "Sources" / "AppEntry.swift").read_text(encoding="utf-8"))
            self.assertIn("private let viewModel = HomeViewModel(", home_view)
            self.assertIn("NavigationSplitView", home_view)
            self.assertIn('Section("Workspace")', home_view)
            self.assertIn('GroupBox("Project Summary")', home_view)
            self.assertIn('GroupBox("Release Checklist")', home_view)
            self.assertIn("struct HomeViewModel", home_view_model)
            self.assertIn("import AppServices", home_view_model)
            self.assertIn("typealias HomeFact = StarterFact", home_view_model)
            self.assertIn("StarterFactBuilder.overviewFacts(", home_view_model)
            self.assertIn("func releaseChecklist() -> [String]", home_view_model)
            self.assertIn("brew bundle", bootstrap)
            self.assertIn("Apple environment doctor", doctor)
            self.assertIn('platform_name="macOS"', doctor)
            self.assertIn('tuist_home="${repo_root}/.cache/tuist/home"', doctor)
            self.assertIn("xcode-select points to", doctor)
            self.assertIn("xcodebuild is available", doctor)
            self.assertIn("tuist is available", doctor)
            self.assertIn("swiftlint is available", doctor)
            self.assertIn("swiftformat is available", doctor)
            self.assertIn("fastlane is not available", doctor)
            self.assertIn("simulator services are not ready", doctor)
            self.assertIn("Doctor completed with", doctor)
            self.assertIn('.macOS("26.0")', design_system)
            self.assertIn('name: "AppServices"', app_services_package)
            self.assertIn("public struct StarterFact: Equatable", app_services_source)
            self.assertIn("public protocol ReleaseChecklistProviding", app_services_source)
            self.assertIn("public enum StarterFactBuilder", app_services_source)
            self.assertIn("enum BiucingTheme", design_system_theme)
            self.assertIn("sectionTitleFont", design_system_theme)
            self.assertIn("import AppServices", app_tests)
            self.assertIn('app_identifier("com.example.pulsemac")', appfile)
            self.assertIn('apple_id("developer@example.com")', appfile)
            self.assertIn('team_id("ABCDE12345")', appfile)
            self.assertIn("Replace this placeholder with the Apple ID", appfile)
            self.assertIn("Beta lane assumes the generated project already builds locally", fastfile)
            self.assertIn("Add match, provisioning, and TestFlight/App Store delivery", fastfile)
            self.assertIn('confirm signing for ABCDE12345 / com.example.pulsemac', fastfile)
            self.assertIn('sh("make lint")', fastfile)
            self.assertIn('sh("make test")', fastfile)
            self.assertIn('sh("make build")', fastfile)
            self.assertIn("@testable import PulseMac", app_tests)
            self.assertIn("func testHomeViewModelBuildsOverviewFacts()", app_tests)
            self.assertIn("func testHomeViewModelUsesMockChecklistProvider()", app_tests)
            self.assertIn("StarterFact(label: \"Bundle ID\"", app_tests)
            self.assertIn("private struct MockReleaseChecklistProvider", app_tests)

    def test_create_apple_ios_renders_platform_specific_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "apple",
                    "pulse-ios",
                    "--output-dir",
                    tmpdir,
                    "--platform",
                    "ios",
                    "--bundle-identifier",
                    "com.example.pulseios",
                    "--organization-name",
                    "Example Labs",
                    "--development-team",
                    "ABCDE12345",
                ]
            )
            project_dir = Path(tmpdir) / "pulse-ios"
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            project_swift = (project_dir / "App" / "Project.swift").read_text(
                encoding="utf-8"
            )
            app_entry = (
                project_dir / "App" / "Targets" / "App" / "Sources" / "AppEntry.swift"
            ).read_text(encoding="utf-8")
            home_view = (
                project_dir / "App" / "Targets" / "App" / "Sources" / "HomeView.swift"
            ).read_text(encoding="utf-8")

            self.assertIn("Created apple project: pulse-ios", output)
            self.assertIn("make doctor", output)
            self.assertIn("Target platform: `iOS`", readme)
            self.assertIn("stacked overview screen", readme)
            self.assertIn("make release", readme)
            self.assertIn("registered in the Apple Developer portal", readme)
            self.assertIn("destinations: .iOS", project_swift)
            self.assertIn('deploymentTargets: .iOS("26.0")', project_swift)
            self.assertIn("WindowGroup {", app_entry)
            self.assertNotIn(".defaultSize(", app_entry)
            self.assertIn("NavigationStack", home_view)
            self.assertIn('Section("Project Summary")', home_view)
            self.assertIn(".listStyle(.insetGrouped)", home_view)
            self.assertIn('navigationTitle("Starter Overview")', home_view)
            self.assertNotIn("NavigationSplitView", home_view)


if __name__ == "__main__":
    unittest.main()
