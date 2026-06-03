package service

import "{{MODULE_NAME}}/internal/model"

type PingService interface {
	Ping() model.PingResponse
}

type pingService struct {
	serviceName string
}

func NewPingService(serviceName string) PingService {
	return pingService{serviceName: serviceName}
}

func (service pingService) Ping() model.PingResponse {
	return model.PingResponse{
		Service: service.serviceName,
		Message: "pong",
		Version: "v1",
	}
}
