package handler

import (
	"net/http"

	"{{MODULE_NAME}}/internal/service"

	"github.com/gin-gonic/gin"
)

type HealthHandler struct {
	service service.HealthService
}

func NewHealthHandler(service service.HealthService) HealthHandler {
	return HealthHandler{service: service}
}

func (handler HealthHandler) RegisterRoutes(engine *gin.Engine) {
	engine.GET("/healthz", handler.GetHealth)
}

func (handler HealthHandler) GetHealth(ctx *gin.Context) {
	ctx.JSON(http.StatusOK, handler.service.Status())
}
