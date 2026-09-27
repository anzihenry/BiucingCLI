package database

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"strconv"
	"time"
)

type Config struct {
	MaxConnections      int32 `yaml:"max_connections"`
	QueryTimeoutSeconds int   `yaml:"query_timeout_seconds"`
}

func (c Config) Validate() error {
	if c.MaxConnections < 1 || c.MaxConnections > 100 || c.QueryTimeoutSeconds < 1 || c.QueryTimeoutSeconds > 60 {
		return errors.New("invalid database connection or query budget")
	}
	return nil
}

type Store struct {
	Pool    *pgxpool.Pool
	timeout time.Duration
}

func Open(ctx context.Context, dsn string, cfg Config) (*Store, error) {
	if err := cfg.Validate(); err != nil {
		return nil, err
	}
	c, err := pgxpool.ParseConfig(dsn)
	if err != nil {
		return nil, errors.New("invalid database configuration")
	}
	c.MaxConns = cfg.MaxConnections
	c.MinConns = 0
	c.MaxConnLifetime = 30 * time.Minute
	c.MaxConnLifetimeJitter = 5 * time.Minute
	c.MaxConnIdleTime = 5 * time.Minute
	c.ConnConfig.ConnectTimeout = 5 * time.Second
	c.ConnConfig.RuntimeParams["statement_timeout"] = strconv.Itoa(cfg.QueryTimeoutSeconds * 1000)
	c.ConnConfig.RuntimeParams["idle_in_transaction_session_timeout"] = "10000"
	pool, err := pgxpool.NewWithConfig(ctx, c)
	if err != nil {
		return nil, errors.New("database pool initialization failed")
	}
	s := &Store{pool, time.Duration(cfg.QueryTimeoutSeconds) * time.Second}
	if err = s.Ping(ctx); err != nil {
		pool.Close()
		return nil, errors.New("database unavailable")
	}
	return s, nil
}

// A caller that ignores cancellation must not make process shutdown unbounded.
func (s *Store) Close() {
	done := make(chan struct{})
	go func() { s.Pool.Close(); close(done) }()
	timer := time.NewTimer(5 * time.Second)
	defer timer.Stop()
	select {
	case <-done:
	case <-timer.C:
	}
}
func (s *Store) Context(ctx context.Context) (context.Context, context.CancelFunc) {
	return context.WithTimeout(ctx, s.timeout)
}
func (s *Store) Ping(ctx context.Context) error {
	ctx, cancel := s.Context(ctx)
	defer cancel()
	return s.Pool.Ping(ctx)
}

// Within bounds acquisition and the whole transaction. Rollback uses its own finite
// context so cancellation of the request does not strand an open transaction.
func (s *Store) Within(ctx context.Context, fn func(context.Context, pgx.Tx) error) error {
	ctx, cancel := s.Context(ctx)
	defer cancel()
	tx, err := s.Pool.BeginTx(ctx, pgx.TxOptions{})
	if err != nil {
		return err
	}
	defer func() {
		cleanup, stop := context.WithTimeout(context.Background(), time.Second)
		defer stop()
		_ = tx.Rollback(cleanup)
	}()
	if err = fn(ctx, tx); err != nil {
		return err
	}
	return tx.Commit(ctx)
}

// Compatibility is an explicit range, not automatically "latest". Dirty or
// unknown versions fail readiness before this application accepts traffic.
func (s *Store) Schema(ctx context.Context) error {
	ctx, cancel := s.Context(ctx)
	defer cancel()
	var version int
	var dirty bool
	if err := s.Pool.QueryRow(ctx, "SELECT version, dirty FROM schema_migrations").Scan(&version, &dirty); err != nil {
		return errors.New("schema unavailable; run migration separately")
	}
	var unsafe bool
	if err := s.Pool.QueryRow(ctx, "SELECT rolsuper OR rolcreatedb OR rolcreaterole OR has_schema_privilege(current_user,'public','CREATE') OR has_table_privilege(current_user,'schema_migrations','INSERT,UPDATE,DELETE') FROM pg_roles WHERE rolname=current_user").Scan(&unsafe); err != nil || unsafe {
		return errors.New("runtime database role has unsafe privileges")
	}
	if dirty || version != 1 {
		return errors.New("incompatible schema")
	}
	return nil
}
