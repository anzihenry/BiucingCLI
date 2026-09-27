package observability

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"go.opentelemetry.io/otel/trace"
	"io"
	"log/slog"
	"regexp"
	"strings"
	"sync"
	"time"
)

type requestKey struct{}

var validID = regexp.MustCompile(`^[a-zA-Z0-9_-]{1,64}$`)

func RequestID(value string) string {
	if validID.MatchString(value) {
		return value
	}
	var b [16]byte
	if _, err := rand.Read(b[:]); err != nil {
		panic("random source unavailable")
	}
	return hex.EncodeToString(b[:])
}
func WithRequestID(ctx context.Context, id string) context.Context {
	return context.WithValue(ctx, requestKey{}, id)
}
func ID(ctx context.Context) string { value, _ := ctx.Value(requestKey{}).(string); return value }
func New(out io.Writer, level string) *slog.Logger {
	var l slog.Level
	_ = l.UnmarshalText([]byte(level))
	return slog.New(slog.NewJSONHandler(out, &slog.HandlerOptions{Level: l, ReplaceAttr: func(_ []string, a slog.Attr) slog.Attr {
		key := strings.ToLower(a.Key)
		for _, sensitive := range []string{"password", "secret", "token", "authorization", "cookie", "dsn", "private_key"} {
			if strings.Contains(key, sensitive) {
				return slog.String(a.Key, "[REDACTED]")
			}
		}
		return a
	}}))
}

// One process-wide budget bounds access/denial logs; no per-user map or unbounded queue.
// Applications must never pass raw URLs, bodies, credentials or arbitrary errors here.
type Events struct {
	Logger  *slog.Logger
	mu      sync.Mutex
	second  int64
	count   int
	dropped int
}

func (e *Events) emit(ctx context.Context, kind, action, outcome string, attrs ...any) {
	e.mu.Lock()
	now := time.Now().Unix()
	if e.second != now {
		if e.dropped > 0 {
			e.Logger.Warn("log budget exceeded", "kind", "log_drop", "count", e.dropped)
		}
		e.second, e.count, e.dropped = now, 0, 0
	}
	if e.count >= 100 {
		e.dropped++
		e.mu.Unlock()
		return
	}
	e.count++
	e.mu.Unlock()
	args := []any{"kind", kind, "action", action, "outcome", outcome, "request_id", ID(ctx)}
	if sc := trace.SpanContextFromContext(ctx); sc.IsValid() {
		args = append(args, "trace_id", sc.TraceID().String(), "span_id", sc.SpanID().String())
	}
	e.Logger.InfoContext(ctx, "request event", append(args, attrs...)...)
}
func (e *Events) Access(ctx context.Context, route string, status int, elapsed time.Duration) {
	e.emit(ctx, "access", route, "completed", "status", status, "duration_ms", elapsed.Milliseconds())
}

// Audit is a separate typed event channel. Storage, durability and retention belong to the platform.
func (e *Events) Audit(ctx context.Context, action string, allowed bool) {
	outcome := "denied"
	if allowed {
		outcome = "allowed"
	}
	switch action {
	case "authorize", "configure", "startup", "shutdown":
	default:
		action = "other"
	}
	e.emit(ctx, "audit", action, outcome)
}
