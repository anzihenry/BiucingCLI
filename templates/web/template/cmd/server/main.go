package main

import (
	"log"

	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/router"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatal(err)
	}

	engine := router.New(cfg)
	log.Printf("starting %s on :%s", cfg.Service.Name, cfg.Service.Port)
	if err := engine.Run(":" + cfg.Service.Port); err != nil {
		log.Fatal(err)
	}
}
