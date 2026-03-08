package services

import (
	"context"

	"go.uber.org/zap"
)

// Service defines the base service struct.
type Service struct {
	logger *zap.Logger
}

// NewService creates a new Service instance.
func NewService(logger *zap.Logger) *Service {
	return &Service{
		logger: logger,
	}
}

// HealthCheck performs a health check.
func (s *Service) HealthCheck(ctx context.Context) error {
	s.logger.Info("Performing health check")
	// Add health check logic here
	return nil
}
