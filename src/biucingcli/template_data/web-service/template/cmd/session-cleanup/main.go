package main

import (
	"context"
	"fmt"
	"os"
	"time"
	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/database"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "session cleanup failed")
		os.Exit(1)
	}
}
func run() error {
	cfg, err := config.Load()
	if err != nil {
		return err
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	s, err := database.Open(ctx, cfg.Database.DSN, cfg.Data)
	if err != nil {
		return err
	}
	defer s.Close()
	_, err = s.Pool.Exec(ctx, "DELETE FROM sessions WHERE expires_at<=now(); DELETE FROM login_attempts WHERE expires_at<=now()")
	return err
}
