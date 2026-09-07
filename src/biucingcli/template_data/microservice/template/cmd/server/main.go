package main

import (
	"context"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/router"
	serverruntime "{{MODULE_NAME}}/internal/runtime"
	"{{MODULE_NAME}}/internal/service"
	"{{MODULE_NAME}}/internal/telemetry"
	"{{MODULE_NAME}}/internal/transport"
)

func main() {
	if len(os.Args) == 3 && os.Args[1] == "healthcheck" {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel()
		if err := serverruntime.CheckHealth(ctx, os.Args[2]); err != nil {
			log.Fatal(err)
		}
		return
	}

	cfg, err := config.Load()
	if err != nil {
		log.Fatal(err)
	}

	shutdown, telemetryErr := telemetry.Setup(
		context.Background(),
		cfg.Service.Name,
		cfg.Telemetry.OTLPHTTPEndpoint,
	)
	if telemetryErr != nil {
		log.Printf("telemetry setup warning: %v", telemetryErr)
	}
	grpcListener, err := net.Listen("tcp", ":"+cfg.Service.GRPCPort)
	if err != nil {
		log.Fatal(err)
	}

	httpListener, err := net.Listen("tcp", ":"+cfg.Service.HTTPPort)
	if err != nil {
		_ = grpcListener.Close()
		log.Fatal(err)
	}

	pingService := service.NewPingService(cfg.Service.Name, "{{PROTO_PACKAGE}}")
	grpcServer := transport.NewGRPCServer(cfg.Service.Name, pingService)
	httpServer := serverruntime.NewHTTPServer(cfg, router.New(cfg))

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	log.Printf("starting %s gRPC server on :%s", cfg.Service.Name, cfg.Service.GRPCPort)
	log.Printf("starting %s HTTP server on :%s", cfg.Service.Name, cfg.Service.HTTPPort)
	shutdownTimeout := time.Duration(cfg.Server.ShutdownTimeoutSeconds) * time.Second
	serveErr := serverruntime.Serve(
		ctx,
		httpServer,
		httpListener,
		grpcServer,
		grpcListener,
		shutdownTimeout,
	)

	telemetryCtx, cancelTelemetry := context.WithTimeout(context.Background(), shutdownTimeout)
	defer cancelTelemetry()
	if err := shutdown(telemetryCtx); err != nil {
		log.Printf("telemetry shutdown warning: %v", err)
	}
	if serveErr != nil {
		log.Fatal(serveErr)
	}
}
