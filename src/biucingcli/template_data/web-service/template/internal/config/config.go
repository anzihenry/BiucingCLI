package config

import (
	"errors"
	"fmt"
	"os"
	"strconv"

	"gopkg.in/yaml.v3"
)

const defaultConfigFile = "configs/config.yaml"

type ComponentConfig struct {
	Driver string `yaml:"driver"`
	DSN    string `yaml:"dsn"`
}

type Config struct {
	Database ComponentConfig `yaml:"database"`
	Cache    ComponentConfig `yaml:"cache"`
	Service  ServiceConfig   `yaml:"service"`
	Server   ServerConfig    `yaml:"server"`
}

type ServiceConfig struct {
	Name string `yaml:"name"`
	Port string `yaml:"port"`
}

type ServerConfig struct {
	ReadTimeoutSeconds       int `yaml:"read_timeout_seconds"`
	ReadHeaderTimeoutSeconds int `yaml:"read_header_timeout_seconds"`
	WriteTimeoutSeconds      int `yaml:"write_timeout_seconds"`
	IdleTimeoutSeconds       int `yaml:"idle_timeout_seconds"`
	ShutdownTimeoutSeconds   int `yaml:"shutdown_timeout_seconds"`
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
	if value, set := os.LookupEnv("SERVICE_NAME"); set {
		cfg.Service.Name = value
	}
	if value, set := os.LookupEnv("HTTP_PORT"); set {
		cfg.Service.Port = value
	}

	if cfg.Service.Name == "" {
		return Config{}, errors.New("service.name is required")
	}

	if cfg.Service.Port == "" {
		cfg.Service.Port = "{{HTTP_PORT}}"
	}
	port, err := strconv.Atoi(cfg.Service.Port)
	if err != nil || port < 1 || port > 65535 {
		return Config{}, fmt.Errorf("service.port must be between 1 and 65535: %q", cfg.Service.Port)
	}

	if err := cfg.Server.applyDefaults(); err != nil {
		return Config{}, err
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
