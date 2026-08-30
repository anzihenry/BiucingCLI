package runtime

import (
	"context"
	"errors"
	"io"
	"log"
	"strings"
	"sync"
	"testing"
	"time"
)

var errTask = errors.New("task failed")

type executionResult struct {
	summary string
	err     error
}

type scriptedExecutor struct {
	mu      sync.Mutex
	results []executionResult
	calls   int
	execute func(context.Context) (string, error)
}

func (executor *scriptedExecutor) Execute(ctx context.Context) (string, error) {
	if executor.execute != nil {
		return executor.execute(ctx)
	}
	executor.mu.Lock()
	defer executor.mu.Unlock()
	executor.calls++
	result := executor.results[executor.calls-1]
	return result.summary, result.err
}

func (executor *scriptedExecutor) Count() int {
	executor.mu.Lock()
	defer executor.mu.Unlock()
	return executor.calls
}

type clockRequest struct {
	delay time.Duration
	fire  chan time.Time
}

type fakeClock struct {
	requests chan clockRequest
}

func newFakeClock() *fakeClock {
	return &fakeClock{requests: make(chan clockRequest, 16)}
}

func (clock *fakeClock) After(delay time.Duration) <-chan time.Time {
	fire := make(chan time.Time, 1)
	clock.requests <- clockRequest{delay: delay, fire: fire}
	return fire
}

func (clock *fakeClock) Next(t *testing.T) clockRequest {
	t.Helper()
	select {
	case request := <-clock.requests:
		return request
	case <-time.After(time.Second):
		t.Fatal("runner did not request a timer")
		return clockRequest{}
	}
}

func fire(request clockRequest) {
	request.fire <- time.Time{}
}

func newTestRunner(mode string, executor Executor, clock Clock) *Runner {
	return New(Options{
		Name:            "demo-worker",
		Mode:            mode,
		TickInterval:    10 * time.Second,
		ShutdownTimeout: 5 * time.Second,
		MaxAttempts:     3,
		InitialBackoff:  time.Second,
		MaxBackoff:      2 * time.Second,
		Executor:        executor,
		Logger:          log.New(io.Discard, "", 0),
		Clock:           clock,
	})
}

func TestRunOneshotRetriesWithCappedExponentialBackoff(t *testing.T) {
	executor := &scriptedExecutor{results: []executionResult{
		{err: errTask}, {err: errTask}, {summary: "heartbeat completed"},
	}}
	clock := newFakeClock()
	done := make(chan error, 1)
	go func() { done <- newTestRunner("oneshot", executor, clock).Run(context.Background()) }()

	firstBackoff := clock.Next(t)
	if firstBackoff.delay != time.Second {
		t.Fatalf("expected first backoff %s, got %s", time.Second, firstBackoff.delay)
	}
	fire(firstBackoff)
	secondBackoff := clock.Next(t)
	if secondBackoff.delay != 2*time.Second {
		t.Fatalf("expected capped second backoff %s, got %s", 2*time.Second, secondBackoff.delay)
	}
	fire(secondBackoff)

	if err := <-done; err != nil {
		t.Fatal(err)
	}
	if executor.Count() != 3 {
		t.Fatalf("expected three attempts, got %d", executor.Count())
	}
}

func TestRunOneshotReturnsFinalErrorAfterRetryExhaustion(t *testing.T) {
	executor := &scriptedExecutor{results: []executionResult{{err: errTask}, {err: errTask}, {err: errTask}}}
	clock := newFakeClock()
	done := make(chan error, 1)
	go func() { done <- newTestRunner("oneshot", executor, clock).Run(context.Background()) }()

	fire(clock.Next(t))
	fire(clock.Next(t))
	err := <-done
	if !errors.Is(err, errTask) || !strings.Contains(err.Error(), "after 3 attempt(s)") {
		t.Fatalf("expected exhausted retry error, got %v", err)
	}
}

func TestRunScheduledContinuesAfterRetryExhaustion(t *testing.T) {
	executor := &scriptedExecutor{results: []executionResult{
		{err: errTask}, {err: errTask}, {err: errTask}, {summary: "next cycle completed"},
	}}
	clock := newFakeClock()
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan error, 1)
	go func() { done <- newTestRunner("scheduled", executor, clock).Run(ctx) }()

	fire(clock.Next(t))
	fire(clock.Next(t))
	scheduleDelay := clock.Next(t)
	if scheduleDelay.delay != 10*time.Second {
		t.Fatalf("expected schedule delay %s, got %s", 10*time.Second, scheduleDelay.delay)
	}
	fire(scheduleDelay)
	nextSchedule := clock.Next(t)
	if nextSchedule.delay != 10*time.Second {
		t.Fatalf("expected next schedule delay %s, got %s", 10*time.Second, nextSchedule.delay)
	}
	cancel()
	if err := <-done; err != nil {
		t.Fatal(err)
	}
	if executor.Count() != 4 {
		t.Fatalf("expected four attempts across two cycles, got %d", executor.Count())
	}
}

func TestCancellationInterruptsRetryBackoff(t *testing.T) {
	executor := &scriptedExecutor{results: []executionResult{{err: errTask}}}
	clock := newFakeClock()
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan error, 1)
	go func() { done <- newTestRunner("oneshot", executor, clock).Run(ctx) }()

	request := clock.Next(t)
	if request.delay != time.Second {
		t.Fatalf("expected retry backoff %s, got %s", time.Second, request.delay)
	}
	cancel()
	if err := <-done; err != nil {
		t.Fatal(err)
	}
	if executor.Count() != 1 {
		t.Fatalf("expected cancellation to prevent another attempt, got %d", executor.Count())
	}
}

func TestShutdownTimeoutIsDeterministic(t *testing.T) {
	releaseExecutor := make(chan struct{})
	defer close(releaseExecutor)
	executor := &scriptedExecutor{execute: func(ctx context.Context) (string, error) {
		<-ctx.Done()
		<-releaseExecutor
		return "", ctx.Err()
	}}
	clock := newFakeClock()
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan error, 1)
	go func() { done <- newTestRunner("oneshot", executor, clock).Run(ctx) }()

	cancel()
	shutdownTimer := clock.Next(t)
	if shutdownTimer.delay != 5*time.Second {
		t.Fatalf("expected shutdown timeout %s, got %s", 5*time.Second, shutdownTimer.delay)
	}
	fire(shutdownTimer)
	if err := <-done; !errors.Is(err, ErrShutdownTimeout) {
		t.Fatalf("expected shutdown timeout, got %v", err)
	}
}

func TestNextBackoffCapsWithoutOverflow(t *testing.T) {
	if actual := nextBackoff(time.Second, 2*time.Second); actual != 2*time.Second {
		t.Fatalf("expected doubled backoff, got %s", actual)
	}
	if actual := nextBackoff(2*time.Second, 2*time.Second); actual != 2*time.Second {
		t.Fatalf("expected capped backoff, got %s", actual)
	}
}
