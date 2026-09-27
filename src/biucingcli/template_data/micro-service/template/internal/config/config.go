package config

import (
	"bytes"
	"errors"
	"io"
	"os"
	"strings"

	"gopkg.in/yaml.v3"
	"{{MODULE_NAME}}/internal/database"
	"{{MODULE_NAME}}/internal/security"
)

const defaultConfigFile = "configs/config.yaml"

type Config struct {
	Workload    security.WorkloadConfig `yaml:"workload"`
	Data        database.Config         `yaml:"data"`
	Environment string                  `yaml:"environment"`
	AdminAddr   string                  `yaml:"admin_addr"`
	LogLevel    string                  `yaml:"log_level"`
	Request     RequestConfig           `yaml:"request"`
	Service     ServiceConfig           `yaml:"service"`
	Server      ServerConfig            `yaml:"server"`
	Telemetry   TelemetryConfig         `yaml:"telemetry"`
	Database    ComponentConfig         `yaml:"database"`
	Cache       ComponentConfig         `yaml:"cache"`
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
		return Config{}, errors.New("configuration file cannot be read")
	}

	var cfg Config
	decoder := yaml.NewDecoder(bytes.NewReader(data))
	decoder.KnownFields(true)
	if err := decoder.Decode(&cfg); err != nil {
		return Config{}, errors.New("invalid configuration YAML")
	}

	var extra any
	if err := decoder.Decode(&extra); err != io.EOF {
		return Config{}, errors.New("expected one configuration document")
	}
	if cfg.Service.Name == "" {
		return Config{}, errors.New("service.name is required")
	}
	if value, set := os.LookupEnv("HTTP_PORT"); set {
		cfg.Service.HTTPPort = value
	}
	if value, set := os.LookupEnv("GRPC_PORT"); set {
		cfg.Service.GRPCPort = value
	}
	if cfg.Service.HTTPPort == "" {
		cfg.Service.HTTPPort = "{{HTTP_PORT}}"
	}
	if cfg.Service.GRPCPort == "" {
		cfg.Service.GRPCPort = "{{GRPC_PORT}}"
	}
	if !validPort(cfg.Service.HTTPPort) || !validPort(cfg.Service.GRPCPort) {
		return Config{}, errors.New("invalid service port")
	}
	if cfg.Service.HTTPPort == cfg.Service.GRPCPort {
		return Config{}, errors.New("service ports must differ")
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
	if cfg.Data.MaxConnections == 0 {
		cfg.Data.MaxConnections = 10
	}
	if cfg.Data.QueryTimeoutSeconds == 0 {
		cfg.Data.QueryTimeoutSeconds = 3
	}
	if err := cfg.Data.Validate(); err != nil {
		return Config{}, err
	}
	if err := cfg.validateCommon(); err != nil {
		return Config{}, err
	}
	if cfg.Environment == "production" {
		for _, identities := range cfg.Workload.Methods {
			for _, identity := range identities {
				if strings.HasPrefix(identity, "spiffe://local/") {
					return Config{}, errors.New("local workload identity is forbidden in production")
				}
			}
		}
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
		if *item.value < 0 || *item.value > 3600 {
			return errors.New(item.name + " must be between 1 and 3600 seconds")
		}
		if *item.value == 0 {
			*item.value = item.defaultValue
		}
	}

	return nil
}
