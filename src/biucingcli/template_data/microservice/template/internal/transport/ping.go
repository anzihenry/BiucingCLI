package transport

import (
	"context"

	servicev1 "{{MODULE_NAME}}/api/gen/go/service/v1"
	"{{MODULE_NAME}}/internal/service"
)

type pingServer struct {
	servicev1.Unimplemented{{SERVICE_TYPE_NAME}}ServiceServer
	service service.PingService
}

func newPingServer(pingService service.PingService) *pingServer {
	return &pingServer{service: pingService}
}

func (server *pingServer) Ping(
	_ context.Context,
	_ *servicev1.PingRequest,
) (*servicev1.PingResponse, error) {
	response := server.service.Ping()
	return &servicev1.PingResponse{
		Message: response.Message,
		Service: response.Service,
	}, nil
}
