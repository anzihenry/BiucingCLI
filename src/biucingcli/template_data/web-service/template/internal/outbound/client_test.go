package outbound

import (
	"context"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/pem"
	"errors"
	"{{MODULE_NAME}}/internal/security"
	"golang.org/x/net/dns/dnsmessage"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/resolver/dns"
	"google.golang.org/grpc/status"
	"math/big"
	"net"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"path/filepath"
	"sync/atomic"
	"testing"
	"time"
)

func TestBudget(t *testing.T) {
	b := budget{slots: make(chan struct{}, 1), total: 100 * time.Millisecond, attempt: 20 * time.Millisecond, dependency: "test"}
	calls := 0
	failure := errors.New("failed")
	err := b.run(context.Background(), "write", Operation{Attempts: 3}, func(error) bool { return true }, func(context.Context) error { calls++; return failure })
	if err != failure || calls != 1 {
		t.Fatal("unsafe retry", err, calls)
	}
	calls = 0
	b.total = time.Second
	err = b.run(context.Background(), "read", Operation{Idempotent: true, Attempts: 3}, func(error) bool { return true }, func(context.Context) error {
		calls++
		if calls < 3 {
			return failure
		}
		return nil
	})
	if err != nil || calls != 3 {
		t.Fatal(err, calls)
	}
	b.slots <- struct{}{}
	if !errors.Is(b.run(context.Background(), "read", Operation{}, nil, nil), ErrOverloaded) {
		t.Fatal("missing backpressure")
	}
	<-b.slots
	b.total = 40 * time.Millisecond
	started := time.Now()
	err = b.run(context.Background(), "slow", Operation{Idempotent: true, Attempts: 3}, func(error) bool { return true }, func(ctx context.Context) error { <-ctx.Done(); return ctx.Err() })
	if err == nil || time.Since(started) > 200*time.Millisecond {
		t.Fatal("unbounded deadline", err)
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	calls = 0
	_ = b.run(ctx, "cancel", Operation{}, func(error) bool { return true }, func(context.Context) error { calls++; return nil })
	if calls != 0 {
		t.Fatal("cancel did work")
	}
}
func certificateFixture(t *testing.T) (Config, *tls.Config, func()) {
	t.Helper()
	dir := t.TempDir()
	key, e := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if e != nil {
		t.Fatal(e)
	}
	ca := &x509.Certificate{SerialNumber: big.NewInt(1), Subject: pkix.Name{CommonName: "fixture"}, IsCA: true, BasicConstraintsValid: true, KeyUsage: x509.KeyUsageCertSign, NotBefore: time.Now().Add(-time.Hour), NotAfter: time.Now().Add(time.Hour)}
	der, e := x509.CreateCertificate(rand.Reader, ca, ca, &key.PublicKey, key)
	if e != nil {
		t.Fatal(e)
	}
	roots := x509.NewCertPool()
	roots.AddCert(ca)
	// Parse the signed certificate so authority/key identifiers match exactly.
	parsed, e := x509.ParseCertificate(der)
	if e != nil {
		t.Fatal(e)
	}
	roots = x509.NewCertPool()
	roots.AddCert(parsed)
	write := func(path string, b []byte) {
		t.Helper()
		if e := os.WriteFile(filepath.Join(dir, path), b, 0600); e != nil {
			t.Fatal(e)
		}
	}
	write("ca.crt", pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: der}))
	issue := func(name string) tls.Certificate {
		k, e := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
		if e != nil {
			t.Fatal(e)
		}
		uri, _ := url.Parse("spiffe://test/" + name)
		leaf := &x509.Certificate{SerialNumber: big.NewInt(time.Now().UnixNano()), DNSNames: []string{"localhost"}, URIs: []*url.URL{uri}, ExtKeyUsage: []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth, x509.ExtKeyUsageClientAuth}, KeyUsage: x509.KeyUsageDigitalSignature, NotBefore: time.Now().Add(-time.Minute), NotAfter: time.Now().Add(time.Hour)}
		der, e := x509.CreateCertificate(rand.Reader, leaf, ca, &k.PublicKey, key)
		if e != nil {
			t.Fatal(e)
		}
		kb, e := x509.MarshalECPrivateKey(k)
		if e != nil {
			t.Fatal(e)
		}
		cp := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: der})
		kp := pem.EncodeToMemory(&pem.Block{Type: "EC PRIVATE KEY", Bytes: kb})
		write(name+".crt", cp)
		write(name+".key", kp)
		cert, e := tls.X509KeyPair(cp, kp)
		if e != nil {
			t.Fatal(e)
		}
		return cert
	}
	server := issue("server")
	issue("caller")
	return Config{Protocol: "http", Address: "https://localhost", ServerName: "localhost", Identity: "spiffe://test/server", Certificate: filepath.Join(dir, "caller.crt"), Key: filepath.Join(dir, "caller.key"), Roots: filepath.Join(dir, "ca.crt"), Concurrent: 2, TimeoutMS: 1000, AttemptMS: 300, Operations: map[string]Operation{"read": {Idempotent: true, Attempts: 3}, "write": {Attempts: 1}, "user": {Attempts: 1, ForwardUser: true}}}, &tls.Config{MinVersion: tls.VersionTLS13, Certificates: []tls.Certificate{server}, ClientAuth: tls.RequireAndVerifyClientCert, ClientCAs: roots}, func() { issue("caller") }
}
func TestHTTPIdentityRetryAndHeaders(t *testing.T) {
	cfg, tc, rotate := certificateFixture(t)
	var calls atomic.Int32
	server := httptest.NewUnstartedServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") != "" || r.Header.Get("Cookie") != "" || r.Header.Get("Baggage") != "" {
			t.Error("credential leak")
		}
		if r.URL.Path == "/user" && r.Header.Get("X-User-Subject") != "person" {
			t.Error("missing verified identity")
		}
		if r.URL.Path == "/retry" && calls.Add(1) < 3 {
			w.WriteHeader(503)
			return
		}
		if r.URL.Path == "/redirect" {
			w.Header().Set("Location", "https://elsewhere.test")
			w.WriteHeader(302)
			return
		}
		w.WriteHeader(200)
	}))
	server.TLS = tc
	server.StartTLS()
	defer server.Close()
	cfg.Address = server.URL
	client, e := New("test", cfg, nil)
	if e != nil {
		t.Fatal(e)
	}
	defer client.Close()
	if _, e = client.HTTP(context.Background(), "read", "GET", "/retry", nil); e != nil || calls.Load() != 3 {
		t.Fatal(e, calls.Load())
	}
	calls.Store(0)
	if _, e = client.HTTP(context.Background(), "write", "POST", "/retry", nil); e == nil || calls.Load() != 1 {
		t.Fatal("write retry", e, calls.Load())
	}
	ctx := security.WithPrincipal(context.Background(), security.Principal{Issuer: "https://issuer", Subject: "person"})
	if _, e = client.HTTP(ctx, "user", "GET", "/user", nil); e != nil {
		t.Fatal(e)
	}
	if _, e = client.HTTP(context.Background(), "user", "GET", "/user", nil); e == nil {
		t.Fatal("unverified delegation")
	}
	if r, e := client.HTTP(ctx, "read", "GET", "/redirect", nil); e != nil || r.Status != 302 {
		t.Fatal("followed redirect", e)
	}
	if _, e = client.HTTP(ctx, "read", "GET", "//elsewhere.test", nil); e == nil {
		t.Fatal("SSRF")
	}
	rotate()
	client.transport.CloseIdleConnections()
	if _, e = client.HTTP(ctx, "read", "GET", "/", nil); e != nil {
		t.Fatal("rotation", e)
	}
	cfg.Identity = "spiffe://test/wrong"
	bad, e := New("wrong", cfg, nil)
	if e != nil {
		t.Fatal(e)
	}
	defer bad.Close()
	if _, e = bad.HTTP(ctx, "read", "GET", "/", nil); e == nil {
		t.Fatal("wrong peer accepted")
	}
	if e = os.WriteFile(cfg.Roots, []byte("bad root replacement"), 0600); e != nil {
		t.Fatal(e)
	}
	client.transport.CloseIdleConnections()
	if _, e = client.HTTP(ctx, "read", "GET", "/", nil); e == nil {
		t.Fatal("bad root accepted")
	}
}

