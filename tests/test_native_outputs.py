"""Focused native regression coverage; extracted without changing assertions."""

import os
import tempfile
import unittest
from pathlib import Path



from cli_support import CLIHelpers


class NativeOutputTests(CLIHelpers, unittest.TestCase):
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
            artifact_info = (project_dir / "scripts" / "artifact-info").read_text(
                encoding="utf-8"
            )
            sync_wrapper = (
                project_dir / "scripts" / "sync-gradle-wrapper"
            ).read_text(encoding="utf-8")
            gradle_supply_chain = (
                project_dir / "scripts" / "verify-gradle-supply-chain"
            ).read_text(encoding="utf-8")
            release_artifact_verifier = (
                project_dir / "scripts" / "verify-release-artifact"
            ).read_text(encoding="utf-8")
            release_signing_example = (
                project_dir / "docs" / "release-signing.properties.example"
            ).read_text(encoding="utf-8")
            release_delivery = (
                project_dir / "docs" / "release-delivery.md"
            ).read_text(encoding="utf-8")
            fastlane_env_example = (
                project_dir / "fastlane" / ".env.example"
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
                "docs/release-delivery.md",
                "docs/release-signing.properties.example",
                "fastlane/.env.example",
                "fastlane/Appfile",
                "fastlane/Fastfile",
                "feature/home/build.gradle.kts",
                "feature/home/src/main/java/home/HomeRoute.kt",
                "feature/settings/build.gradle.kts",
                "feature/settings/src/main/java/settings/SettingsRoute.kt",
                "gradle.properties",
                "gradle/libs.versions.toml",
                "gradle/verification-metadata.xml",
                "gradle/wrapper/gradle-wrapper.jar.sha256",
                "gradle/wrapper/gradle-wrapper.properties",
                "gradlew",
                "gradlew.bat",
                "scripts/bootstrap",
                "scripts/artifact-info",
                "scripts/doctor",
                "scripts/setup-android-sdk",
                "scripts/sync-gradle-wrapper",
                "scripts/verify-gradle-supply-chain",
                "scripts/verify-release-artifact",
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
            self.assertIn("make release-doctor", readme)
            self.assertIn("make archive", readme)
            self.assertIn("make verify", readme)
            self.assertIn("make verify-release-signing", readme)
            self.assertIn("make verify-supply-chain", readme)
            self.assertIn("make verify-release-artifact", readme)
            self.assertIn("make artifact-info", readme)
            self.assertIn("Google Play `internal` track", readme)
            self.assertIn("production` track as a `draft`", readme)
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
            self.assertIn("val debugApplicationIdSuffix =", app_build)
            self.assertIn('providers.gradleProperty("biucing.worktree.applicationIdSuffix")', app_build)
            self.assertIn("applicationIdSuffix = debugApplicationIdSuffix", app_build)
            self.assertIn('versionNameSuffix = "-debug"', app_build)
            self.assertIn('create("release")', app_build)
            self.assertIn('signingConfig = signingConfigs.getByName("release")', app_build)
            self.assertIn('storeFile = rootProject.file(releaseStoreFile!!)', app_build)
            self.assertIn('tasks.register("verifyReleaseSigning")', app_build)
            self.assertIn("KeyStore.getInstance", app_build)
            self.assertIn('biucing.release.storeFile', app_build)
            self.assertIn('BIUCING_RELEASE_STORE_FILE', app_build)
            self.assertIn('hasCompleteReleaseSigning', app_build)
            self.assertIn('implementation(project(":core:network"))', app_build)
            self.assertIn('implementation(project(":feature:settings"))', app_build)
            self.assertIn('testImplementation(project(":core:testing"))', app_build)
            self.assertIn('android:label="@string/app_name"', manifest)
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
            self.assertIn('APP_IDENTIFIER = "com.example.demoandroid.app"', fastfile)
            self.assertIn("lane :release_doctor", fastfile)
            self.assertIn("lane :archive", fastfile)
            self.assertIn("make bundle-release", fastfile)
            self.assertIn("make verify-release-signing", fastfile)
            self.assertIn("make artifact-info", fastfile)
            self.assertIn("make verify-release-artifact", fastfile)
            self.assertIn("upload_to_play_store", fastfile)
            self.assertIn('PLAY_STORE_BETA_TRACK", "internal"', fastfile)
            self.assertIn('PLAY_STORE_RELEASE_TRACK", "production"', fastfile)
            self.assertIn('PLAY_STORE_RELEASE_STATUS", "draft"', fastfile)
            self.assertIn("GOOGLE_PLAY_SERVICE_ACCOUNT_JSON", fastfile)
            self.assertIn("BIUCING_RELEASE_STORE_FILE", fastlane_env_example)
            self.assertIn(
                "GOOGLE_PLAY_SERVICE_ACCOUNT_JSON=credentials/play-store-service-account.json",
                fastlane_env_example,
            )
            self.assertIn("make release-doctor", release_delivery)
            self.assertIn("make artifact-info", release_delivery)
            self.assertIn("uploads the AAB to the `internal` track", release_delivery)
            self.assertIn("production` track as a `draft`", release_delivery)
            self.assertIn("./scripts/setup-android-sdk", bootstrap)
            self.assertNotIn("./scripts/sync-gradle-wrapper", bootstrap)
            self.assertIn("Android environment doctor", doctor)
            self.assertIn("JAVA_HOME is set to", doctor)
            self.assertIn("cmdline-tools/latest", doctor)
            self.assertIn("adb is available", doctor)
            self.assertIn("Emulator command is available", doctor)
            self.assertIn("gradle-wrapper.jar is missing", doctor)
            self.assertIn("Gradle supply-chain verification failed", doctor)
            self.assertIn("fastlane is not available", doctor)
            self.assertIn("Doctor found", doctor)
            self.assertIn("biucing.release.storeFile=signing/release.keystore", release_signing_example)
            self.assertIn("BIUCING_RELEASE_KEY_ALIAS", release_signing_example)
            android_makefile = (project_dir / "Makefile").read_text(encoding="utf-8")
            self.assertIn("WORKTREE_ROOT ?= $(shell git rev-parse --show-toplevel", android_makefile)
            self.assertIn("WORKTREE_LABEL ?= $(shell basename", android_makefile)
            self.assertIn("WORKTREE_ID ?= w$(shell printf '%s' \"$(WORKTREE_ROOT)\" | shasum | cut -c1-8)", android_makefile)
            self.assertIn("WORKTREE_ID", android_makefile)
            self.assertIn("GRADLE_USER_HOME", android_makefile)
            self.assertIn("DEBUG_APPLICATION_ID_SUFFIX", android_makefile)
            self.assertIn("worktree-info:", android_makefile)
            self.assertIn("worktree-doctor:", android_makefile)
            self.assertIn("clean-worktree:", android_makefile)
            self.assertIn("$(GRADLE) spotlessApply", android_makefile)
            self.assertIn("$(GRADLE) bundleRelease", android_makefile)
            self.assertIn("verify-release-signing:", android_makefile)
            self.assertIn("artifact-info:", android_makefile)
            self.assertIn("verify-supply-chain:", android_makefile)
            self.assertIn("verify-release-signing test test-ui lint format install-debug: verify-supply-chain", android_makefile)
            self.assertIn("verify-release-artifact:", android_makefile)
            self.assertIn("verify: verify-supply-chain doctor lint test build", android_makefile)
            self.assertIn("release-doctor:", android_makefile)
            self.assertIn("archive:", android_makefile)
            self.assertIn("$(GRADLE) connectedDebugAndroidTest", android_makefile)
            self.assertIn("Worktree Workflow", readme)
            self.assertIn("debug application ID", readme)
            self.assertIn("androidTestImplementation(libs.androidx.compose.ui.test.junit4)", app_build)
            self.assertIn("debugImplementation(libs.androidx.compose.ui.test.manifest)", app_build)
            self.assertIn("Android App Bundle artifact check", artifact_info)
            self.assertIn("./scripts/verify-release-artifact", artifact_info)
            self.assertIn("gradle wrapper", sync_wrapper)
            self.assertIn("--gradle-version 8.10.2", sync_wrapper)
            self.assertIn("--gradle-distribution-sha256-sum", sync_wrapper)
            self.assertIn("Android Gradle supply-chain verification", gradle_supply_chain)
            self.assertIn("gradle/verification-metadata.xml", gradle_supply_chain)
            self.assertIn("Gradle wrapper JAR checksum mismatch", gradle_supply_chain)
            self.assertIn("Android release artifact signature verification", release_artifact_verifier)
            self.assertIn("AAB signer certificate does not match", release_artifact_verifier)
            self.assertIn("jarsigner", release_artifact_verifier)
            self.assertIn("org.gradle.wrapper.GradleWrapperMain", gradlew)
            self.assertTrue(expected_files.issubset(generated_files))
            self.assertIn("gradle/wrapper/gradle-wrapper.jar", generated_files)
            self.assertTrue(os.access(project_dir / "gradlew", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "bootstrap", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "artifact-info", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "doctor", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "sync-gradle-wrapper", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "verify-gradle-supply-chain", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "verify-release-artifact", os.X_OK))

    def test_create_harmonyos_renders_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "harmonyos",
                    "demo-harmony",
                    "--output-dir",
                    tmpdir,
                    "--bundle-name",
                    "com.example.demoharmony",
                    "--harmony-module-name",
                    "entry",
                    "--ability-name",
                    "EntryAbility",
                    "--compatible-sdk-version",
                    "5.0.0(12)",
                    "--target-sdk-version",
                    "5.0.0(12)",
                    "--min-api-version",
                    "12",
                    "--harmony-version-code",
                    "7",
                    "--harmony-version-name",
                    "1.2.3",
                    "--organization-name",
                    "Example Labs",
                ]
            )
            project_dir = Path(tmpdir) / "demo-harmony"
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            root_package = (project_dir / "oh-package.json5").read_text(encoding="utf-8")
            root_lock = (project_dir / "oh-package-lock.json5").read_text(encoding="utf-8")
            app_json = (project_dir / "AppScope" / "app.json5").read_text(encoding="utf-8")
            app_scope_strings = (
                project_dir
                / "AppScope"
                / "resources"
                / "base"
                / "element"
                / "string.json"
            ).read_text(encoding="utf-8")
            layered_image = (
                project_dir
                / "AppScope"
                / "resources"
                / "base"
                / "media"
                / "layered_image.json"
            ).read_text(encoding="utf-8")
            build_profile = (project_dir / "build-profile.json5").read_text(encoding="utf-8")
            root_hvigorfile = (project_dir / "hvigorfile.ts").read_text(encoding="utf-8")
            hvigor_config = (
                project_dir / "hvigor" / "hvigor-config.json5"
            ).read_text(encoding="utf-8")
            entry_hvigorfile = (project_dir / "entry" / "hvigorfile.ts").read_text(
                encoding="utf-8"
            )
            module_json = (
                project_dir / "entry" / "src" / "main" / "module.json5"
            ).read_text(encoding="utf-8")
            ability = (
                project_dir
                / "entry"
                / "src"
                / "main"
                / "ets"
                / "entryability"
                / "EntryAbility.ets"
            ).read_text(encoding="utf-8")
            page = (
                project_dir / "entry" / "src" / "main" / "ets" / "pages" / "Index.ets"
            ).read_text(encoding="utf-8")
            app_config = (
                project_dir
                / "entry"
                / "src"
                / "main"
                / "ets"
                / "core"
                / "config"
                / "AppConfig.ets"
            ).read_text(encoding="utf-8")
            design_tokens = (
                project_dir
                / "entry"
                / "src"
                / "main"
                / "ets"
                / "core"
                / "designsystem"
                / "Tokens.ets"
            ).read_text(encoding="utf-8")
            settings_page = (
                project_dir / "entry" / "src" / "main" / "ets" / "pages" / "Settings.ets"
            ).read_text(encoding="utf-8")
            strings = (
                project_dir
                / "entry"
                / "src"
                / "main"
                / "resources"
                / "base"
                / "element"
                / "string.json"
            ).read_text(encoding="utf-8")
            main_pages = (
                project_dir
                / "entry"
                / "src"
                / "main"
                / "resources"
                / "base"
                / "profile"
                / "main_pages.json"
            ).read_text(encoding="utf-8")
            makefile = (project_dir / "Makefile").read_text(encoding="utf-8")
            bootstrap = (project_dir / "scripts" / "bootstrap").read_text(encoding="utf-8")
            doctor = (project_dir / "scripts" / "doctor").read_text(encoding="utf-8")
            lint = (project_dir / "scripts" / "lint").read_text(encoding="utf-8")
            test_script = (project_dir / "scripts" / "test").read_text(encoding="utf-8")
            artifact_info = (project_dir / "scripts" / "artifact-info").read_text(
                encoding="utf-8"
            )
            release_preflight = (
                project_dir / "scripts" / "release-preflight"
            ).read_text(encoding="utf-8")
            release_build = (project_dir / "scripts" / "release-build").read_text(
                encoding="utf-8"
            )
            supply_chain = (project_dir / "scripts" / "verify-supply-chain").read_text(
                encoding="utf-8"
            )
            release_artifact_verifier = (
                project_dir / "scripts" / "verify-release-artifact"
            ).read_text(encoding="utf-8")
            starter_test = (
                project_dir / "entry" / "src" / "test" / "List.test.ets"
            ).read_text(encoding="utf-8")
            signing_example = (
                project_dir / "docs" / "release-signing.local.properties.example"
            ).read_text(encoding="utf-8")

            self.assertTrue(project_dir.exists())
            self.assertIn("Created harmonyos project: demo-harmony", output)
            self.assertIn("make bootstrap", output)
            self.assertIn("make doctor", output)
            self.assertIn("make lint", output)
            self.assertIn("make test", output)
            self.assertIn("make build", output)
            self.assertIn("make artifact-info", output)
            self.assertIn("make verify", output)
            self.assertIn("make release-preflight", output)
            self.assertIn('open -a "DevEco Studio" .', output)
            self.assertIn("Bundle name: `com.example.demoharmony`", readme)
            self.assertIn("Compatible SDK: `5.0.0(12)`", readme)
            self.assertIn("Version: `1.2.3` (`7`)", readme)
            self.assertIn('"modelVersion": "5.0.0"', root_package)
            self.assertIn('"@ohos/hypium": "1.0.28"', root_package)
            self.assertIn('"lockfileVersion": 3', root_lock)
            self.assertIn('"@ohos/hypium@1.0.28"', root_lock)
            self.assertIn('"bundleName": "com.example.demoharmony"', app_json)
            self.assertIn('"vendor": "Example Labs"', app_json)
            self.assertIn('"versionCode": 7', app_json)
            self.assertIn('"versionName": "1.2.3"', app_json)
            self.assertIn('"icon": "$media:layered_image"', app_json)
            self.assertIn('"value": "Demo Harmony"', app_scope_strings)
            self.assertIn('"background": "$media:background"', layered_image)
            self.assertIn('"compatibleSdkVersion": "5.0.0(12)"', build_profile)
            self.assertIn('"targetSdkVersion": "5.0.0(12)"', build_profile)
            self.assertIn('"signingConfigs": []', build_profile)
            self.assertIn('"srcPath": "./entry"', build_profile)
            self.assertIn("import { appTasks } from '@ohos/hvigor-ohos-plugin';", root_hvigorfile)
            self.assertIn('"modelVersion": "5.0.0"', hvigor_config)
            self.assertIn("import { hapTasks } from '@ohos/hvigor-ohos-plugin';", entry_hvigorfile)
            self.assertIn('"name": "entry"', module_json)
            self.assertIn('"mainElement": "EntryAbility"', module_json)
            self.assertIn('"srcEntry": "./ets/entryability/EntryAbility.ets"', module_json)
            self.assertIn('"metadata"', module_json)
            self.assertIn("export default class EntryAbility extends UIAbility", ability)
            self.assertIn("windowStage.loadContent('pages/Index'", ability)
            self.assertIn("Text(AppConfig.displayName)", page)
            self.assertIn("this.getUIContext().getRouter().pushUrl", page)
            self.assertIn("BiucingSpacing.large", page)
            self.assertIn("static readonly displayName: string = 'Demo Harmony';", app_config)
            self.assertIn("static readonly bundleName: string = 'com.example.demoharmony';", app_config)
            self.assertIn("static readonly worktreeBundleSuffix: string = '';", app_config)
            self.assertIn("static readonly versionName: string = '1.2.3';", app_config)
            self.assertIn("class BiucingSpacing", design_tokens)
            self.assertIn("class BiucingTypography", design_tokens)
            self.assertIn("struct Settings", settings_page)
            self.assertIn("Text(`Bundle: ${AppConfig.bundleName}`)", settings_page)
            self.assertIn("Text(`Version ${AppConfig.versionName}`)", settings_page)
            self.assertIn('"value": "Demo Harmony entry module"', strings)
            self.assertIn('"pages/Index"', main_pages)
            self.assertIn('"pages/Settings"', main_pages)
            self.assertIn("HVIGOR ?= hvigorw", makefile)
            self.assertIn("./scripts/lint", makefile)
            self.assertIn("./scripts/test", makefile)
            self.assertIn("./scripts/artifact-info", makefile)
            self.assertIn("verify: verify-supply-chain doctor lint test build artifact-info", makefile)
            self.assertIn("./scripts/release-preflight", makefile)
            self.assertIn("./scripts/release-build", makefile)
            self.assertIn("./scripts/verify-supply-chain", makefile)
            self.assertIn("./scripts/verify-release-artifact", makefile)
            self.assertIn("release-preflight release: verify-supply-chain", makefile)
            self.assertIn("WORKTREE_ROOT ?= $(shell git rev-parse --show-toplevel", makefile)
            self.assertIn("WORKTREE_LABEL ?= $(shell basename", makefile)
            self.assertIn("WORKTREE_ID ?= $(shell printf '%s' \"$(WORKTREE_ROOT)\" | shasum | cut -c1-8)", makefile)
            self.assertIn("WORKTREE_ID", makefile)
            self.assertIn("HVIGOR_HOME", makefile)
            self.assertIn("OHPM_HOME", makefile)
            self.assertIn("DEBUG_BUNDLE_SUFFIX", makefile)
            self.assertIn("worktree-info:", makefile)
            self.assertIn("worktree-doctor:", makefile)
            self.assertIn("worktree-debug-identity:", makefile)
            self.assertIn("Debug bundle rewriting: deferred", makefile)
            self.assertIn("Status: bundle rewriting is deferred", makefile)
            self.assertIn("clean-worktree:", makefile)
            self.assertIn("$(HVIGOR) assembleHap --mode module $(HVIGOR_PROPS)", makefile)
            self.assertIn("make signing-info", readme)
            self.assertIn("make test", readme)
            self.assertIn("make artifact-info", readme)
            self.assertIn("make verify", readme)
            self.assertIn("make release-preflight", readme)
            self.assertIn("make release", readme)
            self.assertIn("Worktree Workflow", readme)
            self.assertIn("DEBUG_BUNDLE_SUFFIX", readme)
            self.assertIn("make worktree-debug-identity", readme)
            self.assertIn("Automatic per-worktree bundle rewriting is deferred", readme)
            self.assertIn("The generated starter exposes `make test`", readme)
            self.assertIn("Pre-Distribution Coverage", readme)
            self.assertIn("release-signing.local.properties.example", readme)
            self.assertIn("local.properties` for local-only signing values", readme)
            self.assertIn("entry/src/main/ets/core/config/", readme)
            self.assertIn("entry/src/main/ets/core/designsystem/", readme)
            self.assertIn("ohpm install", bootstrap)
            self.assertIn("--lockfile_stable_order --resolve_conflict_strict", bootstrap)
            self.assertIn("ohpm changed oh-package-lock.json5", bootstrap)
            self.assertIn("HarmonyOS environment doctor", doctor)
            self.assertIn("DevEco Studio is installed", doctor)
            self.assertIn("ohpm is available", doctor)
            self.assertIn("hvigorw is available", doctor)
            self.assertIn("DEVECO_SDK_HOME must be set for hvigorw builds", doctor)
            self.assertIn("SDK entry ${sdk_entry} exists", doctor)
            self.assertIn("code-linter.json5 is parseable", doctor)
            self.assertIn("Local builds can produce unsigned HAPs", doctor)
            self.assertIn("make release requires local signing material", doctor)
            self.assertIn("entry/src/main/module.json5 is missing", doctor)
            self.assertIn("entry/src/main/ets/core/config/AppConfig.ets", doctor)
            self.assertIn("entry/src/main/ets/pages/Settings.ets", doctor)
            self.assertIn("HarmonyOS lint configuration guard", lint)
            self.assertIn("code-linter.json5 is valid JSON", lint)
            self.assertIn("entry/src/main/ets/core/designsystem/Tokens.ets", lint)
            self.assertIn("entry/src/main/ets/pages/Settings.ets", lint)
            self.assertIn("scripts/release-build", lint)
            self.assertIn("scripts/release-preflight", lint)
            self.assertIn("scripts/test", lint)
            self.assertIn("scripts/artifact-info", lint)
            self.assertIn("scripts/verify-supply-chain", lint)
            self.assertIn("scripts/verify-release-artifact", lint)
            self.assertIn("Hypium test dependency and starter test suite are present", lint)
            self.assertIn("no unrendered template placeholders found", lint)
            self.assertIn("Running HarmonyOS ArkTS unit tests with hvigor", test_script)
            self.assertIn("@ohos/hypium is not installed", test_script)
            self.assertIn('"$HVIGOR_BIN" test --mode module', test_script)
            self.assertIn("HarmonyOS package artifact check", artifact_info)
            self.assertIn("No HAP artifact found", artifact_info)
            self.assertIn("HarmonyOS release signing preflight", release_preflight)
            self.assertIn("contains signing material", release_preflight)
            self.assertIn("Release signing material is present", release_preflight)
            self.assertIn("import { describe, expect, it } from '@ohos/hypium';", starter_test)
            self.assertIn("export default function testsuite", starter_test)
            self.assertIn("com.example.demoharmony", starter_test)
            self.assertIn("local.properties is missing", release_build)
            self.assertIn("./scripts/release-preflight", release_build)
            self.assertIn("git diff --quiet", release_build)
            self.assertIn("cmp -s", release_build)
            self.assertIn("trap 'exit 143' TERM", release_build)
            self.assertIn("biucing.harmony.signing.certpath", release_build)
            self.assertIn("type: 'HarmonyOS'", release_build)
            self.assertIn("buildMode=release", release_build)
            self.assertIn("./scripts/verify-release-artifact", release_build)
            self.assertIn("./scripts/verify-supply-chain", release_build)
            self.assertIn("HarmonyOS ohpm supply-chain verification", supply_chain)
            self.assertIn("sha512", supply_chain)
            self.assertIn("https://ohpm.openharmony.cn/ohpm/", supply_chain)
            self.assertIn("HarmonyOS release artifact signature verification", release_artifact_verifier)
            self.assertIn("verify-app", release_artifact_verifier)
            self.assertIn("verify-profile", release_artifact_verifier)
            self.assertIn("com.example.demoharmony", release_artifact_verifier)
            self.assertIn("biucing.harmony.signing.certpath", signing_example)
            self.assertIn("change-me-32-characters-minimum", signing_example)
            self.assertIn("biucing.harmony.signing.signAlg=SHA256withECDSA", signing_example)
            self.assertTrue(os.access(project_dir / "scripts" / "bootstrap", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "doctor", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "lint", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "test", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "artifact-info", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "release-preflight", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "release-build", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "verify-supply-chain", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "verify-release-artifact", os.X_OK))

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
            gitignore = (project_dir / ".gitignore").read_text(encoding="utf-8")
            appfile = (project_dir / "fastlane" / "Appfile").read_text(encoding="utf-8")
            fastfile = (project_dir / "fastlane" / "Fastfile").read_text(encoding="utf-8")
            matchfile = (project_dir / "fastlane" / "Matchfile").read_text(encoding="utf-8")
            fastlane_env_example = (
                project_dir / "fastlane" / ".env.example"
            ).read_text(encoding="utf-8")
            release_delivery = (
                project_dir / "docs" / "release-delivery.md"
            ).read_text(encoding="utf-8")
            app_tests = (
                project_dir / "App" / "Targets" / "AppTests" / "Sources" / "AppTests.swift"
            ).read_text(encoding="utf-8")
            test_destination = (
                project_dir / "scripts" / "test-destination"
            ).read_text(encoding="utf-8")
            release_identity_script = (
                project_dir / "scripts" / "verify-release-identity"
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
            self.assertIn("APP_STORE_CONNECT_API_KEY_PATH", readme)
            self.assertIn("MATCH_GIT_URL", readme)
            self.assertIn("make release-doctor", readme)
            self.assertIn("signed App Store archive", readme)
            self.assertIn("uploads the signed ipa/pkg to TestFlight", readme)
            self.assertIn("uploads the signed ipa/pkg to App Store Connect", readme)
            self.assertIn("APP_STORE_SUBMIT_FOR_REVIEW=true", readme)
            self.assertIn("generate:", makefile)
            self.assertIn("tuist generate --no-open", makefile)
            self.assertIn("platform=macOS", makefile)
            self.assertIn("release-doctor:", makefile)
            self.assertIn("release-generate:", makefile)
            self.assertIn("release-identity-check:", makefile)
            self.assertIn(
                "$(MAKE) --no-print-directory DEBUG_BUNDLE_SUFFIX= generate", makefile
            )
            self.assertIn("archive:", makefile)
            self.assertIn("DEBUG_BUNDLE_SUFFIX= fastlane archive", makefile)
            self.assertIn("DEBUG_BUNDLE_SUFFIX= fastlane beta", makefile)
            self.assertIn("DEBUG_BUNDLE_SUFFIX= fastlane release", makefile)
            self.assertIn("WORKTREE_ROOT ?= $(shell git rev-parse --show-toplevel", makefile)
            self.assertIn("WORKTREE_LABEL ?= $(shell basename", makefile)
            self.assertIn("WORKTREE_ID ?= $(shell printf '%s' \"$(WORKTREE_ROOT)\" | shasum | cut -c1-8)", makefile)
            self.assertIn("WORKTREE_ID", makefile)
            self.assertIn("DERIVED_DATA_PATH", makefile)
            self.assertIn("TEST_DESTINATION ?= $(shell ./scripts/test-destination macos", makefile)
            self.assertIn("-destination '$(TEST_DESTINATION)'", makefile)
            self.assertIn("TUIST_HOME", makefile)
            self.assertIn("XDG_CACHE_HOME=$(TUIST_XDG_CACHE_HOME)", makefile)
            self.assertIn("DEBUG_BUNDLE_SUFFIX", makefile)
            self.assertIn(
                "Release bundle identifier: $(RELEASE_BUNDLE_IDENTIFIER)", makefile
            )
            self.assertIn("worktree-info:", makefile)
            self.assertIn("worktree-doctor:", makefile)
            self.assertIn("clean-worktree:", makefile)
            self.assertIn("swiftlint lint --cache-path $(SWIFTLINT_CACHE)", makefile)
            self.assertIn("swiftformat . --cache $(SWIFTFORMAT_CACHE)", makefile)
            self.assertIn("-derivedDataPath $(DERIVED_DATA_PATH)", makefile)
            self.assertIn("Worktree Workflow", readme)
            self.assertIn("debug bundle identifier", readme)
            self.assertIn("included:", swiftlint_config)
            self.assertIn("modifier_order", swiftlint_config)
            self.assertIn("--swiftversion 6", swiftformat_config)
            self.assertIn("--disable trailingCommas", swiftformat_config)
            self.assertIn("--maxwidth 120", swiftformat_config)
            self.assertIn("let config = Config(", tuist_config)
            self.assertNotIn("fullHandle:", tuist_config)
            self.assertIn(
                'let debugBundleSuffix = Environment.debugBundleSuffix.getString(default: "")',
                project_swift,
            )
            self.assertIn('bundleId: "com.example.pulsemac\\(debugBundleSuffix)"', project_swift)
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
            self.assertIn('tuist_home="${TUIST_HOME:-${repo_root}/.cache/tuist/${worktree_id}/home}"', doctor)
            self.assertIn("xcode-select points to", doctor)
            self.assertIn("xcodebuild is available", doctor)
            self.assertIn("tuist is available", doctor)
            self.assertIn("swiftlint is available", doctor)
            self.assertIn("swiftformat is available", doctor)
            self.assertIn("fastlane is not available", doctor)
            self.assertIn("simulator services are not ready", doctor)
            self.assertIn("Doctor completed with", doctor)
            self.assertIn('printf \'%s\\n\' "platform=macOS"', test_destination)
            self.assertIn("No available", test_destination)
            self.assertTrue(os.access(project_dir / "scripts" / "test-destination", os.X_OK))
            self.assertIn('.macOS("26.0")', design_system)
            self.assertIn('name: "AppServices"', app_services_package)
            self.assertIn("public struct StarterFact: Equatable", app_services_source)
            self.assertIn("public protocol ReleaseChecklistProviding", app_services_source)
            self.assertIn("public enum StarterFactBuilder", app_services_source)
            self.assertIn("enum BiucingTheme", design_system_theme)
            self.assertIn("sectionTitleFont", design_system_theme)
            self.assertIn("import AppServices", app_tests)
            self.assertIn("!.env.example", gitignore)
            self.assertIn("/credentials/", gitignore)
            self.assertIn("/signing/", gitignore)
            self.assertIn("*.mobileprovision", gitignore)
            self.assertIn("/fastlane/*.json", gitignore)
            self.assertIn('app_identifier("com.example.pulsemac")', appfile)
            self.assertIn('apple_id(ENV.fetch("FASTLANE_USER", "developer@example.com"))', appfile)
            self.assertIn('team_id(ENV.fetch("DEVELOPMENT_TEAM_ID", "ABCDE12345"))', appfile)
            self.assertIn("default_platform(:mac)", fastfile)
            self.assertIn('APP_STORE_PLATFORM = "osx"', fastfile)
            self.assertIn("lane :release_doctor", fastfile)
            self.assertIn("lane :archive", fastfile)
            self.assertIn("sync_app_store_signing", fastfile)
            self.assertIn("build_signed_app", fastfile)
            self.assertIn('sh("make release-generate")', fastfile)
            self.assertIn('sh("make release-identity-check")', fastfile)
            self.assertIn(
                'sh("./scripts/verify-release-identity", "archive", ARCHIVE_PATH)',
                fastfile,
            )
            self.assertIn("upload_to_testflight", fastfile)
            self.assertIn("upload_to_app_store", fastfile)
            self.assertIn("api_key_path: app_store_api_key_path", fastfile)
            self.assertIn("submit_for_review: env_true?", fastfile)
            self.assertIn('sh("make lint")', fastfile)
            self.assertIn('sh("make test")', fastfile)
            self.assertIn('git_url(ENV.fetch("MATCH_GIT_URL"', matchfile)
            self.assertIn('app_identifier(["com.example.pulsemac"])', matchfile)
            self.assertIn('team_id(ENV.fetch("DEVELOPMENT_TEAM_ID", "ABCDE12345"))', matchfile)
            self.assertIn(
                "APP_STORE_CONNECT_API_KEY_PATH=credentials/app-store-connect-api-key.json",
                fastlane_env_example,
            )
            self.assertIn("MATCH_ALLOW_WRITE=false", fastlane_env_example)
            self.assertIn("make release-doctor", release_delivery)
            self.assertIn("MATCH_ALLOW_WRITE=true fastlane match appstore", release_delivery)
            self.assertIn("uploads the signed ipa/pkg to TestFlight", release_delivery)
            self.assertIn("does not submit it for review", release_delivery)
            self.assertIn("@testable import PulseMac", app_tests)
            self.assertIn("func testHomeViewModelBuildsOverviewFacts()", app_tests)
            self.assertIn("func testHomeViewModelUsesMockChecklistProvider()", app_tests)
            self.assertIn("StarterFact(label: \"Bundle ID\"", app_tests)
            self.assertIn("private struct MockReleaseChecklistProvider", app_tests)
            self.assertIn(
                'EXPECTED_BUNDLE_IDENTIFIER = "com.example.pulsemac"',
                release_identity_script,
            )
            self.assertIn('when "workspace"', release_identity_script)
            self.assertIn('when "archive"', release_identity_script)
            self.assertTrue(
                os.access(project_dir / "scripts" / "verify-release-identity", os.X_OK)
            )

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
