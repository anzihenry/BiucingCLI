"""Backend generation boundaries and independent component topology."""
import io
import json
import os
import shutil
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

from biucingcli.cli import main


class BackendComponentsTests(unittest.TestCase):
    def test_component_matrix_and_container_endpoints(self):
        for family in ("web-service", "micro-service"):
            for database in (("postgres",) if family == "web-service" else ("none", "postgres")):
                for cache in ("none", "redis"):
                    with self.subTest(family=family, database=database, cache=cache), tempfile.TemporaryDirectory() as tmp:
                        options = ["--proto-package", "platform.audit.v2"] if family == "micro-service" else []
                        with redirect_stdout(io.StringIO()):
                            main(["create", family, "audit-edge", "--module-name", "example.org/platform/audit-edge",
                                  "--output-dir", tmp, "--non-interactive", "--database", database, "--cache", cache, *options])
                        root = Path(tmp) / "audit-edge"
                        for filename in ("compose.dev.yaml", "compose.yaml" if family == "web-service" else "compose.yaml"):
                            services = yaml.safe_load((root / filename).read_text())["services"]
                            self.assertEqual("postgres" in services, database == "postgres")
                            self.assertEqual("redis" in services, cache == "redis")
                            app = services["app-dev" if filename == "compose.dev.yaml" else "audit-edge"]
                            expected = (["postgres"] if database == "postgres" else []) + (["redis"] if cache == "redis" else [])
                            self.assertEqual(app["depends_on"], expected)
                            self.assertEqual(bool(app["environment"]["DATABASE_DSN"]), database == "postgres")
                            self.assertEqual(bool(app["environment"]["CACHE_DSN"]), cache == "redis")
                            for component in expected:
                                self.assertNotIn("ports", services[component])
                            self.assertNotIn("STORE_DSN", app["environment"])
                        self.assertTrue((root / "scripts/verify-container").stat().st_mode & 0o111)
                        self.assertTrue((root / ".github/workflows/verify.yml").is_file())

    def test_invalid_and_removed_inputs_do_not_create_projects(self):
        cases = [
            ("web-service", ["--database", "none"]),
            ("web-service", ["--service-name", "a" * 55]),
            ("micro-service", ["--set", "database=redis"]),
            ("micro-service", ["--set", "cache=postgres"]),
            ("micro-service", ["--set", "dependency_store=postgres"]),
            ("micro-service", ["--dependency-store", "redis"]),
            ("microservice", []),
        ]
        for family, args in cases:
            with self.subTest(family=family, args=args), tempfile.TemporaryDirectory() as tmp:
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    try:
                        code = main(["create", family, "invalid", "--module-name", "example.org/invalid",
                                     "--output-dir", tmp, "--non-interactive", *args])
                    except SystemExit as exc:
                        code = exc.code
                self.assertNotEqual(code, 0)
                self.assertFalse((Path(tmp) / "invalid").exists())

    def test_generate_only_evidence_never_claims_container_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "evidence"
            command = [sys.executable, "scripts/verify-backends", "--generate-only", "--output-dir", str(output)]
            subprocess.run(command, capture_output=True, text=True, check=True)
            evidence = json.loads((output / "evidence.json").read_text())
            self.assertEqual(evidence["result"], "rendered")
            self.assertEqual(len(evidence["cases"]), 6)
            self.assertTrue(all(case["container"] == "not-run" for case in evidence["cases"]))
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_verification_failure_cleans_only_its_own_project(self):
        for family in ("web-service", "micro-service"):
            with self.subTest(family=family), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "scripts").mkdir()
                (root / "tools").mkdir()
                source = Path("src/biucingcli/template_data") / family / "template/scripts/verify-container"
                shutil.copy2(source, root / "scripts/verify-container")
                shutil.copy2(source.parent / "task", root / "scripts/task")
                if family == "micro-service":
                    stub = root / "scripts/local-ca"
                    stub.write_text("#!/bin/sh\nexit 0\n")
                    stub.chmod(0o755)
                (root / "scripts/task").write_text((source.parent / "task").read_text().replace("{{SERVICE_NAME}}", "fixture").replace("{{HTTP_PORT}}", "8080"))
                fake = "#!" + sys.executable + "\n" + """import json, os, sys
with open(os.environ["CALL_LOG"], "a") as log:
    log.write(json.dumps([os.path.basename(sys.argv[0]), *sys.argv[1:]]) + "\\n")
sys.exit(7 if "run" in sys.argv else 0)
"""
                for tool in ("docker", "make"):
                    executable = root / "tools" / tool
                    executable.write_text(fake)
                    executable.chmod(0o755)
                log = root / "calls.jsonl"
                env = {**os.environ, "PATH": str(root / "tools") + os.pathsep + os.environ["PATH"],
                       "CALL_LOG": str(log), "COMPOSE": "do-not-use-production",
                       "COMPOSE_PROJECT_NAME": "production", "DEV_COMPOSE_FILE": "production.yaml"}
                result = subprocess.run([str(root / "scripts/verify-container")], env=env,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 7, result.stderr)
                calls = [json.loads(line) for line in log.read_text().splitlines()]
                cleanup = calls[-1]
                self.assertIn("down", cleanup)
                self.assertIn("--volumes", cleanup)
                project = cleanup[cleanup.index("--project-name") + 1]
                self.assertTrue(project.startswith("verify-"))
                run = next(call for call in calls if "run" in call)
                self.assertEqual(run[run.index("--project-name") + 1], project)
                self.assertIn("compose.dev.yaml", run)
                self.assertNotIn("production", " ".join(run + cleanup))