type healthFixture struct {
	grpc_health_v1.UnimplementedHealthServer
	calls              atomic.Int32
	entered, cancelled chan struct{}
}

func (h *healthFixture) Check(ctx context.Context, request *grpc_health_v1.HealthCheckRequest) (*grpc_health_v1.HealthCheckResponse, error) {
	if request.Service == "slow" {
		close(h.entered)
		<-ctx.Done()
		close(h.cancelled)
		return nil, status.FromContextError(ctx.Err()).Err()
	}
	md, _ := metadata.FromIncomingContext(ctx)
	if len(md.Get("authorization")) > 0 || len(md.Get("cookie")) > 0 || len(md.Get("baggage")) > 0 {
		return nil, status.Error(codes.Internal, "leaked metadata")
	}
	if len(md.Get("x-user-subject")) != 1 || md.Get("x-user-subject")[0] != "person" {
		return nil, status.Error(codes.PermissionDenied, "wrong user")
	}
	if h.calls.Add(1) < 2 {
		return nil, status.Error(codes.Unavailable, "retry")
	}
	return &grpc_health_v1.HealthCheckResponse{}, nil
}
func TestGRPCGeneratedClientAndSanitizedMetadata(t *testing.T) {
	cfg, tc, _ := certificateFixture(t)
	listener, e := net.Listen("tcp", "127.0.0.1:0")
	if e != nil {
		t.Fatal(e)
	}
	server := grpc.NewServer(grpc.Creds(credentials.NewTLS(tc)))
	fixture := &healthFixture{}
	grpc_health_v1.RegisterHealthServer(server, fixture)
	go func() { _ = server.Serve(listener) }()
	defer server.Stop()
	cfg.Protocol = "grpc"
	cfg.Address = "dns:///" + listener.Addr().String()
	cfg.Operations["user"] = Operation{Attempts: 3, Idempotent: true, ForwardUser: true}
	c, e := New("test", cfg, nil)
	if e != nil {
		t.Fatal(e)
	}
	defer c.Close()
	ctx := metadata.NewOutgoingContext(context.Background(), metadata.Pairs("authorization", "secret", "cookie", "secret", "x-user-subject", "forged", "baggage", "secret"))
	ctx = security.WithPrincipal(ctx, security.Principal{Subject: "person", Issuer: "https://issuer"})
	_, e = grpc_health_v1.NewHealthClient(c.Bound("user")).Check(ctx, &grpc_health_v1.HealthCheckRequest{})
	if e != nil || fixture.calls.Load() != 2 {
		t.Fatal(e, fixture.calls.Load())
	}
}

