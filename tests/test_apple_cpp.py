"""Portable core source and native integration contracts in generated starters."""

import tempfile
import unittest
from pathlib import Path

from cli_support import CLIHelpers


class AppleCppTests(CLIHelpers, unittest.TestCase):
    def test_all_platforms_share_identical_portable_module(self):
        reference = None
        with tempfile.TemporaryDirectory() as tmp:
            for platform in ("ios", "macos", "watchos", "tvos"):
                self.run_cli([
                    "create", "apple", platform, "--platform", platform,
                    "--bundle-identifier", f"com.example.{platform}",
                    "--output-dir", tmp, "--non-interactive",
                ])
                root = Path(tmp) / platform
                core = root / "Shared/Core"
                files = {p.relative_to(core).as_posix(): p.read_bytes()
                         for p in core.rglob("*") if p.is_file()}
                self.assertIn("Sources/CoreNative/core.cpp", files)
                self.assertIn("Sources/CoreNative/include/CoreNative.h", files)
                self.assertIn("Sources/SharedCore/SharedCore.swift", files)
                self.assertIn("Tests/Native/core_test.c", files)
                self.assertIn(b"Tests/Native/core_test.c", files["CMakeLists.txt"])
                if reference is None:
                    reference = files
                else:
                    self.assertEqual(files, reference)
                package = (root / "Components/Package.swift").read_text()
                self.assertIn('name: "ProductContracts"', package)
                self.assertIn('name: "HomeFeature"', package)
                makefile = (root / "Makefile").read_text()
                self.assertIn("core-swift-test component-test di-test test-all build-all", makefile)
                self.assertIn('"$(CORE_BUILD_PATH)"', makefile)
                app_tests = (root / f"Apps/{platform}/Tests/AppTests.swift").read_text()
                self.assertIn("testBinaryCoreThroughInjectedService", app_tests)
