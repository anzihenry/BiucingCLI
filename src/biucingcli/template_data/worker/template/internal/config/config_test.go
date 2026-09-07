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
	if cfg.Worker.RetryMaxAttempts != 3 || cfg.Worker.RetryInitialSeconds != 1 || cfg.Worker.RetryMaxSeconds != 30 {
		t.Fatalf("unexpected retry defaults: %+v", cfg.Worker)
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
	t.Setenv("WORKER_RETRY_MAX_ATTEMPTS", "5")
	t.Setenv("WORKER_RETRY_INITIAL_BACKOFF_SECONDS", "2")
	t.Setenv("WORKER_RETRY_MAX_BACKOFF_SECONDS", "8")

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
	if cfg.Worker.RetryMaxAttempts != 5 || cfg.Worker.RetryInitialSeconds != 2 || cfg.Worker.RetryMaxSeconds != 8 {
		t.Fatalf("unexpected retry overrides: %+v", cfg.Worker)
	}
}

func TestLoadRejectsRetryBackoffRange(t *testing.T) {
	configPath := filepath.Join(t.TempDir(), "config.json")
	data := []byte(`{"worker":{"name":"demo-worker","retry_initial_backoff_seconds":10,"retry_max_backoff_seconds":2}}`)
	if err := os.WriteFile(configPath, data, 0o644); err != nil {
		t.Fatal(err)
	}
	t.Setenv("CONFIG_FILE", configPath)

	if _, err := Load(); err == nil {
		t.Fatal("expected retry backoff range validation to fail")
	}
}
