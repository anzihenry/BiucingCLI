package database

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5"
	"os"
	"testing"
	"time"
)

func TestPostgresBoundaries(t *testing.T) {
	dsn := os.Getenv("TEST_DATABASE_DSN")
	if dsn == "" {
		t.Skip("requires isolated PostgreSQL fixture")
	}
	ctx := context.Background()
	s, err := Open(ctx, dsn, Config{1, 1})
	if err != nil {
		t.Fatal(err)
	}
	defer s.Close()
	if err = s.Schema(ctx); err != nil {
		t.Fatal(err)
	}
	marker := errors.New("rollback")
	err = s.Within(ctx, func(ctx context.Context, tx pgx.Tx) error {
		_, e := tx.Exec(ctx, "INSERT INTO runtime_metadata VALUES ('rollback-test','x')")
		if e != nil {
			return e
		}
		return marker
	})
	if !errors.Is(err, marker) {
		t.Fatal(err)
	}
	var n int
	if err = s.Pool.QueryRow(ctx, "SELECT count(*) FROM runtime_metadata WHERE key='rollback-test'").Scan(&n); err != nil || n != 0 {
		t.Fatal(n, err)
	}
	started := time.Now()
	err = s.Within(ctx, func(ctx context.Context, tx pgx.Tx) error { _, e := tx.Exec(ctx, "SELECT pg_sleep(10)"); return e })
	if err == nil || time.Since(started) > 3*time.Second {
		t.Fatal("query not bounded", err)
	}
	conn, err := s.Pool.Acquire(ctx)
	if err != nil {
		t.Fatal(err)
	}
	deadline, cancel := context.WithTimeout(ctx, 50*time.Millisecond)
	defer cancel()
	_, err = s.Pool.Acquire(deadline)
	conn.Release()
	if err == nil {
		t.Fatal("pool acquisition ignored deadline")
	}
	if _, err = s.Pool.Exec(ctx, "CREATE TABLE forbidden(id int)"); err == nil {
		t.Fatal("runtime role can create tables")
	}
	if _, err = s.Pool.Exec(ctx, "UPDATE schema_migrations SET dirty=true"); err == nil {
		t.Fatal("runtime role can alter migration state")
	}
	conn, err = s.Pool.Acquire(ctx)
	if err != nil {
		t.Fatal(err)
	}
	_ = conn.Conn().Close(ctx)
	conn.Release()
	if err = s.Ping(ctx); err != nil {
		t.Fatal("pool failed to replace broken connection", err)
	}
}
