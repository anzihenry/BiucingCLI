package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

// Handler defines the main handler struct.
type Handler struct {
	logger *zap.Logger
}

// NewHandler creates a new Handler instance.
func NewHandler(logger *zap.Logger) *Handler {
	return &Handler{
		logger: logger,
	}
}

// Ping handles the ping endpoint.
// @Summary Ping endpoint
// @Description Returns a pong response
// @Tags health
// @Produce json
// @Success 200 {object} map[string]string
// @Router /api/v1/ping [get]
func (h *Handler) Ping(c *gin.Context) {
	h.logger.Info("Ping request received")
	c.JSON(http.StatusOK, gin.H{
		"message": "pong",
	})
}
