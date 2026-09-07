ARG BUILDER_IMAGE=golang:1.26-alpine
ARG RUNTIME_IMAGE=alpine:3.20

FROM ${BUILDER_IMAGE} AS builder
ARG GOPROXY=https://proxy.golang.org,direct
ARG GOSUMDB=sum.golang.org
WORKDIR /app
ENV GOPROXY=${GOPROXY}
ENV GOSUMDB=${GOSUMDB}
COPY go.mod go.sum ./
RUN go mod download || true
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=${TARGETARCH:-amd64} go build -o /out/worker ./cmd/worker

FROM ${RUNTIME_IMAGE}
WORKDIR /app
COPY --from=builder /out/worker /usr/local/bin/worker
COPY configs ./configs
CMD ["/usr/local/bin/worker"]
