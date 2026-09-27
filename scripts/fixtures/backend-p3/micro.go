// Technical fixture only; generated Micro still has its independent production entrypoint.
package main
import (
 "context"
 "net"
 "os"
 "time"
 "google.golang.org/grpc"
 "google.golang.org/grpc/credentials"
 rpc "example.org/p3/internal-api/api/gen/go/service/v1"
 "example.org/p3/internal-api/internal/config"
 "example.org/p3/internal-api/internal/observability"
 "example.org/p3/internal-api/internal/pipeline"
 "example.org/p3/internal-api/internal/security"
 "example.org/p3/internal-api/internal/telemetry"
 "example.org/p3/internal-api/internal/transport"
)
type server struct{rpc.UnimplementedInternalApiServiceServer}
func(server)Ping(ctx context.Context,_ *rpc.PingRequest)(*rpc.PingResponse,error){p,_:=security.FromContext(ctx);return &rpc.PingResponse{Message:p.Subject,Service:"fixture"},nil}
func main(){
 cfg,e:=config.Load();if e!=nil{panic(e)};shutdown,e:=telemetry.Setup(context.Background(),cfg.Service.Name,"fixture",cfg.Environment,cfg.Telemetry);if e!=nil{panic(e)};defer func(){_ = shutdown(context.Background())}()
 tc,e:=cfg.Workload.TLS();if e!=nil{panic(e)}
 gate:=transport.NewGate(pipeline.Limits{Timeout:time.Second},func(_ context.Context,p security.Principal,_ string)bool{return p.Workload!=""},nil,&observability.Events{Logger:observability.New(os.Stdout,"INFO")},cfg.Workload.Authenticate)
 s:=grpc.NewServer(grpc.Creds(credentials.NewTLS(tc)),grpc.UnaryInterceptor(gate.Unary));rpc.RegisterInternalApiServiceServer(s,server{});l,e:=net.Listen("tcp",":9090");if e!=nil{panic(e)};if e=s.Serve(l);e!=nil{panic(e)}
}
