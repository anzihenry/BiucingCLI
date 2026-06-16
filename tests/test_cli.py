import io
import os
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
        self.assertIn("microservice", output)
        self.assertIn("web-service", output)

    def test_info_prints_template_details(self):
        output = self.run_cli(["info", "web-service"])

        self.assertIn("Template: web-service", output)
        self.assertIn("Go, Gin", output)
        self.assertIn("module_name", output)

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

    def test_version_prints_cli_version(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        with self.assertRaises(SystemExit) as excinfo:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                main(["--version"])

        self.assertEqual(excinfo.exception.code, 0)
        self.assertEqual(stdout.getvalue(), "biucing 0.1.0\n")
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
            self.assertIn("<title>Demo App</title>", index_html)
            self.assertIn("docker compose -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE)", makefile)
            self.assertIn('bash -lc "pnpm install && pnpm browser:install"', makefile)
            self.assertIn('bash -lc "pnpm install && pnpm browser:smoke"', makefile)
            self.assertIn("docker build -t $(IMAGE_REF) .", makefile)
            self.assertIn("FROM node:20-alpine AS builder", dockerfile)
            self.assertIn("FROM nginx:1.27-alpine", dockerfile)
            self.assertIn("COPY --from=builder /app/dist /usr/share/nginx/html", dockerfile)
            self.assertIn("FROM node:20-bookworm", dockerfile_dev)
            self.assertIn("PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright", dockerfile_dev)
            self.assertIn("pnpm dev --host 0.0.0.0 --port 5173", dockerfile_dev)
            self.assertIn("frontend-dev", compose_dev)
            self.assertIn("pnpm install && pnpm dev --host 0.0.0.0 --port 5173 --strictPort", compose_dev)
            self.assertIn("frontend-node-modules", compose_dev)
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
            self.assertIn("docker compose -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE) redis otel-collector", makefile)
            self.assertIn("docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) buf generate ./api", makefile)
            self.assertIn('bash -lc "buf lint ./api && golangci-lint run', makefile)
            self.assertIn("HOST_GRPC_PORT ?=9191", makefile)
            self.assertIn("BUILDER_IMAGE ?= golang:1.26-alpine", makefile)
            self.assertIn("EXPOSE 9191", dockerfile)
            self.assertIn("ARG BUILDER_IMAGE=golang:1.26-alpine", dockerfile)
            self.assertIn("ARG BUF_VERSION=1.70.0", dockerfile_dev)
            self.assertIn("ARG GOLANGCI_LINT_VERSION=2.12.2", dockerfile_dev)
            self.assertIn("buf-Linux-${buf_arch}.tar.gz", dockerfile_dev)
            self.assertIn("golangci-lint-${GOLANGCI_LINT_VERSION}-linux-${golangci_arch}.tar.gz", dockerfile_dev)
            self.assertIn('CMD ["air", "-c", ".air.toml"]', dockerfile_dev)
            self.assertIn("app-dev", compose_dev)
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
            self.assertIn("DEV_COMPOSE_FILE ?=compose.dev.yaml", makefile)
            self.assertIn("docker compose -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE)", makefile)
            self.assertIn("public.ecr.aws/docker/library/golang:1.26", makefile)
            self.assertIn("public.ecr.aws/docker/library/ubuntu:26.04", makefile)
            self.assertIn("IMAGE ?=$(APP_NAME)", makefile)
            self.assertIn("--build-arg BUILDER_IMAGE=$(BUILDER_IMAGE)", makefile)
            self.assertIn("--build-arg RUNTIME_IMAGE=$(RUNTIME_IMAGE)", makefile)
            self.assertIn("docker run --rm -p $(HOST_PORT):$(CONTAINER_PORT) $(IMAGE_REF)", makefile)
            self.assertIn("docker push $(IMAGE_REF)", makefile)
            self.assertIn("ARG AIR_VERSION=1.65.3", dockerfile_dev)
            self.assertIn("ARG GOLANGCI_LINT_VERSION=2.12.2", dockerfile_dev)
            self.assertIn("air_${AIR_VERSION}_linux_${air_arch}.tar.gz", dockerfile_dev)
            self.assertIn("golangci-lint-${GOLANGCI_LINT_VERSION}-linux-${golangci_arch}.tar.gz", dockerfile_dev)
            self.assertIn("app-dev", compose_dev)
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
