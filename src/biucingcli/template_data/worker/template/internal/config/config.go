package config

import (
	"encoding/json"
	"errors"
	"os"
	"strconv"
)

const defaultConfigFile = "configs/config.json"

type Config struct {
	Worker WorkerConfig `json:"worker"`
}

type WorkerConfig struct {
	Name                   string `json:"name"`
	RunMode                string `json:"run_mode"`
	TickIntervalSeconds    int    `json:"tick_interval_seconds"`
	ShutdownTimeoutSeconds int    `json:"shutdown_timeout_seconds"`
	RetryMaxAttempts       int    `json:"retry_max_attempts"`
	RetryInitialSeconds    int    `json:"retry_initial_backoff_seconds"`
	RetryMaxSeconds        int    `json:"retry_max_backoff_seconds"`
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
	if err := json.Unmarshal(data, &cfg); err != nil {
		return Config{}, err
	}

	applyStringOverride("WORKER_NAME", &cfg.Worker.Name)
	applyStringOverride("WORKER_RUN_MODE", &cfg.Worker.RunMode)
	if err := applyIntOverride("WORKER_TICK_INTERVAL_SECONDS", &cfg.Worker.TickIntervalSeconds); err != nil {
		return Config{}, err
	}
	if err := applyIntOverride("WORKER_SHUTDOWN_TIMEOUT_SECONDS", &cfg.Worker.ShutdownTimeoutSeconds); err != nil {
		return Config{}, err
	}
	if err := applyIntOverride("WORKER_RETRY_MAX_ATTEMPTS", &cfg.Worker.RetryMaxAttempts); err != nil {
		return Config{}, err
	}
	if err := applyIntOverride("WORKER_RETRY_INITIAL_BACKOFF_SECONDS", &cfg.Worker.RetryInitialSeconds); err != nil {
		return Config{}, err
	}
	if err := applyIntOverride("WORKER_RETRY_MAX_BACKOFF_SECONDS", &cfg.Worker.RetryMaxSeconds); err != nil {
		return Config{}, err
	}

	if cfg.Worker.Name == "" {
		return Config{}, errors.New("worker.name is required")
	}
	if cfg.Worker.RunMode == "" {
		cfg.Worker.RunMode = "{{RUN_MODE}}"
	}
	if cfg.Worker.RunMode != "scheduled" && cfg.Worker.RunMode != "oneshot" {
		return Config{}, errors.New("worker.run_mode must be one of: scheduled, oneshot")
	}
	if cfg.Worker.TickIntervalSeconds <= 0 {
		cfg.Worker.TickIntervalSeconds = {{TICK_INTERVAL_SECONDS}}
	}
	if cfg.Worker.ShutdownTimeoutSeconds <= 0 {
		cfg.Worker.ShutdownTimeoutSeconds = {{SHUTDOWN_TIMEOUT_SECONDS}}
	}
	if cfg.Worker.RetryMaxAttempts <= 0 {
		cfg.Worker.RetryMaxAttempts = 3
	}
	if cfg.Worker.RetryInitialSeconds <= 0 {
		cfg.Worker.RetryInitialSeconds = 1
	}
	if cfg.Worker.RetryMaxSeconds <= 0 {
		cfg.Worker.RetryMaxSeconds = 30
	}
	if cfg.Worker.RetryMaxSeconds < cfg.Worker.RetryInitialSeconds {
		return Config{}, errors.New("worker.retry_max_backoff_seconds must be greater than or equal to worker.retry_initial_backoff_seconds")
	}

	return cfg, nil
}

func applyStringOverride(envKey string, target *string) {
	if value := os.Getenv(envKey); value != "" {
		*target = value
	}
}

func applyIntOverride(envKey string, target *int) error {
	value := os.Getenv(envKey)
	if value == "" {
		return nil
	}
	parsed, err := strconv.Atoi(value)
	if err != nil {
		return errors.New(envKey + " must be an integer")
	}
	*target = parsed
	return nil
}
