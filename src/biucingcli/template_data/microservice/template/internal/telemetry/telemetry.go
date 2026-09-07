package telemetry

import (
	"context"
	"strings"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
)

func Setup(
	ctx context.Context,
	serviceName string,
	endpoint string,
) (func(context.Context) error, error) {
	resourceAttributes := resource.NewWithAttributes(
		semconv.SchemaURL,
		semconv.ServiceName(serviceName),
	)

	options := []sdktrace.TracerProviderOption{
		sdktrace.WithResource(resourceAttributes),
	}

	var setupErr error
	if endpoint != "" {
		exporterOptions := []otlptracehttp.Option{
			otlptracehttp.WithEndpointURL(endpoint),
		}
		if strings.HasPrefix(endpoint, "http://") {
			exporterOptions = append(exporterOptions, otlptracehttp.WithInsecure())
		}

		exporter, err := otlptracehttp.New(ctx, exporterOptions...)
		if err != nil {
			setupErr = err
		} else {
			options = append(options, sdktrace.WithBatcher(exporter))
		}
	}

	provider := sdktrace.NewTracerProvider(options...)
	otel.SetTracerProvider(provider)
	otel.SetTextMapPropagator(
		propagation.NewCompositeTextMapPropagator(
			propagation.TraceContext{},
			propagation.Baggage{},
		),
	)

	return provider.Shutdown, setupErr
}