func TestIndependentDependencyCapacity(t *testing.T) {
	a := budget{slots: make(chan struct{}, 1), total: time.Second, attempt: time.Second, dependency: "slow"}
	b := budget{slots: make(chan struct{}, 1), total: time.Second, attempt: time.Second, dependency: "healthy"}
	entered := make(chan struct{})
	done := make(chan error, 1)
	ctx, cancel := context.WithCancel(context.Background())
	go func() {
		done <- a.run(ctx, "read", Operation{}, nil, func(ctx context.Context) error { close(entered); <-ctx.Done(); return ctx.Err() })
	}()
	<-entered
	if err := b.run(context.Background(), "read", Operation{}, nil, func(context.Context) error { return nil }); err != nil {
		t.Fatal("other dependency blocked", err)
	}
	if err := a.run(context.Background(), "read", Operation{}, nil, nil); !errors.Is(err, ErrOverloaded) {
		t.Fatal(err)
	}
	cancel()
	if err := <-done; !errors.Is(err, context.Canceled) {
		t.Fatal(err)
	}
	if len(a.slots) != 0 {
		t.Fatal("capacity leaked")
	}
}
func TestWrongDNSAndMissingClientCertificate(t *testing.T) {
	cfg, tc, _ := certificateFixture(t)
	server := httptest.NewUnstartedServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) { w.WriteHeader(200) }))
	server.TLS = tc
	server.StartTLS()
	defer server.Close()
	cfg.Address = server.URL
	cfg.ServerName = "different.example"
	c, e := New("dns", cfg, nil)
	if e != nil {
		t.Fatal(e)
	}
	defer c.Close()
	if _, e = c.HTTP(context.Background(), "read", "GET", "/", nil); e == nil {
		t.Fatal("wrong DNS accepted")
	}
	cfg.ServerName = "localhost"
	cfg.Certificate = ""
	cfg.Key = ""
	c2, e := New("missing", cfg, nil)
	if e != nil {
		t.Fatal(e)
	}
	defer c2.Close()
	if _, e = c2.HTTP(context.Background(), "read", "GET", "/", nil); e == nil {
		t.Fatal("missing client cert accepted")
	}
}

