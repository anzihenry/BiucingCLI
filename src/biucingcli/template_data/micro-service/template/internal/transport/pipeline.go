package transport

import (
	"context"
	"errors"
	"time"

	"google.golang.org/genproto/googleapis/rpc/errdetails"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
	"{{MODULE_NAME}}/internal/observability"
	"{{MODULE_NAME}}/internal/pipeline"
	"{{MODULE_NAME}}/internal/security"
)

type Gate struct {
	authenticate func(context.Context, string) (context.Context, error)
	limits       pipeline.Limits
	slots        chan struct{}
	policy       security.Policy
	public       map[string]bool
	events       *observability.Events
}

func NewGate(limits pipeline.Limits, policy security.Policy, public map[string]bool, events *observability.Events) *Gate {
	l := limits.Defaults()
	return &Gate{limits: l, slots: make(chan struct{}, l.Concurrent), policy: policy, public: public, events: events}
}
func (g *Gate) admit(ctx context.Context, method string) (context.Context, context.CancelFunc, error) {
	if g.authenticate != nil {
		verified, err := g.authenticate(ctx, method)
		if err != nil {
			code := codes.Unauthenticated
			if errors.Is(err, security.ErrWorkloadDenied) {
				code = codes.PermissionDenied
			}
			return ctx, func() {}, status.Error(code, "workload denied")
		}
		ctx = verified
	}
	md, _ := metadata.FromIncomingContext(ctx)
	value := ""
	if ids := md.Get("x-request-id"); len(ids) == 1 {
		value = ids[0]
	}
	ctx = observability.WithRequestID(ctx, observability.RequestID(value))
	if !g.public[method] && !security.Authorized(ctx, method, g.policy) {
		g.events.Audit(ctx, "authorize", false)
		code := codes.Unauthenticated
		if _, ok := security.FromContext(ctx); ok {
			code = codes.PermissionDenied
		}
		return ctx, func() {}, status.Error(code, "access denied")
	}
	if !g.public[method] {
		g.events.Audit(ctx, "authorize", true)
	}
	select {
	case g.slots <- struct{}{}:
	default:
		return ctx, func() {}, status.Error(codes.ResourceExhausted, "overloaded")
	}
	child, cancel := context.WithTimeout(ctx, g.limits.Timeout)
	return child, cancel, nil
}
func safeCall(call func() (any, error)) (value any, err error) {
	defer func() {
		if recover() != nil {
			value = nil
			err = status.Error(codes.Internal, "internal error")
		}
	}()
	return call()
}
func (g *Gate) Unary(ctx context.Context, req any, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (response any, callErr error) {
	ctx, cancel, err := g.admit(ctx, info.FullMethod)
	defer cancel()
	if err != nil {
		return nil, err
	}
	_ = grpc.SetHeader(ctx, metadata.Pairs("x-request-id", observability.ID(ctx)))
	type result struct {
		value any
		err   error
	}
	done := make(chan result, 1)
	start := time.Now()
	go func() {
		v, e := safeCall(func() (any, error) {
			if err := validateMessage(req); err != nil {
				return nil, err
			}
			return handler(ctx, req)
		})
		<-g.slots
		done <- result{v, e}
	}()
	defer func() { g.events.Access(ctx, info.FullMethod, int(status.Code(callErr)), time.Since(start)) }()
	select {
	case r := <-done:
		return r.value, publicError(r.err)
	case <-ctx.Done():
		return nil, status.FromContextError(ctx.Err()).Err()
	}
}

type boundedStream struct {
	grpc.ServerStream
	ctx context.Context
}

func (s *boundedStream) Context() context.Context { return s.ctx }
func (s *boundedStream) RecvMsg(value any) error {
	if err := s.ctx.Err(); err != nil {
		return status.FromContextError(err).Err()
	}
	if err := s.ServerStream.RecvMsg(value); err != nil {
		return err
	}
	return validateMessage(value)
}
func (s *boundedStream) SendMsg(value any) error {
	if err := s.ctx.Err(); err != nil {
		return status.FromContextError(err).Err()
	}
	return s.ServerStream.SendMsg(value)
}
func (g *Gate) Stream(srv any, stream grpc.ServerStream, info *grpc.StreamServerInfo, handler grpc.StreamHandler) (callErr error) {
	ctx, cancel, err := g.admit(stream.Context(), info.FullMethod)
	defer cancel()
	if err != nil {
		return err
	}
	_ = stream.SetHeader(metadata.Pairs("x-request-id", observability.ID(ctx)))
	done := make(chan error, 1)
	start := time.Now()
	go func() {
		_, err := safeCall(func() (any, error) { return nil, handler(srv, &boundedStream{stream, ctx}) })
		<-g.slots
		done <- err
	}()
	defer func() { g.events.Access(ctx, info.FullMethod, int(status.Code(callErr)), time.Since(start)) }()
	select {
	case err := <-done:
		return publicError(err)
	case <-ctx.Done():
		return status.FromContextError(ctx.Err()).Err()
	}
}

func publicError(err error) error {
	if err == nil {
		return nil
	}
	if errors.Is(err, context.Canceled) || errors.Is(err, context.DeadlineExceeded) {
		return status.FromContextError(err).Err()
	}
	code := status.Code(err)
	if code == codes.Unknown {
		code = codes.Internal
	}
	safe := status.New(code, code.String())
	withDetails, e := safe.WithDetails(&errdetails.ErrorInfo{Reason: code.String(), Domain: "rpc.service"})
	if e != nil {
		return safe.Err()
	}
	return withDetails.Err()
}
func validateMessage(value any) error {
	if validator, ok := value.(interface{ Validate() error }); ok && validator.Validate() != nil {
		return status.Error(codes.InvalidArgument, "InvalidArgument")
	}
	return nil
}
