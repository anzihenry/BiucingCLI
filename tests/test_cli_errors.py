"""Exercise CLI stream and exit-code contracts across process boundaries."""

import json
import os
import select
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


class CLIErrorTests(unittest.TestCase):
    def invoke(self, *args, code=None):
        command = [sys.executable, "-m", "biucingcli.cli"]
        if code is not None:
            command = [sys.executable, "-c", code]
        return subprocess.run(command + list(args), input="", text=True,
                              capture_output=True, timeout=30)

    def assert_json_error(self, result, code, status=2):
        self.assertEqual(result.returncode, status, result.stderr)
        self.assertEqual(result.stdout, "")
        payload = json.loads(result.stderr)
        self.assertEqual(payload["schema_version"], 1)
        self.assertIs(payload["ok"], False)
        self.assertEqual(payload["error"]["code"], code)
        self.assertTrue(payload["error"]["message"])
        self.assertNotIn("Traceback", result.stderr)
        return payload

    def test_argument_errors_are_json(self):
        cases = [
            ["info", "--json"],
            ["info", "frontend", "--bad-option", "--json"],
            ["create", "worker", "demo", "--run-mode", "invalid", "--json"],
            ["create", "frontend", "demo", "--output-dir", "--json"],
        ]
        for args in cases:
            with self.subTest(args=args):
                self.assert_json_error(self.invoke(*args), "usage_error")

    def test_domain_errors_are_json(self):
        self.assert_json_error(self.invoke("info", "missing", "--json"), "unknown_template")
        self.assert_json_error(self.invoke("create", "frontend", "demo", "--set", "bad",
                                           "--json"), "invalid_input")
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "demo").mkdir()
            self.assert_json_error(self.invoke("create", "frontend", "demo", "--output-dir",
                                               tmp, "--json"), "target_conflict")
            self.assert_json_error(self.invoke("create", "frontend", "demo", "--output-dir",
                                               str(Path(tmp) / "missing"), "--json"),
                                   "generation_failed")

    def test_non_terminal_missing_values_fail_without_prompt(self):
        result = self.invoke("create", "web-service", "demo")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("module_name", result.stderr)
        self.assertNotIn("Go module name:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assert_json_error(self.invoke("create", "web-service", "demo", "--json"),
                               "missing_input")

    def test_json_never_prompts_even_if_stdin_is_a_terminal(self):
        code = ('from unittest.mock import patch\nfrom biucingcli.cli import main\n'
                'with patch("sys.stdin.isatty", return_value=True), '
                'patch("builtins.input", side_effect=AssertionError("must not prompt")):\n'
                '    main()\n')
        self.assert_json_error(self.invoke("create", "web-service", "demo", "--json",
                                           code=code), "missing_input")

    def test_validation_failure_and_invalid_metadata(self):
        code = ('from unittest.mock import patch\nfrom biucingcli.cli import main\n'
                'with patch("biucingcli.cli.validate_templates", return_value=["broken resource"]):\n'
                '    main()\n')
        payload = self.assert_json_error(self.invoke("validate", "--json", code=code),
                                         "validation_failed", 1)
        self.assertEqual(payload["error"]["details"], ["broken resource"])
        code = ('from unittest.mock import patch\nfrom biucingcli.cli import main\n'
                'from biucingcli.templates import InvalidTemplateError\n'
                'with patch("biucingcli.cli.load_template", side_effect=InvalidTemplateError("bad metadata")):\n'
                '    main()\n')
        self.assert_json_error(self.invoke("info", "frontend", "--json", code=code),
                               "invalid_template", 1)

    def test_success_and_help_keep_their_contract(self):
        result = self.invoke("list", "--json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn("templates", json.loads(result.stdout))
        result = self.invoke("create", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)

    @unittest.skipUnless(os.name == "posix", "PTY and SIGINT require POSIX")
    def test_interactive_eof_and_interrupt(self):
        import pty
        for action, status, message in (("eof", 2, "Input ended"),
                                         ("interrupt", 130, "Operation cancelled")):
            with self.subTest(action=action):
                master, slave = pty.openpty()
                process = subprocess.Popen(
                    [sys.executable, "-m", "biucingcli.cli", "create", "web-service", "demo"],
                    stdin=slave, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                )
                os.close(slave)
                try:
                    prompt = b""
                    deadline = time.monotonic() + 10
                    while not prompt.endswith(b"Go module name: "):
                        remaining = deadline - time.monotonic()
                        self.assertGreater(remaining, 0, prompt)
                        ready, _, _ = select.select([process.stderr], [], [], remaining)
                        self.assertTrue(ready, prompt)
                        chunk = os.read(process.stderr.fileno(), 1)
                        self.assertTrue(chunk, prompt)
                        prompt += chunk
                    if action == "eof":
                        os.write(master, b"\x04")
                    else:
                        process.send_signal(signal.SIGINT)
                    stdout, stderr = process.communicate(timeout=10)
                    self.assertEqual(process.returncode, status)
                    self.assertEqual(stdout, b"")
                    self.assertIn(message, stderr.decode())
                    self.assertNotIn(b"Traceback", stderr)
                finally:
                    if process.poll() is None:
                        process.kill()
                    process.communicate()
                    os.close(master)

    @unittest.skipUnless(os.name == "posix", "SIGINT requires POSIX")
    def test_interrupt_cleans_staging_and_emits_one_json_error(self):
        code = ('import os, signal\nfrom unittest.mock import patch\n'
                'from biucingcli.cli import main\n'
                'def interrupt(*args, **kwargs):\n'
                '    os.kill(os.getpid(), signal.SIGINT)\n'
                'with patch("biucingcli.templates.shutil.copytree", side_effect=interrupt):\n'
                '    main()\n')
        with tempfile.TemporaryDirectory() as tmp:
            result = self.invoke("create", "frontend", "demo", "--output-dir", tmp,
                                 "--json", code=code)
            self.assert_json_error(result, "cancelled", 130)
            self.assertEqual(list(Path(tmp).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
