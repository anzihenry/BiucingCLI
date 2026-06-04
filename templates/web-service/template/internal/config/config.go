package config

import (
	"errors"
	"os"

	"gopkg.in/yaml.v3"
)

const defaultConfigFile = "configs/config.yaml"

type Config struct {
	Service ServiceConfig `yaml:"service"`
}

type ServiceConfig struct {
	Name string `yaml:"name"`
	Port string `yaml:"port"`
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

	return cfg, nil
}
