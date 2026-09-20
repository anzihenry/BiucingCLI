"""Focused service regression coverage; extracted without changing assertions."""

import os
import tempfile
import unittest
from pathlib import Path



from cli_support import CLIHelpers


class ServiceOutputTests(CLIHelpers, unittest.TestCase):
    def test_create_frontend_renders_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                ["create", "frontend", "demo-app", "--output-dir", tmpdir]
            )
            project_dir = Path(tmpdir) / "demo-app"
            package_json = (project_dir / "package.json").read_text(encoding="utf-8")
            pnpm_lock = (project_dir / "pnpm-lock.yaml").read_text(encoding="utf-8")
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            index_html = (project_dir / "index.html").read_text(encoding="utf-8")
            eslint_config = (project_dir / "eslint.config.js").read_text(encoding="utf-8")
            prettier_config = (project_dir / ".prettierrc.json").read_text(encoding="utf-8")
            env_example = (project_dir / ".env.example").read_text(encoding="utf-8")
            vite_config = (project_dir / "vite.config.ts").read_text(encoding="utf-8")
            makefile = (project_dir / "Makefile").read_text(encoding="utf-8")
            dockerfile = (project_dir / "Dockerfile").read_text(encoding="utf-8")
            dockerfile_dev = (project_dir / "Dockerfile.dev").read_text(encoding="utf-8")
            dockerfile_dev_full = (
                project_dir / "Dockerfile.dev.full"
            ).read_text(encoding="utf-8")
            npmrc = (project_dir / ".npmrc").read_text(encoding="utf-8")
            compose_dev = (project_dir / "compose.dev.yaml").read_text(encoding="utf-8")
            nginx_conf = (project_dir / "nginx.conf").read_text(encoding="utf-8")
            dockerignore = (project_dir / ".dockerignore").read_text(encoding="utf-8")
            app_test = (project_dir / "src" / "App.test.tsx").read_text(encoding="utf-8")
            app_file = (project_dir / "src" / "App.tsx").read_text(encoding="utf-8")
            env_config = (project_dir / "src" / "config" / "env.ts").read_text(encoding="utf-8")
            playwright_config = (
                project_dir / "playwright.smoke.config.ts"
            ).read_text(encoding="utf-8")
            playwright_production_config = (
                project_dir / "playwright.production.config.ts"
            ).read_text(encoding="utf-8")
            browser_smoke_test = (
                project_dir / "tests" / "browser-smoke.spec.ts"
            ).read_text(encoding="utf-8")
            production_browser_smoke_test = (
                project_dir / "tests" / "production-browser-smoke.spec.ts"
            ).read_text(encoding="utf-8")
            production_browser_smoke_script = (
                project_dir / "scripts" / "browser-smoke-production"
            ).read_text(encoding="utf-8")
            app_router = (
                project_dir / "src" / "router" / "AppRouter.tsx"
            ).read_text(encoding="utf-8")
            api_client = (
                project_dir / "src" / "services" / "api" / "client.ts"
            ).read_text(encoding="utf-8")
            test_setup = (
                project_dir / "src" / "test" / "setup.ts"
            ).read_text(encoding="utf-8")
            home_page = (project_dir / "src" / "pages" / "HomePage.tsx").read_text(
                encoding="utf-8"
            )
            overview_service = (
                project_dir / "src" / "services" / "projectOverview.ts"
            ).read_text(encoding="utf-8")
            overview_type = (
                project_dir / "src" / "types" / "projectOverview.ts"
            ).read_text(encoding="utf-8")

            self.assertTrue(project_dir.exists())
            self.assertTrue((project_dir / "package.json").exists())
            self.assertIn("Created frontend project: demo-app", output)
            self.assertIn("make dev", output)
            self.assertIn("make test", output)
            self.assertIn("make docker-build", output)
            self.assertIn("make docker-run", output)
            self.assertIn("demo-app", package_json)
            self.assertIn('"packageManager": "pnpm@9.9.0"', package_json)
            self.assertIn('"node": ">=20.0.0"', package_json)
            self.assertIn("react-router-dom", package_json)
            self.assertIn('"lint": "eslint ."', package_json)
            self.assertIn('"typecheck": "tsc --noEmit"', package_json)
            self.assertIn('"test": "vitest run"', package_json)
            self.assertIn('"test:watch": "vitest"', package_json)
            self.assertIn('"browser:install": "playwright install chromium"', package_json)
            self.assertIn('"browser:smoke": "playwright test -c playwright.smoke.config.ts"', package_json)
            self.assertIn(
                '"browser:smoke:production": "playwright test -c playwright.production.config.ts"',
                package_json,
            )
            self.assertIn('lockfileVersion: "9.0"', pnpm_lock)
            self.assertIn("playwright@1.55.0", pnpm_lock)
            self.assertIn("@testing-library/jest-dom@6.9.1", pnpm_lock)
            self.assertIn('"format": "prettier --write ."', package_json)
            self.assertIn("Docker Workflow", readme)
            self.assertIn("Available Commands", readme)
            self.assertIn("Quality Checks", readme)
            self.assertIn("Runtime Configuration", readme)
            self.assertIn("Docker Files", readme)
            self.assertIn("Package Manager", readme)
            self.assertIn("make dev", readme)
            self.assertIn("make browser-smoke", readme)
            self.assertIn("make browser-smoke-production", readme)
            self.assertIn("make lockfile-update", readme)
            self.assertIn("committed `pnpm-lock.yaml`", readme)
            self.assertIn("The default development image stays relatively light", readme)
            self.assertIn("make bootstrap-full", readme)
            self.assertIn("DEV_DOCKERFILE=Dockerfile.dev.full make dev", readme)
            self.assertIn("<title>Demo App</title>", index_html)
            self.assertIn("WORKTREE_LABEL ?=$(shell basename", makefile)
            self.assertIn("WORKTREE_ID ?=$(shell printf", makefile)
            self.assertIn("COMPOSE_PROJECT_NAME ?=$(WORKTREE_SLUG)", makefile)
            self.assertIn("IMAGE ?=$(WORKTREE_SLUG)", makefile)
            self.assertIn("TAG ?=dev", makefile)
            self.assertIn("DEV_HOST_PORT ?=$(DEV_PORT)", makefile)
            self.assertIn("PNPM_HOME ?=$(WORKTREE_ROOT)/.pnpm-home/$(WORKTREE_ID)", makefile)
            self.assertIn("PNPM_STORE_DIR ?=$(WORKTREE_ROOT)/.pnpm-store", makefile)
            self.assertIn("RUNTIME_CONTAINER ?=$(WORKTREE_SLUG)-production-smoke", makefile)
            self.assertIn("worktree-info:", makefile)
            self.assertIn("worktree-doctor:", makefile)
            self.assertIn("PNPM_STORE_DIR should stay inside this worktree", makefile)
            self.assertIn("clean-worktree:", makefile)
            self.assertIn("Port occupancy checks skipped: lsof is not available.", makefile)
            self.assertIn("Warning: DEV_HOST_PORT $(DEV_HOST_PORT) is already in use.", makefile)
            self.assertIn("Suggested override: DEV_HOST_PORT=$$(( $(DEV_HOST_PORT) + 10000 )) make dev", makefile)
            self.assertIn("Suggested override: HOST_PORT=$$(( $(HOST_PORT) + 10000 )) make docker-run", makefile)
            self.assertIn("Docker is not available; cannot render Compose config.", makefile)
            self.assertIn("$(COMPOSE) -f $(DEV_COMPOSE_FILE) config", makefile)
            self.assertIn("make worktree-compose-config", readme)
            self.assertIn("prints suggested overrides", readme)
            self.assertIn("DEV_DOCKERFILE ?=Dockerfile.dev", makefile)
            self.assertIn(
                "DEV_DOCKERFILE=$(DEV_DOCKERFILE) $(COMPOSE) -f $(DEV_COMPOSE_FILE) build $(DEV_SERVICE)",
                makefile,
            )
            self.assertIn(
                "DEV_DOCKERFILE=Dockerfile.dev.full $(COMPOSE) -f $(DEV_COMPOSE_FILE) build $(DEV_SERVICE)",
                makefile,
            )
            self.assertIn(
                "DEV_DOCKERFILE=$(DEV_DOCKERFILE) $(COMPOSE) -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE)",
                makefile,
            )
            self.assertIn(
                'DEV_DOCKERFILE=$(DEV_DOCKERFILE) $(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) bash -lc "pnpm install --frozen-lockfile && pnpm browser:install"',
                makefile,
            )
            self.assertIn(
                "DEV_DOCKERFILE=$(DEV_DOCKERFILE) $(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) pnpm browser:smoke",
                makefile,
            )
            self.assertIn("BUILDER_IMAGE ?=node:20-alpine", makefile)
            self.assertIn("RUNTIME_IMAGE ?=nginx:1.27-alpine", makefile)
            self.assertIn("DEV_BASE_IMAGE ?=node:20-bookworm", makefile)
            self.assertIn("--build-arg BUILDER_IMAGE=$(BUILDER_IMAGE)", makefile)
            self.assertIn("browser-smoke-production: docker-build browser-install", makefile)
            self.assertIn("./scripts/browser-smoke-production", makefile)
            self.assertIn("lockfile-update:", makefile)
            self.assertIn("pnpm install --no-frozen-lockfile", makefile)
            self.assertIn("ARG BUILDER_IMAGE=node:20-alpine", dockerfile)
            self.assertIn("FROM ${BUILDER_IMAGE} AS builder", dockerfile)
            self.assertIn("ARG RUNTIME_IMAGE=nginx:1.27-alpine", dockerfile)
            self.assertIn("FROM ${RUNTIME_IMAGE}", dockerfile)
            self.assertIn("COPY package.json pnpm-lock.yaml ./", dockerfile)
            self.assertIn("pnpm install --frozen-lockfile", dockerfile)
            self.assertIn("HEALTHCHECK", dockerfile)
            self.assertIn("COPY --from=builder /app/dist /usr/share/nginx/html", dockerfile)
            self.assertIn("ARG DEV_BASE_IMAGE=node:20-bookworm", dockerfile_dev)
            self.assertIn("FROM ${DEV_BASE_IMAGE}", dockerfile_dev)
            self.assertIn("PNPM_STORE_DIR=/pnpm-store", dockerfile_dev)
            self.assertIn("PLAYWRIGHT_BROWSERS_PATH=/ms-playwright", dockerfile_dev)
            self.assertIn(
                'CMD ["bash", "-lc", "if [ ! -d node_modules/.pnpm ]; then pnpm install --frozen-lockfile; fi; pnpm dev --host 0.0.0.0 --port 5173"]',
                dockerfile_dev,
            )
            self.assertIn("ARG DEV_BASE_IMAGE=node:20-bookworm", dockerfile_dev_full)
            self.assertIn("COPY package.json pnpm-lock.yaml ./", dockerfile_dev_full)
            self.assertIn("pnpm install --frozen-lockfile", dockerfile_dev_full)
            self.assertIn("pnpm exec playwright install chromium", dockerfile_dev_full)
            self.assertIn("frontend-dev", compose_dev)
            self.assertIn("dockerfile: ${DEV_DOCKERFILE:-Dockerfile.dev}", compose_dev)
            self.assertIn("DEV_BASE_IMAGE: ${DEV_BASE_IMAGE:-node:20-bookworm}", compose_dev)
            self.assertIn(
                'command: bash -lc "if [ ! -d node_modules/.pnpm ]; then pnpm install --frozen-lockfile; fi; pnpm dev --host 0.0.0.0 --port ${DEV_PORT:-5173} --strictPort"',
                compose_dev,
            )
            self.assertIn('"host.docker.internal:host-gateway"', compose_dev)
            self.assertIn('"${DEV_HOST_PORT:-5173}:${DEV_PORT:-5173}"', compose_dev)
            self.assertIn("frontend-node-modules", compose_dev)
            self.assertIn("frontend-pnpm-store", compose_dev)
            self.assertIn("frontend-playwright-cache", compose_dev)
            self.assertIn("store-dir=.pnpm-store", npmrc)
            self.assertIn("try_files $uri $uri/ /index.html;", nginx_conf)
            self.assertIn("node_modules/", dockerignore)
            self.assertIn(".pnpm-store/", dockerignore)
            self.assertIn("dist/", dockerignore)
            self.assertIn("react-refresh/only-export-components", eslint_config)
            self.assertIn('"trailingComma": "all"', prettier_config)
            self.assertIn("VITE_API_BASE_URL=http://localhost:8080", env_example)
            self.assertIn('environment: "jsdom"', vite_config)
            self.assertIn('include: ["src/**/*.test.{ts,tsx}"]', vite_config)
            self.assertIn("await getProjectOverview()", app_test)
            self.assertIn('from "vitest"', app_test)
            self.assertIn("toBeInTheDocument", app_test)
            self.assertIn("AppRouter", app_file)
            self.assertIn("apiBaseUrl", env_config)
            self.assertIn("pnpm exec vite", playwright_config)
            self.assertIn('testMatch: "browser-smoke.spec.ts"', playwright_config)
            self.assertIn('baseURL: "http://127.0.0.1:4173"', playwright_config)
            self.assertIn("PLAYWRIGHT_BASE_URL is required", playwright_production_config)
            self.assertNotIn("webServer", playwright_production_config)
            self.assertIn('name: "Demo App"', browser_smoke_test)
            self.assertIn("browser-smoke-homepage.png", browser_smoke_test)
            self.assertIn('toContain("nginx")', production_browser_smoke_test)
            self.assertIn("production-image-homepage.png", production_browser_smoke_test)
            self.assertIn("State.Health.Status", production_browser_smoke_script)
            self.assertIn("pnpm browser:smoke:production", production_browser_smoke_script)
            self.assertIn("docker.internal", production_browser_smoke_script)
            self.assertTrue(
                os.access(
                    project_dir / "scripts" / "browser-smoke-production", os.X_OK
                )
            )
            self.assertIn("createBrowserRouter", app_router)
            self.assertIn("v7_startTransition", app_router)
            self.assertIn("VITE_API_BASE_URL is not configured", api_client)
            self.assertIn("@testing-library/jest-dom/vitest", test_setup)
            self.assertIn("useProjectOverview", home_page)
            self.assertIn('title: "Demo App"', overview_service)
            self.assertIn("getProjectOverviewFallback", overview_service)
            self.assertIn("export type ProjectOverview", overview_type)

    def test_create_microservice_renders_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self.run_cli(
                [
                    "create",
                    "microservice",
                    "user-service",
                    "--output-dir",
                    tmpdir,
                    "--module-name",
                    "github.com/example/user-service",
                    "--proto-package",
                    "user.v1",
                    "--grpc-port",
                    "9191",
                    "--dependency-store",
                    "redis",
                    "--otel-exporter-endpoint",
                    "http://localhost:14318",
                ]
            )
            project_dir = Path(tmpdir) / "user-service"
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            makefile = (project_dir / "Makefile").read_text(encoding="utf-8")
            dockerfile = (project_dir / "Dockerfile").read_text(encoding="utf-8")
            dockerfile_dev = (project_dir / "Dockerfile.dev").read_text(encoding="utf-8")
            compose_dev = (project_dir / "compose.dev.yaml").read_text(encoding="utf-8")
            air_toml = (project_dir / ".air.toml").read_text(encoding="utf-8")
            dockerignore = (project_dir / ".dockerignore").read_text(encoding="utf-8")
            compose_yaml = (project_dir / "deploy" / "compose.yaml").read_text(encoding="utf-8")
            config_yaml = (project_dir / "configs" / "config.yaml").read_text(encoding="utf-8")
            proto_file = (
                project_dir / "api" / "proto" / "service" / "v1" / "service.proto"
            ).read_text(encoding="utf-8")
            buf_yaml = (project_dir / "api" / "buf.yaml").read_text(encoding="utf-8")
            buf_gen = (project_dir / "api" / "buf.gen.yaml").read_text(encoding="utf-8")
            go_sum = (project_dir / "go.sum").read_text(encoding="utf-8")
            mise_toml = (project_dir / ".mise.toml").read_text(encoding="utf-8")
            go_mod = (project_dir / "go.mod").read_text(encoding="utf-8")
            main_go = (project_dir / "cmd" / "server" / "main.go").read_text(encoding="utf-8")
            telemetry_go = (
                project_dir / "internal" / "telemetry" / "telemetry.go"
            ).read_text(encoding="utf-8")
            grpc_transport = (
                project_dir / "internal" / "transport" / "grpc.go"
            ).read_text(encoding="utf-8")
            grpc_ping_transport = (
                project_dir / "internal" / "transport" / "ping.go"
            ).read_text(encoding="utf-8")
            config_go = (project_dir / "internal" / "config" / "config.go").read_text(
                encoding="utf-8"
            )
            config_test = (
                project_dir / "internal" / "config" / "config_test.go"
            ).read_text(encoding="utf-8")
            runtime_go = (
                project_dir / "internal" / "runtime" / "server.go"
            ).read_text(encoding="utf-8")
            runtime_test = (
                project_dir / "internal" / "runtime" / "server_test.go"
            ).read_text(encoding="utf-8")
            doctor = (project_dir / "scripts" / "doctor").read_text(encoding="utf-8")
            bootstrap = (project_dir / "scripts" / "bootstrap").read_text(encoding="utf-8")
            server_test = (project_dir / "tests" / "server_test.go").read_text(
                encoding="utf-8"
            )

            self.assertTrue(project_dir.exists())
            self.assertIn("Created microservice project: user-service", output)
            self.assertIn("make dev", output)
            self.assertIn("make verify", output)
            self.assertIn("make up", output)
            self.assertIn("OpenTelemetry", readme)
            self.assertIn("Docker Workflow", readme)
            self.assertIn("make dev-shell", readme)
            self.assertIn("Proto package: `user.v1`", readme)
            self.assertIn("Local dependency store: `redis`", readme)
            self.assertIn("make verify", readme)
            self.assertIn(
                "the first `make proto` may still fetch remote Buf plugin artifacts",
                readme,
            )
            self.assertIn("GOPROXY", readme)
            self.assertIn("GOSUMDB", readme)
            self.assertIn("COMPOSE_PROJECT_NAME ?=$(WORKTREE_SLUG)", makefile)
            self.assertIn("GOMODCACHE ?= $(CURDIR)/.cache/go-mod", makefile)
            self.assertIn("Go module cache: $(GOMODCACHE)", makefile)
            self.assertIn("GOMODCACHE should stay inside this worktree", makefile)
            self.assertIn("WORKTREE_LABEL ?=$(shell basename", makefile)
            self.assertIn("HOST_DEPENDENCY_STORE_PORT ?=6379", makefile)
            self.assertIn("HOST_OTEL_GRPC_PORT ?=4317", makefile)
            self.assertIn("HOST_OTEL_HTTP_PORT ?=4318", makefile)
            self.assertIn("worktree-info:", makefile)
            self.assertIn("worktree-compose-config:", makefile)
            self.assertIn("clean-worktree:", makefile)
            self.assertIn("Warning: HOST_HTTP_PORT $(HOST_HTTP_PORT) is already in use.", makefile)
            self.assertIn("Suggested override: HOST_HTTP_PORT=$$(( $(HOST_HTTP_PORT) + 10000 )) make dev", makefile)
            self.assertIn("Suggested override: HOST_DEPENDENCY_STORE_PORT=$$(( $(HOST_DEPENDENCY_STORE_PORT) + 10000 )) make dev", makefile)
            self.assertIn("$(COMPOSE) -f $(DEV_COMPOSE_FILE) config", makefile)
            self.assertIn("$(COMPOSE) -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE) redis otel-collector", makefile)
            self.assertIn('bash -lc "cd api && buf generate"', makefile)
            self.assertIn('bash -lc "cd api && buf lint && cd .. && golangci-lint run', makefile)
            self.assertIn("test: proto", makefile)
            self.assertIn("build: proto", makefile)
            self.assertIn("docker-build: proto", makefile)
            self.assertIn("HOST_GRPC_PORT ?=9191", makefile)
            self.assertIn("BUILDER_IMAGE ?= golang:1.26-alpine", makefile)
            self.assertIn("EXPOSE 9191", dockerfile)
            self.assertIn("HEALTHCHECK", dockerfile)
            self.assertIn("http://127.0.0.1:8080/healthz", dockerfile)
            self.assertIn('["/app/server", "healthcheck"', dockerfile)
            self.assertIn("ARG BUILDER_IMAGE=golang:1.26-alpine", dockerfile)
            self.assertIn("ARG BUF_VERSION=1.70.0", dockerfile_dev)
            self.assertIn("ARG GOLANGCI_LINT_VERSION=2.12.2", dockerfile_dev)
            self.assertIn("ARG GOPROXY=https://proxy.golang.org,direct", dockerfile_dev)
            self.assertIn("ARG GOSUMDB=sum.golang.org", dockerfile_dev)
            self.assertIn("buf-Linux-${buf_arch}.tar.gz", dockerfile_dev)
            self.assertIn("golangci-lint-${GOLANGCI_LINT_VERSION}-linux-${golangci_arch}.tar.gz", dockerfile_dev)
            self.assertIn("COPY go.mod go.sum ./", dockerfile_dev)
            self.assertIn("until go mod download; do", dockerfile_dev)
            self.assertIn('CMD ["air", "-c", ".air.toml"]', dockerfile_dev)
            self.assertIn("app-dev", compose_dev)
            self.assertIn("GOPROXY: ${GOPROXY:-https://proxy.golang.org,direct}", compose_dev)
            self.assertIn("GOSUMDB: ${GOSUMDB:-sum.golang.org}", compose_dev)
            self.assertIn("GOMODCACHE: /workspace/.cache/go-mod", compose_dev)
            self.assertIn("microservice-go-mod:/workspace/.cache/go-mod", compose_dev)
            self.assertIn("otel/opentelemetry-collector-contrib:0.126.0", compose_dev)
            self.assertIn("STORE_DSN: redis://redis:6379/0", compose_dev)
            self.assertIn("stop_grace_period: 15s", compose_dev)
            self.assertIn('cmd = "go build -o ./tmp/server ./cmd/server"', air_toml)
            self.assertIn("include_ext = [\"go\", \"yaml\", \"proto\"]", air_toml)
            self.assertIn(".cache/", dockerignore)
            self.assertIn('image: ${IMAGE:-user-service}:${TAG:-latest}', compose_yaml)
            self.assertIn('- "${HOST_GRPC_PORT:-9191}:9191"', compose_yaml)
            self.assertIn("BUILDER_IMAGE: ${BUILDER_IMAGE:-golang:1.26-alpine}", compose_yaml)
            self.assertIn("STORE_DSN: redis://redis:6379/0", compose_yaml)
            self.assertIn("stop_grace_period: 15s", compose_yaml)
            self.assertIn("image: redis:7-alpine", compose_yaml)
            self.assertNotIn("POSTGRES_PASSWORD", compose_yaml)
            self.assertIn("driver: redis", config_yaml)
            self.assertIn("dsn: redis://localhost:6379/0", config_yaml)
            self.assertIn('otlp_http_endpoint: "http://localhost:14318"', config_yaml)
            self.assertIn("shutdown_timeout_seconds: 10", config_yaml)
            self.assertIn("package user.v1;", proto_file)
            self.assertIn('option go_package = "github.com/example/user-service/api/gen/go/service/v1;servicev1";', proto_file)
            self.assertIn("service UserServiceService", proto_file)
            self.assertIn("version: v2", buf_yaml)
            self.assertIn("PACKAGE_DIRECTORY_MATCH", buf_yaml)
            self.assertIn("remote: buf.build/protocolbuffers/go", buf_gen)
            self.assertIn("remote: buf.build/grpc/go", buf_gen)
            self.assertIn('go = "1.26.0"', mise_toml)
            self.assertIn("go 1.26.0", go_mod)
            self.assertIn("go.opentelemetry.io/otel v1.43.0", go_sum)
            self.assertIn("telemetry.Setup", main_go)
            self.assertIn("signal.NotifyContext", main_go)
            self.assertIn("serverruntime.Serve", main_go)
            self.assertIn("service.NewPingService", main_go)
            self.assertIn('log.Printf("starting %s gRPC server on :%s"', main_go)
            self.assertIn("otlptracehttp.New", telemetry_go)
            self.assertIn("semconv.ServiceName(serviceName)", telemetry_go)
            self.assertIn("grpc.NewServer()", grpc_transport)
            self.assertIn("healthpb.RegisterHealthServer", grpc_transport)
            self.assertIn("func (server *GRPCServer) SetServing", grpc_transport)
            self.assertIn("HealthCheckResponse_NOT_SERVING", grpc_transport)
            self.assertIn("servicev1.RegisterUserServiceServiceServer", grpc_transport)
            self.assertIn("reflection.Register(server)", grpc_transport)
            self.assertIn("UnimplementedUserServiceServiceServer", grpc_ping_transport)
            self.assertIn("func (server *pingServer) Ping(", grpc_ping_transport)
            self.assertIn("servicev1.PingResponse", grpc_ping_transport)
            self.assertIn('cfg.Store.Driver = "redis"', config_go)
            self.assertIn('cfg.Telemetry.OTLPHTTPEndpoint = "http://localhost:14318"', config_go)
            self.assertIn("TestLoadUsesEnvironmentOverrides", config_test)
            self.assertIn("TestLoadRejectsNegativeTimeout", config_test)
            self.assertIn("ReadHeaderTimeout", runtime_go)
            self.assertIn("func CheckHealth", runtime_go)
            self.assertIn("grpcServer.SetServing(false)", runtime_go)
            self.assertIn("grpcServer.GracefulStop()", runtime_go)
            self.assertIn("grpcServer.Stop()", runtime_go)
            self.assertIn("TestServeMarksGRPCNotServingBeforeGracefulStop", runtime_test)
            self.assertIn("TestServeForcesGRPCStopAfterTimeout", runtime_test)
            self.assertIn("buf is not installed or not on PATH.", doctor)
            self.assertIn("service.grpc_port must be between 1 and 65535", doctor)
            self.assertIn("go mod tidy", bootstrap)
            self.assertIn("buf is not available on PATH.", bootstrap)
            self.assertIn("TestHealthz", server_test)
            self.assertIn("TestPing", server_test)
            self.assertIn("TestGRPCPingContract", server_test)
            self.assertIn("bufconn.Listen", server_test)
            self.assertIn("NewUserServiceServiceClient", server_test)
            self.assertIn("healthpb.NewHealthClient", server_test)
            self.assertIn("HealthCheckResponse_SERVING", server_test)
            self.assertIn("UserServiceService_Ping_FullMethodName", server_test)
            self.assertIn("user.v1.UserServiceService/Ping", readme)
            self.assertIn("gRPC health service switches to `NOT_SERVING`", readme)
            self.assertTrue(os.access(project_dir / "scripts" / "bootstrap", os.X_OK))
            self.assertTrue(os.access(project_dir / "scripts" / "doctor", os.X_OK))


if __name__ == "__main__":
    unittest.main()
