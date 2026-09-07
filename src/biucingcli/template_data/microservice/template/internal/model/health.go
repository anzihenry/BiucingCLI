package model

type HealthResponse struct {
	Service  string `json:"service"`
	Status   string `json:"status"`
	Store    string `json:"store"`
	GRPCPort string `json:"grpcPort"`
}
