package main

import (
	"context"
	"log"
	"net"

	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/router"
	"{{MODULE_NAME}}/internal/telemetry"
	"{{MODULE_NAME}}/internal/transport"
)

func main() {
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
	defer func() {
		if err := shutdown(context.Background()); err != nil {
			log.Printf("telemetry shutdown warning: %v", err)
		}
	}()

	grpcListener, err := net.Listen("tcp", ":"+cfg.Service.GRPCPort)
	if err != nil {
		log.Fatal(err)
	}

	grpcServer := transport.NewGRPCServer(cfg.Service.Name)
	go func() {
		log.Printf("starting %s gRPC server on :%s", cfg.Service.Name, cfg.Service.GRPCPort)
		if err := grpcServer.Serve(grpcListener); err != nil {
			log.Fatal(err)
		}
	}()

	engine := router.New(cfg)
	log.Printf("starting %s HTTP server on :%s", cfg.Service.Name, cfg.Service.HTTPPort)
	if err := engine.Run(":" + cfg.Service.HTTPPort); err != nil {
		log.Fatal(err)
	}
}
