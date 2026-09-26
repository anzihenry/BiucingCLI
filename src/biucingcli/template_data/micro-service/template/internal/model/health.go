package model

type HealthResponse struct {
	Service  string `json:"service"`
	Status   string `json:"status"`
	Database string `json:"database"`
	GRPCPort string `json:"grpcPort"`
}
