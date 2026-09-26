package config

import (
	"bytes"
	"errors"
	"io"
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
	Environment string          `yaml:"environment"`
	AdminAddr   string          `yaml:"admin_addr"`
	LogLevel    string          `yaml:"log_level"`
	Request     RequestConfig   `yaml:"request"`
	Database    ComponentConfig `yaml:"database"`
	Cache       ComponentConfig `yaml:"cache"`
	Service     ServiceConfig   `yaml:"service"`
	Server      ServerConfig    `yaml:"server"`
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
		return Config{}, errors.New("configuration file cannot be read")
	}

	var cfg Config
	decoder := yaml.NewDecoder(bytes.NewReader(data))
	decoder.KnownFields(true)
	if err := decoder.Decode(&cfg); err != nil {
		return Config{}, errors.New("invalid configuration YAML")
	}
	if value, set := os.LookupEnv("SERVICE_NAME"); set {
		cfg.Service.Name = value
	}
	if value, set := os.LookupEnv("HTTP_PORT"); set {
		cfg.Service.Port = value
	}

	var extra any
	if err := decoder.Decode(&extra); err != io.EOF {
		return Config{}, errors.New("expected one configuration document")
	}
	if cfg.Service.Name == "" {
		return Config{}, errors.New("service.name is required")
	}

	if cfg.Service.Port == "" {
		cfg.Service.Port = "{{HTTP_PORT}}"
	}
	port, err := strconv.Atoi(cfg.Service.Port)
	if err != nil || port < 1 || port > 65535 {
		return Config{}, errors.New("service.port must be between 1 and 65535")
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
	if err := cfg.validateCommon(); err != nil {
		return Config{}, err
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
