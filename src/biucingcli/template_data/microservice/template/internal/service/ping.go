package service

import "{{MODULE_NAME}}/internal/model"

type PingService struct {
	serviceName  string
	protoPackage string
}

func NewPingService(serviceName string, protoPackage string) PingService {
	return PingService{
		serviceName:  serviceName,
		protoPackage: protoPackage,
	}
}

func (service PingService) Ping() model.PingResponse {
	return model.PingResponse{
		Message:      "pong",
		Service:      service.serviceName,
		ProtoPackage: service.protoPackage,
	}
}
