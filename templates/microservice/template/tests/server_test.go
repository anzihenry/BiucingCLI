package tests

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/model"
	"{{MODULE_NAME}}/internal/router"
)

func TestHealthz(t *testing.T) {
	engine := router.New(config.Config{
		Service: config.ServiceConfig{
			Name:     "{{SERVICE_NAME}}",
			HTTPPort: "{{HTTP_PORT}}",
			GRPCPort: "{{GRPC_PORT}}",
		},
		Store: config.StoreConfig{
			Driver: "{{DEPENDENCY_STORE}}",
		},
	})

	request := httptest.NewRequest(http.MethodGet, "/healthz", nil)
	recorder := httptest.NewRecorder()

	engine.ServeHTTP(recorder, request)

	if recorder.Code != http.StatusOK {
		t.Fatalf("expected status %d, got %d", http.StatusOK, recorder.Code)
	}

	var response model.HealthResponse
	if err := json.Unmarshal(recorder.Body.Bytes(), &response); err != nil {
		t.Fatal(err)
	}

	if response.Service != "{{SERVICE_NAME}}" {
		t.Fatalf("expected service %q, got %q", "{{SERVICE_NAME}}", response.Service)
	}

	if response.Store != "{{DEPENDENCY_STORE}}" {
		t.Fatalf("expected store %q, got %q", "{{DEPENDENCY_STORE}}", response.Store)
	}
}

func TestPing(t *testing.T) {
	engine := router.New(config.Config{
		Service: config.ServiceConfig{
			Name:     "{{SERVICE_NAME}}",
			HTTPPort: "{{HTTP_PORT}}",
			GRPCPort: "{{GRPC_PORT}}",
		},
		Store: config.StoreConfig{
			Driver: "{{DEPENDENCY_STORE}}",
		},
	})

	request := httptest.NewRequest(http.MethodGet, "/api/v1/ping", nil)
	recorder := httptest.NewRecorder()

	engine.ServeHTTP(recorder, request)

	if recorder.Code != http.StatusOK {
		t.Fatalf("expected status %d, got %d", http.StatusOK, recorder.Code)
	}

	var response model.PingResponse
	if err := json.Unmarshal(recorder.Body.Bytes(), &response); err != nil {
		t.Fatal(err)
	}

	if response.Message != "pong" {
		t.Fatalf("expected message %q, got %q", "pong", response.Message)
	}

	if response.ProtoPackage != "{{PROTO_PACKAGE}}" {
		t.Fatalf("expected proto package %q, got %q", "{{PROTO_PACKAGE}}", response.ProtoPackage)
	}
}
