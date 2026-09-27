package tests

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"context"
	"github.com/gin-gonic/gin"
	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/model"
	"{{MODULE_NAME}}/internal/router"
	"{{MODULE_NAME}}/internal/security"
)

func TestHealthzIsNotPublic(t *testing.T) {
	engine := router.New(config.Config{})
	response := httptest.NewRecorder()
	engine.ServeHTTP(response, httptest.NewRequest("GET", "/healthz", nil))
	if response.Code == http.StatusOK {
		t.Fatal("admin health exposed on application listener")
	}
}

func TestPing(t *testing.T) {
	engine := testRouter(config.Config{
		Service: config.ServiceConfig{
			Name: "{{SERVICE_NAME}}",
			Port: "{{HTTP_PORT}}",
		},
	})

	request := httptest.NewRequest(http.MethodGet, "/api/v1/ping", nil)
	request = request.WithContext(security.WithPrincipal(request.Context(), security.Principal{Subject: "fixture"}))
	recorder := httptest.NewRecorder()

	engine.ServeHTTP(recorder, request)

	if recorder.Code != http.StatusOK {
		t.Fatalf("expected status %d, got %d", http.StatusOK, recorder.Code)
	}

	var response model.PingResponse
	if err := json.Unmarshal(recorder.Body.Bytes(), &response); err != nil {
		t.Fatal(err)
	}

	if response.Service != "{{SERVICE_NAME}}" {
		t.Fatalf("expected service %q, got %q", "{{SERVICE_NAME}}", response.Service)
	}

	if response.Message != "pong" {
		t.Fatalf("expected message %q, got %q", "pong", response.Message)
	}

	if response.Version != "v1" {
		t.Fatalf("expected version %q, got %q", "v1", response.Version)
	}
}

func testRouter(cfg config.Config) *gin.Engine {
	return router.New(cfg, router.Options{Policy: func(_ context.Context, p security.Principal, _ string) bool { return p.Subject == "fixture" }})
}
