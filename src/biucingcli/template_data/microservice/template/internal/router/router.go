package router

import "{{MODULE_NAME}}/internal/config"
import "{{MODULE_NAME}}/internal/handler"
import "{{MODULE_NAME}}/internal/service"

import "github.com/gin-gonic/gin"

func New(cfg config.Config) *gin.Engine {
	engine := gin.Default()

	healthService := service.NewHealthService(
		cfg.Service.Name,
		cfg.Service.GRPCPort,
		cfg.Store.Driver,
	)
	healthHandler := handler.NewHealthHandler(healthService)
	healthHandler.RegisterRoutes(engine)

	apiGroup := engine.Group("/api/v1")
	pingService := service.NewPingService(cfg.Service.Name, "{{PROTO_PACKAGE}}")
	pingHandler := handler.NewPingHandler(pingService)
	pingHandler.RegisterRoutes(apiGroup)

	return engine
}
