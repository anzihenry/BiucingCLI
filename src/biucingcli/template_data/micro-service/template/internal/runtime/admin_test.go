package runtime

import (
	"context"
	"net"
	"net/http/httptest"
	"testing"
)

func TestReadinessAndLivenessAreIndependent(t *testing.T) {
	state := &Readiness{}
	handler := state.Handler()
	check := func(path string, code int) {
		t.Helper()
		w := httptest.NewRecorder()
		handler.ServeHTTP(w, httptest.NewRequest("GET", path, nil))
		if w.Code != code {
			t.Fatalf("%s: %d", path, w.Code)
		}
	}
	check("/livez", 200)
	check("/readyz", 503)
	state.Set(true)
	check("/readyz", 200)
	state.AddCritical(func(context.Context) bool { return false })
	check("/readyz", 503)
	check("/livez", 200)
	state.Set(false)
	check("/readyz", 503)
	check("/debug/pprof", 404)
}
func TestBindAllRollsBackPartialStartup(t *testing.T) {
	occupied, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer func() { _ = occupied.Close() }()
	available, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	addr := available.Addr().String()
	_ = available.Close()
	if _, err := BindAll(addr, occupied.Addr().String()); err == nil {
		t.Fatal("expected startup failure")
	}
	retry, err := net.Listen("tcp", addr)
	if err != nil {
		t.Fatal("partial listener leaked")
	}
	_ = retry.Close()
}
