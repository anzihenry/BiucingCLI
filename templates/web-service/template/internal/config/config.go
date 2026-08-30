package config

import (
	"errors"
	"os"

	"gopkg.in/yaml.v3"
)

const defaultConfigFile = "configs/config.yaml"

type Config struct {
	Service ServiceConfig `yaml:"service"`
	Server  ServerConfig  `yaml:"server"`
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

	if cfg.Service.Name == "" {
		return Config{}, errors.New("service.name is required")
	}

	if cfg.Service.Port == "" {
		cfg.Service.Port = "{{HTTP_PORT}}"
	}

	if err := cfg.Server.applyDefaults(); err != nil {
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
		if *item.value < 0 {
			return errors.New(item.name + " must be greater than zero")
		}
		if *item.value == 0 {
			*item.value = item.defaultValue
		}
	}

	return nil
}
