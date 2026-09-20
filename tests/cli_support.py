"""Shared CLI fixtures (no test methods)."""

import io
import subprocess
from contextlib import redirect_stdout
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

from biucingcli.cli import main


class CLIHelpers:
    def golden_path(self, name):
        return Path(__file__).resolve().parent / "golden" / name

    def assert_matches_golden(self, name, actual):
        expected = self.golden_path(name).read_text(encoding="utf-8")
        self.assertEqual(actual, expected)

    def run_cli(self, argv, stdin_values=None):
        output = io.StringIO()
        with redirect_stdout(output):
            if stdin_values is None:
                main(argv)
            else:
                with patch("builtins.input", side_effect=stdin_values), patch("sys.stdin.isatty", return_value=True):
                    main(argv)
        return output.getvalue()

    def run_cli_failure(self, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with self.assertRaises(SystemExit) as excinfo:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                main(argv)
        return excinfo.exception.code, stdout.getvalue(), stderr.getvalue()

    def init_git_repository(self, project_dir, *, commit=False):
        subprocess.run(["git", "init", "-q"], cwd=project_dir, check=True)
        if commit:
            subprocess.run(
                ["git", "config", "user.email", "tests@example.com"],
                cwd=project_dir,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "BiucingCLI Tests"],
                cwd=project_dir,
                check=True,
            )
            subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "test fixture"],
                cwd=project_dir,
                check=True,
            )

    def create_harmony_release_fixture(self, tmpdir, name):
        self.run_cli(
            [
                "create",
                "harmonyos",
                name,
                "--output-dir",
                tmpdir,
                "--bundle-name",
                f"com.example.{name.replace('-', '')}",
            ]
        )
        project_dir = Path(tmpdir) / name
        self.init_git_repository(project_dir, commit=True)

        signing_dir = project_dir / "signing"
        signing_dir.mkdir()
        for filename in ("release.cer", "release.p7b", "release.p12"):
            (signing_dir / filename).write_text("test signing material", encoding="utf-8")
        (project_dir / "local.properties").write_text(
            "\n".join(
                [
                    "biucing.harmony.signing.certpath=signing/release.cer",
                    "biucing.harmony.signing.profile=signing/release.p7b",
                    "biucing.harmony.signing.storeFile=signing/release.p12",
                    "biucing.harmony.signing.storePassword=store-secret-value",
                    "biucing.harmony.signing.keyAlias=release",
                    "biucing.harmony.signing.keyPassword=key-secret-value",
                    "biucing.harmony.signing.signAlg=SHA256withECDSA",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return project_dir
