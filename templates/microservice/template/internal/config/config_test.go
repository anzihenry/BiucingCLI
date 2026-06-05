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
		[]byte("service:\n  name: demo\n  http_port: 8080\n  grpc_port: 9090\ntelemetry:\n  otlp_http_endpoint: http://localhost:4318\nstore:\n  driver: postgres\n  dsn: postgres://postgres:postgres@localhost:5432/demo?sslmode=disable\n"),
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
		[]byte("service:\n  name: demo\ntelemetry:\n  otlp_http_endpoint: http://localhost:4318\nstore:\n  driver: redis\n  dsn: redis://localhost:6379/0\n"),
		0o644,
	); err != nil {
		t.Fatal(err)
	}

	t.Setenv("CONFIG_FILE", configFile)
	t.Setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318")
	t.Setenv("STORE_DSN", "redis://redis:6379/0")

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
	if cfg.Store.DSN != "redis://redis:6379/0" {
		t.Fatalf("expected store override, got %q", cfg.Store.DSN)
	}
}
