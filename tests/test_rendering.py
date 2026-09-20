"""Focused rendering regression coverage; extracted without changing assertions."""

import unittest

from biucingcli.rendering import render_text


from cli_support import CLIHelpers


class RenderingTests(CLIHelpers, unittest.TestCase):
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

    def test_render_text_replaces_harmonyos_placeholders(self):
        rendered = render_text(
            "\n".join(
                [
                    "bundleName = {{BUNDLE_NAME}}",
                    "module = {{HARMONY_MODULE_NAME}}",
                    "ability = {{ABILITY_NAME}}",
                    "compatible = {{COMPATIBLE_SDK_VERSION}}",
                    "target = {{TARGET_SDK_VERSION}}",
                    "minApi = {{MIN_API_VERSION}}",
                    "versionCode = {{HARMONY_VERSION_CODE}}",
                    "versionName = {{HARMONY_VERSION_NAME}}",
                ]
            ),
            {
                "bundle_name": "com.example.demo",
                "harmony_module_name": "entry",
                "ability_name": "EntryAbility",
                "compatible_sdk_version": "5.0.0(12)",
                "target_sdk_version": "5.0.0(12)",
                "min_api_version": "12",
                "harmony_version_code": "1",
                "harmony_version_name": "1.0.0",
            },
        )

        self.assertIn("bundleName = com.example.demo", rendered)
        self.assertIn("module = entry", rendered)
        self.assertIn("ability = EntryAbility", rendered)
        self.assertIn("compatible = 5.0.0(12)", rendered)
        self.assertIn("target = 5.0.0(12)", rendered)
        self.assertIn("minApi = 12", rendered)
        self.assertIn("versionCode = 1", rendered)
        self.assertIn("versionName = 1.0.0", rendered)

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


if __name__ == "__main__":
    unittest.main()
