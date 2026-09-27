package config

import (
	"errors"
	"net/url"
	"os"
	"strings"
)

func MigrationDSN() (string, error) {
	switch os.Getenv("APP_ENV") {
	case "", "development", "test", "production":
	default:
		return "", errors.New("invalid migration environment")
	}
	dsn, err := secret("MIGRATION_DSN", "")
	if err != nil {
		return "", err
	}
	if dsn == "" {
		return "", errors.New("MIGRATION_DSN or MIGRATION_DSN_FILE is required")
	}
	u, err := url.Parse(dsn)
	if err != nil || u.User == nil {
		return "", errors.New("invalid migration configuration")
	}
	if os.Getenv("APP_ENV") == "production" {
		pass, _ := u.User.Password()
		if u.Query().Get("sslmode") != "verify-full" || pass == "postgres" || strings.HasPrefix(pass, "local-") {
			return "", errors.New("unsafe production migration configuration")
		}
	}
	return dsn, nil
}
