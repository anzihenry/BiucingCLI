package config

import (
	"errors"
	"os"

	"gopkg.in/yaml.v3"
)

const defaultConfigFile = "configs/config.yaml"

type Config struct {
	Service   ServiceConfig   `yaml:"service"`
	Server    ServerConfig    `yaml:"server"`
	Telemetry TelemetryConfig `yaml:"telemetry"`
	Database  ComponentConfig `yaml:"database"`
	Cache     ComponentConfig `yaml:"cache"`
}

type ServerConfig struct {
	ReadTimeoutSeconds       int `yaml:"read_timeout_seconds"`
	ReadHeaderTimeoutSeconds int `yaml:"read_header_timeout_seconds"`
	WriteTimeoutSeconds      int `yaml:"write_timeout_seconds"`
	IdleTimeoutSeconds       int `yaml:"idle_timeout_seconds"`
	ShutdownTimeoutSeconds   int `yaml:"shutdown_timeout_seconds"`
}

type ServiceConfig struct {
	Name     string `yaml:"name"`
	HTTPPort string `yaml:"http_port"`
	GRPCPort string `yaml:"grpc_port"`
}

type TelemetryConfig struct {
	OTLPHTTPEndpoint string `yaml:"otlp_http_endpoint"`
}

type ComponentConfig struct {
	Driver string `yaml:"driver"`
	DSN    string `yaml:"dsn"`
}

func Load() (Config, error) {
	configFile := os.Getenv("CONFIG_FILE")
	if configFile == "" {
		configFile = defaultConfigFile
	}

	data, err := os.ReadFile(configFile)
	if err != nil {
		return Config{}, err
	}

	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return Config{}, err
	}

	if cfg.Service.Name == "" {
		return Config{}, errors.New("service.name is required")
	}
	if cfg.Service.HTTPPort == "" {
		cfg.Service.HTTPPort = "{{HTTP_PORT}}"
	}
	if cfg.Service.GRPCPort == "" {
		cfg.Service.GRPCPort = "{{GRPC_PORT}}"
	}
	if err := cfg.Server.applyDefaults(); err != nil {
		return Config{}, err
	}
	if override := os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT"); override != "" {
		cfg.Telemetry.OTLPHTTPEndpoint = override
	}
	if cfg.Telemetry.OTLPHTTPEndpoint == "" {
		cfg.Telemetry.OTLPHTTPEndpoint = "{{OTEL_EXPORTER_ENDPOINT_JSON}}"
	}

	if cfg.Database.Driver == "" {
		cfg.Database.Driver = "{{DATABASE}}"
	}
	if cfg.Cache.Driver == "" {
		cfg.Cache.Driver = "{{CACHE}}"
	}
	if cfg.Database.DSN == "" {
		cfg.Database.DSN = "{{DATABASE_DSN}}"
	}
	if cfg.Cache.DSN == "" {
		cfg.Cache.DSN = "{{CACHE_DSN}}"
	}
	if value, set := os.LookupEnv("DATABASE_DSN"); set {
		cfg.Database.DSN = value
	}
	if value, set := os.LookupEnv("CACHE_DSN"); set {
		cfg.Cache.DSN = value
	}
	if cfg.Database.Driver != "none" && cfg.Database.Driver != "postgres" {
		return Config{}, errors.New("unsupported database.driver")
	}
	if cfg.Cache.Driver != "none" && cfg.Cache.Driver != "redis" {
		return Config{}, errors.New("unsupported cache.driver")
	}
	if cfg.Database.Driver == "none" {
		cfg.Database.DSN = ""
	}
	if cfg.Cache.Driver == "none" {
		cfg.Cache.DSN = ""
	}
	return cfg, nil
}

func (cfg *ServerConfig) applyDefaults() error {
	values := []struct {
		name         string
		value        *int
		defaultValue int
	}{
		{"server.read_timeout_seconds", &cfg.ReadTimeoutSeconds, 5},
		{"server.read_header_timeout_seconds", &cfg.ReadHeaderTimeoutSeconds, 5},
		{"server.write_timeout_seconds", &cfg.WriteTimeoutSeconds, 15},
		{"server.idle_timeout_seconds", &cfg.IdleTimeoutSeconds, 60},
		{"server.shutdown_timeout_seconds", &cfg.ShutdownTimeoutSeconds, 10},
	}

	for _, item := range values {
		if *item.value < 0 {
			return errors.New(item.name + " must be greater than zero")
		}
		if *item.value == 0 {
			*item.value = item.defaultValue
		}
	}

	return nil
}
