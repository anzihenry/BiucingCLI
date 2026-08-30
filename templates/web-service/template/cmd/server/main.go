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

	listener, err := net.Listen("tcp", ":"+cfg.Service.Port)
	if err != nil {
		log.Fatal(err)
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	server := serverruntime.NewHTTPServer(cfg, router.New(cfg))
	log.Printf("starting %s on :%s", cfg.Service.Name, cfg.Service.Port)
	if err := serverruntime.Serve(
		ctx,
		server,
		listener,
		time.Duration(cfg.Server.ShutdownTimeoutSeconds)*time.Second,
	); err != nil {
		log.Fatal(err)
	}
}
