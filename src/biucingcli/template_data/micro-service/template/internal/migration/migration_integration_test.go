package migration

import (
	"context"
	"fmt"
	"github.com/jackc/pgx/v5"
	"net/url"
	"os"
	"sync"
	"testing"
	"testing/fstest"
	"time"
)

func TestMigrationLockUpgradeAndDirtyFailure(t *testing.T) {
	dsn := os.Getenv("TEST_MIGRATION_DSN")
	if dsn == "" {
		t.Skip("requires PostgreSQL migration role")
	}
	ctx := context.Background()
	conn, err := pgx.Connect(ctx, dsn)
	if err != nil {
		t.Fatal(err)
	}
	defer func() { _ = conn.Close(ctx) }()
	suffix := fmt.Sprintf("%d", time.Now().UnixNano())
	table := "migration_test_" + suffix
	data := "migration_data_" + suffix
	defer func() { _, _ = conn.Exec(ctx, "DROP TABLE IF EXISTS "+table+", "+data) }()
	u, err := url.Parse(dsn)
	if err != nil {
		t.Fatal(err)
	}
	query := u.Query()
	query.Set("x-migrations-table", table)
	u.RawQuery = query.Encode()
	target := u.String()
	first := fstest.MapFS{"sql/000001_init.up.sql": &fstest.MapFile{Data: []byte("CREATE TABLE " + data + "(id int PRIMARY KEY);")}}
	if err = Up(target, first); err != nil {
		t.Fatal(err)
	}
	second := fstest.MapFS{"sql/000001_init.up.sql": first["sql/000001_init.up.sql"], "sql/000002_expand.up.sql": &fstest.MapFile{Data: []byte("ALTER TABLE " + data + " ADD COLUMN label text;")}}
	var wg sync.WaitGroup
	results := make(chan error, 2)
	for i := 0; i < 2; i++ {
		wg.Add(1)
		go func() { defer wg.Done(); results <- Up(target, second) }()
	}
	wg.Wait()
	close(results)
	for e := range results {
		if e != nil {
			t.Fatal(e)
		}
	}
	var version int
	var dirty bool
	if err = conn.QueryRow(ctx, "SELECT version,dirty FROM "+table).Scan(&version, &dirty); err != nil || version != 2 || dirty {
		t.Fatal(version, dirty, err)
	}
	second["sql/000003_broken.up.sql"] = &fstest.MapFile{Data: []byte("BEGIN; SELECT nonexistent_function(); COMMIT;")}
	if Up(target, second) == nil {
		t.Fatal("failed migration reported success")
	}
	if Up(target, second) == nil {
		t.Fatal("dirty schema automatically retried")
	}
	if err = conn.QueryRow(ctx, "SELECT dirty FROM "+table).Scan(&dirty); err != nil || !dirty {
		t.Fatal("dirty failure not recorded", err)
	}
}
