package config

import (
	"strings"
	"testing"
)

func TestMigrationSecretGuards(t *testing.T) {
	unset(t, "MIGRATION_DSN")
	unset(t, "MIGRATION_DSN_FILE")
	if _, err := MigrationDSN(); err == nil {
		t.Fatal("missing migration credential accepted")
	}
	t.Setenv("APP_ENV", "production")
	for _, dsn := range []string{"postgres://user:local-migrate-only@db/service?sslmode=verify-full", "postgres://user:fixture-private@db/service?sslmode=disable"} {
		t.Setenv("MIGRATION_DSN", dsn)
		if _, err := MigrationDSN(); err == nil || strings.Contains(err.Error(), "fixture-private") {
			t.Fatal("unsafe migration credential handling")
		}
	}
	t.Setenv("MIGRATION_DSN", "postgres://user:fixture-private@db/service?sslmode=verify-full")
	if _, err := MigrationDSN(); err != nil {
		t.Fatal(err)
	}
}
