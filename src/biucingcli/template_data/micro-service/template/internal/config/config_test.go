package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadDefaultConfig(t *testing.T) {
	tempDir := t.TempDir()
	configDir := filepath.Join(tempDir, "configs")
	if err := os.MkdirAll(configDir, 0o755); err != nil {
		t.Fatal(err)
	}

	configFile := filepath.Join(configDir, "config.yaml")
	if err := os.WriteFile(
		configFile,
		[]byte("service:\n  name: demo\n  http_port: 8080\n  grpc_port: 9090\ntelemetry:\n  otlp_http_endpoint: http://localhost:4318\ndatabase:\n  driver: postgres\n  dsn: postgres://postgres:postgres@localhost:5432/demo?sslmode=disable\n"),
		0o644,
	); err != nil {
		t.Fatal(err)
	}

	t.Setenv("CONFIG_FILE", configFile)
	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}

	if cfg.Service.Name != "demo" {
		t.Fatalf("expected service name %q, got %q", "demo", cfg.Service.Name)
	}
	if cfg.Service.GRPCPort != "9090" {
		t.Fatalf("expected gRPC port %q, got %q", "9090", cfg.Service.GRPCPort)
	}
	if cfg.Server.ShutdownTimeoutSeconds != 10 {
		t.Fatalf("expected default shutdown timeout %d, got %d", 10, cfg.Server.ShutdownTimeoutSeconds)
	}
}

func TestLoadRejectsNegativeTimeout(t *testing.T) {
	configFile := filepath.Join(t.TempDir(), "invalid.yaml")
	if err := os.WriteFile(
		configFile,
		[]byte("service:\n  name: demo\nserver:\n  read_timeout_seconds: -1\n"),
		0o644,
	); err != nil {
		t.Fatal(err)
	}
	t.Setenv("CONFIG_FILE", configFile)

	if _, err := Load(); err == nil {
		t.Fatal("expected a negative timeout to fail validation")
	}
}

func TestLoadUsesEnvironmentOverrides(t *testing.T) {
	tempDir := t.TempDir()
	configDir := filepath.Join(tempDir, "configs")
	if err := os.MkdirAll(configDir, 0o755); err != nil {
		t.Fatal(err)
	}

	configFile := filepath.Join(configDir, "config.yaml")
	if err := os.WriteFile(
		configFile,
		[]byte("service:\n  name: demo\ntelemetry:\n  otlp_http_endpoint: http://localhost:4318\ndatabase:\n  driver: postgres\n  dsn: postgres://localhost:5432/demo\n"),
		0o644,
	); err != nil {
		t.Fatal(err)
	}

	t.Setenv("CONFIG_FILE", configFile)
	t.Setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318")
	t.Setenv("DATABASE_DSN", "postgres://postgres:5432/demo")

	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}

	if cfg.Service.HTTPPort != "{{HTTP_PORT}}" {
		t.Fatalf("expected default HTTP port %q, got %q", "{{HTTP_PORT}}", cfg.Service.HTTPPort)
	}
	if cfg.Telemetry.OTLPHTTPEndpoint != "http://otel-collector:4318" {
		t.Fatalf("expected telemetry endpoint override, got %q", cfg.Telemetry.OTLPHTTPEndpoint)
	}
	if cfg.Database.DSN != "postgres://postgres:5432/demo" {
		t.Fatalf("expected database override, got %q", cfg.Database.DSN)
	}
}

func TestComponentEnvironmentOverridesAreIndependent(t *testing.T) {
	path := filepath.Join(t.TempDir(), "components.yaml")
	data := []byte("service:\n  name: components\ndatabase:\n  driver: postgres\ncache:\n  driver: redis\n")
	if err := os.WriteFile(path, data, 0o600); err != nil {
		t.Fatal(err)
	}
	t.Setenv("CONFIG_FILE", path)
	t.Setenv("DATABASE_DSN", "postgres://db.example/test")
	t.Setenv("CACHE_DSN", "redis://cache.example/1")
	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}
	if cfg.Database.DSN != "postgres://db.example/test" || cfg.Cache.DSN != "redis://cache.example/1" {
		t.Fatal("component configuration crossed database/cache boundaries")
	}
}

func TestDisabledComponentsIgnoreStaleDSNs(t *testing.T) {
	path := filepath.Join(t.TempDir(), "components.yaml")
	data := []byte("service:\n  name: components\ndatabase:\n  driver: none\ncache:\n  driver: none\n")
	if err := os.WriteFile(path, data, 0o600); err != nil {
		t.Fatal(err)
	}
	t.Setenv("CONFIG_FILE", path)
	t.Setenv("DATABASE_DSN", "postgres://stale/test")
	t.Setenv("CACHE_DSN", "redis://stale/0")
	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}
	if cfg.Database.DSN != "" || cfg.Cache.DSN != "" {
		t.Fatal("disabled component retained a DSN")
	}
}
