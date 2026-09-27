package outbound

import (
	"bytes"
	"context"
	"crypto/tls"
	"crypto/x509"
	"errors"
	"{{MODULE_NAME}}/internal/observability"
	"{{MODULE_NAME}}/internal/security"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/propagation"
	"google.golang.org/grpc"
	_ "google.golang.org/grpc/balancer/roundrobin"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
	"io"
	"net"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"
	"time"
)

var label = regexp.MustCompile(`^[a-z][a-z0-9_-]{0,47}$`)

type Config struct {
	Protocol    string               `yaml:"protocol"`
	Address     string               `yaml:"address"`
	ServerName  string               `yaml:"server_name"`
	Identity    string               `yaml:"identity"`
	Certificate string               `yaml:"certificate"`
	Key         string               `yaml:"key"`
	Roots       string               `yaml:"roots"`
	Concurrent  int                  `yaml:"concurrent"`
	TimeoutMS   int                  `yaml:"timeout_ms"`
	AttemptMS   int                  `yaml:"attempt_ms"`
	Operations  map[string]Operation `yaml:"operations"`
}

func (c Config) Validate() error {
	if c.Concurrent < 1 || c.Concurrent > 256 || c.TimeoutMS < 1 || c.TimeoutMS > 60000 || c.AttemptMS < 1 || c.AttemptMS > c.TimeoutMS {
		return errors.New("invalid dependency budget")
	}
	if c.Protocol != "http" && c.Protocol != "grpc" {
		return errors.New("invalid dependency protocol")
	}
	if c.Protocol == "http" {
		u, e := url.Parse(c.Address)
		if e != nil || u.Scheme != "https" || u.Host == "" || u.User != nil || u.RawQuery != "" || u.Fragment != "" || (u.Path != "" && u.Path != "/") {
			return errors.New("dependency requires HTTPS origin")
		}
	}
	if c.Protocol == "grpc" {
		a := strings.TrimPrefix(c.Address, "dns:///")
		if a == c.Address {
			return errors.New("gRPC dependency requires dns:///host:port")
		}
		h, p, e := net.SplitHostPort(a)
		if e != nil || h == "" || p == "" || strings.ContainsAny(h, "/?#@") {
			return errors.New("invalid gRPC address")
		}
		if c.Certificate == "" || c.Identity == "" || c.ServerName == "" {
			return errors.New("gRPC requires workload mTLS and server name")
		}
	}
	if (c.Certificate == "") != (c.Key == "") || (c.Certificate != "" && (c.Identity == "" || c.Roots == "")) {
		return errors.New("incomplete workload TLS")
	}
	if c.Identity != "" {
		u, e := url.Parse(c.Identity)
		if e != nil || u.Scheme != "spiffe" || u.Host == "" || u.User != nil || u.RawQuery != "" || u.Fragment != "" {
			return errors.New("invalid peer identity")
		}
	}
	if len(c.Operations) > 64 {
		return errors.New("too many dependency operations")
	}
	for name, op := range c.Operations {
		if !label.MatchString(name) || op.Attempts < 1 || op.Attempts > 3 || (!op.Idempotent && op.Attempts != 1) {
			return errors.New("invalid dependency operation")
		}
	}
	return nil
}

// Standard chain, server-auth EKU and DNS verification plus exact URI SAN.
// Custom verification reloads trust on every handshake; it never bypasses verification.
func (c Config) TLS() (*tls.Config, error) {
	roots := func() (*x509.CertPool, error) {
		if c.Roots == "" {
			return x509.SystemCertPool()
		}
		p, e := os.ReadFile(c.Roots)
		if e != nil {
			return nil, errors.New("dependency trust unavailable")
		}
		r := x509.NewCertPool()
		if !r.AppendCertsFromPEM(p) {
			return nil, errors.New("invalid dependency trust")
		}
		return r, nil
	}
	if _, e := roots(); e != nil {
		return nil, e
	}
	load := func(*tls.CertificateRequestInfo) (*tls.Certificate, error) {
		cert, e := tls.LoadX509KeyPair(c.Certificate, c.Key)
		if e != nil {
			return nil, errors.New("dependency certificate unavailable")
		}
		return &cert, nil
	}
	if c.Certificate != "" {
		if _, e := load(nil); e != nil {
			return nil, e
		}
	}
	cfg := &tls.Config{MinVersion: tls.VersionTLS13, ServerName: c.ServerName, InsecureSkipVerify: true} // Verified below using fresh roots and DNS.
	if c.Certificate != "" {
		cfg.GetClientCertificate = load
	}
	cfg.VerifyConnection = func(s tls.ConnectionState) error {
		if len(s.PeerCertificates) == 0 {
			return errors.New("missing peer certificate")
		}
		r, e := roots()
		if e != nil {
			return e
		}
		intermediates := x509.NewCertPool()
		for _, cert := range s.PeerCertificates[1:] {
			intermediates.AddCert(cert)
		}
		if s.ServerName == "" {
			return errors.New("missing peer DNS name")
		}
		leaf := s.PeerCertificates[0]
		if _, e = leaf.Verify(x509.VerifyOptions{Roots: r, Intermediates: intermediates, DNSName: s.ServerName, KeyUsages: []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth}}); e != nil {
			return errors.New("unverified dependency peer")
		}
		if c.Identity != "" && (len(leaf.URIs) != 1 || leaf.URIs[0].String() != c.Identity) {
			return errors.New("dependency identity mismatch")
		}
		return nil
	}
	return cfg, nil
}

