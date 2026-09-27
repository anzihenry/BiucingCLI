// rpc-probe is a standalone consumer: only the published generated API is imported.
package main

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
	"os"
	"time"
	servicev1 "{{MODULE_NAME}}/api/gen/go/service/v1"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "RPC probe failed")
		os.Exit(1)
	}
}
func run() error {
	cert, err := tls.LoadX509KeyPair(".secrets/client.crt", ".secrets/client.key")
	if err != nil {
		return err
	}
	pem, err := os.ReadFile(".secrets/ca.crt")
	if err != nil {
		return err
	}
	roots := x509.NewCertPool()
	if !roots.AppendCertsFromPEM(pem) {
		return fmt.Errorf("invalid roots")
	}
	target := os.Getenv("RPC_TARGET")
	if target == "" {
		target = "localhost:{{GRPC_PORT}}"
	}
	conn, err := grpc.NewClient(target, grpc.WithTransportCredentials(credentials.NewTLS(&tls.Config{MinVersion: tls.VersionTLS13, RootCAs: roots, Certificates: []tls.Certificate{cert}, ServerName: "localhost"})))
	if err != nil {
		return err
	}
	defer func() { _ = conn.Close() }()
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	_, err = servicev1.New{{SERVICE_TYPE_NAME}}ServiceClient(conn).Ping(ctx, &servicev1.PingRequest{})
	return err
}
