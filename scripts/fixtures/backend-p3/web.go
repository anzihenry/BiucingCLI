// Copied only by verify-backend-calls; never part of generated production APIs.
package main

import (
 "context"
 "errors"
 "net/http"
 "os"
 "time"
 "github.com/gin-gonic/gin"
 "google.golang.org/grpc/codes"
 "google.golang.org/grpc/status"
 rpc "example.org/p3/internal-api/api/gen/go/service/v1"
 "example.org/p3/edge-api/internal/auth"
 "example.org/p3/edge-api/internal/config"
 "example.org/p3/edge-api/internal/database"
 "example.org/p3/edge-api/internal/observability"
 "example.org/p3/edge-api/internal/outbound"
 "example.org/p3/edge-api/internal/router"
 "example.org/p3/edge-api/internal/security"
 "example.org/p3/edge-api/internal/telemetry"
)
func main(){
 cfg,e:=config.Load();if e!=nil{panic(e)};ctx:=context.Background()
 shutdown,e:=telemetry.Setup(ctx,cfg.Service.Name,"fixture",cfg.Environment,cfg.Telemetry);if e!=nil{panic(e)};defer func(){_ = shutdown(ctx)}()
 store,e:=database.Open(ctx,cfg.Database.DSN,cfg.Data);if e!=nil{panic(e)};defer store.Close();if e=store.Schema(ctx);e!=nil{panic(e)}
 clients,closeAll,e:=outbound.OpenAll(cfg.Dependencies);if e!=nil{panic(e)};defer closeAll()
 engine:=router.New(cfg,router.Options{Auth:auth.New(ctx,cfg.Auth,store),Events:&observability.Events{Logger:observability.New(os.Stdout,"INFO")},Policy:func(_ context.Context,p security.Principal,_ string)bool{return p.Subject!=""}})
 engine.GET("/_fixture/call",func(c *gin.Context){
  ctx:=c.Request.Context();if c.Query("cancel")=="yes"{child,cancel:=context.WithCancel(ctx);cancel();ctx=child}
  name:="peer";if c.Query("denied")=="yes"{name="denied"}
  response,e:=rpc.NewInternalApiServiceClient(clients[name].Bound("ping")).Ping(ctx,&rpc.PingRequest{})
  if e!=nil{code:=503;if status.Code(e)==codes.PermissionDenied{code=403};if errors.Is(e,context.Canceled)||status.Code(e)==codes.Canceled{code=499};if errors.Is(e,context.DeadlineExceeded)||status.Code(e)==codes.DeadlineExceeded{code=504};c.JSON(code,gin.H{"error":"dependency_failed"});return}
  c.JSON(200,gin.H{"subject":response.Message})
 })
 server:=&http.Server{Addr:":8080",Handler:engine,ReadHeaderTimeout:time.Second};if e=server.ListenAndServe();e!=nil{panic(e)}
}
