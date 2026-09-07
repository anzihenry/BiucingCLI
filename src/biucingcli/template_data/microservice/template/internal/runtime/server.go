package runtime

import (
	"context"
	"errors"
	"fmt"
	"net"
	"net/http"
	"time"

	"{{MODULE_NAME}}/internal/config"

	"google.golang.org/grpc"
)

type GRPCServer interface {
	Serve(net.Listener) error
	GracefulStop()
	Stop()
	SetServing(bool)
}

func NewHTTPServer(cfg config.Config, handler http.Handler) *http.Server {
	return &http.Server{
		Addr:              ":" + cfg.Service.HTTPPort,
		Handler:           handler,
		ReadTimeout:       time.Duration(cfg.Server.ReadTimeoutSeconds) * time.Second,
		ReadHeaderTimeout: time.Duration(cfg.Server.ReadHeaderTimeoutSeconds) * time.Second,
		WriteTimeout:      time.Duration(cfg.Server.WriteTimeoutSeconds) * time.Second,
		IdleTimeout:       time.Duration(cfg.Server.IdleTimeoutSeconds) * time.Second,
	}
}

func CheckHealth(ctx context.Context, url string) error {
	request, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return err
	}
	response, err := http.DefaultClient.Do(request)
	if err != nil {
		return err
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusOK {
		return errors.New("health endpoint returned " + response.Status)
	}
	return nil
}

func Serve(
	ctx context.Context,
	httpServer *http.Server,
	httpListener net.Listener,
	grpcServer GRPCServer,
	grpcListener net.Listener,
	shutdownTimeout time.Duration,
) error {
	type result struct {
		name string
		err  error
	}
	serveResults := make(chan result, 2)
	go func() {
		serveResults <- result{name: "HTTP", err: httpServer.Serve(httpListener)}
	}()
	go func() {
		serveResults <- result{name: "gRPC", err: grpcServer.Serve(grpcListener)}
	}()

	var serveErr error
	select {
	case result := <-serveResults:
		if !isExpectedServeError(result.err) {
			serveErr = fmt.Errorf("%s server: %w", result.name, result.err)
		}
	case <-ctx.Done():
	}

	grpcServer.SetServing(false)
	shutdownCtx, cancel := context.WithTimeout(context.Background(), shutdownTimeout)
	defer cancel()

	httpDone := make(chan error, 1)
	go func() {
		httpDone <- httpServer.Shutdown(shutdownCtx)
	}()
	grpcDone := make(chan struct{})
	go func() {
		grpcServer.GracefulStop()
		close(grpcDone)
	}()

	var shutdownErr error
	select {
	case err := <-httpDone:
		if err != nil {
			shutdownErr = errors.Join(shutdownErr, fmt.Errorf("HTTP shutdown: %w", err))
		}
	case <-shutdownCtx.Done():
		_ = httpServer.Close()
		shutdownErr = errors.Join(shutdownErr, shutdownCtx.Err())
	}

	select {
	case <-grpcDone:
	case <-shutdownCtx.Done():
		grpcServer.Stop()
		shutdownErr = errors.Join(shutdownErr, shutdownCtx.Err())
	}

	return errors.Join(serveErr, shutdownErr)
}

func isExpectedServeError(err error) bool {
	return err == nil || errors.Is(err, http.ErrServerClosed) || errors.Is(err, grpc.ErrServerStopped)
}
