import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class SharedCoreSyncTests(unittest.TestCase):
    def test_rename_removes_stale_native_file_and_preserves_swift_wrapper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "scripts/sync-shared-core"
            script.parent.mkdir()
            shutil.copyfile(Path(__file__).resolve().parents[1] / "scripts" / script.name, script)
            command = [sys.executable, str(script)]
            source = root / "shared/core/Sources/CoreNative/old.cpp"
            source.parent.mkdir(parents=True)
            source.write_text("original")
            subprocess.run(command, check=True)
            apple = root / "src/biucingcli/template_data/apple/template/Shared/Core/Sources"
            wrapper = apple / "SharedCore/wrapper.swift"
            wrapper.parent.mkdir()
            wrapper.write_text("wrapper")
            source.rename(source.with_name("new.cpp"))
            check = subprocess.run([*command, "--check"], capture_output=True, text=True)
            self.assertNotEqual(check.returncode, 0)
            self.assertIn("old.cpp", check.stderr)
            subprocess.run(command, check=True)
            subprocess.run([*command, "--check"], check=True)
            self.assertFalse((apple / "CoreNative/old.cpp").exists())
            self.assertEqual(wrapper.read_text(), "wrapper")
