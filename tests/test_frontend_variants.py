"""Shipped CSR preset contracts; Node/browser gates run separately."""

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from biucingcli.catalog import load_template
from biucingcli.generation import build_generation_plan, execute_generation_plan
from biucingcli.models import CreateRequest
from biucingcli.resources import resolve_resources
from biucingcli.validation import validate_templates
from generation_baseline import inventory


class FrontendVariantTests(unittest.TestCase):
    def test_only_csr_is_advertised_and_validated(self):
        definition = load_template("frontend")
        self.assertEqual(definition.variant_summary(), {
            "selector": "rendering", "default": "csr", "choices": ["csr"],
        })
        self.assertEqual(validate_templates(), [])
        for mode in ("ssg", "ssr", "auto"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                with self.assertRaises(ValueError):
                    build_generation_plan(CreateRequest("frontend", "demo", Path(tmp), {"rendering": mode}))
                self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_default_and_explicit_csr_have_identical_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = build_generation_plan(CreateRequest("frontend", "demo", root))
            second = build_generation_plan(CreateRequest("frontend", "demo", root, {"rendering": "csr"}))
            self.assertEqual(first.resources, second.resources)
            self.assertEqual(first.values, second.values)
            execute_generation_plan(first)
            target = root / "explicit"
            execute_generation_plan(replace(second, target_dir=target))
            self.assertEqual(inventory(first.target_dir), inventory(target))

    def test_resource_ownership_and_no_source_layer_leaks(self):
        definition = load_template("frontend")
        resources = resolve_resources(definition, {"rendering": "csr"})
        entries = {e.output_path: e for e in resources.entries}
        for name in ("package.json", "pnpm-lock.yaml", "pnpm-workspace.yaml", "components.json",
                     "app/root.tsx", "app/app.css", "app/features/welcome.tsx", "vitest.config.ts"):
            self.assertEqual(entries[name].layer, "common", name)
        for name in ("react-router.config.ts", "app/routes.ts", "app/routes/home.tsx", "Dockerfile",
                     "Makefile", "README.md", "nginx.conf", "compose.dev.yaml", ".env.example"):
            self.assertNotEqual(entries[name].layer, "common", name)
        self.assertFalse(any(p.startswith(("variants/", "src/")) for p in entries))
        self.assertNotIn("template.json", entries)
        self.assertNotIn("index.html", entries)

    def test_toolchain_roles_and_static_deployment_contract(self):
        resources = resolve_resources(load_template("frontend"), {"rendering": "csr"})
        files = {e.output_path: e.source for e in resources.entries if e.kind == "file"}
        package = json.loads(files["package.json"].read_text())
        self.assertEqual(package["dependencies"]["react"], "19.3.0")
        self.assertEqual(package["devDependencies"]["@typescript/native"], "npm:typescript@7.0.2")
        self.assertEqual(package["devDependencies"]["typescript"], "npm:@typescript/typescript6@6.0.2")
        self.assertIn("node ./node_modules/@typescript/native/bin/tsc", package["scripts"]["typecheck"])
        self.assertIn("format:check", package["scripts"]["verify"])
        self.assertNotIn("shadcn", package["devDependencies"])
        self.assertIn("storeDir: ${PNPM_STORE_DIR:-.pnpm-store}", files["pnpm-workspace.yaml"].read_text())
        self.assertIn("strictPeerDependencies: true", files["pnpm-workspace.yaml"].read_text())
        # SPA prerender must not depend on container localhost address-family order.
        self.assertIn('preview: { host: "127.0.0.1" }', files["vite.config.ts"].read_text())
        dockerfile = files["Dockerfile"].read_text()
        runtime = dockerfile.split("FROM ${RUNTIME_IMAGE}")[1]
        self.assertIn("/app/build/client /usr/share/nginx/html", runtime)
        self.assertNotIn("node_modules", runtime)
        self.assertNotIn("build/server", runtime)
        self.assertIn("Copyright (c) 2023 shadcn", files["THIRD_PARTY_NOTICES.md"].read_text())
