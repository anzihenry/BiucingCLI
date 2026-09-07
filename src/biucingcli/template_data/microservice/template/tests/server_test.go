package tests

import (
	"context"
	"encoding/json"
	"net"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	servicev1 "{{MODULE_NAME}}/api/gen/go/service/v1"
	"{{MODULE_NAME}}/internal/config"
	"{{MODULE_NAME}}/internal/model"
	"{{MODULE_NAME}}/internal/router"
	"{{MODULE_NAME}}/internal/service"
	"{{MODULE_NAME}}/internal/transport"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	healthpb "google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/test/bufconn"
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

func TestGRPCPingContract(t *testing.T) {
	listener := bufconn.Listen(1024 * 1024)
	pingService := service.NewPingService("{{SERVICE_NAME}}", "{{PROTO_PACKAGE}}")
	server := transport.NewGRPCServer("{{SERVICE_NAME}}", pingService)

	go func() {
		_ = server.Serve(listener)
	}()
	t.Cleanup(func() {
		server.Stop()
		_ = listener.Close()
	})

	connection, err := grpc.NewClient(
		"passthrough:///bufnet",
		grpc.WithContextDialer(func(context.Context, string) (net.Conn, error) {
			return listener.Dial()
		}),
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		t.Fatalf("create gRPC client: %v", err)
	}
	t.Cleanup(func() { _ = connection.Close() })

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	client := servicev1.New{{SERVICE_TYPE_NAME}}ServiceClient(connection)
	healthClient := healthpb.NewHealthClient(connection)
	healthResponse, err := healthClient.Check(ctx, &healthpb.HealthCheckRequest{Service: "{{SERVICE_NAME}}"})
	if err != nil {
		t.Fatalf("check gRPC health: %v", err)
	}
	if healthResponse.GetStatus() != healthpb.HealthCheckResponse_SERVING {
		t.Fatalf("expected gRPC health status SERVING, got %s", healthResponse.GetStatus())
	}

	response, err := client.Ping(ctx, &servicev1.PingRequest{RequestId: "contract-test"})
	if err != nil {
		t.Fatalf("call Ping: %v", err)
	}

	if response.GetMessage() != "pong" {
		t.Fatalf("expected message %q, got %q", "pong", response.GetMessage())
	}
	if response.GetService() != "{{SERVICE_NAME}}" {
		t.Fatalf("expected service %q, got %q", "{{SERVICE_NAME}}", response.GetService())
	}

	expectedMethod := "/{{PROTO_PACKAGE}}.{{SERVICE_TYPE_NAME}}Service/Ping"
	if servicev1.{{SERVICE_TYPE_NAME}}Service_Ping_FullMethodName != expectedMethod {
		t.Fatalf(
			"expected full method %q, got %q",
			expectedMethod,
			servicev1.{{SERVICE_TYPE_NAME}}Service_Ping_FullMethodName,
		)
	}
}
