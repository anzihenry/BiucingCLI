package security

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"errors"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/peer"
	"os"
	"strings"
	"time"
)

var ErrWorkloadDenied = errors.New("workload action denied")

type WorkloadConfig struct {
	Certificate string              `yaml:"certificate"`
	Key         string              `yaml:"key"`
	Roots       string              `yaml:"roots"`
	Methods     map[string][]string `yaml:"methods"`
	Delegates   map[string][]string `yaml:"delegates"`
}

// Reload at every handshake, including roots. Atomic directory/symlink swaps
// keep key and certificate consistent; a bad replacement fails closed.
func (c WorkloadConfig) TLS() (*tls.Config, error) {
	load := func() (*tls.Config, error) {
		cert, err := tls.LoadX509KeyPair(c.Certificate, c.Key)
		if err != nil {
			return nil, errors.New("workload certificate unavailable")
		}
		pem, err := os.ReadFile(c.Roots)
		if err != nil {
			return nil, errors.New("workload trust unavailable")
		}
		roots := x509.NewCertPool()
		if !roots.AppendCertsFromPEM(pem) {
			return nil, errors.New("invalid workload trust")
		}
		return &tls.Config{MinVersion: tls.VersionTLS13, Certificates: []tls.Certificate{cert}, ClientAuth: tls.RequireAndVerifyClientCert, ClientCAs: roots, SessionTicketsDisabled: true}, nil
	}
	first, err := load()
	if err != nil {
		return nil, err
	}
	first.GetConfigForClient = func(*tls.ClientHelloInfo) (*tls.Config, error) { return load() }
	return first, nil
}
func contains(values []string, s string) bool {
	for _, v := range values {
		if v == s {
			return true
		}
	}
	return false
}

// Identity is taken only from the verified URI SAN, never from metadata/CN.
func (c WorkloadConfig) Authenticate(ctx context.Context, method string) (context.Context, error) {
	p, ok := peer.FromContext(ctx)
	if !ok {
		return ctx, errors.New("missing workload")
	}
	info, ok := p.AuthInfo.(credentials.TLSInfo)
	if !ok || len(info.State.VerifiedChains) == 0 {
		return ctx, errors.New("unverified workload")
	}
	cert := info.State.VerifiedChains[0][0]
	if time.Now().After(cert.NotAfter) || time.Now().Before(cert.NotBefore) || len(cert.URIs) != 1 {
		return ctx, errors.New("invalid workload certificate")
	}
	uri := cert.URIs[0]
	if uri.Scheme != "spiffe" || uri.Host == "" || uri.RawQuery != "" || uri.Fragment != "" {
		return ctx, errors.New("invalid workload identity")
	}
	workload := uri.String()
	if !contains(c.Methods[method], workload) {
		return ctx, ErrWorkloadDenied
	}
	principal := Principal{Workload: workload}
	md, _ := metadata.FromIncomingContext(ctx)
	issuers, subjects := md.Get("x-user-issuer"), md.Get("x-user-subject")
	if len(issuers) > 0 || len(subjects) > 0 {
		if !contains(c.Delegates[method], workload) || len(issuers) != 1 || len(subjects) != 1 || !validContext(issuers[0]) || !validContext(subjects[0]) {
			return ctx, ErrWorkloadDenied
		}
		principal.Issuer, principal.Subject = issuers[0], subjects[0]
	}
	return WithPrincipal(ctx, principal), nil
}
func validContext(s string) bool {
	return len(s) > 0 && len(s) <= 256 && strings.IndexFunc(s, func(r rune) bool { return r < 33 || r > 126 }) < 0
}
