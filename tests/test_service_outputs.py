"""Focused service regression coverage; extracted without changing assertions."""

import os
import tempfile
import unittest
from pathlib import Path



from cli_support import CLIHelpers


class ServiceOutputTests(CLIHelpers, unittest.TestCase):
    def test_create_frontend_renders_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(["create", "frontend", "demo-app", "--output-dir", tmpdir])
            root = Path(tmpdir) / "demo-app"
            self.assertIn("Created frontend project: demo-app", output)
            for name in ("bootstrap", "dev", "test", "docker-build", "docker-run"):
                self.assertIn("make " + name, output)
            for path in ("package.json", "pnpm-lock.yaml", "pnpm-workspace.yaml", "components.json",
                         "app/root.tsx", "app/routes.ts", "app/routes/home.tsx", "app/routes/about.tsx",
                         "app/components/ui/button.tsx", "app/components/ui/dialog.tsx",
                         "app/features/welcome.test.tsx", "vitest.config.ts", "THIRD_PARTY_NOTICES.md"):
                self.assertTrue((root / path).is_file(), path)
            self.assertFalse((root / "src").exists())
            self.assertFalse((root / "index.html").exists())
            package = (root / "package.json").read_text()
            self.assertIn('"packageManager": "pnpm@11.21.0"', package)
            self.assertIn('"react": "19.3.0"', package)
            self.assertIn('npm:typescript@7.0.2', package)
            self.assertNotIn("react-router-dom", package)
            self.assertIn("ssr: false", (root / "react-router.config.ts").read_text())
            self.assertIn('title: "Demo App"', (root / "app/lib/project.ts").read_text())
            makefile = (root / "Makefile").read_text()
            for contract in ("WORKTREE_ID ?=", "COMPOSE_PROJECT_NAME ?=$(WORKTREE_SLUG)",
                             "IMAGE ?=$(WORKTREE_SLUG)", "DEV_HOST_PORT ?=$(DEV_PORT)",
                             "PNPM_HOME ?=$(WORKTREE_ROOT)/.pnpm-home/$(WORKTREE_ID)",
                             "PNPM_STORE_DIR ?=$(WORKTREE_ROOT)/.pnpm-store", "clean-worktree:",
                             "worktree-compose-config:", "lockfile-update:",
                             "verify: doctor format-check lint typecheck test build"):
                self.assertIn(contract, makefile)
            for path in ("scripts/doctor", "scripts/browser-smoke-production"):
                self.assertTrue(os.access(root / path, os.X_OK))
            docker = (root / "Dockerfile").read_text()
            self.assertIn("pnpm install --frozen-lockfile", docker)
            self.assertIn("/app/build/client /usr/share/nginx/html", docker)
            self.assertIn("HEALTHCHECK", docker)
            nginx = (root / "nginx.conf").read_text()
            self.assertIn("try_files $uri $uri/ /index.html;", nginx)
            self.assertIn("try_files $uri =404;", nginx)
            compose = (root / "compose.dev.yaml").read_text()
            for volume in ("frontend-node-modules", "frontend-pnpm-store", "frontend-playwright-cache"):
                self.assertIn(volume, compose)
            self.assertIn("pnpm install --frozen-lockfile && pnpm dev", compose)

    def test_create_microservice_renders_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cli(["create", "micro-service", "internal-api", "--module-name", "example.org/internal-api",
                          "--proto-package", "internal.v2", "--cache", "redis", "--output-dir", tmp, "--non-interactive"])
            root=Path(tmp)/"internal-api"
            for path in ("compose.yaml", "compose.dev.yaml", "internal/app/app.go", "internal/transport/pipeline.go",
                         "internal/runtime/admin.go", "internal/security/principal.go", "internal/observability/log.go"):
                self.assertTrue((root/path).is_file(), path)
            self.assertNotIn("reflection.Register", (root/"internal/transport/grpc.go").read_text())
            self.assertIn("127.0.0.1:${HOST_GRPC_PORT:-0}", (root/"compose.dev.yaml").read_text())
            self.assertTrue(os.access(root/"scripts/task", os.X_OK))


if __name__ == "__main__":
    unittest.main()
