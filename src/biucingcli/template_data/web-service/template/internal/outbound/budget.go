// Package outbound owns reusable, bounded dependency clients. Create once at startup.
package outbound

import (
	"context"
	"errors"
	"math/rand/v2"
	"time"
	"{{MODULE_NAME}}/internal/telemetry"
)

var ErrOverloaded = errors.New("dependency overloaded")
var ErrCircuitOpen = errors.New("dependency circuit open")

// Breaker implementations must be concurrency safe, bounded, and allow only a
// limited number of recovery probes. No implicit fallback is performed here.
type Breaker interface {
	Allow() bool
	Done(error)
}
type Operation struct {
	Idempotent  bool `yaml:"idempotent"`
	Attempts    int  `yaml:"attempts"`
	ForwardUser bool `yaml:"forward_user"`
}
type budget struct {
	slots          chan struct{}
	total, attempt time.Duration
	dependency     string
	breaker        Breaker
}

func (b *budget) run(ctx context.Context, name string, op Operation, retryable func(error) bool, call func(context.Context) error) (err error) {
	ctx, cancel := context.WithTimeout(ctx, b.total)
	defer cancel()
	if err = ctx.Err(); err != nil {
		return err
	}
	select {
	case b.slots <- struct{}{}:
		defer func() { <-b.slots }()
	default:
		telemetry.Reject(ctx, b.dependency, "overloaded")
		return ErrOverloaded
	}
	if b.breaker != nil {
		if !b.breaker.Allow() {
			telemetry.Reject(ctx, b.dependency, "circuit_open")
			return ErrCircuitOpen
		}
		defer func() { b.breaker.Done(err) }()
	}
	attempts := op.Attempts
	if attempts < 1 {
		attempts = 1
	}
	if !op.Idempotent {
		attempts = 1
	}
	for n := 0; n < attempts; n++ {
		child, stop := context.WithTimeout(ctx, b.attempt)
		child, finish := telemetry.Start(child, "client", b.dependency+"/"+name)
		err = call(child)
		finish(err)
		stop()
		if err == nil || ctx.Err() != nil || n+1 == attempts || !retryable(err) {
			break
		}
		telemetry.Retry(ctx, b.dependency, name)
		delay := time.Duration(rand.Int64N(int64(50*time.Millisecond)*(1<<n) + 1))
		timer := time.NewTimer(delay)
		select {
		case <-ctx.Done():
			timer.Stop()
			return ctx.Err()
		case <-timer.C:
		}
	}
	if ctx.Err() != nil {
		return ctx.Err()
	}
	return err
}
