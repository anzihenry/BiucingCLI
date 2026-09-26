package router

import "{{MODULE_NAME}}/internal/config"
import "{{MODULE_NAME}}/internal/handler"
import "{{MODULE_NAME}}/internal/repository"
import "{{MODULE_NAME}}/internal/service"

import "github.com/gin-gonic/gin"
import "os"
import "{{MODULE_NAME}}/internal/pipeline"
import "{{MODULE_NAME}}/internal/observability"
import "{{MODULE_NAME}}/internal/security"
import "time"

type Options struct {
	Policy security.Policy
	Events *observability.Events
}

func New(cfg config.Config, options ...Options) *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	engine := gin.New()
	var opts Options
	if len(options) > 0 {
		opts = options[0]
	}
	if opts.Events == nil {
		opts.Events = &observability.Events{Logger: observability.New(os.Stdout, "INFO")}
	}
	limits := pipeline.Limits{MaxBytes: cfg.Request.MaxBytes, Concurrent: cfg.Request.Concurrent, Timeout: time.Duration(cfg.Request.TimeoutSeconds) * time.Second}
	engine.Use(pipeline.Middleware(limits, map[string]bool{"GET /api/v1/ping": true}, opts.Policy, opts.Events))

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
