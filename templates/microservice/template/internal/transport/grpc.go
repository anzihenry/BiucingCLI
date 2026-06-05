package transport

import (
	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	healthpb "google.golang.org/grpc/health/grpc_health_v1"
)

func NewGRPCServer(serviceName string) *grpc.Server {
	server := grpc.NewServer()
	healthServer := health.NewServer()
	healthServer.SetServingStatus(serviceName, healthpb.HealthCheckResponse_SERVING)
	healthpb.RegisterHealthServer(server, healthServer)
	return server
}
