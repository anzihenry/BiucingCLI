package tests

import (
	"context"
	"io"
	"log"
	"testing"
	"time"

	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/runtime"
	"{{MODULE_NAME}}/internal/task"
)

func TestWorkerConfigDefaults(t *testing.T) {
	t.Setenv("CONFIG_FILE", "../configs/config.json")

	cfg, err := config.Load()
	if err != nil {
		t.Fatal(err)
	}

	if cfg.Worker.Name != "{{WORKER_NAME}}" {
		t.Fatalf("expected worker name %q, got %q", "{{WORKER_NAME}}", cfg.Worker.Name)
	}
	if cfg.Worker.RunMode != "{{RUN_MODE}}" {
		t.Fatalf("expected run mode %q, got %q", "{{RUN_MODE}}", cfg.Worker.RunMode)
	}
}

func TestOneshotRunnerUsesHeartbeatTask(t *testing.T) {
	runner := runtime.New(runtime.Options{
		Name:            "{{WORKER_NAME}}",
		Mode:            "oneshot",
		TickInterval:    10 * time.Millisecond,
		ShutdownTimeout: time.Second,
		Executor:        task.NewHeartbeatTask("{{WORKER_NAME}}"),
		Logger:          log.New(io.Discard, "", 0),
	})

	if err := runner.Run(context.Background()); err != nil {
		t.Fatal(err)
	}
}
