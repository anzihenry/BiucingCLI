package runtime

import (
	"context"
	"errors"
	"net"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"{{MODULE_NAME}}/internal/config"
)

func TestCheckHealthRequiresSuccessfulResponse(t *testing.T) {
	healthServer := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.URL.Path != "/healthz" {
			writer.WriteHeader(http.StatusNotFound)
			return
		}
		writer.WriteHeader(http.StatusOK)
	}))
	defer healthServer.Close()

	if err := CheckHealth(context.Background(), healthServer.URL+"/healthz"); err != nil {
		t.Fatal(err)
	}
	if err := CheckHealth(context.Background(), healthServer.URL+"/missing"); err == nil {
		t.Fatal("expected a non-success status to fail the health check")
	}
}

func TestNewHTTPServerAppliesTimeouts(t *testing.T) {
	server := NewHTTPServer(config.Config{
		Service: config.ServiceConfig{Port: "8080"},
		Server: config.ServerConfig{
			ReadTimeoutSeconds:       1,
			ReadHeaderTimeoutSeconds: 2,
			WriteTimeoutSeconds:      3,
			IdleTimeoutSeconds:       4,
		},
	}, http.NewServeMux())

	if server.ReadTimeout != time.Second || server.ReadHeaderTimeout != 2*time.Second {
		t.Fatalf("unexpected read timeouts: %s, %s", server.ReadTimeout, server.ReadHeaderTimeout)
	}
	if server.WriteTimeout != 3*time.Second || server.IdleTimeout != 4*time.Second {
		t.Fatalf("unexpected connection timeouts: %s, %s", server.WriteTimeout, server.IdleTimeout)
	}
}

func TestServeDrainsInFlightRequest(t *testing.T) {
	requestStarted := make(chan struct{})
	releaseRequest := make(chan struct{})
	handler := http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		close(requestStarted)
		<-releaseRequest
		writer.WriteHeader(http.StatusNoContent)
	})

	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}

	ctx, cancel := context.WithCancel(context.Background())
	serveDone := make(chan error, 1)
	go func() {
		serveDone <- Serve(ctx, &http.Server{Handler: handler}, listener, time.Second)
	}()

	requestDone := make(chan error, 1)
	go func() {
		response, requestErr := http.Get("http://" + listener.Addr().String())
		if response != nil {
			_ = response.Body.Close()
		}
		requestDone <- requestErr
	}()

	select {
	case <-requestStarted:
	case <-time.After(time.Second):
		t.Fatal("request did not reach the server")
	}

	cancel()
	select {
	case err := <-serveDone:
		t.Fatalf("server returned before the request drained: %v", err)
	case <-time.After(25 * time.Millisecond):
	}

	close(releaseRequest)
	if err := <-requestDone; err != nil {
		t.Fatal(err)
	}
	if err := <-serveDone; err != nil {
		t.Fatal(err)
	}
}

func TestServeEnforcesShutdownTimeout(t *testing.T) {
	requestStarted := make(chan struct{})
	handler := http.HandlerFunc(func(_ http.ResponseWriter, request *http.Request) {
		close(requestStarted)
		<-request.Context().Done()
	})

	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}

	ctx, cancel := context.WithCancel(context.Background())
	serveDone := make(chan error, 1)
	go func() {
		serveDone <- Serve(ctx, &http.Server{Handler: handler}, listener, 25*time.Millisecond)
	}()
	go func() {
		_, _ = http.Get("http://" + listener.Addr().String())
	}()

	select {
	case <-requestStarted:
	case <-time.After(time.Second):
		t.Fatal("request did not reach the server")
	}
	cancel()

	select {
	case err := <-serveDone:
		if !errors.Is(err, context.DeadlineExceeded) {
			t.Fatalf("expected shutdown deadline, got %v", err)
		}
	case <-time.After(time.Second):
		t.Fatal("shutdown timeout was not enforced")
	}
}