type Client struct {
	cfg       Config
	budget    budget
	transport *http.Transport
	conn      *grpc.ClientConn
}

func New(name string, cfg Config, breaker Breaker) (*Client, error) {
	if !label.MatchString(name) {
		return nil, errors.New("invalid dependency name")
	}
	if e := cfg.Validate(); e != nil {
		return nil, e
	}
	tc, e := cfg.TLS()
	if e != nil {
		return nil, e
	}
	c := &Client{cfg: cfg, budget: budget{slots: make(chan struct{}, cfg.Concurrent), total: time.Duration(cfg.TimeoutMS) * time.Millisecond, attempt: time.Duration(cfg.AttemptMS) * time.Millisecond, dependency: name, breaker: breaker}}
	if cfg.Protocol == "http" {
		c.transport = &http.Transport{TLSClientConfig: tc, ForceAttemptHTTP2: true, MaxConnsPerHost: cfg.Concurrent, MaxIdleConns: cfg.Concurrent, MaxIdleConnsPerHost: cfg.Concurrent, IdleConnTimeout: 30 * time.Second, TLSHandshakeTimeout: 3 * time.Second, ResponseHeaderTimeout: c.budget.attempt, DialContext: (&net.Dialer{Timeout: 3 * time.Second, KeepAlive: 30 * time.Second}).DialContext}
		return c, nil
	}
	c.conn, e = grpc.NewClient(cfg.Address, grpc.WithTransportCredentials(credentials.NewTLS(tc)), grpc.WithDisableRetry(), grpc.WithDisableServiceConfig(), grpc.WithDefaultServiceConfig(`{"loadBalancingConfig":[{"round_robin":{}}]}`), grpc.WithDefaultCallOptions(grpc.MaxCallRecvMsgSize(1<<20), grpc.MaxCallSendMsgSize(1<<20)))
	return c, e
}
func (c *Client) Close() {
	if c.transport != nil {
		c.transport.CloseIdleConnections()
	}
	if c.conn != nil {
		_ = c.conn.Close()
	}
}
func (c *Client) operation(name string) (Operation, error) {
	op, ok := c.cfg.Operations[name]
	if !ok {
		return op, errors.New("undeclared dependency operation")
	}
	return op, nil
}
func user(ctx context.Context, op Operation) (string, string, error) {
	if !op.ForwardUser {
		return "", "", nil
	}
	p, ok := security.FromContext(ctx)
	valid := func(s string) bool {
		return len(s) > 0 && len(s) <= 256 && strings.IndexFunc(s, func(r rune) bool { return r < 33 || r > 126 }) < 0
	}
	if !ok || !valid(p.Issuer) || !valid(p.Subject) {
		return "", "", errors.New("verified user required")
	}
	return p.Issuer, p.Subject, nil
}

// Bound returns a generated-client-compatible unary invoker. Incoming metadata,
// cookies, bearer tokens and baggage are never copied. Streaming belongs to E07.
func (c *Client) Bound(operation string) grpc.ClientConnInterface { return &invoker{c, operation} }

type invoker struct {
	c         *Client
	operation string
}

