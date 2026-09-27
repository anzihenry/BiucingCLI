package config

import (
	"errors"
	"io"
	"log/slog"
	"net"
	"net/url"
	"os"
	"strconv"
	"strings"
)

type RequestConfig struct {
	MaxBytes       int64 `yaml:"max_bytes"`
	Concurrent     int   `yaml:"concurrent"`
	TimeoutSeconds int   `yaml:"timeout_seconds"`
}

func secret(name, fallback string) (string, error) {
	value, set := os.LookupEnv(name)
	path, fileSet := os.LookupEnv(name + "_FILE")
	if set && fileSet {
		return "", errors.New(name + " and " + name + "_FILE are mutually exclusive")
	}
	if fileSet {
		if path == "" {
			return "", errors.New(name + "_FILE must name a file")
		}
		f, err := os.Open(path)
		if err != nil {
			return "", errors.New(name + "_FILE cannot be read")
		}
		defer func() { _ = f.Close() }()
		data, err := io.ReadAll(io.LimitReader(f, 65537))
		if err != nil || len(data) > 65536 {
			return "", errors.New(name + "_FILE exceeds limit or cannot be read")
		}
		value = strings.TrimSuffix(strings.TrimSuffix(string(data), "\n"), "\r")
		if value == "" {
			return "", errors.New(name + "_FILE is empty")
		}
		return value, nil
	}
	if set {
		return value, nil
	}
	return fallback, nil
}
func validPort(value string) bool {
	n, err := strconv.Atoi(value)
	return err == nil && n > 0 && n <= 65535
}
func (cfg *Config) validateCommon() error {
	if env, set := os.LookupEnv("APP_ENV"); set {
		cfg.Environment = env
	}
	if cfg.Environment == "" {
		cfg.Environment = "development"
	}
	if cfg.Environment != "development" && cfg.Environment != "production" && cfg.Environment != "test" {
		return errors.New("invalid environment")
	}
	if v, set := os.LookupEnv("ADMIN_ADDR"); set {
		cfg.AdminAddr = v
	}
	if cfg.AdminAddr == "" {
		cfg.AdminAddr = "127.0.0.1:9000"
	}
	host, port, err := net.SplitHostPort(cfg.AdminAddr)
	if err != nil || !validPort(port) || net.ParseIP(host) == nil {
		return errors.New("admin_addr requires an IP address and valid port")
	}
	if cfg.LogLevel == "" {
		cfg.LogLevel = "INFO"
	}
	if v, set := os.LookupEnv("LOG_LEVEL"); set {
		cfg.LogLevel = v
	}
	var level slog.Level
	if level.UnmarshalText([]byte(cfg.LogLevel)) != nil {
		return errors.New("invalid log_level")
	}
	if cfg.Request.MaxBytes == 0 {
		cfg.Request.MaxBytes = 1048576
	}
	if cfg.Request.Concurrent == 0 {
		cfg.Request.Concurrent = 64
	}
	if cfg.Request.TimeoutSeconds == 0 {
		cfg.Request.TimeoutSeconds = 5
	}
	if cfg.Request.MaxBytes < 1 || cfg.Request.MaxBytes > 16777216 || cfg.Request.Concurrent < 1 || cfg.Request.Concurrent > 10000 || cfg.Request.TimeoutSeconds < 1 || cfg.Request.TimeoutSeconds > 300 {
		return errors.New("request limits out of range")
	}
	if cfg.Request.TimeoutSeconds >= cfg.Server.WriteTimeoutSeconds {
		return errors.New("request timeout must be shorter than server write timeout")
	}
	for _, item := range []struct {
		name      string
		component *ComponentConfig
	}{{"DATABASE_DSN", &cfg.Database}, {"CACHE_DSN", &cfg.Cache}} {
		value, err := secret(item.name, item.component.DSN)
		if err != nil {
			return err
		}
		item.component.DSN = value
		if item.component.Driver == "none" {
			item.component.DSN = ""
			continue
		}
		parsed, err := url.Parse(value)
		if err != nil || parsed.Host == "" {
			return errors.New(item.name + " must be a valid component URL")
		}
		if item.name == "DATABASE_DSN" && parsed.Scheme != "postgres" && parsed.Scheme != "postgresql" {
			return errors.New("invalid database URL scheme")
		}
		if item.name == "CACHE_DSN" && parsed.Scheme != "redis" && parsed.Scheme != "rediss" {
			return errors.New("invalid cache URL scheme")
		}
		if cfg.Environment == "production" {
			_, direct := os.LookupEnv(item.name)
			_, file := os.LookupEnv(item.name + "_FILE")
			if !direct && !file {
				return errors.New(item.name + " must be explicitly supplied in production")
			}
			if item.name == "DATABASE_DSN" {
				password, _ := parsed.User.Password()
				if (password == "postgres" || strings.HasPrefix(password, "local-")) || (parsed.Query().Get("sslmode") != "verify-full") {
					return errors.New("production database requires non-development credentials and sslmode=verify-full")
				}
			} else if parsed.Scheme != "rediss" {
				return errors.New("production cache requires TLS")
			}
		}
	}
	return nil
}

// Deliberate allowlist: never serialize Config itself into logs or diagnostics.
func (cfg Config) Summary() map[string]any {
	return map[string]any{"environment": cfg.Environment, "admin_addr": cfg.AdminAddr, "database": cfg.Database.Driver, "cache": cfg.Cache.Driver, "log_level": cfg.LogLevel, "max_bytes": cfg.Request.MaxBytes, "concurrent": cfg.Request.Concurrent}
}
