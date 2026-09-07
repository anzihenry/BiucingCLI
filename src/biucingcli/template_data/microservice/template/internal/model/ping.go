package model

type PingResponse struct {
	Message      string `json:"message"`
	Service      string `json:"service"`
	ProtoPackage string `json:"protoPackage"`
}