func (i *invoker) Invoke(ctx context.Context, method string, args, reply any, opts ...grpc.CallOption) error {
	c := i.c
	if c.conn == nil {
		return errors.New("not a gRPC dependency")
	}
	op, e := c.operation(i.operation)
	if e != nil {
		return e
	}
	issuer, subject, e := user(ctx, op)
	if e != nil {
		return e
	}
	err := c.budget.run(ctx, i.operation, op, func(e error) bool { return status.Code(e) == codes.Unavailable }, func(child context.Context) error {
		carrier := propagation.MapCarrier{}
		otel.GetTextMapPropagator().Inject(child, carrier)
		md := metadata.Pairs("x-request-id", observability.RequestID(observability.ID(ctx)))
		for k, v := range carrier {
			if k == "traceparent" || k == "tracestate" {
				md.Set(k, v)
			}
		}
		if issuer != "" {
			md.Set("x-user-issuer", issuer)
			md.Set("x-user-subject", subject)
		}
		return c.conn.Invoke(metadata.NewOutgoingContext(child, md), method, args, reply, opts...)
	})
	if errors.Is(err, context.Canceled) || errors.Is(err, context.DeadlineExceeded) {
		return status.FromContextError(err).Err()
	}
	return err
}
func (i *invoker) NewStream(context.Context, *grpc.StreamDesc, string, ...grpc.CallOption) (grpc.ClientStream, error) {
	return nil, status.Error(codes.Unimplemented, "streaming requires an explicit lifecycle policy")
}

type Response struct {
	Status int
	Body   []byte
}
type retryStatus struct{}

func (retryStatus) Error() string { return "retryable dependency status" }

// HTTP buffers a bounded response inside the attempt deadline. No redirects or
// arbitrary credentials/headers are accepted. Path is application-supplied, not a URL.
func (c *Client) HTTP(ctx context.Context, operation, method, path string, body []byte) (out Response, err error) {
	if c.transport == nil {
		return out, errors.New("not an HTTP dependency")
	}
	op, err := c.operation(operation)
	if err != nil {
		return out, err
	}
	u, e := url.Parse(path)
	if e != nil || !strings.HasPrefix(path, "/") || strings.HasPrefix(path, "//") || u.IsAbs() || u.Host != "" || u.Fragment != "" || len(body) > 1<<20 {
		return out, errors.New("invalid dependency request")
	}
	issuer, subject, e := user(ctx, op)
	if e != nil {
		return out, e
	}
	err = c.budget.run(ctx, operation, op, func(e error) bool { var r retryStatus; return errors.As(e, &r) }, func(child context.Context) error {
		req, e := http.NewRequestWithContext(child, method, strings.TrimRight(c.cfg.Address, "/")+path, bytes.NewReader(body))
		if e != nil {
			return errors.New("invalid dependency request")
		}
		req.GetBody = nil // prevent transport from replaying request bodies
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("X-Request-ID", observability.RequestID(observability.ID(ctx)))
		if issuer != "" {
			req.Header.Set("X-User-Issuer", issuer)
			req.Header.Set("X-User-Subject", subject)
		}
		propagation.TraceContext{}.Inject(child, propagation.HeaderCarrier(req.Header))
		response, e := c.transport.RoundTrip(req)
		if e != nil {
			if child.Err() != nil {
				return child.Err()
			}
			return errors.New("dependency transport failed")
		}
		defer func() { _ = response.Body.Close() }()
		data, e := io.ReadAll(io.LimitReader(response.Body, (1<<20)+1))
		if e != nil || len(data) > 1<<20 {
			return errors.New("dependency response unavailable or too large")
		}
		out = Response{response.StatusCode, data}
		if response.StatusCode == 502 || response.StatusCode == 503 || response.StatusCode == 504 {
			return retryStatus{}
		}
		if response.StatusCode >= 400 {
			return errors.New("dependency HTTP error")
		}
		return nil
	})
	return out, err
}

// OpenAll owns handles for this process; unused/default empty dependencies need no infrastructure.
func Validate(configs map[string]Config) error {
	if len(configs) > 32 {
		return errors.New("too many dependencies")
	}
	for name, c := range configs {
		if !label.MatchString(name) {
			return errors.New("invalid dependency name")
		}
		if err := c.Validate(); err != nil {
			return err
		}
	}
	return nil
}
func OpenAll(configs map[string]Config) (map[string]*Client, func(), error) {
	if err := Validate(configs); err != nil {
		return nil, func() {}, err
	}
	clients := map[string]*Client{}
	closeAll := func() {
		for _, c := range clients {
			c.Close()
		}
	}
	for name, cfg := range configs {
		c, e := New(name, cfg, nil)
		if e != nil {
			closeAll()
			return nil, func() {}, e
		}
		clients[name] = c
	}
	return clients, closeAll, nil
}
