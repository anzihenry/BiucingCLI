ARG BUILDER_IMAGE=golang:1.26.8-alpine
ARG RUNTIME_IMAGE=alpine:3.23.6

FROM ${BUILDER_IMAGE} AS builder

WORKDIR /app

ARG TARGETARCH
ARG GOPROXY=https://proxy.golang.org,direct
ARG GOSUMDB=sum.golang.org
ENV GOPROXY=${GOPROXY}
ENV GOSUMDB=${GOSUMDB}

COPY go.mod go.sum ./
RUN set -eux; \
    attempt=1; \
    until go mod download; do \
      if [ "$attempt" -ge 3 ]; then \
        exit 1; \
      fi; \
      attempt=$((attempt + 1)); \
      sleep 5; \
    done

COPY . .
ARG VERSION=dev
ARG COMMIT=unknown
ARG BUILT_AT=unknown
RUN CGO_ENABLED=0 GOOS=linux GOARCH=${TARGETARCH:-amd64} go build -buildvcs=false -trimpath -ldflags="-X {{MODULE_NAME}}/internal/runtime.Version=${VERSION} -X {{MODULE_NAME}}/internal/runtime.Commit=${COMMIT} -X {{MODULE_NAME}}/internal/runtime.BuiltAt=${BUILT_AT}" -o /out/server ./cmd/server

RUN CGO_ENABLED=0 GOOS=linux GOARCH=${TARGETARCH:-amd64} go build -trimpath -o /out/migrate ./cmd/migrate

RUN CGO_ENABLED=0 GOOS=linux GOARCH=${TARGETARCH:-amd64} go build -trimpath -o /out/session-cleanup ./cmd/session-cleanup

FROM ${RUNTIME_IMAGE}

WORKDIR /app

USER 65532:65532

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=builder /out/server /app/server
COPY --from=builder /out/migrate /app/migrate
COPY --from=builder /out/session-cleanup /app/session-cleanup
COPY configs/config.yaml /app/configs/config.yaml

EXPOSE {{HTTP_PORT}}

ENV CONFIG_FILE=/app/configs/config.yaml

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD ["/app/server", "healthcheck", "http://127.0.0.1:9000/livez"]

CMD ["/app/server"]
