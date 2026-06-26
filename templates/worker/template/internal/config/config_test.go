package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadDefaults(t *testing.T) {
	tempDir := t.TempDir()
	configPath := filepath.Join(tempDir, "config.json")
	if err := os.WriteFile(configPath, []byte(`{"worker":{"name":"demo-worker","run_mode":"scheduled","tick_interval_seconds":15,"shutdown_timeout_seconds":8}}`), 0o644); err != nil {
		t.Fatal(err)
	}

	t.Setenv("CONFIG_FILE", configPath)

	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}

	if cfg.Worker.Name != "demo-worker" {
		t.Fatalf("expected worker name %q, got %q", "demo-worker", cfg.Worker.Name)
	}
	if cfg.Worker.RunMode != "scheduled" {
		t.Fatalf("expected run mode %q, got %q", "scheduled", cfg.Worker.RunMode)
	}
	if cfg.Worker.TickIntervalSeconds != 15 {
		t.Fatalf("expected tick interval %d, got %d", 15, cfg.Worker.TickIntervalSeconds)
	}
}

func TestLoadUsesEnvironmentOverrides(t *testing.T) {
	tempDir := t.TempDir()
	configPath := filepath.Join(tempDir, "config.json")
	if err := os.WriteFile(configPath, []byte(`{"worker":{"name":"demo-worker","run_mode":"scheduled","tick_interval_seconds":15,"shutdown_timeout_seconds":8}}`), 0o644); err != nil {
		t.Fatal(err)
	}

	t.Setenv("CONFIG_FILE", configPath)
	t.Setenv("WORKER_NAME", "override-worker")
	t.Setenv("WORKER_RUN_MODE", "oneshot")
	t.Setenv("WORKER_TICK_INTERVAL_SECONDS", "3")
	t.Setenv("WORKER_SHUTDOWN_TIMEOUT_SECONDS", "2")

	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}

	if cfg.Worker.Name != "override-worker" {
		t.Fatalf("expected worker name %q, got %q", "override-worker", cfg.Worker.Name)
	}
	if cfg.Worker.RunMode != "oneshot" {
		t.Fatalf("expected run mode %q, got %q", "oneshot", cfg.Worker.RunMode)
	}
	if cfg.Worker.TickIntervalSeconds != 3 {
		t.Fatalf("expected tick interval %d, got %d", 3, cfg.Worker.TickIntervalSeconds)
	}
	if cfg.Worker.ShutdownTimeoutSeconds != 2 {
		t.Fatalf("expected shutdown timeout %d, got %d", 2, cfg.Worker.ShutdownTimeoutSeconds)
	}
}
