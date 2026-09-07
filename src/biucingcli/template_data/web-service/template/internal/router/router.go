package router

import "{{MODULE_NAME}}/internal/config"
import "{{MODULE_NAME}}/internal/handler"
import "{{MODULE_NAME}}/internal/repository"
import "{{MODULE_NAME}}/internal/service"

import "github.com/gin-gonic/gin"

func New(cfg config.Config) *gin.Engine {
	engine := gin.Default()

	healthService := service.NewHealthService(cfg.Service.Name)
	healthHandler := handler.NewHealthHandler(healthService)
	healthHandler.RegisterRoutes(engine)

	apiGroup := engine.Group("/api/v1")
	pingService := service.NewPingService(cfg.Service.Name)
	pingHandler := handler.NewPingHandler(pingService)
	pingHandler.RegisterRoutes(apiGroup)

	userRepository := repository.NewUserRepository()
	userService := service.NewUserService(userRepository)
	userHandler := handler.NewUserHandler(userService)
	userHandler.RegisterRoutes(apiGroup)

	return engine
}
