import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from biucingcli.cli import default_kotlin_module_name
from biucingcli.cli import main
from biucingcli.templates import render_text


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
        self.assertIn("android", output)
        self.assertIn("apple", output)
        self.assertIn("frontend", output)
        self.assertIn("web", output)

    def test_info_prints_template_details(self):
        output = self.run_cli(["info", "web"])

        self.assertIn("Template: web", output)
        self.assertIn("Go, Gin", output)
        self.assertIn("module_name", output)

    def test_info_prints_android_template_details(self):
        output = self.run_cli(["info", "android"])

        self.assertIn("Template: android", output)
        self.assertIn("Kotlin, Android, Gradle, Jetpack Compose, fastlane", output)
        self.assertIn("package_name", output)
        self.assertIn("compile_sdk", output)

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
            home_route = (
                project_dir / "feature" / "home" / "src" / "main" / "java" / "home" / "HomeRoute.kt"
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
            appfile = (project_dir / "fastlane" / "Appfile").read_text(encoding="utf-8")
            bootstrap = (project_dir / "scripts" / "bootstrap").read_text(encoding="utf-8")
            doctor = (project_dir / "scripts" / "doctor").read_text(encoding="utf-8")
            sync_wrapper = (
                project_dir / "scripts" / "sync-gradle-wrapper"
            ).read_text(encoding="utf-8")
            gradlew = (project_dir / "gradlew").read_text(encoding="utf-8")
            generated_files = {
                path.relative_to(project_dir).as_posix()
                for path in project_dir.rglob("*")
                if path.is_file()
            }
            expected_files = {
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
                "app/src/test/java/app/AppSmokeTest.kt",
                "build.gradle.kts",
                "core/designsystem/build.gradle.kts",
                "core/designsystem/src/main/java/designsystem/Theme.kt",
                "core/model/build.gradle.kts",
                "core/model/src/main/java/model/Greeting.kt",
                "core/model/src/test/java/model/GreetingTest.kt",
                "fastlane/Appfile",
                "fastlane/Fastfile",
                "feature/home/build.gradle.kts",
                "feature/home/src/main/java/home/HomeRoute.kt",
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
            self.assertIn('open -a "Android Studio" .', output)
            self.assertIn("Application ID: `com.example.demoandroid.app`", readme)
            self.assertIn('rootProject.name = "demo-android"', settings_gradle)
            self.assertIn('include(":feature:home")', settings_gradle)
            self.assertIn('namespace = "com.example.demoandroid"', app_build)
            self.assertIn('applicationId = "com.example.demoandroid.app"', app_build)
            self.assertIn('versionCode = 7', app_build)
            self.assertIn('versionName = "1.2.3"', app_build)
            self.assertIn('android:label="Demo Android"', manifest)
            self.assertIn('android:theme="@style/Theme.DemoAndroid"', manifest)
            self.assertIn("package com.example.demoandroid", main_activity)
            self.assertIn("BiucingTheme", main_activity)
            self.assertIn("package com.example.demoandroid.feature.home", home_route)
            self.assertIn('title = "Demo Android"', home_route)
            self.assertIn("fun BiucingTheme", theme)
            self.assertIn('package_name("com.example.demoandroid.app")', appfile)
            self.assertIn("./scripts/setup-android-sdk", bootstrap)
            self.assertNotIn("./scripts/sync-gradle-wrapper", bootstrap)
            self.assertIn("gradle-wrapper.jar is missing", doctor)
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
