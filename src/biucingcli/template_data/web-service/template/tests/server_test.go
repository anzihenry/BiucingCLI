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

func TestListUsers(t *testing.T) {
	engine := testRouter(config.Config{
		Service: config.ServiceConfig{
			Name: "{{SERVICE_NAME}}",
			Port: "{{HTTP_PORT}}",
		},
	})

	request := httptest.NewRequest(http.MethodGet, "/api/v1/users", nil)
	request = request.WithContext(security.WithPrincipal(request.Context(), security.Principal{Subject: "fixture"}))
	recorder := httptest.NewRecorder()

	engine.ServeHTTP(recorder, request)

	if recorder.Code != http.StatusOK {
		t.Fatalf("expected status %d, got %d", http.StatusOK, recorder.Code)
	}

	var response struct {
		Items []model.User `json:"items"`
	}
	if err := json.Unmarshal(recorder.Body.Bytes(), &response); err != nil {
		t.Fatal(err)
	}

	if len(response.Items) != 2 {
		t.Fatalf("expected %d users, got %d", 2, len(response.Items))
	}

	if response.Items[0].ID != "u_001" {
		t.Fatalf("expected first user id %q, got %q", "u_001", response.Items[0].ID)
	}
}

func TestGetUser(t *testing.T) {
	engine := testRouter(config.Config{
		Service: config.ServiceConfig{
			Name: "{{SERVICE_NAME}}",
			Port: "{{HTTP_PORT}}",
		},
	})

	request := httptest.NewRequest(http.MethodGet, "/api/v1/users/u_002", nil)
	request = request.WithContext(security.WithPrincipal(request.Context(), security.Principal{Subject: "fixture"}))
	recorder := httptest.NewRecorder()

	engine.ServeHTTP(recorder, request)

	if recorder.Code != http.StatusOK {
		t.Fatalf("expected status %d, got %d", http.StatusOK, recorder.Code)
	}

	var response model.User
	if err := json.Unmarshal(recorder.Body.Bytes(), &response); err != nil {
		t.Fatal(err)
	}

	if response.ID != "u_002" {
		t.Fatalf("expected user id %q, got %q", "u_002", response.ID)
	}

	if response.Email != "alan@example.com" {
		t.Fatalf("expected email %q, got %q", "alan@example.com", response.Email)
	}
}

func TestGetUserNotFound(t *testing.T) {
	engine := testRouter(config.Config{
		Service: config.ServiceConfig{
			Name: "{{SERVICE_NAME}}",
			Port: "{{HTTP_PORT}}",
		},
	})

	request := httptest.NewRequest(http.MethodGet, "/api/v1/users/u_999", nil)
	request = request.WithContext(security.WithPrincipal(request.Context(), security.Principal{Subject: "fixture"}))
	recorder := httptest.NewRecorder()

	engine.ServeHTTP(recorder, request)

	if recorder.Code != http.StatusNotFound {
		t.Fatalf("expected status %d, got %d", http.StatusNotFound, recorder.Code)
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
