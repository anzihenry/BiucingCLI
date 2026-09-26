package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadDefaultConfig(t *testing.T) {
	unset(t, "DATABASE_DSN")
	unset(t, "CACHE_DSN")
	t.Setenv("CONFIG_FILE", "")
	tempDir := t.TempDir()
	configDir := filepath.Join(tempDir, "configs")
	if err := os.MkdirAll(configDir, 0o755); err != nil {
		t.Fatal(err)
	}

	configFile := filepath.Join(configDir, "config.yaml")
	configData := []byte("service:\n  name: test-service\n  port: 8080\n")
	if err := os.WriteFile(configFile, configData, 0o644); err != nil {
		t.Fatal(err)
	}

	currentDir, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}

	if err := os.Chdir(tempDir); err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() {
		if chdirErr := os.Chdir(currentDir); chdirErr != nil {
			t.Fatalf("restore working directory: %v", chdirErr)
		}
	})

	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}

	if cfg.Service.Name != "test-service" {
		t.Fatalf("expected service name %q, got %q", "test-service", cfg.Service.Name)
	}

	if cfg.Service.Port != "8080" {
		t.Fatalf("expected service port %q, got %q", "8080", cfg.Service.Port)
	}
	if cfg.Server.ShutdownTimeoutSeconds != 10 {
		t.Fatalf("expected default shutdown timeout %d, got %d", 10, cfg.Server.ShutdownTimeoutSeconds)
	}
}

func TestLoadRejectsNegativeTimeout(t *testing.T) {
	configFile := filepath.Join(t.TempDir(), "invalid.yaml")
	configData := []byte("service:\n  name: invalid-service\nserver:\n  shutdown_timeout_seconds: -1\n")
	if err := os.WriteFile(configFile, configData, 0o644); err != nil {
		t.Fatal(err)
	}
	t.Setenv("CONFIG_FILE", configFile)

	if _, err := Load(); err == nil {
		t.Fatal("expected a negative timeout to fail validation")
	}
}

func TestLoadUsesConfigFileOverride(t *testing.T) {
	tempDir := t.TempDir()
	configFile := filepath.Join(tempDir, "override.yaml")
	configData := []byte("service:\n  name: override-service\n  port: 9090\n")
	if err := os.WriteFile(configFile, configData, 0o644); err != nil {
		t.Fatal(err)
	}

	t.Setenv("CONFIG_FILE", configFile)

	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}

	if cfg.Service.Name != "override-service" {
		t.Fatalf("expected service name %q, got %q", "override-service", cfg.Service.Name)
	}

	if cfg.Service.Port != "9090" {
		t.Fatalf("expected service port %q, got %q", "9090", cfg.Service.Port)
	}
}

func TestLoadUsesDeploymentOverrides(t *testing.T) {
	configFile := filepath.Join(t.TempDir(), "config.yaml")
	if err := os.WriteFile(configFile, []byte("service:\n  name: local\n  port: 8080\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	t.Setenv("CONFIG_FILE", configFile)
	t.Setenv("SERVICE_NAME", "deployed")
	t.Setenv("HTTP_PORT", "9090")
	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}
	if cfg.Service.Name != "deployed" || cfg.Service.Port != "9090" {
		t.Fatalf("unexpected deployment overrides: %+v", cfg.Service)
	}
}

func TestLoadRejectsInvalidPort(t *testing.T) {
	configFile := filepath.Join(t.TempDir(), "config.yaml")
	if err := os.WriteFile(configFile, []byte("service:\n  name: local\n  port: 8080\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	t.Setenv("CONFIG_FILE", configFile)
	t.Setenv("HTTP_PORT", "invalid")
	if _, err := Load(); err == nil {
		t.Fatal("expected invalid HTTP_PORT to fail")
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
