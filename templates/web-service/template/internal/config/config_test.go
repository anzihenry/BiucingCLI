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
