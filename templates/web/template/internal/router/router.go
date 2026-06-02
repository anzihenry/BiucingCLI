package router

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func New() *gin.Engine {
	engine := gin.Default()
	engine.GET("/healthz", func(ctx *gin.Context) {
		ctx.JSON(http.StatusOK, gin.H{
			"service": "{{SERVICE_NAME}}",
			"status":  "ok",
		})
	})
	return engine
}
