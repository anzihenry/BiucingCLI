package pipeline

import (
	"bytes"
	"context"
	"github.com/gin-gonic/gin"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
	"{{MODULE_NAME}}/internal/observability"
	"{{MODULE_NAME}}/internal/security"
)

func engine(l Limits, policy security.Policy, public bool, handler gin.HandlerFunc) http.Handler {
	gin.SetMode(gin.ReleaseMode)
	e := gin.New()
	e.Use(Middleware(l, map[string]bool{"POST /test": public}, policy, &observability.Events{Logger: observability.New(io.Discard, "INFO")}))
	e.POST("/test", handler)
	return Bounded(e, l)
}
func TestDenyByDefaultAndVerifiedPrincipal(t *testing.T) {
	policy := func(_ context.Context, p security.Principal, _ string) bool { return p.Subject == "allowed" }
	handler := engine(Limits{}, policy, false, func(c *gin.Context) { c.Status(204) })
	for _, subject := range []string{"", "denied", "allowed"} {
		req := httptest.NewRequest("POST", "/test", nil)
		req.Header.Set("X-User-ID", "allowed")
		if subject != "" {
			req = req.WithContext(security.WithPrincipal(req.Context(), security.Principal{Subject: subject}))
		}
		rec := httptest.NewRecorder()
		handler.ServeHTTP(rec, req)
		expected := 401
		if subject == "denied" {
			expected = 403
		}
		if subject == "allowed" {
			expected = 204
		}
		if rec.Code != expected {
			t.Fatalf("subject %s: status %d", subject, rec.Code)
		}
	}
}
func TestBodyLimitIncludesUnknownLengthAndPanicIsPrivate(t *testing.T) {
	handler := engine(Limits{MaxBytes: 4}, nil, true, func(_ *gin.Context) { panic("secret-token") })
	for _, body := range []string{"12345", "ok"} {
		req := httptest.NewRequest("POST", "/test", strings.NewReader(body))
		req.ContentLength = -1
		req.Header.Set("X-Request-ID", strings.Repeat("x", 1000))
		rec := httptest.NewRecorder()
		handler.ServeHTTP(rec, req)
		expected := 500
		if len(body) > 4 {
			expected = 413
		}
		if rec.Code != expected || strings.Contains(rec.Body.String(), "secret-token") {
			t.Fatalf("response %d %s", rec.Code, rec.Body)
		}
		if len(rec.Header().Get("X-Request-ID")) > 64 {
			t.Fatal("unbounded request ID")
		}
	}
}
func TestDeadlineKeepsAdmissionSlotUntilHandlerExits(t *testing.T) {
	started := make(chan struct{})
	release := make(chan struct{})
	finished := make(chan struct{})
	handler := engine(Limits{Concurrent: 1, Timeout: 30 * time.Millisecond}, nil, true, func(c *gin.Context) { close(started); <-release; close(finished) })
	first := httptest.NewRecorder()
	done := make(chan struct{})
	go func() { handler.ServeHTTP(first, httptest.NewRequest("POST", "/test", nil)); close(done) }()
	<-started
	<-done
	if first.Code != 503 {
		t.Fatalf("timeout status %d", first.Code)
	}
	second := httptest.NewRecorder()
	handler.ServeHTTP(second, httptest.NewRequest("POST", "/test", nil))
	if second.Code != 429 {
		t.Fatalf("lost admission slot: %d", second.Code)
	}
	close(release)
	<-finished
}
func TestRequestLogsExcludeBodiesHeadersAndQuery(t *testing.T) {
	var out bytes.Buffer
	gin.SetMode(gin.ReleaseMode)
	e := gin.New()
	e.Use(Middleware(Limits{}, map[string]bool{"POST /test": true}, nil, &observability.Events{Logger: observability.New(&out, "INFO")}))
	e.POST("/test", func(c *gin.Context) { c.Status(204) })
	req := httptest.NewRequest("POST", "/test?token=private", strings.NewReader("body-secret"))
	req.Header.Set("Authorization", "Bearer auth-secret")
	req.Header.Set("Cookie", "session=cookie-secret")
	e.ServeHTTP(httptest.NewRecorder(), req)
	for _, value := range []string{"private", "body-secret", "auth-secret", "cookie-secret"} {
		if strings.Contains(out.String(), value) {
			t.Fatal("sensitive request data logged")
		}
	}
	if !strings.Contains(out.String(), "request_id") {
		t.Fatal("missing correlation")
	}
}

func TestDecodeJSONRejectsUnknownFieldsAndTrailingDocuments(t *testing.T) {
	for _, body := range []string{`{"unknown":true}`, `{"name":"ok"} {"name":"extra"}`, `{"name":42}`} {
		var request struct {
			Name string `json:"name"`
		}
		if DecodeJSON(strings.NewReader(body), &request) == nil {
			t.Fatalf("accepted invalid payload: %s", body)
		}
	}
	var request struct {
		Name string `json:"name"`
	}
	if err := DecodeJSON(strings.NewReader(`{"name":"ok"}`), &request); err != nil {
		t.Fatal(err)
	}
}

func TestIdentityHookRunsInsideGate(t *testing.T) {
	gin.SetMode(gin.ReleaseMode)
	e := gin.New()
	e.Use(Middleware(Limits{}, nil, func(_ context.Context, p security.Principal, _ string) bool { return p.Subject == "verified" }, &observability.Events{Logger: observability.New(io.Discard, "INFO")}, func(c *gin.Context) {
		c.Request = c.Request.WithContext(security.WithPrincipal(c.Request.Context(), security.Principal{Subject: "verified"}))
	}))
	e.GET("/private", func(c *gin.Context) { c.Status(204) })
	rec := httptest.NewRecorder()
	e.ServeHTTP(rec, httptest.NewRequest("GET", "/private", nil))
	if rec.Code != 204 {
		t.Fatal("verified context was lost before policy", rec.Code)
	}
}
