package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/runtime"
	"{{MODULE_NAME}}/internal/task"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("load config: %v", err)
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	logger := log.New(os.Stdout, "", log.LstdFlags)
	runner := runtime.New(runtime.Options{
		Name:            cfg.Worker.Name,
		Mode:            cfg.Worker.RunMode,
		TickInterval:    time.Duration(cfg.Worker.TickIntervalSeconds) * time.Second,
		ShutdownTimeout: time.Duration(cfg.Worker.ShutdownTimeoutSeconds) * time.Second,
		Executor:        task.NewHeartbeatTask(cfg.Worker.Name),
		Logger:          logger,
	})

	if err := runner.Run(ctx); err != nil {
		log.Fatalf("run worker: %v", err)
	}
}
