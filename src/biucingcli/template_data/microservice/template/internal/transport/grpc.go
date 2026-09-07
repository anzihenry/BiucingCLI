package transport

import (
	"net"

	servicev1 "{{MODULE_NAME}}/api/gen/go/service/v1"
	"{{MODULE_NAME}}/internal/service"

	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	healthpb "google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/reflection"
)

type GRPCServer struct {
	server      *grpc.Server
	health      *health.Server
	serviceName string
}

func NewGRPCServer(serviceName string, pingService service.PingService) *GRPCServer {
	server := grpc.NewServer()
	healthServer := health.NewServer()
	healthServer.SetServingStatus(serviceName, healthpb.HealthCheckResponse_SERVING)
	healthServer.SetServingStatus("", healthpb.HealthCheckResponse_SERVING)
	healthpb.RegisterHealthServer(server, healthServer)
	servicev1.Register{{SERVICE_TYPE_NAME}}ServiceServer(server, newPingServer(pingService))
	reflection.Register(server)
	return &GRPCServer{server: server, health: healthServer, serviceName: serviceName}
}

func (server *GRPCServer) Serve(listener net.Listener) error {
	return server.server.Serve(listener)
}

func (server *GRPCServer) GracefulStop() {
	server.server.GracefulStop()
}

func (server *GRPCServer) Stop() {
	server.server.Stop()
}

func (server *GRPCServer) SetServing(serving bool) {
	status := healthpb.HealthCheckResponse_NOT_SERVING
	if serving {
		status = healthpb.HealthCheckResponse_SERVING
	}
	server.health.SetServingStatus(server.serviceName, status)
	server.health.SetServingStatus("", status)
}
