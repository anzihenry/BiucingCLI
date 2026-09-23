"""Artifact/lock policy tests run without Xcode; native consumer tests live in the starter."""
import os
import plistlib
import runpy
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cli_support import CLIHelpers


class AppleComponentTests(CLIHelpers, unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.run_cli([
            "create", "apple", "sdk-test", "--bundle-identifier", "com.example.sdktest",
            "--output-dir", self.temporary.name, "--non-interactive",
        ])
        self.root = Path(self.temporary.name) / "sdk-test"
        self.environment = patch.dict(os.environ, {"CI": "", "CONFIGURATION": "Debug"})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        with patch.dict(os.environ):
            os.environ.pop("COMPONENT_REGISTRY", None)
            self.api = runpy.run_path(str(self.root / "scripts/components"), run_name="component_test")
        self.registry = self.api["REGISTRY"]
        for name in self.api["MODULES"]:
            self.artifact(name)

    def artifact(self, name, version="0.1.0", dependency_version="0.1.0"):
        folder = self.registry / name / version
        folder.mkdir(parents=True)
        for module in self.api["MODULES"][name]:
            xc = folder / f"{module}.xcframework"
            xc.mkdir()
            libraries = []
            for sdk, (os_name, architectures, suffix) in self.api["SLICES"].items():
                framework = xc / sdk / f"{module}.framework"
                framework.mkdir(parents=True)
                # Minimal static archive fixture: production binaries are built with Xcode.
                (framework / module).write_bytes(b"!<arch>\n")
                library = {"LibraryIdentifier": sdk, "LibraryPath": f"{module}.framework",
                           "SupportedPlatform": os_name, "SupportedArchitectures": architectures}
                if suffix:
                    library["SupportedPlatformVariant"] = "simulator"
                libraries.append(library)
            (xc / "Info.plist").write_bytes(plistlib.dumps({"AvailableLibraries": libraries}))
        if name == "HomeFeature":
            resources = folder / "Resources/HomeFeature.bundle"
            resources.mkdir(parents=True)
            (resources / "Info.plist").write_bytes(plistlib.dumps({"CFBundlePackageType": "BNDL"}))
        manifest = {"schema": 1, "name": name, "version": version, "linkage": "static",
                    "modules": self.api["MODULES"][name], "abi": 1, "minimumOS": "26.0",
                    "slices": {key: value[1] for key, value in self.api["SLICES"].items()},
                    "dependencies": {dep: dependency_version for dep in self.api["DEPENDENCIES"][name]},
                    "files": self.api["inventory"](folder)}
        self.api["write"](folder / "manifest.json", manifest)
        return folder

    def test_lock_resolve_and_tamper_fail_closed(self):
        self.api["lock"]()
        self.api["resolve"]()
        self.api["verify_resolved"]()
        binary = next((self.api["RESOLVED"] / "SharedCore").rglob("CoreNative"))
        binary.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            self.api["verify_resolved"]()

    def test_locked_manifest_cannot_be_replaced_even_with_new_checksums(self):
        self.api["lock"]()
        folder = self.registry / "HomeFeature/0.1.0"
        manifest = self.api["read"](folder / "manifest.json")
        manifest["publisherNote"] = "changed"
        self.api["write"](folder / "manifest.json", manifest)
        with self.assertRaisesRegex(ValueError, "Locked manifest changed"):
            self.api["resolve"]()

    def test_overrides_require_consistent_dependencies_and_are_forbidden_in_release(self):
        self.api["lock"]()
        folder = self.artifact("HomeFeature", "0.1.1")
        self.api["write"](self.api["OVERRIDES"], {"HomeFeature": str(folder)})
        self.api["resolve"]()
        self.api["verify_resolved"]()
        with self.assertRaisesRegex(ValueError, "forbids local"):
            self.api["resolve"](release=True)
        with patch.dict(os.environ, {"CI": "true"}), self.assertRaisesRegex(ValueError, "forbids local"):
            self.api["resolve"]()
        with (patch.dict(os.environ, {"CONFIGURATION": "Release"}),
              self.assertRaisesRegex(ValueError, "refuses local")):
            self.api["verify_resolved"]()
        incompatible = self.artifact("HomeFeature", "0.2.0", dependency_version="0.2.0")
        self.api["write"](self.api["OVERRIDES"], {"HomeFeature": str(incompatible)})
        with self.assertRaisesRegex(ValueError, "requires FoundationKit@0.2.0"):
            self.api["resolve"]()

    def test_independent_upgrade_preserves_foundation_version(self):
        self.artifact("HomeFeature", "0.1.1")
        declaration = self.api["read"](self.api["DECLARATION"])
        declaration["components"]["HomeFeature"] = "0.1.1"
        self.api["write"](self.api["DECLARATION"], declaration)
        self.api["lock"]()
        self.api["resolve"]()
        entries = self.api["read"](self.api["LOCK"])["components"]
        self.assertEqual(entries["HomeFeature"]["version"], "0.1.1")
        self.assertEqual(entries["FoundationKit"]["version"], "0.1.0")

    def test_missing_slices_resources_and_duplicate_core_boundary_are_rejected(self):
        folder = self.registry / "HomeFeature/0.1.0"
        manifest_path = folder / "manifest.json"
        original = self.api["read"](manifest_path)
        invalid = dict(original, dependencies={"FoundationKit": "0.1.0", "SharedCore": "0.1.0"})
        self.api["write"](manifest_path, invalid)
        with self.assertRaisesRegex(ValueError, "dependency boundary"):
            self.api["validate"](folder, "HomeFeature")
        self.api["write"](manifest_path, original)
        (folder / "Resources/HomeFeature.bundle/Info.plist").unlink()
        original["files"] = self.api["inventory"](folder)
        self.api["write"](manifest_path, original)
        with self.assertRaisesRegex(ValueError, "resource bundle"):
            self.api["validate"](folder, "HomeFeature")
        foundation = self.registry / "FoundationKit/0.1.0"
        manifest = self.api["read"](foundation / "manifest.json")
        manifest["slices"].pop("watchos")
        self.api["write"](foundation / "manifest.json", manifest)
        with self.assertRaisesRegex(ValueError, "platform matrix"):
            self.api["validate"](foundation, "FoundationKit")

    def test_published_version_is_immutable_and_declaration_requires_explicit_lock(self):
        with self.assertRaisesRegex(ValueError, "Immutable version already exists"):
            self.api["build"]("0.1.0")
        self.api["lock"]()
        declaration = self.api["read"](self.api["DECLARATION"])
        declaration["components"]["HomeFeature"] = "0.1.1"
        self.api["write"](self.api["DECLARATION"], declaration)
        with self.assertRaisesRegex(ValueError, "Declaration/lock mismatch"):
            self.api["resolve"]()

    def test_universal_dynamic_binary_is_not_mistaken_for_a_static_archive(self):
        binary = self.root / "fat-binary"
        header = struct.pack(">IIIIIII", 0xCAFEBABE, 1, 0x0100000C, 0, 28, 8, 0)
        binary.write_bytes(header + b"!<arch>\n")
        self.assertTrue(self.api["is_static_archive"](binary))
        binary.write_bytes(header + b"\xcf\xfa\xed\xfeABCD")
        self.assertFalse(self.api["is_static_archive"](binary))
        binary.write_bytes(header)
        self.assertFalse(self.api["is_static_archive"](binary))

    def test_missing_lock_never_falls_back_to_sources(self):
        with self.assertRaises(FileNotFoundError):
            self.api["resolve"]()
        for platform in ("ios", "macos", "watchos", "tvos"):
            source = (self.root / f"Apps/{platform}/Project.swift").read_text()
            self.assertNotIn(".package(", source)
            self.assertNotIn("Components/Sources", source)
            self.assertIn("verify-resolved", source)


if __name__ == "__main__":
    unittest.main()
