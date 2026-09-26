package runtime

import (
	"context"
	"encoding/json"
	"net"
	"net/http"
	"sync"
	"sync/atomic"
	"time"
)

var Version = "dev"
var Commit = "unknown"
var BuiltAt = "unknown"

type Readiness struct {
	ready    atomic.Bool
	mu       sync.RWMutex
	critical []func(context.Context) bool
}

func (r *Readiness) Set(value bool) { r.ready.Store(value) }

// Critical checks must respect context; optional telemetry must never be registered here.
func (r *Readiness) AddCritical(check func(context.Context) bool) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.critical = append(r.critical, check)
}
func (r *Readiness) Handler() http.Handler {
	mux := http.NewServeMux()
	live := func(w http.ResponseWriter, _ *http.Request) { w.WriteHeader(200) }
	mux.HandleFunc("GET /livez", live)
	mux.HandleFunc("GET /healthz", live) // migration alias, admin listener only
	mux.HandleFunc("GET /readyz", func(w http.ResponseWriter, req *http.Request) {
		if !r.ready.Load() {
			w.WriteHeader(503)
			return
		}
		ctx, cancel := context.WithTimeout(req.Context(), time.Second)
		defer cancel()
		r.mu.RLock()
		checks := append([]func(context.Context) bool{}, r.critical...)
		r.mu.RUnlock()
		for _, check := range checks {
			if !check(ctx) {
				w.WriteHeader(503)
				return
			}
		}
		w.WriteHeader(200)
	})
	mux.HandleFunc("GET /version", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]string{"version": Version, "commit": Commit, "built_at": BuiltAt})
	})
	return http.TimeoutHandler(mux, 2*time.Second, "probe timed out")
}

// BindAll closes earlier listeners on partial initialization failure.
func BindAll(addresses ...string) ([]net.Listener, error) {
	listeners := make([]net.Listener, 0, len(addresses))
	for _, addr := range addresses {
		l, err := net.Listen("tcp", addr)
		if err != nil {
			for _, previous := range listeners {
				_ = previous.Close()
			}
			return nil, err
		}
		listeners = append(listeners, l)
	}
	return listeners, nil
}
