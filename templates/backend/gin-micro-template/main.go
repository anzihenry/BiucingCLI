package main

import (
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/spf13/viper"
	"go.uber.org/zap"
)

// @title {{project_name}} API
// @version 1.0
// @description {{project_name}} API Documentation
// @host localhost:8080
// @BasePath /api/v1
func main() {
	// Initialize config
	if err := initConfig(); err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Initialize logger
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	// Initialize Gin router
	gin.SetMode(viper.GetString("server.mode"))
	r := gin.Default()

	// Register routes
	registerRoutes(r, logger)

	// Start server
	port := viper.GetString("server.port")
	logger.Info("Starting server", zap.String("port", port))
	if err := r.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func initConfig() error {
	viper.SetConfigFile("configs/config.yaml")
	viper.AutomaticEnv()
	return viper.ReadInConfig()
}

func registerRoutes(r *gin.Engine, logger *zap.Logger) {
	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// API v1 group
	v1 := r.Group("/api/v1")
	{
		v1.GET("/ping", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "pong"})
		})
	}

	// Swagger
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
}
