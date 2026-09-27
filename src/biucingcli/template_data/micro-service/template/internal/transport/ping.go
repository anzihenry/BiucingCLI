package transport

import (
	"context"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"regexp"

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
	request *servicev1.PingRequest,
) (*servicev1.PingResponse, error) {
	if request.GetRequestId() != "" && !regexp.MustCompile(`^[a-zA-Z0-9_-]{1,64}$`).MatchString(request.GetRequestId()) {
		return nil, status.Error(codes.InvalidArgument, "invalid request ID")
	}
	response := server.service.Ping()
	return &servicev1.PingResponse{
		Message: response.Message,
		Service: response.Service,
	}, nil
}
