package app

import (
	"context"
	"errors"
	"net/http"
	"os"
	"time"
	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/database"
	"{{MODULE_NAME}}/internal/observability"
	"{{MODULE_NAME}}/internal/outbound"
	"{{MODULE_NAME}}/internal/pipeline"
	"{{MODULE_NAME}}/internal/router"
	serverruntime "{{MODULE_NAME}}/internal/runtime"
	"{{MODULE_NAME}}/internal/security"
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
	shutdown, telemetryErr := telemetry.Setup(ctx, cfg.Service.Name, serverruntime.Version, cfg.Environment, cfg.Telemetry)
	if telemetryErr != nil {
		logger.Warn("telemetry initialization failed", "code", "telemetry_unavailable")
	}
	defer func() {
		closeCtx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel()
		_ = shutdown(closeCtx)
	}()
	tlsConfig, err := cfg.Workload.TLS()
	if err != nil {
		return err
	}
	grpcServer := transport.NewGRPCServer(cfg.Service.Name, service.NewPingService(cfg.Service.Name, "{{PROTO_PACKAGE}}"), transport.Options{Limits: limits, Events: events, TLS: tlsConfig, Authenticate: cfg.Workload.Authenticate, Policy: func(_ context.Context, p security.Principal, _ string) bool { return p.Workload != "" }})
	defer grpcServer.Stop()

	clients, closeClients, err := outbound.OpenAll(cfg.Dependencies)
	if err != nil {
		return err
	}
	defer closeClients()
	state := &serverruntime.Readiness{}
	var store *database.Store
	if cfg.Database.Driver == "postgres" {
		store, err = database.Open(ctx, cfg.Database.DSN, cfg.Data)
		if err != nil {
			return err
		}
		defer store.Close()
		if err = store.Schema(ctx); err != nil {
			return err
		}
		state.AddCritical(func(check context.Context) bool { return store.Ping(check) == nil && store.Schema(check) == nil })
	}
	admin := &http.Server{Handler: state.Handler(), ReadHeaderTimeout: 2 * time.Second, ReadTimeout: 3 * time.Second, WriteTimeout: 3 * time.Second, IdleTimeout: 30 * time.Second}
	defer func() { _ = admin.Close() }()
	httpServer := serverruntime.NewHTTPServer(cfg, pipeline.Bounded(router.New(cfg, router.Options{Dependencies: clients, Events: events}), limits))
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
	go func() {
		ticker := time.NewTicker(time.Second)
		defer ticker.Stop()
		defer grpcServer.SetServing(false)
		for {
			select {
			case <-child.Done():
				return
			case <-ticker.C:
				check, finish := context.WithTimeout(child, time.Second)
				ready := state.Check(check)
				finish()
				if child.Err() != nil {
					return
				}
				grpcServer.SetServing(ready)
			}
		}
	}()
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
