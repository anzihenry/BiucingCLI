package app

import (
	"context"
	"errors"
	"net/http"
	"os"
	"time"
	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/observability"
	"{{MODULE_NAME}}/internal/pipeline"
	"{{MODULE_NAME}}/internal/router"
	serverruntime "{{MODULE_NAME}}/internal/runtime"
	"{{MODULE_NAME}}/internal/service"
	"{{MODULE_NAME}}/internal/telemetry"
	"{{MODULE_NAME}}/internal/transport"
)

// Bind before starting resources; every exit path closes partial initialization.
func Run(ctx context.Context, cfg config.Config) error {
	logger := observability.New(os.Stdout, cfg.LogLevel)
	events := &observability.Events{Logger: logger}
	timeout := time.Duration(cfg.Server.ShutdownTimeoutSeconds) * time.Second
	limits := pipeline.Limits{MaxBytes: cfg.Request.MaxBytes, Concurrent: cfg.Request.Concurrent, Timeout: time.Duration(cfg.Request.TimeoutSeconds) * time.Second}
	listeners, err := serverruntime.BindAll(":"+cfg.Service.HTTPPort, ":"+cfg.Service.GRPCPort, cfg.AdminAddr)
	if err != nil {
		return err
	}
	defer func() {
		for _, l := range listeners {
			_ = l.Close()
		}
	}()
	shutdown, telemetryErr := telemetry.Setup(ctx, cfg.Service.Name, cfg.Telemetry.OTLPHTTPEndpoint)
	if telemetryErr != nil {
		logger.Warn("telemetry initialization failed", "code", "telemetry_unavailable")
	}
	defer func() {
		closeCtx, cancel := context.WithTimeout(context.Background(), timeout)
		defer cancel()
		_ = shutdown(closeCtx)
	}()
	grpcServer := transport.NewGRPCServer(cfg.Service.Name, service.NewPingService(cfg.Service.Name, "{{PROTO_PACKAGE}}"), transport.Options{Limits: limits, Events: events})
	defer grpcServer.Stop()

	state := &serverruntime.Readiness{}
	admin := &http.Server{Handler: state.Handler(), ReadHeaderTimeout: 2 * time.Second, ReadTimeout: 3 * time.Second, WriteTimeout: 3 * time.Second, IdleTimeout: 30 * time.Second}
	defer func() { _ = admin.Close() }()
	httpServer := serverruntime.NewHTTPServer(cfg, pipeline.Bounded(router.New(cfg, router.Options{Events: events}), limits))
	defer func() { _ = httpServer.Close() }()
	child, cancel := context.WithCancel(ctx)
	defer cancel()
	results := make(chan error, 2)
	go func() { results <- admin.Serve(listeners[len(listeners)-1]) }()
	go func() {
		results <- serverruntime.Serve(child, httpServer, listeners[0], grpcServer, listeners[1], timeout)
	}()
	grpcServer.SetServing(true)
	state.Set(true)
	logger.Info("service ready", "version", serverruntime.Version, "commit", serverruntime.Commit, "environment", cfg.Environment)
	events.Audit(ctx, "configure", true)
	events.Audit(ctx, "startup", true)
	remaining := 2
	var runErr error
	select {
	case <-ctx.Done():
	case runErr = <-results:
		remaining--
	}
	state.Set(false)
	grpcServer.SetServing(false)
	cancel()
	drainCtx, stop := context.WithTimeout(context.Background(), timeout)
	defer stop()
	if err := admin.Shutdown(drainCtx); err != nil {
		_ = admin.Close()
	}
	for remaining > 0 {
		select {
		case err := <-results:
			remaining--
			if err != nil && !errors.Is(err, http.ErrServerClosed) {
				runErr = errors.Join(runErr, err)
			}
		case <-drainCtx.Done():
			return drainCtx.Err()
		}
	}
	events.Audit(ctx, "shutdown", true)
	if errors.Is(runErr, http.ErrServerClosed) {
		return nil
	}
	return runErr
}
