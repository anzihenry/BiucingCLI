package pipeline

import (
	"bytes"
	"context"
	"errors"
	"io"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"{{MODULE_NAME}}/internal/observability"
	"{{MODULE_NAME}}/internal/security"
)

type Limits struct {
	MaxBytes   int64
	Concurrent int
	Timeout    time.Duration
}

func (l Limits) Defaults() Limits {
	if l.MaxBytes <= 0 {
		l.MaxBytes = 1 << 20
	}
	if l.Concurrent <= 0 {
		l.Concurrent = 64
	}
	if l.Timeout <= 0 {
		l.Timeout = 5 * time.Second
	}
	return l
}
func Middleware(limits Limits, public map[string]bool, policy security.Policy, events *observability.Events, identity ...gin.HandlerFunc) gin.HandlerFunc {
	l := limits.Defaults()
	slots := make(chan struct{}, l.Concurrent)
	return func(c *gin.Context) {
		started := time.Now()
		id := observability.RequestID(c.GetHeader("X-Request-ID"))
		ctx := observability.WithRequestID(c.Request.Context(), id)
		c.Request = c.Request.WithContext(ctx)
		c.Header("X-Request-ID", id)
		route := c.FullPath()
		if route == "" {
			route = "unmatched"
		}
		defer func() {
			if recover() != nil {
				c.AbortWithStatusJSON(500, gin.H{"error": "internal_error"})
			}
			events.Access(ctx, route, c.Writer.Status(), time.Since(started))
		}()
		select {
		case slots <- struct{}{}:
			defer func() { <-slots }()
		default:
			c.AbortWithStatusJSON(429, gin.H{"error": "overloaded"})
			return
		}
		for _, authenticate := range identity {
			authenticate(c)
			if c.IsAborted() {
				if c.Writer.Status() >= 400 {
					events.Audit(c.Request.Context(), "authorize", false)
				}
				return
			}
		}
		ctx = c.Request.Context()
		action := c.Request.Method + " " + c.FullPath()
		if !public[action] && !security.Authorized(ctx, action, policy) {
			events.Audit(ctx, "authorize", false)
			code := 401
			if _, ok := security.FromContext(ctx); ok {
				code = 403
			}
			c.AbortWithStatusJSON(code, gin.H{"error": "access_denied"})
			return
		}
		if !public[action] {
			events.Audit(ctx, "authorize", true)
		}
		// Read at most the configured limit before handing bytes to a decoder, including chunked bodies.
		if c.Request.Body != nil {
			c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, l.MaxBytes)
			body, err := io.ReadAll(c.Request.Body)
			if err != nil {
				var tooLarge *http.MaxBytesError
				code := 400
				if errors.As(err, &tooLarge) {
					code = 413
				}
				c.AbortWithStatusJSON(code, gin.H{"error": "invalid_body"})
				return
			}
			c.Request.Body = io.NopCloser(bytes.NewReader(body))
		}
		c.Next()
	}
}

// TimeoutHandler bounds the client response. The admission slot stays held until a
// cooperative handler exits; an uncooperative handler cannot cause unbounded new work.
func Bounded(handler http.Handler, limits Limits) http.Handler {
	l := limits.Defaults()
	return http.TimeoutHandler(handler, l.Timeout, `{"error":"deadline_exceeded"}`)
}

// ChildContext keeps an earlier upstream deadline and propagates cancellation.
func ChildContext(ctx context.Context, timeout time.Duration) (context.Context, context.CancelFunc) {
	return context.WithTimeout(ctx, timeout)
}
