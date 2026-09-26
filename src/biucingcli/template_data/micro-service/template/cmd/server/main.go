package main

import (
	"context"
	"encoding/json"
	"os"
	"os/signal"
	"syscall"
	"time"
	"{{MODULE_NAME}}/internal/app"
	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/observability"
	serverruntime "{{MODULE_NAME}}/internal/runtime"
)

func main() { os.Exit(execute()) }
func execute() int {
	logger := observability.New(os.Stdout, "INFO")
	if len(os.Args) == 3 && os.Args[1] == "healthcheck" {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel()
		if serverruntime.CheckHealth(ctx, os.Args[2]) != nil {
			return 1
		}
		return 0
	}
	cfg, err := config.Load()
	if err != nil {
		logger.Error("configuration rejected", "code", "invalid_config", "reason", err.Error())
		return 1
	}
	if len(os.Args) == 2 && os.Args[1] == "check-config" {
		if json.NewEncoder(os.Stdout).Encode(cfg.Summary()) != nil {
			return 1
		}
		return 0
	}
	if len(os.Args) > 1 {
		logger.Error("unknown command")
		return 2
	}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	if app.Run(ctx, cfg) != nil {
		logger.Error("service stopped with error", "code", "runtime_failure")
		return 1
	}
	return 0
}
