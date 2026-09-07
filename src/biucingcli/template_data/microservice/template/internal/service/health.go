package service

import "{{MODULE_NAME}}/internal/model"

type HealthService struct {
	serviceName string
	grpcPort    string
	storeDriver string
}

func NewHealthService(serviceName string, grpcPort string, storeDriver string) HealthService {
	return HealthService{
		serviceName: serviceName,
		grpcPort:    grpcPort,
		storeDriver: storeDriver,
	}
}

func (service HealthService) Status() model.HealthResponse {
	return model.HealthResponse{
		Service:  service.serviceName,
		Status:   "ok",
		Store:    service.storeDriver,
		GRPCPort: service.grpcPort,
	}
}
