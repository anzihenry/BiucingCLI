package main

import (
	"fmt"
	"os"
	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/migration"
	"{{MODULE_NAME}}/migrations"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
func run() error {
	dsn, err := config.MigrationDSN()
	if err != nil {
		return err
	}
	return migration.Up(dsn, migrations.Files)
}
