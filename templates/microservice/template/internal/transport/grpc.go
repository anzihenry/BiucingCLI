package transport

import (
	servicev1 "{{MODULE_NAME}}/api/gen/go/service/v1"
	"{{MODULE_NAME}}/internal/service"

	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	healthpb "google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/reflection"
)

func NewGRPCServer(serviceName string, pingService service.PingService) *grpc.Server {
	server := grpc.NewServer()
	healthServer := health.NewServer()
	healthServer.SetServingStatus(serviceName, healthpb.HealthCheckResponse_SERVING)
	healthpb.RegisterHealthServer(server, healthServer)
	servicev1.Register{{SERVICE_TYPE_NAME}}ServiceServer(server, newPingServer(pingService))
	reflection.Register(server)
	return server
}
