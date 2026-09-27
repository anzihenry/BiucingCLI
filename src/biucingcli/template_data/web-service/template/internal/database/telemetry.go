package database

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/metric"
	"{{MODULE_NAME}}/internal/telemetry"
)

type traceKey struct{}
type queryTracer struct{}

func (queryTracer) TraceQueryStart(ctx context.Context, _ *pgx.Conn, _ pgx.TraceQueryStartData) context.Context {
	ctx, finish := telemetry.Start(ctx, "database", "query")
	return context.WithValue(ctx, traceKey{}, finish)
}
func (queryTracer) TraceQueryEnd(ctx context.Context, _ *pgx.Conn, data pgx.TraceQueryEndData) {
	if finish, ok := ctx.Value(traceKey{}).(func(error)); ok {
		finish(data.Err)
	}
}
func (s *Store) observe() (func(), error) {
	m := otel.Meter("backend")
	used, e1 := m.Int64ObservableGauge("backend.db.connections.used")
	idle, e2 := m.Int64ObservableGauge("backend.db.connections.idle")
	max, e3 := m.Int64ObservableGauge("backend.db.connections.max")
	waits, e4 := m.Int64ObservableCounter("backend.db.acquire.empty")
	cancelled, e5 := m.Int64ObservableCounter("backend.db.acquire.cancelled")
	if e := errors.Join(e1, e2, e3, e4, e5); e != nil {
		return func() {}, e
	}
	registration, e := m.RegisterCallback(func(_ context.Context, o metric.Observer) error {
		stats := s.Pool.Stat()
		o.ObserveInt64(used, int64(stats.AcquiredConns()))
		o.ObserveInt64(idle, int64(stats.IdleConns()))
		o.ObserveInt64(max, int64(stats.MaxConns()))
		o.ObserveInt64(waits, stats.EmptyAcquireCount())
		o.ObserveInt64(cancelled, stats.CanceledAcquireCount())
		return nil
	}, used, idle, max, waits, cancelled)
	if e != nil {
		return func() {}, e
	}
	return func() { _ = registration.Unregister() }, nil
}
