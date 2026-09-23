"""Focused platform regression coverage; extracted without changing assertions."""

import json
import os
import plistlib
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from suite_support import platform_test

from biucingcli.templates import REQUIRED_COMMAND_CONTRACT
from biucingcli.templates import load_templates
from biucingcli.resources import resolve_resources


from cli_support import CLIHelpers


class PlatformIntegrationTests(CLIHelpers, unittest.TestCase):
    @platform_test
    def test_all_templates_implement_the_common_make_command_contract(self):
        expected_commands = set(REQUIRED_COMMAND_CONTRACT)

        for definition in load_templates():
            with self.subTest(template=definition.name):
                self.assertEqual(set(definition.commands), expected_commands)
                makefiles = [definition.template_dir / "Makefile"]
                if definition.variants is not None:
                    makefiles = [
                        next(e.source for e in resolve_resources(
                            definition, {definition.variants.selector: mode}
                        ).entries if e.output_path == "Makefile")
                        for mode in definition.variants.options
                    ]
                for makefile in makefiles:
                    self.assert_make_help(makefile, definition.template_dir)

    def assert_make_help(self, makefile, directory):
        result = subprocess.run(
            ["make", "-s", "-f", str(makefile), "help"],
            cwd=directory,
            check=True,
            capture_output=True,
            text=True,
        )
        for command in REQUIRED_COMMAND_CONTRACT:
            self.assertIn(f"make {command}", result.stdout)

    @platform_test
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
            runner_test = (
                project_dir / "internal" / "runtime" / "runner_test.go"
            ).read_text(encoding="utf-8")
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
            self.assertIn("WORKER_RETRY_MAX_ATTEMPTS ?=3", makefile)
            self.assertIn("WORKER_RETRY_INITIAL_BACKOFF_SECONDS ?=1", makefile)
            self.assertIn("WORKER_RETRY_MAX_BACKOFF_SECONDS ?=30", makefile)
            self.assertIn("GOMODCACHE ?= $(CURDIR)/.cache/go-mod", makefile)
            self.assertIn("Go module cache: $(GOMODCACHE)", makefile)
            self.assertIn("GOMODCACHE should stay inside this worktree", makefile)
            self.assertIn("worktree-compose-config:", makefile)
            self.assertIn("Docker is not available; cannot render Compose config.", makefile)
            self.assertIn("$(COMPOSE) -f $(DEV_COMPOSE_FILE) config", makefile)
            self.assertIn("make worktree-compose-config", readme)
            self.assertIn("docker run --rm -e WORKER_RUN_MODE=$(WORKER_RUN_MODE)", makefile)
            self.assertIn("ARG BUILDER_IMAGE=golang:1.26-alpine", dockerfile)
            self.assertIn('CMD ["/usr/local/bin/worker"]', dockerfile)
            self.assertIn('CMD ["sh", "-lc", "go run ./cmd/worker"]', dockerfile_dev)
            self.assertIn('WORKER_RUN_MODE: ${WORKER_RUN_MODE:-oneshot}', compose_dev)
            self.assertIn("WORKER_RETRY_MAX_ATTEMPTS: ${WORKER_RETRY_MAX_ATTEMPTS:-3}", compose_dev)
            self.assertIn("GOMODCACHE: /cache/go-mod", compose_dev)
            self.assertIn("worker-go-mod-cache:/cache/go-mod", compose_dev)
            self.assertIn('"name": "mailer-worker"', config_json)
            self.assertIn('"run_mode": "oneshot"', config_json)
            self.assertIn('"tick_interval_seconds": 15', config_json)
            self.assertIn('"shutdown_timeout_seconds": 5', config_json)
            self.assertIn('"retry_max_attempts": 3', config_json)
            self.assertIn('"retry_initial_backoff_seconds": 1', config_json)
            self.assertIn('"retry_max_backoff_seconds": 30', config_json)
            self.assertIn("signal.NotifyContext", main_go)
            self.assertIn("task.NewHeartbeatTask", main_go)
            self.assertIn('cfg.Worker.RunMode != "scheduled" && cfg.Worker.RunMode != "oneshot"', config_go)
            self.assertIn("runScheduled", runner_go)
            self.assertIn("executeWithRetry", runner_go)
            self.assertIn("ErrShutdownTimeout", runner_go)
            self.assertIn("context.WithoutCancel", runner_go)
            self.assertIn("TestRunOneshotRetriesWithCappedExponentialBackoff", runner_test)
            self.assertIn("TestRunScheduledContinuesAfterRetryExhaustion", runner_test)
            self.assertIn("TestCancellationInterruptsRetryBackoff", runner_test)
            self.assertIn("TestShutdownTimeoutIsDeterministic", runner_test)
            self.assertNotIn("time.Sleep", runner_test)
            self.assertIn("oneshot` returns the final error", readme)
            self.assertIn("scheduled` logs an exhausted cycle", readme)
            self.assertIn("heartbeat completed", heartbeat_go)
            self.assertIn("Worker environment doctor", doctor)
            self.assertIn("go mod tidy", bootstrap)
            self.assertIn('cfg.Worker.Name != "mailer-worker"', worker_test)
            self.assertTrue(os.access(project_dir / "scripts" / "bootstrap", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "doctor", os.X_OK))

            env = os.environ.copy()
            env["GOCACHE"] = str(project_dir / ".cache" / "go-build")
            env["GOMODCACHE"] = str(project_dir / ".cache" / "go-mod")
            env["GOTMPDIR"] = str(project_dir / ".cache" / "go-tmp")
            os.makedirs(env["GOCACHE"], exist_ok=True)
            os.makedirs(env["GOMODCACHE"], exist_ok=True)
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

    @platform_test
    def test_apple_release_generation_discards_debug_bundle_suffix(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.run_cli(
                [
                    "create",
                    "apple",
                    "release-identity-app",
                    "--output-dir",
                    tmpdir,
                    "--platform",
                    "macos",
                    "--bundle-identifier",
                    "com.example.releaseidentity",
                    "--non-interactive",
                ]
            )
            project_dir = Path(tmpdir) / "release-identity-app"
            # This test isolates release identity from SDK publication (covered separately).
            (project_dir / "scripts/components").write_text("#!/bin/sh\nexit 0\n")
            fake_bin = Path(tmpdir) / "fake-bin"
            fake_bin.mkdir()
            tuist_log = Path(tmpdir) / "tuist.log"
            fake_tuist = fake_bin / "tuist"
            fake_tuist.write_text(
                "#!/bin/sh\n"
                "printf '%s|%s|%s\\n' \"$1\" \"${DEBUG_BUNDLE_SUFFIX-<unset>}\" "
                "\"${TUIST_DEBUG_BUNDLE_SUFFIX-<unset>}\" "
                ">> \"$TUIST_LOG\"\n",
                encoding="utf-8",
            )
            fake_tuist.chmod(0o755)

            environment = os.environ.copy()
            environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
            environment["TUIST_LOG"] = str(tuist_log)

            debug_result = subprocess.run(
                ["make", "generate", "WORKTREE_ID=alpha"],
                cwd=project_dir,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(debug_result.returncode, 0, msg=debug_result.stderr)
            self.assertEqual(
                tuist_log.read_text(encoding="utf-8").splitlines(),
                ["install|.alpha|.alpha", "generate|.alpha|.alpha"],
            )

            tuist_log.unlink()
            release_result = subprocess.run(
                [
                    "make",
                    "release-generate",
                    "WORKTREE_ID=alpha",
                    "DEBUG_BUNDLE_SUFFIX=.unexpected",
                ],
                cwd=project_dir,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(release_result.returncode, 0, msg=release_result.stderr)
            self.assertIn(
                "Release generation ignores DEBUG_BUNDLE_SUFFIX=.unexpected",
                release_result.stdout,
            )
            self.assertEqual(
                tuist_log.read_text(encoding="utf-8").splitlines(),
                ["install||", "generate||"],
            )

    @platform_test
    def test_apple_release_identity_script_checks_workspace_and_archive(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.run_cli(
                [
                    "create",
                    "apple",
                    "identity-check-app",
                    "--output-dir",
                    tmpdir,
                    "--platform",
                    "macos",
                    "--bundle-identifier",
                    "com.example.identitycheck",
                    "--non-interactive",
                ]
            )
            project_dir = Path(tmpdir) / "identity-check-app"
            script = project_dir / "scripts" / "verify-release-identity"
            fake_bin = Path(tmpdir) / "fake-bin"
            fake_bin.mkdir()
            fake_xcodebuild = fake_bin / "xcodebuild"
            xcodebuild_payload = Path(tmpdir) / "xcodebuild.json"
            fake_xcodebuild.write_text(
                "#!/bin/sh\ncat \"$XCODEBUILD_PAYLOAD\"\n",
                encoding="utf-8",
            )
            fake_xcodebuild.chmod(0o755)

            environment = os.environ.copy()
            environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
            environment["XCODEBUILD_PAYLOAD"] = str(xcodebuild_payload)

            def run_workspace(payload):
                xcodebuild_payload.write_text(json.dumps(payload), encoding="utf-8")
                return subprocess.run(
                    [str(script), "workspace"],
                    cwd=project_dir,
                    env=environment,
                    capture_output=True,
                    text=True,
                    check=False,
                )

            result = run_workspace(
                [
                    {
                        "target": "IdentityCheckApp_macos",
                        "buildSettings": {
                            "PRODUCT_BUNDLE_IDENTIFIER": "com.example.identitycheck.macos"
                        },
                    }
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("workspace identity verified", result.stdout)

            result = run_workspace(
                [
                    {
                        "target": "IdentityCheckApp_macos",
                        "buildSettings": {
                            "PRODUCT_BUNDLE_IDENTIFIER": (
                                "com.example.identitycheck.macos.alpha"
                            )
                        },
                    }
                ]
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Expected: com.example.identitycheck.macos", result.stderr)
            self.assertIn("Actual: com.example.identitycheck.macos.alpha", result.stderr)

            result = run_workspace(
                [{"target": "IdentityCheckApp_macos", "buildSettings": {}}]
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Actual: <missing>", result.stderr)

            result = run_workspace(
                [
                    {"target": "IdentityCheckApp_macos", "buildSettings": {}},
                    {"target": "IdentityCheckApp_macos", "buildSettings": {}},
                ]
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("expected exactly one", result.stderr)

            archive_dir = Path(tmpdir) / "IdentityCheckApp.xcarchive"
            archive_dir.mkdir()
            archive_plist = archive_dir / "Info.plist"

            def write_archive(bundle_identifier=None):
                properties = {}
                if bundle_identifier is not None:
                    properties["CFBundleIdentifier"] = bundle_identifier
                with archive_plist.open("wb") as handle:
                    plistlib.dump({"ApplicationProperties": properties}, handle)

            write_archive("com.example.identitycheck.macos")
            result = subprocess.run(
                [str(script), "archive", str(archive_dir)],
                cwd=project_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("archive identity verified", result.stdout)

            write_archive("com.example.identitycheck.macos.alpha")
            result = subprocess.run(
                [str(script), "archive", str(archive_dir)],
                cwd=project_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Actual: com.example.identitycheck.macos.alpha", result.stderr)

            write_archive()
            result = subprocess.run(
                [str(script), "archive", str(archive_dir)],
                cwd=project_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Actual: <missing>", result.stderr)

            archive_plist.unlink()
            result = subprocess.run(
                [str(script), "archive", str(archive_dir)],
                cwd=project_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("archive Info.plist is missing", result.stderr)

    @platform_test
    def test_native_templates_ignore_credentials_without_hiding_public_fixtures(self):
        cases = {
            "apple": {
                "args": [
                    "create",
                    "apple",
                    "ignore-apple",
                    "--bundle-identifier",
                    "com.example.ignoreapple",
                ],
                "project": "ignore-apple",
                "ignored": [
                    "credentials/api-key.json",
                    "signing/distribution.cer",
                    "private-key.p8",
                    "distribution.p12",
                    "distribution.pfx",
                    "profile.mobileprovision",
                    "profile.provisionprofile",
                    "fastlane/private.json",
                    "fastlane/.env.production",
                    "app-store-connect-api-key.json",
                ],
                "trackable": [
                    "fastlane/.env.example",
                    "fixtures/public.cer",
                    "fixtures/public.pem",
                    "fixtures/config.json",
                    "fixtures/profile.p7b",
                ],
            },
            "android": {
                "args": [
                    "create",
                    "android",
                    "ignore-android",
                    "--package-name",
                    "com.example.ignoreandroid",
                ],
                "project": "ignore-android",
                "ignored": [
                    "credentials/play.json",
                    "signing/release.keystore",
                    "release.jks",
                    "release.keystore",
                    "release.p12",
                    "release.pfx",
                    "key.properties",
                    "keystore.properties",
                    "signing.properties",
                    "fastlane/private.json",
                    "fastlane/.env.local",
                    "play-store-service-account.json",
                    "local.properties",
                ],
                "trackable": [
                    "fastlane/.env.example",
                    "docs/release-signing.properties.example",
                    "gradle.properties",
                    "fixtures/public.cer",
                    "fixtures/public.pem",
                    "fixtures/config.json",
                    "fixtures/profile.p7b",
                ],
            },
            "harmonyos": {
                "args": [
                    "create",
                    "harmonyos",
                    "ignore-harmony",
                    "--bundle-name",
                    "com.example.ignoreharmony",
                ],
                "project": "ignore-harmony",
                "ignored": [
                    "credentials/account.json",
                    "signing/release.cer",
                    "signing/release.p7b",
                    "signing/release.p12",
                    "release.p8",
                    "release.pfx",
                    ".biucing/release/build-profile.json5.backup",
                    ".env.release",
                    "local.properties",
                ],
                "trackable": [
                    "docs/release-signing.local.properties.example",
                    "build-profile.json5",
                    "fixtures/public.cer",
                    "fixtures/public.pem",
                    "fixtures/config.json",
                    "fixtures/profile.p7b",
                ],
            },
        }

        for platform, case in cases.items():
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as tmpdir:
                self.run_cli([*case["args"], "--output-dir", tmpdir])
                project_dir = Path(tmpdir) / case["project"]
                self.init_git_repository(project_dir)

                for relative_path in [*case["ignored"], *case["trackable"]]:
                    path = project_dir / relative_path
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if not path.exists():
                        path.write_text("fixture", encoding="utf-8")

                for relative_path in case["ignored"]:
                    result = subprocess.run(
                        ["git", "check-ignore", "-q", "--", relative_path],
                        cwd=project_dir,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, relative_path)

                for relative_path in case["trackable"]:
                    result = subprocess.run(
                        ["git", "check-ignore", "-q", "--", relative_path],
                        cwd=project_dir,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 1, relative_path)

    @platform_test
    def test_android_supply_chain_and_signed_aab_verification(self):
        if not all(shutil.which(tool) for tool in ("keytool", "jarsigner")):
            self.skipTest("JDK signing tools are unavailable")

        with tempfile.TemporaryDirectory() as tmpdir:
            self.run_cli(
                [
                    "create", "android", "verified-android", "--output-dir", tmpdir,
                    "--package-name", "com.example.verifiedandroid",
                    "--application-id", "com.example.verifiedandroid.app",
                ]
            )
            project_dir = Path(tmpdir) / "verified-android"
            supply_script = project_dir / "scripts" / "verify-gradle-supply-chain"
            result = subprocess.run(
                [str(supply_script)], cwd=project_dir, capture_output=True, text=True, check=False
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            wrapper_properties = project_dir / "gradle" / "wrapper" / "gradle-wrapper.properties"
            original_properties = wrapper_properties.read_text(encoding="utf-8")
            wrapper_properties.write_text(
                original_properties.replace("distributionSha256Sum=31c557", "distributionSha256Sum=deadbe"),
                encoding="utf-8",
            )
            result = subprocess.run(
                [str(supply_script)], cwd=project_dir, capture_output=True, text=True, check=False
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Unexpected Gradle distribution SHA-256", result.stderr)
            wrapper_properties.write_text(original_properties, encoding="utf-8")

            artifact_path = project_dir / "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab"
            artifact_path.parent.mkdir(parents=True)
            with zipfile.ZipFile(artifact_path, "w") as archive:
                archive.writestr("BundleConfig.pb", b"bundle")
                archive.writestr("base/manifest/AndroidManifest.xml", b"manifest")

            stores = []
            for index in (1, 2):
                store_path = Path(tmpdir) / f"release-{index}.jks"
                subprocess.run(
                    [
                        "keytool", "-genkeypair", "-alias", "release", "-keyalg", "RSA",
                        "-keystore", str(store_path), "-storepass", "test-password",
                        "-keypass", "test-password", "-dname", f"CN=Release {index}",
                        "-validity", "1",
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                stores.append(store_path)
            subprocess.run(
                [
                    "jarsigner", "-keystore", str(stores[0]), "-storepass", "test-password",
                    "-keypass", "test-password", str(artifact_path), "release",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            verifier = project_dir / "scripts" / "verify-release-artifact"
            env = os.environ.copy()
            env.update(
                {
                    "BIUCING_RELEASE_STORE_FILE": str(stores[0]),
                    "BIUCING_RELEASE_STORE_PASSWORD": "test-password",
                    "BIUCING_RELEASE_KEY_ALIAS": "release",
                }
            )
            result = subprocess.run(
                [str(verifier), str(artifact_path)], cwd=project_dir, env=env,
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("matches the configured release certificate", result.stdout)

            env["BIUCING_RELEASE_STORE_FILE"] = str(stores[1])
            result = subprocess.run(
                [str(verifier), str(artifact_path)], cwd=project_dir, env=env,
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("does not match the configured release key", result.stderr)

    @platform_test
    def test_harmonyos_supply_chain_and_hap_identity_verification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = self.create_harmony_release_fixture(tmpdir, "verified-harmony")
            supply_script = project_dir / "scripts" / "verify-supply-chain"
            result = subprocess.run(
                [str(supply_script)], cwd=project_dir, capture_output=True, text=True, check=False
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            lock_path = project_dir / "oh-package-lock.json5"
            original_lock = lock_path.read_text(encoding="utf-8")
            lock_path.write_text(
                original_lock.replace("https://ohpm.openharmony.cn/ohpm/", "https://example.invalid/"),
                encoding="utf-8",
            )
            result = subprocess.run(
                [str(supply_script)], cwd=project_dir, capture_output=True, text=True, check=False
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("outside the approved ohpm registry", result.stderr)
            lock_path.write_text(original_lock, encoding="utf-8")

            fake_bin = Path(tmpdir) / "fake-bin"
            fake_bin.mkdir()
            fake_ohpm = fake_bin / "ohpm"
            fake_ohpm.write_text(
                "#!/usr/bin/env bash\nprintf '\\n' >> oh-package-lock.json5\n",
                encoding="utf-8",
            )
            fake_ohpm.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
            result = subprocess.run(
                [str(project_dir / "scripts" / "bootstrap")], cwd=project_dir, env=env,
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("changed oh-package-lock.json5", result.stderr)
            self.assertEqual(lock_path.read_text(encoding="utf-8"), original_lock)

            artifact_path = project_dir / "entry" / "build" / "release" / "verified.hap"
            artifact_path.parent.mkdir(parents=True)
            with zipfile.ZipFile(artifact_path, "w") as archive:
                archive.writestr("module.json", '{"module":{"name":"entry"}}')

            fake_sign_tool = Path(tmpdir) / "fake-hap-sign-tool"
            fake_sign_tool.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
command="$1"; shift
value_for() { local expected="$1"; shift; while [[ "$#" -gt 1 ]]; do if [[ "$1" == "$expected" ]]; then printf '%s' "$2"; return; fi; shift; done; }
if [[ "$command" == "verify-app" ]]; then
  if [[ "${FAKE_SIGNER_MISMATCH:-0}" == "1" ]]; then printf '%s' bad-signer > "$(value_for -outCertChain "$@")"; else cp signing/release.cer "$(value_for -outCertChain "$@")"; fi
  cp signing/release.p7b "$(value_for -outProfile "$@")"
elif [[ "$command" == "verify-profile" ]]; then
  printf '{"profile":{"bundle-name":"%s"}}\n' "${FAKE_BUNDLE_NAME:-com.example.verifiedharmony}" > "$(value_for -outFile "$@")"
fi
""",
                encoding="utf-8",
            )
            fake_sign_tool.chmod(0o755)
            fake_keytool = Path(tmpdir) / "fake-keytool"
            fake_keytool.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
path="${@: -1}"
if [[ -f "$path" ]] && grep -q bad-signer "$path"; then printf '%s\n' 'SHA256: DD:EE:FF'; else printf '%s\n' 'SHA256: AA:BB:CC'; fi
""",
                encoding="utf-8",
            )
            fake_keytool.chmod(0o755)

            verifier = project_dir / "scripts" / "verify-release-artifact"
            env = os.environ.copy()
            env["HAP_SIGN_TOOL"] = str(fake_sign_tool)
            env["KEYTOOL"] = str(fake_keytool)
            result = subprocess.run(
                [str(verifier), str(artifact_path)], cwd=project_dir, env=env,
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            env["FAKE_SIGNER_MISMATCH"] = "1"
            result = subprocess.run(
                [str(verifier), str(artifact_path)], cwd=project_dir, env=env,
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("does not match the configured release certificate", result.stderr)

            env.pop("FAKE_SIGNER_MISMATCH")
            env["FAKE_BUNDLE_NAME"] = "com.example.wrong"
            result = subprocess.run(
                [str(verifier), str(artifact_path)], cwd=project_dir, env=env,
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("bundle identity does not match", result.stderr)

    @platform_test
    def test_harmonyos_release_restores_profile_after_success_and_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = self.create_harmony_release_fixture(
                tmpdir, "release-restore-harmony"
            )
            build_profile_path = project_dir / "build-profile.json5"
            original_profile = build_profile_path.read_bytes()
            fake_hvigor = Path(tmpdir) / "fake-hvigor"
            fake_hvigor.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
node - <<'NODE'
const fs = require('fs');
const profile = JSON.parse(fs.readFileSync('build-profile.json5', 'utf8'));
const configs = profile.app.signingConfigs || [];
if (configs.length !== 1 || configs[0].name !== 'release') {
  console.error('release signing config was not injected');
  process.exit(20);
}
NODE
if [[ "${FAKE_HVIGOR_FAIL:-0}" == "1" ]]; then
  exit 42
fi
if [[ -n "${FAKE_HVIGOR_SIGNAL:-}" ]]; then
  kill -s "$FAKE_HVIGOR_SIGNAL" "$PPID"
  sleep 0.2
fi
mkdir -p entry/build/default/outputs/default /tmp/biucing-empty-hap
printf '%s' 'fixture' > /tmp/biucing-empty-hap/module.json
(cd /tmp/biucing-empty-hap && zip -q "${OLDPWD}/entry/build/default/outputs/default/entry-default-signed.hap" -r .)
""",
                encoding="utf-8",
            )
            fake_hvigor.chmod(0o755)
            fake_sign_tool = Path(tmpdir) / "fake-hap-sign-tool"
            fake_sign_tool.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
command="$1"
shift
value_for() {
  local expected="$1"
  shift
  while [[ "$#" -gt 1 ]]; do
    if [[ "$1" == "$expected" ]]; then printf '%s' "$2"; return; fi
    shift
  done
}
if [[ "$command" == "verify-app" ]]; then
  cp signing/release.cer "$(value_for -outCertChain "$@")"
  cp signing/release.p7b "$(value_for -outProfile "$@")"
elif [[ "$command" == "verify-profile" ]]; then
  printf '%s\n' '{"profile":{"bundle-name":"com.example.releaserestoreharmony"}}' > "$(value_for -outFile "$@")"
fi
""",
                encoding="utf-8",
            )
            fake_sign_tool.chmod(0o755)
            fake_keytool = Path(tmpdir) / "fake-keytool"
            fake_keytool.write_text(
                "#!/usr/bin/env bash\nprintf '%s\\n' 'SHA256: AA:BB:CC'\n",
                encoding="utf-8",
            )
            fake_keytool.chmod(0o755)
            release_script = project_dir / "scripts" / "release-build"

            for should_fail in (False, True):
                with self.subTest(should_fail=should_fail):
                    env = os.environ.copy()
                    env["HVIGOR"] = str(fake_hvigor)
                    env["HAP_SIGN_TOOL"] = str(fake_sign_tool)
                    env["KEYTOOL"] = str(fake_keytool)
                    if should_fail:
                        env["FAKE_HVIGOR_FAIL"] = "1"
                    result = subprocess.run(
                        [str(release_script)],
                        cwd=project_dir,
                        env=env,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 42 if should_fail else 0)
                    self.assertEqual(build_profile_path.read_bytes(), original_profile)
                    self.assertFalse((project_dir / ".biucing" / "release").exists())
                    self.assertNotIn("store-secret-value", result.stdout + result.stderr)
                    self.assertNotIn("key-secret-value", result.stdout + result.stderr)

            for signal_name, expected_status in (("HUP", 129), ("INT", 130), ("TERM", 143)):
                with self.subTest(signal=signal_name):
                    env = os.environ.copy()
                    env["HVIGOR"] = str(fake_hvigor)
                    env["FAKE_HVIGOR_SIGNAL"] = signal_name
                    result = subprocess.run(
                        [str(release_script)],
                        cwd=project_dir,
                        env=env,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, expected_status)
                    self.assertEqual(build_profile_path.read_bytes(), original_profile)
                    self.assertFalse((project_dir / ".biucing" / "release").exists())

    @platform_test
    def test_harmonyos_release_rejects_residue_and_dirty_build_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = self.create_harmony_release_fixture(
                tmpdir, "release-guard-harmony"
            )
            build_profile_path = project_dir / "build-profile.json5"
            original_profile = build_profile_path.read_text(encoding="utf-8")
            release_script = project_dir / "scripts" / "release-build"
            preflight_script = project_dir / "scripts" / "release-preflight"

            dirty_profile = f"{original_profile}\n"
            build_profile_path.write_text(dirty_profile, encoding="utf-8")
            result = subprocess.run(
                [str(release_script)],
                cwd=project_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("has staged or unstaged changes", result.stderr)

            build_profile_path.write_text(original_profile, encoding="utf-8")
            build_profile_path.write_text(dirty_profile, encoding="utf-8")
            subprocess.run(
                ["git", "add", "build-profile.json5"], cwd=project_dir, check=True
            )
            result = subprocess.run(
                [str(release_script)],
                cwd=project_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("has staged or unstaged changes", result.stderr)

            residue = json.loads(original_profile)
            residue["app"]["signingConfigs"] = [
                {
                    "name": "release",
                    "material": {
                        "storePassword": "residual-store-secret",
                        "keyPassword": "residual-key-secret",
                    },
                }
            ]
            build_profile_path.write_text(json.dumps(residue), encoding="utf-8")
            result = subprocess.run(
                [str(preflight_script)],
                cwd=project_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("contains signing material", result.stderr)
            self.assertNotIn("residual-store-secret", result.stdout + result.stderr)
            self.assertNotIn("residual-key-secret", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
