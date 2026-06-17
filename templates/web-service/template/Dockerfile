ARG BUILDER_IMAGE=golang:1.26-alpine
ARG RUNTIME_IMAGE=alpine:3.20

FROM ${BUILDER_IMAGE} AS builder

WORKDIR /app

ARG GOPROXY=https://proxy.golang.org,direct
ARG GOSUMDB=sum.golang.org
ENV GOPROXY=${GOPROXY}
ENV GOSUMDB=${GOSUMDB}

COPY go.mod ./
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
RUN CGO_ENABLED=0 GOOS=linux GOARCH=${TARGETARCH:-amd64} go build -o /out/server ./cmd/server

FROM ${RUNTIME_IMAGE}

WORKDIR /app

COPY --from=builder /out/server /app/server
COPY configs/config.yaml /app/configs/config.yaml

EXPOSE {{HTTP_PORT}}

ENV CONFIG_FILE=/app/configs/config.yaml

CMD ["/app/server"]
