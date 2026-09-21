"""Shipped CSR/SSG/SSR preset contracts; Node/browser gates run separately."""

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
    def test_shipped_modes_are_advertised_and_validated(self):
        definition = load_template("frontend")
        self.assertEqual(definition.variant_summary(), {
            "selector": "rendering", "default": "csr", "choices": ["csr", "ssg", "ssr"],
        })
        self.assertEqual(validate_templates(), [])
        for mode in ("SSR", "auto"):
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
        for dependency in ("@base-ui/react/button", "@base-ui/react/dialog", "lucide-react"):
            self.assertIn(f'"{dependency}"', files["vite.config.ts"].read_text())
        dockerfile = files["Dockerfile"].read_text()
        runtime = dockerfile.split("FROM ${RUNTIME_IMAGE}")[1]
        self.assertIn("/app/build/client /usr/share/nginx/html", runtime)
        self.assertNotIn("node_modules", runtime)
        self.assertNotIn("build/server", runtime)
        self.assertIn("Copyright (c) 2023 shadcn", files["THIRD_PARTY_NOTICES.md"].read_text())

    def test_ssg_shares_toolchain_without_csr_route_or_deployment_leaks(self):
        definition = load_template("frontend")
        csr = {e.output_path: e for e in resolve_resources(definition, {"rendering": "csr"}).entries}
        ssg = {e.output_path: e for e in resolve_resources(definition, {"rendering": "ssg"}).entries}
        for name in ("package.json", "pnpm-lock.yaml", "pnpm-workspace.yaml", "app/root.tsx",
                     "app/components/ui/button.tsx", "tests/interactions.ts", "vite.config.ts"):
            self.assertEqual(ssg[name].source, csr[name].source, name)
            self.assertEqual(ssg[name].layer, "common", name)
        for name in ("nginx.conf", "react-router.config.ts", "app/routes/home.tsx", "README.md"):
            self.assertNotEqual(ssg[name].source, csr[name].source, name)
        self.assertIn("app/routes/article.tsx", ssg)
        self.assertNotIn("app/routes/article.tsx", csr)
        self.assertIn("public/404.html", ssg)
        self.assertNotIn("public/404.html", csr)
        config = ssg["react-router.config.ts"].source.read_text()
        self.assertIn("ssr: false", config)
        self.assertIn("contentPaths()", config)
        self.assertIn("requireSiteOrigin(process.env.SITE_URL)", config)
        nginx = ssg["nginx.conf"].source.read_text()
        self.assertIn("try_files $uri $uri/index.html =404", nginx)
        self.assertNotIn("try_files $uri $uri/ /index.html", nginx)
        docker = ssg["Dockerfile"].source.read_text()
        self.assertIn("ARG SITE_URL", docker)
        runtime = docker.split("FROM ${RUNTIME_IMAGE}")[1]
        self.assertNotIn("node_modules", runtime)
        self.assertNotIn("build/server", runtime)

    def test_ssg_generation_is_deterministic_and_preserves_special_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            values = {"rendering": "ssg", "display_name": 'R&D "引号" <研发> \\ $HOME {{PROJECT_NAME}}'}
            plan = build_generation_plan(CreateRequest("frontend", "demo", Path(tmp), values))
            execute_generation_plan(plan)
            target = Path(tmp) / "second"
            execute_generation_plan(replace(plan, target_dir=target))
            self.assertEqual(inventory(plan.target_dir), inventory(target))
            text = (target / "app/lib/project.ts").read_text()
            self.assertIn("{{PROJECT_NAME}}", text)
            self.assertNotIn("variants", {p.name for p in target.iterdir()})
            self.assertTrue((target / "scripts/browser-smoke-production").stat().st_mode & 0o111)

    def test_ssr_shares_toolchain_and_owns_node_runtime(self):
        definition = load_template("frontend")
        csr = {e.output_path: e for e in resolve_resources(definition, {"rendering": "csr"}).entries}
        ssr = {e.output_path: e for e in resolve_resources(definition, {"rendering": "ssr"}).entries}
        for name in ("package.json", "pnpm-lock.yaml", "tsconfig.json", "app/root.tsx", "tests/interactions.ts"):
            self.assertEqual(csr[name].source, ssr[name].source, name)
        for name in ("app/entry.server.tsx", "app/lib/request.server.ts", "server/index.ts", "server/runtime.ts"):
            self.assertIn(name, ssr)
            self.assertNotIn(name, csr)
            self.assertNotEqual(ssr[name].layer, "common")
        self.assertNotIn("nginx.conf", ssr)
        self.assertNotIn("public/404.html", ssr)
        self.assertIn("ssr: true", ssr["react-router.config.ts"].source.read_text())
        docker = ssr["Dockerfile"].source.read_text()
        self.assertIn("pnpm install --prod --frozen-lockfile", docker)
        self.assertIn("USER node", docker)
        self.assertIn('CMD ["node", "server/index.ts"]', docker)

    def test_ssr_generation_preserves_special_input_and_executable_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            values = {"rendering": "ssr", "display_name": 'R&D "引号" <研发> \\ $HOME {{PROJECT_NAME}}'}
            plan = build_generation_plan(CreateRequest("frontend", "demo", Path(tmp), values))
            execute_generation_plan(plan)
            target = Path(tmp) / "second"
            execute_generation_plan(replace(plan, target_dir=target))
            self.assertEqual(inventory(plan.target_dir), inventory(target))
            self.assertTrue((target / "scripts/browser-smoke-production").stat().st_mode & 0o111)
            self.assertIn("{{PROJECT_NAME}}", (target / "app/lib/project.ts").read_text())
