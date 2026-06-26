package runtime

import (
	"context"
	"io"
	"log"
	"sync"
	"testing"
	"time"
)

type recordingExecutor struct {
	mu    sync.Mutex
	calls int
}

func (executor *recordingExecutor) Execute(context.Context) (string, error) {
	executor.mu.Lock()
	defer executor.mu.Unlock()
	executor.calls++
	return "heartbeat completed", nil
}

func (executor *recordingExecutor) Count() int {
	executor.mu.Lock()
	defer executor.mu.Unlock()
	return executor.calls
}

func TestRunOneshotExecutesOnce(t *testing.T) {
	executor := &recordingExecutor{}
	runner := New(Options{
		Name:            "demo-worker",
		Mode:            "oneshot",
		TickInterval:    10 * time.Millisecond,
		ShutdownTimeout: time.Second,
		Executor:        executor,
		Logger:          log.New(io.Discard, "", 0),
	})

	if err := runner.Run(context.Background()); err != nil {
		t.Fatal(err)
	}

	if executor.Count() != 1 {
		t.Fatalf("expected executor to run once, got %d", executor.Count())
	}
}

func TestRunScheduledExecutesMoreThanOnce(t *testing.T) {
	executor := &recordingExecutor{}
	runner := New(Options{
		Name:            "demo-worker",
		Mode:            "scheduled",
		TickInterval:    10 * time.Millisecond,
		ShutdownTimeout: time.Second,
		Executor:        executor,
		Logger:          log.New(io.Discard, "", 0),
	})

	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan error, 1)
	go func() {
		done <- runner.Run(ctx)
	}()

	time.Sleep(35 * time.Millisecond)
	cancel()

	if err := <-done; err != nil {
		t.Fatal(err)
	}

	if executor.Count() < 2 {
		t.Fatalf("expected executor to run at least twice, got %d", executor.Count())
	}
}
