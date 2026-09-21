"""Artifact and acceptance-runner contracts; no Node/browser/Docker in core tests."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

import yaml

from scripts.distribution_resources import (
    RESOURCE_PREFIX, assert_resources_equal, extract_sdist, fingerprint,
    sdist_resources, source_resources, wheel_resources,
)
from scripts.frontend_verification import Audit, clean_environment, fresh_workspace, runtime_acceptance


class DistributionAcceptanceTests(unittest.TestCase):
    def test_all_layers_hidden_binary_and_executable_resources_match(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            files = {"frontend/template/.gitignore": (b"node_modules/\n", 0o644),
                     "frontend/variants/csr/template/scripts/doctor": (b"#!/bin/sh\n", 0o755),
                     "frontend/variants/ssg/template/.env.example": (b"SITE_URL=\n", 0o644),
                     "frontend/variants/ssr/template/server/index.ts": (b"export {};\n", 0o644),
                     "android/template/wrapper.jar": (b"\x00\xff\x01", 0o644)}
            wheel, sdist = root / "test.whl", root / "test.tar.gz"
            with zipfile.ZipFile(wheel, "w") as output, tarfile.open(sdist, "w:gz") as source:
                for name, (body, mode) in files.items():
                    path = root / "resources" / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(body)
                    path.chmod(mode)
                    entry = zipfile.ZipInfo(RESOURCE_PREFIX + name)
                    entry.external_attr = (0o100000 | mode) << 16
                    output.writestr(entry, body)
                    member = tarfile.TarInfo("pkg/src/" + RESOURCE_PREFIX + name)
                    member.size, member.mode = len(body), mode
                    source.addfile(member, io.BytesIO(body))
            expected = source_resources(root / "resources")
            assert_resources_equal(expected, wheel_resources(wheel), "wheel")
            assert_resources_equal(expected, sdist_resources(sdist), "sdist")

    def test_missing_extra_changed_and_permission_drift_fail(self):
        expected = {"ssr/.env.example": fingerprint(b"private example", 0o644)}
        for actual in ({}, {**expected, "unexpected": fingerprint(b"", 0o644)},
                       {"ssr/.env.example": fingerprint(b"changed", 0o644)},
                       {"ssr/.env.example": fingerprint(b"private example", 0o755)}):
            with self.subTest(actual=actual), self.assertRaises(AssertionError):
                assert_resources_equal(expected, actual, "fixture")
        with self.assertRaises(AssertionError):
            assert_resources_equal({}, {}, "empty")
        with self.assertRaises(AssertionError):
            assert_resources_equal({"script": fingerprint(b"", 0o755)},
                                   {"script": fingerprint(b"", 0o744)}, "execute bits")

    def test_duplicate_wheel_resources_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            wheel = Path(temporary) / "duplicate.whl"
            with warnings.catch_warnings(), zipfile.ZipFile(wheel, "w") as archive:
                warnings.simplefilter("ignore", UserWarning)
                archive.writestr(RESOURCE_PREFIX + "frontend/.env.example", b"first")
                archive.writestr(RESOURCE_PREFIX + "frontend/.env.example", b"second")
            with self.assertRaisesRegex(AssertionError, "duplicate wheel resource"):
                wheel_resources(wheel)

    def test_sdist_rejects_traversal_and_links_before_writes(self):
        for name, kind in (("../escape", tarfile.REGTYPE), ("/absolute", tarfile.REGTYPE),
                           ("pkg/link", tarfile.SYMTYPE), ("pkg/hardlink", tarfile.LNKTYPE),
                           ("pkg/pipe", tarfile.FIFOTYPE)):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                archive = root / "unsafe.tar.gz"
                with tarfile.open(archive, "w:gz") as output:
                    entry = tarfile.TarInfo(name)
                    entry.type = kind
                    output.addfile(entry)
                with self.assertRaises(AssertionError):
                    extract_sdist(archive, root / "output")
                self.assertFalse((root / "output").exists())

    def test_sdist_extraction_requires_project_and_single_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "safe.tar.gz"
            with tarfile.open(archive, "w:gz") as output:
                entry = tarfile.TarInfo("pkg/pyproject.toml")
                body = b"[project]\n"
                entry.size = len(body)
                output.addfile(entry, io.BytesIO(body))
            self.assertEqual(extract_sdist(archive, root / "out"), root / "out/pkg")

    def test_workspace_is_new_and_outside_checkout(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(fresh_workspace(root / "fresh"), (root / "fresh").resolve())
            with self.assertRaises(FileExistsError):
                fresh_workspace(root / "fresh")
        with self.assertRaises(ValueError):
            fresh_workspace(Path(__file__).resolve().parents[1] / "invalid-audit")

    def test_environment_cannot_import_checkout_or_reuse_external_server(self):
        with patch.dict("os.environ", {"PYTHONPATH": "/checkout/src", "PYTHONHOME": "/checkout",
                                       "PLAYWRIGHT_BASE_URL": "https://external.invalid",
                                       "PLAYWRIGHT_CHANNEL": "chrome", "SSR_PRIVATE_TOKEN": "real-private"}):
            environment = clean_environment()
        for key in ("PYTHONPATH", "PYTHONHOME", "PLAYWRIGHT_BASE_URL", "PLAYWRIGHT_CHANNEL"):
            self.assertNotIn(key, environment)
        self.assertEqual(environment["SSR_PRIVATE_TOKEN"], "private-smoke-sentinel")

    def test_command_failure_keeps_logs_and_failed_summary(self):
        with tempfile.TemporaryDirectory() as temporary:
            audit = Audit(Path(temporary), clean_environment())
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(subprocess.CalledProcessError):
                    audit.run("failure", [sys.executable, "-c", "print('diagnostic'); raise SystemExit(7)"])
            summary = json.loads((audit.reports / "summary.json").read_text())
            self.assertFalse(summary["ok"])
            self.assertFalse(summary["stages"][0]["ok"])
            self.assertIn("diagnostic", (audit.reports / "failure.log").read_text())

    def test_command_timeout_is_not_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            audit = Audit(Path(temporary), clean_environment())
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(subprocess.TimeoutExpired):
                    audit.run("timeout", [sys.executable, "-c", "import time; time.sleep(30)"], timeout=0.1)
            self.assertFalse(audit.summary["stages"][0]["ok"])

    def test_ci_and_release_share_artifact_matrix_without_python_cross_product(self):
        root = Path(__file__).resolve().parents[1]
        def workflow(name):
            return yaml.load((root / ".github/workflows" / name).read_text(), Loader=yaml.BaseLoader)
        frontend = workflow("frontend.yml")["jobs"]["frontend"]
        self.assertEqual(frontend["strategy"]["matrix"], {
            "os": ["ubuntu-latest", "macos-latest"], "mode": ["csr", "ssg", "ssr"],
        })
        self.assertEqual(workflow("ci.yml")["jobs"]["frontend"]["needs"], "frontend-artifact")
        publishing = workflow("publish.yml")["jobs"]
        self.assertIn("frontend", publishing["publish"]["needs"])
        self.assertEqual(publishing["frontend"]["with"]["artifact-name"], "python-distributions")
        self.assertIn("ref", publishing["frontend"]["with"])

    def test_runtime_failure_still_removes_only_owned_container_and_image(self):
        class FakeAudit:
            def __init__(self):
                self.commands = []

            def run(self, label, command, **kwargs):
                self.commands.append(command)
                if label.endswith("-docker-start"):
                    return "Docker warning\n" + "a" * 64 + "\n"
                if label.endswith("-docker-port"):
                    return '[{"HostPort":"18091"}]'
                return ""

            def browser(self, label, project, script, environment):
                if environment["PLAYWRIGHT_BASE_URL"] != "http://127.0.0.1:18091":
                    raise AssertionError("wrong runtime target")
                raise RuntimeError("browser failure")

        audit = FakeAudit()
        state = json.dumps({"Running": True, "Health": {"Status": "healthy"}})
        with patch("scripts.frontend_verification.subprocess.check_output", return_value=state):
            with self.assertRaisesRegex(RuntimeError, "browser failure"):
                runtime_acceptance(audit, "csr", Path("/unused"), {})
        self.assertEqual(audit.commands[-2], ["docker", "rm", "--force", "a" * 64])
        self.assertEqual(audit.commands[-1][:3], ["docker", "image", "rm"])
        self.assertTrue(audit.commands[-1][3].startswith("biucing-audit-csr-"))


if __name__ == "__main__":
    unittest.main()
