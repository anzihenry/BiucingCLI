package main

import (
	"log"

	"{{MODULE_NAME}}/internal/router"
)

func main() {
	engine := router.New()
	log.Printf("starting {{SERVICE_NAME}} on :{{HTTP_PORT}}")
	if err := engine.Run(":{{HTTP_PORT}}"); err != nil {
		log.Fatal(err)
	}
}