// Real DNS replies change the resolved address while the client handle is reused.
func TestDNSAddressChangeAndInFlightCancellation(t *testing.T) {
	cfg, tc, _ := certificateFixture(t)
	listener, e := net.Listen("tcp", "127.0.0.1:0")
	if e != nil {
		t.Fatal(e)
	}
	_, port, _ := net.SplitHostPort(listener.Addr().String())
	start := func(l net.Listener, h *healthFixture) *grpc.Server {
		s := grpc.NewServer(grpc.Creds(credentials.NewTLS(tc)))
		grpc_health_v1.RegisterHealthServer(s, h)
		go func() { _ = s.Serve(l) }()
		return s
	}
	first := &healthFixture{}
	first.calls.Store(2)
	s1 := start(listener, first)
	defer s1.Stop()
	dnsSocket, e := net.ListenPacket("udp", "127.0.0.1:0")
	if e != nil {
		t.Fatal(e)
	}
	defer func() { _ = dnsSocket.Close() }()
	var address atomic.Uint32
	address.Store(1)
	go func() {
		buffer := make([]byte, 4096)
		for {
			n, peer, e := dnsSocket.ReadFrom(buffer)
			if e != nil {
				return
			}
			var request dnsmessage.Message
			if request.Unpack(buffer[:n]) != nil {
				continue
			}
			response := dnsmessage.Message{Header: dnsmessage.Header{ID: request.ID, Response: true, RecursionAvailable: true}, Questions: request.Questions}
			for _, q := range request.Questions {
				if q.Type == dnsmessage.TypeA {
					response.Answers = append(response.Answers, dnsmessage.Resource{Header: dnsmessage.ResourceHeader{Name: q.Name, Type: dnsmessage.TypeA, Class: dnsmessage.ClassINET, TTL: 0}, Body: &dnsmessage.AResource{A: [4]byte{127, 0, 0, byte(address.Load())}}})
				}
			}
			packet, e := response.Pack()
			if e == nil {
				_, _ = dnsSocket.WriteTo(packet, peer)
			}
		}
	}()
	old := net.DefaultResolver
	net.DefaultResolver = &net.Resolver{PreferGo: true, Dial: func(ctx context.Context, _, _ string) (net.Conn, error) {
		return (&net.Dialer{}).DialContext(ctx, "udp", dnsSocket.LocalAddr().String())
	}}
	dns.SetMinResolutionInterval(10 * time.Millisecond)
	defer func() { net.DefaultResolver = old; dns.SetMinResolutionInterval(30 * time.Second) }()
	cfg.Protocol = "grpc"
	cfg.Address = "dns:///peer.test:" + port
	cfg.Operations["user"] = Operation{Attempts: 3, Idempotent: true, ForwardUser: true}
	c, e := New("changing", cfg, nil)
	if e != nil {
		t.Fatal(e)
	}
	defer c.Close()
	ctx := security.WithPrincipal(context.Background(), security.Principal{Issuer: "https://issuer", Subject: "person"})
	rpc := grpc_health_v1.NewHealthClient(c.Bound("user"))
	if _, e = rpc.Check(ctx, &grpc_health_v1.HealthCheckRequest{}); e != nil {
		t.Fatal(e)
	}
	l2, e := net.Listen("tcp", "127.0.0.2:"+port)
	if e != nil {
		t.Fatal(e)
	}
	second := &healthFixture{entered: make(chan struct{}), cancelled: make(chan struct{})}
	second.calls.Store(2)
	s2 := start(l2, second)
	defer s2.Stop()
	address.Store(2)
	s1.Stop()
	deadline := time.Now().Add(8 * time.Second)
	for {
		_, e = rpc.Check(ctx, &grpc_health_v1.HealthCheckRequest{})
		if e == nil {
			break
		}
		if time.Now().After(deadline) {
			t.Fatal("DNS reconnect failed", e)
		}
		time.Sleep(20 * time.Millisecond)
	}
	if second.calls.Load() < 3 {
		t.Fatal("new address not used")
	}
	child, cancel := context.WithCancel(ctx)
	defer cancel()
	done := make(chan error, 1)
	go func() { _, e := rpc.Check(child, &grpc_health_v1.HealthCheckRequest{Service: "slow"}); done <- e }()
	select {
	case <-second.entered:
	case <-time.After(time.Second):
		t.Fatal("request did not reach server")
	}
	cancel()
	if e = <-done; status.Code(e) != codes.Canceled {
		t.Fatal("client cancellation lost", e)
	}
	select {
	case <-second.cancelled:
	case <-time.After(time.Second):
		t.Fatal("server cancellation lost")
	}
}
