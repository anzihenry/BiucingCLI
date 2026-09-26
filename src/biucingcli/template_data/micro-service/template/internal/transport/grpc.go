package transport

import (
	"net"

	servicev1 "{{MODULE_NAME}}/api/gen/go/service/v1"
	"{{MODULE_NAME}}/internal/service"

	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	healthpb "google.golang.org/grpc/health/grpc_health_v1"
	"os"
	"{{MODULE_NAME}}/internal/observability"
	"{{MODULE_NAME}}/internal/pipeline"
	"{{MODULE_NAME}}/internal/security"
)

type GRPCServer struct {
	server      *grpc.Server
	health      *health.Server
	serviceName string
}

type Options struct {
	Limits pipeline.Limits
	Policy security.Policy
	Public map[string]bool
	Events *observability.Events
}

func NewGRPCServer(serviceName string, pingService service.PingService, options ...Options) *GRPCServer {
	var opts Options
	if len(options) > 0 {
		opts = options[0]
	}
	opts.Limits = opts.Limits.Defaults()
	if opts.Events == nil {
		opts.Events = &observability.Events{Logger: observability.New(os.Stdout, "INFO")}
	}
	public := map[string]bool{"/grpc.health.v1.Health/Check": true, "/grpc.health.v1.Health/Watch": true}
	for name, allowed := range opts.Public {
		public[name] = allowed
	}
	gate := NewGate(opts.Limits, opts.Policy, public, opts.Events)
	server := grpc.NewServer(grpc.UnaryInterceptor(gate.Unary), grpc.StreamInterceptor(gate.Stream), grpc.MaxRecvMsgSize(int(opts.Limits.MaxBytes)), grpc.MaxSendMsgSize(int(opts.Limits.MaxBytes)), grpc.MaxConcurrentStreams(uint32(opts.Limits.Concurrent)))
	healthServer := health.NewServer()
	healthServer.SetServingStatus(serviceName, healthpb.HealthCheckResponse_NOT_SERVING)
	healthServer.SetServingStatus("", healthpb.HealthCheckResponse_NOT_SERVING)
	healthpb.RegisterHealthServer(server, healthServer)
	servicev1.Register{{SERVICE_TYPE_NAME}}ServiceServer(server, newPingServer(pingService))
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
