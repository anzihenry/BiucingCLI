package observability

import (
	"bytes"
	"context"
	"strings"
	"testing"
)

func TestRedactionAndLogBudget(t *testing.T) {
	var out bytes.Buffer
	logger := New(&out, "INFO")
	logger.Info("config", "database_dsn", "credential-secret", "Authorization", "bearer-secret")
	if strings.Contains(out.String(), "credential-secret") || strings.Contains(out.String(), "bearer-secret") {
		t.Fatal("secret leaked")
	}
	events := &Events{Logger: logger}
	for i := 0; i < 10000; i++ {
		events.Audit(context.Background(), "authorize", false)
	}
	if strings.Count(out.String(), "\n") > 205 {
		t.Fatal("unbounded audit flood")
	}
	if !strings.Contains(out.String(), `"kind":"audit"`) {
		t.Fatal("missing audit category")
	}
}
