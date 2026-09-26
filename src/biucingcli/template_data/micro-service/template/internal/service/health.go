package service

import "{{MODULE_NAME}}/internal/model"

type HealthService struct {
	serviceName    string
	grpcPort       string
	databaseDriver string
}

func NewHealthService(serviceName string, grpcPort string, databaseDriver string) HealthService {
	return HealthService{
		serviceName:    serviceName,
		grpcPort:       grpcPort,
		databaseDriver: databaseDriver,
	}
}

func (service HealthService) Status() model.HealthResponse {
	return model.HealthResponse{
		Service:  service.serviceName,
		Status:   "ok",
		Database: service.databaseDriver,
		GRPCPort: service.grpcPort,
	}
}
