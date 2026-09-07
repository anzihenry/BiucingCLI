package runtime

import (
	"context"
	"errors"
	"fmt"
	"io"
	"log"
	"time"
)

var ErrShutdownTimeout = errors.New("worker shutdown timed out")

type Executor interface {
	Execute(context.Context) (string, error)
}

type Clock interface {
	After(time.Duration) <-chan time.Time
}

type realClock struct{}

func (realClock) After(delay time.Duration) <-chan time.Time {
	return time.After(delay)
}

type Options struct {
	Name            string
	Mode            string
	TickInterval    time.Duration
	ShutdownTimeout time.Duration
	MaxAttempts     int
	InitialBackoff  time.Duration
	MaxBackoff      time.Duration
	Executor        Executor
	Logger          *log.Logger
	Clock           Clock
}

type Runner struct {
	name            string
	mode            string
	tickInterval    time.Duration
	shutdownTimeout time.Duration
	maxAttempts     int
	initialBackoff  time.Duration
	maxBackoff      time.Duration
	executor        Executor
	logger          *log.Logger
	clock           Clock
}

func New(options Options) *Runner {
	logger := options.Logger
	if logger == nil {
		logger = log.New(io.Discard, "", 0)
	}
	clock := options.Clock
	if clock == nil {
		clock = realClock{}
	}
	maxAttempts := options.MaxAttempts
	if maxAttempts <= 0 {
		maxAttempts = 1
	}
	initialBackoff := options.InitialBackoff
	if initialBackoff <= 0 {
		initialBackoff = time.Second
	}
	maxBackoff := options.MaxBackoff
	if maxBackoff < initialBackoff {
		maxBackoff = initialBackoff
	}
	return &Runner{
		name:            options.Name,
		mode:            options.Mode,
		tickInterval:    options.TickInterval,
		shutdownTimeout: options.ShutdownTimeout,
		maxAttempts:     maxAttempts,
		initialBackoff:  initialBackoff,
		maxBackoff:      maxBackoff,
		executor:        options.Executor,
		logger:          logger,
		clock:           clock,
	}
}

func (runner *Runner) Run(ctx context.Context) error {
	if runner.executor == nil {
		return errors.New("executor is required")
	}

	switch runner.mode {
	case "oneshot":
		err := runner.executeWithRetry(ctx)
		if ctx.Err() != nil && !errors.Is(err, ErrShutdownTimeout) {
			return nil
		}
		return err
	case "scheduled":
		return runner.runScheduled(ctx)
	default:
		return errors.New("unsupported worker mode: " + runner.mode)
	}
}

func (runner *Runner) runScheduled(ctx context.Context) error {
	for {
		if err := runner.executeWithRetry(ctx); err != nil {
			if ctx.Err() != nil {
				if errors.Is(err, ErrShutdownTimeout) {
					return err
				}
				runner.logger.Printf("%s: shutdown requested", runner.name)
				return nil
			}
			runner.logger.Printf("%s: execution cycle failed: %v", runner.name, err)
		}

		if err := runner.wait(ctx, runner.tickInterval); err != nil {
			runner.logger.Printf("%s: shutdown requested", runner.name)
			return nil
		}
	}
}

func (runner *Runner) executeWithRetry(ctx context.Context) error {
	backoff := runner.initialBackoff
	for attempt := 1; attempt <= runner.maxAttempts; attempt++ {
		summary, err := runner.executeAttempt(ctx)
		if err == nil {
			runner.logger.Printf("%s: %s", runner.name, summary)
			return nil
		}
		if ctx.Err() != nil || attempt == runner.maxAttempts {
			return fmt.Errorf("execution failed after %d attempt(s): %w", attempt, err)
		}

		runner.logger.Printf(
			"%s: attempt %d/%d failed: %v; retrying in %s",
			runner.name,
			attempt,
			runner.maxAttempts,
			err,
			backoff,
		)
		if err := runner.wait(ctx, backoff); err != nil {
			return err
		}
		backoff = nextBackoff(backoff, runner.maxBackoff)
	}
	return nil
}

func (runner *Runner) executeAttempt(ctx context.Context) (string, error) {
	type result struct {
		summary string
		err     error
	}

	executionCtx, cancelExecution := context.WithCancel(context.WithoutCancel(ctx))
	defer cancelExecution()
	resultChannel := make(chan result, 1)
	go func() {
		summary, err := runner.executor.Execute(executionCtx)
		resultChannel <- result{summary: summary, err: err}
	}()

	select {
	case executionResult := <-resultChannel:
		return executionResult.summary, executionResult.err
	case <-ctx.Done():
		cancelExecution()
	}

	select {
	case executionResult := <-resultChannel:
		return executionResult.summary, executionResult.err
	case <-runner.clock.After(runner.shutdownTimeout):
		return "", fmt.Errorf("%w after %s", ErrShutdownTimeout, runner.shutdownTimeout)
	}
}

func (runner *Runner) wait(ctx context.Context, delay time.Duration) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-runner.clock.After(delay):
		return nil
	}
}

func nextBackoff(current time.Duration, maximum time.Duration) time.Duration {
	if current >= maximum || current > maximum/2 {
		return maximum
	}
	return current * 2
}
