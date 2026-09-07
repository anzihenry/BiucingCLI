package handler

import (
	"net/http"

	"{{MODULE_NAME}}/internal/service"

	"github.com/gin-gonic/gin"
)

type PingHandler struct {
	service service.PingService
}

func NewPingHandler(service service.PingService) PingHandler {
	return PingHandler{service: service}
}

func (handler PingHandler) RegisterRoutes(group *gin.RouterGroup) {
	group.GET("/ping", handler.Ping)
}

func (handler PingHandler) Ping(ctx *gin.Context) {
	ctx.JSON(http.StatusOK, handler.service.Ping())
}
