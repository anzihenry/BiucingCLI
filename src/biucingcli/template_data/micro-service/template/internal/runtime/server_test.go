package runtime

import (
	"context"
	"net"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"

	"{{MODULE_NAME}}/internal/config"

	"google.golang.org/grpc"
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

type fakeGRPCServer struct {
	stopOnce       sync.Once
	stopped        chan struct{}
	servingChanges chan bool
	blockGraceful  bool
	forcedStop     chan struct{}
}

func newFakeGRPCServer(blockGraceful bool) *fakeGRPCServer {
	return &fakeGRPCServer{
		stopped:        make(chan struct{}),
		servingChanges: make(chan bool, 1),
		blockGraceful:  blockGraceful,
		forcedStop:     make(chan struct{}, 1),
	}
}

func (server *fakeGRPCServer) Serve(net.Listener) error {
	<-server.stopped
	return grpc.ErrServerStopped
}

func (server *fakeGRPCServer) GracefulStop() {
	if server.blockGraceful {
		<-server.stopped
		return
	}
	server.stopOnce.Do(func() { close(server.stopped) })
}

func (server *fakeGRPCServer) Stop() {
	server.stopOnce.Do(func() { close(server.stopped) })
	server.forcedStop <- struct{}{}
}

func (server *fakeGRPCServer) SetServing(serving bool) {
	server.servingChanges <- serving
}

func TestNewHTTPServerAppliesTimeouts(t *testing.T) {
	server := NewHTTPServer(config.Config{
		Service: config.ServiceConfig{HTTPPort: "8080"},
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

func TestServeMarksGRPCNotServingBeforeGracefulStop(t *testing.T) {
	httpListener, grpcListener := testListeners(t)
	grpcServer := newFakeGRPCServer(false)
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	if err := Serve(
		ctx,
		&http.Server{Handler: http.NewServeMux()},
		httpListener,
		grpcServer,
		grpcListener,
		time.Second,
	); err != nil {
		t.Fatal(err)
	}

	select {
	case serving := <-grpcServer.servingChanges:
		if serving {
			t.Fatal("expected gRPC health to switch to NOT_SERVING")
		}
	default:
		t.Fatal("expected a gRPC health status update")
	}
}

func TestServeForcesGRPCStopAfterTimeout(t *testing.T) {
	httpListener, grpcListener := testListeners(t)
	grpcServer := newFakeGRPCServer(true)
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	err := Serve(
		ctx,
		&http.Server{Handler: http.NewServeMux()},
		httpListener,
		grpcServer,
		grpcListener,
		25*time.Millisecond,
	)
	if err == nil {
		t.Fatal("expected the shutdown deadline to be reported")
	}

	select {
	case <-grpcServer.forcedStop:
	default:
		t.Fatal("expected gRPC Stop after the graceful shutdown deadline")
	}
}

func testListeners(t *testing.T) (net.Listener, net.Listener) {
	t.Helper()
	httpListener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	grpcListener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		_ = httpListener.Close()
		t.Fatal(err)
	}
	t.Cleanup(func() {
		_ = httpListener.Close()
		_ = grpcListener.Close()
	})
	return httpListener, grpcListener
}
