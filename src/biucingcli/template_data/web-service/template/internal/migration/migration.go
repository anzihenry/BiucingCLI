package migration

import (
	"errors"
	"github.com/golang-migrate/migrate/v4"
	_ "github.com/golang-migrate/migrate/v4/database/pgx/v5"
	"github.com/golang-migrate/migrate/v4/source/iofs"
	"io/fs"
	"net/url"
	"os"
	"time"
)

// Up uses a dedicated migration login and PostgreSQL advisory lock. It never
// clears a dirty version: an operator must inspect and repair a failed change.
func Up(dsn string, files fs.FS) error {
	u, err := url.Parse(dsn)
	if err != nil || (u.Scheme != "postgres" && u.Scheme != "postgresql") {
		return errors.New("invalid migration DSN")
	}
	u.Scheme = "pgx5"
	role := os.Getenv("DATABASE_RUNTIME_ROLE")
	if role == "" {
		role = "{{SERVICE_NAME}}_app"
	}
	q := u.Query()
	q.Set("app.runtime_role", role)
	u.RawQuery = q.Encode()
	source, err := iofs.New(files, "sql")
	if err != nil {
		return err
	}
	m, err := migrate.NewWithSourceInstance("iofs", source, u.String())
	if err != nil {
		_ = source.Close()
		return errors.New("migration initialization failed")
	}
	defer func() { _, _ = m.Close() }()
	m.LockTimeout = 15 * time.Second
	err = m.Up()
	if errors.Is(err, migrate.ErrNoChange) {
		return nil
	}
	if err != nil {
		return errors.New("migration failed; inspect schema version/dirty state before retry")
	}
	return nil
}
