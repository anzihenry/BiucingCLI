package config

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func unset(t *testing.T, name string) {
	t.Helper()
	value, set := os.LookupEnv(name)
	if err := os.Unsetenv(name); err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() {
		if set {
			_ = os.Setenv(name, value)
		} else {
			_ = os.Unsetenv(name)
		}
	})
}
func TestFileSecretConflictAndMissingFile(t *testing.T) {
	path := filepath.Join(t.TempDir(), "secret")
	if err := os.WriteFile(path, []byte("private-value\n"), 0600); err != nil {
		t.Fatal(err)
	}
	unset(t, "DATABASE_DSN")
	t.Setenv("DATABASE_DSN_FILE", path)
	value, err := secret("DATABASE_DSN", "")
	if err != nil || value != "private-value" {
		t.Fatal("file secret failed")
	}
	t.Setenv("DATABASE_DSN", "")
	if _, err := secret("DATABASE_DSN", ""); err == nil {
		t.Fatal("empty direct variable must conflict with file")
	}
	unset(t, "DATABASE_DSN")
	t.Setenv("DATABASE_DSN_FILE", path+"-missing")
	if _, err := secret("DATABASE_DSN", ""); err == nil || strings.Contains(err.Error(), path) {
		t.Fatal("missing file must return sanitized error")
	}
}
func TestProductionCannotUseDevelopmentFallback(t *testing.T) {
	unset(t, "DATABASE_DSN")
	unset(t, "DATABASE_DSN_FILE")
	unset(t, "APP_ENV")
	cfg := Config{Environment: "production", Database: ComponentConfig{Driver: "postgres", DSN: "postgres://postgres:postgres@db/test?sslmode=disable"}, Cache: ComponentConfig{Driver: "none"}, Server: ServerConfig{WriteTimeoutSeconds: 15}}
	if cfg.validateCommon() == nil {
		t.Fatal("accepted development credentials")
	}
	t.Setenv("DATABASE_DSN", "postgres://app:strong-value@db/test?sslmode=verify-full")
	if err := cfg.validateCommon(); err != nil {
		t.Fatal(err)
	}
	for _, v := range cfg.Summary() {
		if s, ok := v.(string); ok && strings.Contains(s, "strong-value") {
			t.Fatal("diagnostic leaked secret")
		}
	}
}

func TestRejectsMultipleConfigurationDocuments(t *testing.T) {
	path := filepath.Join(t.TempDir(), "multi.yaml")
	if err := os.WriteFile(path, []byte("service:\n  name: valid\n---\nservice:\n  name: hidden\n"), 0600); err != nil {
		t.Fatal(err)
	}
	t.Setenv("CONFIG_FILE", path)
	if _, err := Load(); err == nil {
		t.Fatal("multiple YAML documents accepted")
	}
}
