package utils

import (
	"github.com/gin-gonic/gin"
)

// Response represents a standard API response.
type Response struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// Success sends a success response.
func Success(c *gin.Context, data interface{}) {
	c.JSON(200, Response{
		Code:    0,
		Message: "success",
		Data:    data,
	})
}

// Error sends an error response.
func Error(c *gin.Context, code int, message string) {
	c.JSON(code, Response{
		Code:    code,
		Message: message,
	})
}

// NotFound sends a 404 response.
func NotFound(c *gin.Context) {
	Error(c, 404, "resource not found")
}

// BadRequest sends a 400 response.
func BadRequest(c *gin.Context, message string) {
	Error(c, 400, message)
}

// Unauthorized sends a 401 response.
func Unauthorized(c *gin.Context) {
	Error(c, 401, "unauthorized")
}
