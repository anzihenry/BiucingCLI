package transport

import (
	"context"
	"errors"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
	"io"
	"testing"
	"time"
	"{{MODULE_NAME}}/internal/observability"
	"{{MODULE_NAME}}/internal/pipeline"
	"{{MODULE_NAME}}/internal/security"
)

func gate(limit int, public bool) *Gate {
	return NewGate(pipeline.Limits{Concurrent: limit, Timeout: 25 * time.Millisecond}, nil, map[string]bool{"/test": public}, &observability.Events{Logger: observability.New(io.Discard, "INFO")})
}
func TestUnaryDenialPanicValidationAndDeadline(t *testing.T) {
	info := &grpc.UnaryServerInfo{FullMethod: "/test"}
	g := gate(1, false)
	_, err := g.Unary(metadata.NewIncomingContext(context.Background(), metadata.Pairs("x-user-id", "admin")), nil, info, func(context.Context, any) (any, error) {
		t.Fatal("unverified metadata bypassed policy")
		return nil, nil
	})
	if status.Code(err) != codes.Unauthenticated {
		t.Fatal(err)
	}
	g = gate(1, true)
	_, err = g.Unary(context.Background(), nil, info, func(context.Context, any) (any, error) { panic("token-secret") })
	if status.Code(err) != codes.Internal || status.Convert(err).Message() != "Internal" {
		t.Fatal(err)
	}
	_, err = g.Unary(context.Background(), invalidMessage{}, info, func(context.Context, any) (any, error) { t.Fatal("invalid message reached handler"); return nil, nil })
	if status.Code(err) != codes.InvalidArgument {
		t.Fatal(err)
	}
	release := make(chan struct{})
	done := make(chan struct{})
	_, err = g.Unary(context.Background(), nil, info, func(ctx context.Context, _ any) (any, error) { <-release; close(done); return nil, nil })
	if status.Code(err) != codes.DeadlineExceeded {
		t.Fatal(err)
	}
	_, err = g.Unary(context.Background(), nil, info, func(context.Context, any) (any, error) { return nil, nil })
	if status.Code(err) != codes.ResourceExhausted {
		t.Fatal("timed out work released its budget early", err)
	}
	close(release)
	<-done
}

type invalidMessage struct{}

func (invalidMessage) Validate() error { return errors.New("secret invalid field") }

type testStream struct {
	grpc.ServerStream
	ctx   context.Context
	block chan struct{}
}

func (s *testStream) Context() context.Context    { return s.ctx }
func (s *testStream) SetHeader(metadata.MD) error { return nil }
func (s *testStream) RecvMsg(any) error           { <-s.block; return io.EOF }
func TestStreamUsesSameAuthorizationAndBoundedDeadline(t *testing.T) {
	stream := &testStream{ctx: context.Background(), block: make(chan struct{})}
	info := &grpc.StreamServerInfo{FullMethod: "/test"}
	if err := gate(1, false).Stream(nil, stream, info, func(any, grpc.ServerStream) error { t.Fatal("stream bypassed authorization"); return nil }); status.Code(err) != codes.Unauthenticated {
		t.Fatal(err)
	}
	g := gate(1, true)
	done := make(chan struct{})
	err := g.Stream(nil, stream, info, func(_ any, s grpc.ServerStream) error { defer close(done); return s.RecvMsg(nil) })
	if status.Code(err) != codes.DeadlineExceeded {
		t.Fatal(err)
	}
	err = g.Stream(nil, stream, info, func(any, grpc.ServerStream) error { return nil })
	if status.Code(err) != codes.ResourceExhausted {
		t.Fatal(err)
	}
	close(stream.block)
	<-done
}
func TestVerifiedServiceStillRequiresPolicy(t *testing.T) {
	ctx := security.WithPrincipal(context.Background(), security.Principal{Workload: "verified-service"})
	_, err := gate(1, false).Unary(ctx, nil, &grpc.UnaryServerInfo{FullMethod: "/test"}, func(context.Context, any) (any, error) { return nil, nil })
	if status.Code(err) != codes.PermissionDenied {
		t.Fatal(err)
	}
}
