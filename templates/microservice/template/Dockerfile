ARG BUILDER_IMAGE=golang:1.25-alpine
ARG RUNTIME_IMAGE=alpine:3.20

FROM ${BUILDER_IMAGE} AS builder

WORKDIR /app

COPY go.mod ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=${TARGETARCH:-amd64} go build -o /out/server ./cmd/server

FROM ${RUNTIME_IMAGE}

WORKDIR /app

COPY --from=builder /out/server /app/server
COPY configs/config.yaml /app/configs/config.yaml
COPY deploy/otel-collector.yaml /app/deploy/otel-collector.yaml

EXPOSE {{HTTP_PORT}}
EXPOSE {{GRPC_PORT}}

ENV CONFIG_FILE=/app/configs/config.yaml
ENV OTEL_EXPORTER_OTLP_ENDPOINT={{OTEL_EXPORTER_ENDPOINT}}

CMD ["/app/server"]
