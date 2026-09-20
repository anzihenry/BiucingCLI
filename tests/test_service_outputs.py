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
