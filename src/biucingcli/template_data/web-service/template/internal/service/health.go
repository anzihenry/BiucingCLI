package service

import "{{MODULE_NAME}}/internal/model"

type HealthService interface {
	Status() model.HealthResponse
}

type healthService struct {
	serviceName string
}

func NewHealthService(serviceName string) HealthService {
	return healthService{serviceName: serviceName}
}

func (service healthService) Status() model.HealthResponse {
	return model.HealthResponse{
		Service: service.serviceName,
		Status:  "ok",
	}
}
