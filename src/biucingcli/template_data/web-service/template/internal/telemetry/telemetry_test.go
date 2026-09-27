package telemetry

import (
	"context"
	"errors"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/propagation"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/metric/metricdata"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	"go.opentelemetry.io/otel/sdk/trace/tracetest"
	"testing"
	"time"
)

func TestTracePropagationAndMetrics(t *testing.T) {
	exporter := tracetest.NewInMemoryExporter()
	tp := sdktrace.NewTracerProvider(sdktrace.WithSyncer(exporter))
	reader := sdkmetric.NewManualReader()
	mp := sdkmetric.NewMeterProvider(sdkmetric.WithReader(reader))
	otel.SetTracerProvider(tp)
	otel.SetMeterProvider(mp)
	otel.SetTextMapPropagator(propagation.TraceContext{})
	defer func() { _ = tp.Shutdown(context.Background()); _ = mp.Shutdown(context.Background()) }()
	parent, end := Start(context.Background(), "server", "GET /fixture")
	carrier := propagation.MapCarrier{}
	otel.GetTextMapPropagator().Inject(parent, carrier)
	child := otel.GetTextMapPropagator().Extract(context.Background(), carrier)
	_, finish := Start(child, "client", "internal/read")
	finish(errors.New("secret error must not export"))
	end(nil)
	spans := exporter.GetSpans()
	if len(spans) != 2 || spans[0].SpanContext.TraceID() != spans[1].SpanContext.TraceID() {
		t.Fatal("broken trace")
	}
	Retry(parent, "internal", "read")
	Reject(parent, "internal", "overloaded")
	var data metricdata.ResourceMetrics
	if e := reader.Collect(context.Background(), &data); e != nil || len(data.ScopeMetrics) == 0 {
		t.Fatal("missing metrics", e)
	}
}
func TestUnavailableExporterIsBounded(t *testing.T) {
	ratio := 1.0
	shutdown, e := Setup(context.Background(), "test", "dev", "test", Config{OTLPHTTPEndpoint: "http://127.0.0.1:1", SampleRatio: &ratio})
	if e != nil {
		t.Fatal(e)
	}
	start := time.Now()
	for i := 0; i < 2000; i++ {
		_, finish := Start(context.Background(), "server", "GET /fixture")
		finish(nil)
	}
	if time.Since(start) > 2*time.Second {
		t.Fatal("exporter blocks requests")
	}
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	_ = shutdown(ctx)
}
