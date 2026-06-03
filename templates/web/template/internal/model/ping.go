package model

type PingResponse struct {
	Service string `json:"service"`
	Message string `json:"message"`
	Version string `json:"version"`
}
