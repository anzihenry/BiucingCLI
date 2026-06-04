package handler

import (
	"net/http"

	"{{MODULE_NAME}}/internal/service"

	"github.com/gin-gonic/gin"
)

type UserHandler struct {
	service service.UserService
}

func NewUserHandler(service service.UserService) UserHandler {
	return UserHandler{service: service}
}

func (handler UserHandler) RegisterRoutes(group *gin.RouterGroup) {
	group.GET("/users", handler.ListUsers)
	group.GET("/users/:id", handler.GetUser)
}

func (handler UserHandler) ListUsers(ctx *gin.Context) {
	ctx.JSON(http.StatusOK, gin.H{
		"items": handler.service.ListUsers(),
	})
}

func (handler UserHandler) GetUser(ctx *gin.Context) {
	user, found := handler.service.GetUser(ctx.Param("id"))
	if !found {
		ctx.JSON(http.StatusNotFound, gin.H{
			"error": "user not found",
		})
		return
	}

	ctx.JSON(http.StatusOK, user)
}
