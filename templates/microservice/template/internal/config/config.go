package config

import (
	"errors"
	"os"

	"gopkg.in/yaml.v3"
)

const defaultConfigFile = "configs/config.yaml"

type Config struct {
	Service   ServiceConfig   `yaml:"service"`
	Telemetry TelemetryConfig `yaml:"telemetry"`
	Store     StoreConfig     `yaml:"store"`
}

type ServiceConfig struct {
	Name     string `yaml:"name"`
	HTTPPort string `yaml:"http_port"`
	GRPCPort string `yaml:"grpc_port"`
}

type TelemetryConfig struct {
	OTLPHTTPEndpoint string `yaml:"otlp_http_endpoint"`
}

type StoreConfig struct {
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
	if cfg.Store.Driver == "" {
		cfg.Store.Driver = "{{DEPENDENCY_STORE}}"
	}
	if cfg.Store.DSN == "" {
		cfg.Store.DSN = "{{DEPENDENCY_STORE_DSN}}"
	}
	if override := os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT"); override != "" {
		cfg.Telemetry.OTLPHTTPEndpoint = override
	}
	if cfg.Telemetry.OTLPHTTPEndpoint == "" {
		cfg.Telemetry.OTLPHTTPEndpoint = "{{OTEL_EXPORTER_ENDPOINT}}"
	}
	if override := os.Getenv("STORE_DSN"); override != "" {
		cfg.Store.DSN = override
	}

	return cfg, nil
}
