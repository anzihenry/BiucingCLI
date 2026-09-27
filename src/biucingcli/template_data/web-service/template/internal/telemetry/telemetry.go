// Package telemetry records bounded, low-cardinality signals. Never pass raw
// URLs, SQL, user IDs, credentials or arbitrary error text as attributes.
package telemetry

import (
	"context"
	"errors"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetrichttp"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/metric"
	"go.opentelemetry.io/otel/propagation"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	"go.opentelemetry.io/otel/trace"
	"math"
	"net/url"
	"time"
)

type Config struct {
	OTLPHTTPEndpoint string   `yaml:"otlp_http_endpoint"`
	SampleRatio      *float64 `yaml:"sample_ratio"`
}

func (c Config) Validate() error {
	if c.SampleRatio != nil && (math.IsNaN(*c.SampleRatio) || *c.SampleRatio < 0 || *c.SampleRatio > 1) {
		return errors.New("invalid telemetry sample ratio")
	}
	if c.OTLPHTTPEndpoint != "" {
		u, e := url.Parse(c.OTLPHTTPEndpoint)
		if e != nil || u.Host == "" || (u.Scheme != "http" && u.Scheme != "https") || u.User != nil || u.RawQuery != "" || u.Fragment != "" {
			return errors.New("invalid telemetry endpoint")
		}
	}
	return nil
}
func Setup(ctx context.Context, name, version, environment string, c Config) (func(context.Context) error, error) {
	if e := c.Validate(); e != nil {
		return func(context.Context) error { return nil }, e
	}
	r := resource.NewSchemaless(attribute.String("service.name", name), attribute.String("service.version", version), attribute.String("deployment.environment.name", environment))
	ratio := 0.1
	if c.SampleRatio != nil {
		ratio = *c.SampleRatio
	}
	// Do not let untrusted remote sampled flags bypass the local sampling budget.
	opts := []sdktrace.TracerProviderOption{sdktrace.WithResource(r), sdktrace.WithSampler(sdktrace.TraceIDRatioBased(ratio))}
	mopts := []sdkmetric.Option{sdkmetric.WithResource(r), sdkmetric.WithCardinalityLimit(256)}
	var setupErr error
	if c.OTLPHTTPEndpoint != "" {
		exp, e := otlptracehttp.New(ctx, otlptracehttp.WithEndpointURL(c.OTLPHTTPEndpoint), otlptracehttp.WithTimeout(time.Second), otlptracehttp.WithRetry(otlptracehttp.RetryConfig{Enabled: false}))
		setupErr = errors.Join(setupErr, e)
		if e == nil {
			opts = append(opts, sdktrace.WithBatcher(exp, sdktrace.WithMaxQueueSize(512), sdktrace.WithMaxExportBatchSize(128), sdktrace.WithBatchTimeout(time.Second), sdktrace.WithExportTimeout(time.Second)))
		}
		mx, e := otlpmetrichttp.New(ctx, otlpmetrichttp.WithEndpointURL(c.OTLPHTTPEndpoint), otlpmetrichttp.WithTimeout(time.Second), otlpmetrichttp.WithRetry(otlpmetrichttp.RetryConfig{Enabled: false}))
		setupErr = errors.Join(setupErr, e)
		if e == nil {
			mopts = append(mopts, sdkmetric.WithReader(sdkmetric.NewPeriodicReader(mx, sdkmetric.WithInterval(10*time.Second), sdkmetric.WithTimeout(time.Second))))
		}
	}
	tp := sdktrace.NewTracerProvider(opts...)
	mp := sdkmetric.NewMeterProvider(mopts...)
	otel.SetTracerProvider(tp)
	otel.SetMeterProvider(mp)
	otel.SetTextMapPropagator(propagation.TraceContext{}) // deliberately exclude baggage
	// SDK export errors can contain transport endpoints. Use a fixed safe signal.
	exportErrors, _ := mp.Meter("backend").Int64Counter("backend.telemetry.export_errors")
	otel.SetErrorHandler(otel.ErrorHandlerFunc(func(error) { exportErrors.Add(context.Background(), 1) }))
	return func(ctx context.Context) error { return errors.Join(tp.Shutdown(ctx), mp.Shutdown(ctx)) }, setupErr
}
func Start(ctx context.Context, kind, operation string) (context.Context, func(error)) {
	sk := trace.SpanKindInternal
	if kind == "client" {
		sk = trace.SpanKindClient
	}
	if kind == "server" {
		sk = trace.SpanKindServer
	}
	attrs := []attribute.KeyValue{attribute.String("kind", kind), attribute.String("operation", operation)}
	ctx, span := otel.Tracer("backend").Start(ctx, kind+" "+operation, trace.WithSpanKind(sk), trace.WithAttributes(attrs...))
	m := otel.Meter("backend")
	count, _ := m.Int64Counter("backend.operations")
	latency, _ := m.Float64Histogram("backend.duration", metric.WithUnit("s"))
	active, _ := m.Int64UpDownCounter("backend.active")
	active.Add(ctx, 1, metric.WithAttributes(attrs...))
	start := time.Now()
	return ctx, func(err error) {
		outcome := "ok"
		if err != nil {
			outcome = "error"
			span.SetStatus(codes.Error, "operation failed")
		}
		active.Add(ctx, -1, metric.WithAttributes(attrs...))
		attrs = append(attrs, attribute.String("outcome", outcome))
		count.Add(ctx, 1, metric.WithAttributes(attrs...))
		latency.Record(ctx, time.Since(start).Seconds(), metric.WithAttributes(attrs...))
		span.End()
	}
}
func Retry(ctx context.Context, dependency, operation string) {
	c, _ := otel.Meter("backend").Int64Counter("backend.retries")
	c.Add(ctx, 1, metric.WithAttributes(attribute.String("dependency", dependency), attribute.String("operation", operation)))
}
func Reject(ctx context.Context, dependency, reason string) {
	c, _ := otel.Meter("backend").Int64Counter("backend.rejections")
	c.Add(ctx, 1, metric.WithAttributes(attribute.String("dependency", dependency), attribute.String("reason", reason)))
}
