FROM golang:1.22-alpine AS builder

WORKDIR /app

COPY go.mod ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /out/server ./cmd/server

FROM alpine:3.20

WORKDIR /app

COPY --from=builder /out/server /app/server
COPY configs/config.yaml /app/configs/config.yaml

EXPOSE {{HTTP_PORT}}

ENV CONFIG_FILE=/app/configs/config.yaml

CMD ["/app/server"]
