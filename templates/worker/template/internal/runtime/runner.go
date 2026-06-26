package runtime

import (
	"context"
	"errors"
	"io"
	"log"
	"time"
)

type Executor interface {
	Execute(context.Context) (string, error)
}

type Options struct {
	Name            string
	Mode            string
	TickInterval    time.Duration
	ShutdownTimeout time.Duration
	Executor        Executor
	Logger          *log.Logger
}

type Runner struct {
	name            string
	mode            string
	tickInterval    time.Duration
	shutdownTimeout time.Duration
	executor        Executor
	logger          *log.Logger
}

func New(options Options) *Runner {
	logger := options.Logger
	if logger == nil {
		logger = log.New(io.Discard, "", 0)
	}
	return &Runner{
		name:            options.Name,
		mode:            options.Mode,
		tickInterval:    options.TickInterval,
		shutdownTimeout: options.ShutdownTimeout,
		executor:        options.Executor,
		logger:          logger,
	}
}

func (runner *Runner) Run(ctx context.Context) error {
	if runner.executor == nil {
		return errors.New("executor is required")
	}

	switch runner.mode {
	case "oneshot":
		return runner.executeOnce(ctx)
	case "scheduled":
		return runner.runScheduled(ctx)
	default:
		return errors.New("unsupported worker mode: " + runner.mode)
	}
}

func (runner *Runner) executeOnce(ctx context.Context) error {
	executionCtx, cancel := context.WithTimeout(ctx, runner.shutdownTimeout)
	defer cancel()

	summary, err := runner.executor.Execute(executionCtx)
	if err != nil {
		return err
	}
	runner.logger.Printf("%s: %s", runner.name, summary)
	return nil
}

func (runner *Runner) runScheduled(ctx context.Context) error {
	if err := runner.executeOnce(ctx); err != nil {
		return err
	}

	ticker := time.NewTicker(runner.tickInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			runner.logger.Printf("%s: shutdown requested", runner.name)
			return nil
		case <-ticker.C:
			if err := runner.executeOnce(ctx); err != nil {
				return err
			}
		}
	}
}
