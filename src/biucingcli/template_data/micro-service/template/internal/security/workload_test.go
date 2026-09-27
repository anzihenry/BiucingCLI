package security

import (
	"context"
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/pem"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/peer"
	"math/big"
	"net"
	"net/url"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestWorkloadAuthorization(t *testing.T) {
	uri, _ := url.Parse("spiffe://test/caller")
	cert := &x509.Certificate{URIs: []*url.URL{uri}, NotBefore: time.Now().Add(-time.Hour), NotAfter: time.Now().Add(time.Hour)}
	verified := peer.NewContext(context.Background(), &peer.Peer{AuthInfo: credentials.TLSInfo{State: tls.ConnectionState{VerifiedChains: [][]*x509.Certificate{{cert}}}}})
	c := WorkloadConfig{Methods: map[string][]string{"/method": {"spiffe://test/caller"}}, Delegates: map[string][]string{}}
	if _, err := c.Authenticate(context.Background(), "/method"); err == nil {
		t.Fatal("missing TLS accepted")
	}
	if _, err := c.Authenticate(verified, "/other"); err == nil {
		t.Fatal("method not allowlisted")
	}
	ctx, err := c.Authenticate(verified, "/method")
	if err != nil {
		t.Fatal(err)
	}
	p, ok := FromContext(ctx)
	if !ok || p.Workload != "spiffe://test/caller" || p.Subject != "" {
		t.Fatal(p)
	}
	delegated := metadata.NewIncomingContext(verified, metadata.Pairs("x-user-issuer", "https://issuer", "x-user-subject", "person"))
	if _, err = c.Authenticate(delegated, "/method"); err == nil {
		t.Fatal("untrusted delegation accepted")
	}
	c.Delegates["/method"] = []string{"spiffe://test/caller"}
	ctx, err = c.Authenticate(delegated, "/method")
	if err != nil {
		t.Fatal(err)
	}
	p, _ = FromContext(ctx)
	if p.Subject != "person" {
		t.Fatal(p)
	}
	duplicate := metadata.NewIncomingContext(verified, metadata.Pairs("x-user-issuer", "https://issuer", "x-user-subject", "one", "x-user-subject", "two"))
	if _, err = c.Authenticate(duplicate, "/method"); err == nil {
		t.Fatal("ambiguous delegation")
	}
	cert.NotAfter = time.Now().Add(-time.Second)
	if _, err = c.Authenticate(verified, "/method"); err == nil {
		t.Fatal("expired certificate on existing connection accepted")
	}
}
func TestTLSHandshakeAndRotation(t *testing.T) {
	dir := t.TempDir()
	caKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		t.Fatal(err)
	}
	ca := &x509.Certificate{SerialNumber: big.NewInt(1), Subject: pkix.Name{CommonName: "test"}, IsCA: true, BasicConstraintsValid: true, KeyUsage: x509.KeyUsageCertSign, NotBefore: time.Now().Add(-time.Hour), NotAfter: time.Now().Add(time.Hour)}
	caDER, err := x509.CreateCertificate(rand.Reader, ca, ca, &caKey.PublicKey, caKey)
	if err != nil {
		t.Fatal(err)
	}
	caPEM := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: caDER})
	if err = os.WriteFile(filepath.Join(dir, "ca.crt"), caPEM, 0600); err != nil {
		t.Fatal(err)
	}
	issue := func(name string, expired bool) tls.Certificate {
		key, e := rsa.GenerateKey(rand.Reader, 2048)
		if e != nil {
			t.Fatal(e)
		}
		uri, _ := url.Parse("spiffe://test/" + name)
		leaf := &x509.Certificate{SerialNumber: big.NewInt(time.Now().UnixNano()), DNSNames: []string{"localhost"}, URIs: []*url.URL{uri}, ExtKeyUsage: []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth, x509.ExtKeyUsageClientAuth}, KeyUsage: x509.KeyUsageDigitalSignature, NotBefore: time.Now().Add(-time.Hour), NotAfter: time.Now().Add(time.Hour)}
		if expired {
			leaf.NotAfter = time.Now().Add(-time.Minute)
		}
		der, e := x509.CreateCertificate(rand.Reader, leaf, ca, &key.PublicKey, caKey)
		if e != nil {
			t.Fatal(e)
		}
		cp := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: der})
		kp := pem.EncodeToMemory(&pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(key)})
		if e = os.WriteFile(filepath.Join(dir, name+".crt"), cp, 0600); e != nil {
			t.Fatal(e)
		}
		if e = os.WriteFile(filepath.Join(dir, name+".key"), kp, 0600); e != nil {
			t.Fatal(e)
		}
		pair, e := tls.X509KeyPair(cp, kp)
		if e != nil {
			t.Fatal(e)
		}
		return pair
	}
	issue("server", false)
	client := issue("client", false)
	expired := issue("expired", true)
	c := WorkloadConfig{Certificate: filepath.Join(dir, "server.crt"), Key: filepath.Join(dir, "server.key"), Roots: filepath.Join(dir, "ca.crt")}
	serverConfig, err := c.TLS()
	if err != nil {
		t.Fatal(err)
	}
	roots := x509.NewCertPool()
	roots.AppendCertsFromPEM(caPEM)
	handshake := func(certs []tls.Certificate) error {
		left, right := net.Pipe()
		defer func() { _ = left.Close(); _ = right.Close() }()
		_ = left.SetDeadline(time.Now().Add(2 * time.Second))
		_ = right.SetDeadline(time.Now().Add(2 * time.Second))
		server := tls.Server(left, serverConfig)
		done := make(chan error, 1)
		go func() { done <- server.Handshake() }()
		client := tls.Client(right, &tls.Config{MinVersion: tls.VersionTLS13, ServerName: "localhost", RootCAs: roots, Certificates: certs})
		_ = client.Handshake()
		return <-done
	}
	if err = handshake([]tls.Certificate{client}); err != nil {
		t.Fatal(err)
	}
	if handshake(nil) == nil || handshake([]tls.Certificate{expired}) == nil {
		t.Fatal("invalid client accepted")
	}
	issue("server", false)
	if err = handshake([]tls.Certificate{client}); err != nil {
		t.Fatal("leaf reload failed", err)
	}
	if err = os.WriteFile(c.Roots, []byte("invalid replacement"), 0600); err != nil {
		t.Fatal(err)
	}
	if handshake([]tls.Certificate{client}) == nil {
		t.Fatal("bad trust replacement allowed")
	}
}
