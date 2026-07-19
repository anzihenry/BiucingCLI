APP_NAME={{SERVICE_NAME}}
WORKTREE_ROOT ?=$(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
WORKTREE_ID ?=$(shell printf '%s' "$(WORKTREE_ROOT)" | shasum | cut -c1-8)
WORKTREE_SLUG ?=$(APP_NAME)-$(WORKTREE_ID)
COMPOSE_PROJECT_NAME ?=$(WORKTREE_SLUG)
IMAGE ?=$(WORKTREE_SLUG)
TAG ?=dev
IMAGE_REF := $(IMAGE):$(TAG)
COMPOSE ?=COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) docker compose
HTTP_PORT ?={{HTTP_PORT}}
GRPC_PORT ?={{GRPC_PORT}}
HOST_HTTP_PORT ?={{HTTP_PORT}}
HOST_GRPC_PORT ?={{GRPC_PORT}}
HOST_DEPENDENCY_STORE_PORT ?={{DEPENDENCY_STORE_PORT}}
HOST_OTEL_GRPC_PORT ?=4317
HOST_OTEL_HTTP_PORT ?=4318
DEV_COMPOSE_FILE ?=compose.dev.yaml
DEV_SERVICE ?=app-dev
DOCKER_VARIANT ?=alpine
DOCKER_PLATFORM ?=linux/arm64
COMPOSE_FILE ?=deploy/compose.yaml
GOPROXY ?=https://proxy.golang.org,direct
GOSUMDB ?=sum.golang.org
GOCACHE ?= $(CURDIR)/.cache/go-build
GOLANGCI_LINT_CACHE ?= $(CURDIR)/.cache/golangci-lint
export COMPOSE_PROJECT_NAME
export IMAGE
export TAG
export HTTP_PORT
export GRPC_PORT
export HOST_HTTP_PORT
export HOST_GRPC_PORT
export HOST_DEPENDENCY_STORE_PORT
export HOST_OTEL_GRPC_PORT
export HOST_OTEL_HTTP_PORT
export GOCACHE
export GOLANGCI_LINT_CACHE

ifeq ($(DOCKER_VARIANT),ubuntu)
BUILDER_IMAGE ?= public.ecr.aws/docker/library/golang:1.26
RUNTIME_IMAGE ?= public.ecr.aws/docker/library/ubuntu:26.04
else
BUILDER_IMAGE ?= golang:1.26-alpine
RUNTIME_IMAGE ?= alpine:3.20
endif

.PHONY: worktree-info worktree-doctor clean-worktree bootstrap doctor dev dev-shell tidy proto lint test verify run up down logs build docker-build docker-run

worktree-info:
	@printf '%s\n' "Worktree root: $(WORKTREE_ROOT)"
	@printf '%s\n' "Worktree ID: $(WORKTREE_ID)"
	@printf '%s\n' "Worktree slug: $(WORKTREE_SLUG)"
	@printf '%s\n' "Compose project: $(COMPOSE_PROJECT_NAME)"
	@printf '%s\n' "HTTP URL: http://127.0.0.1:$(HOST_HTTP_PORT)"
	@printf '%s\n' "gRPC host port: $(HOST_GRPC_PORT)"
	@printf '%s\n' "{{DEPENDENCY_STORE}} host port: $(HOST_DEPENDENCY_STORE_PORT)"
	@printf '%s\n' "OTel gRPC host port: $(HOST_OTEL_GRPC_PORT)"
	@printf '%s\n' "OTel HTTP host port: $(HOST_OTEL_HTTP_PORT)"
	@printf '%s\n' "Image ref: $(IMAGE_REF)"
	@printf '%s\n' "Go cache: $(GOCACHE)"
	@printf '%s\n' "golangci-lint cache: $(GOLANGCI_LINT_CACHE)"

worktree-doctor:
	@$(MAKE) --no-print-directory worktree-info
	@if [ "$(HOST_HTTP_PORT)" = "{{HTTP_PORT}}" ]; then printf '%s\n' "Warning: HOST_HTTP_PORT uses the generated default {{HTTP_PORT}}; override it when another worktree is running."; fi
	@if [ "$(HOST_GRPC_PORT)" = "{{GRPC_PORT}}" ]; then printf '%s\n' "Warning: HOST_GRPC_PORT uses the generated default {{GRPC_PORT}}; override it when another worktree is running."; fi
	@if [ "$(HOST_DEPENDENCY_STORE_PORT)" = "{{DEPENDENCY_STORE_PORT}}" ]; then printf '%s\n' "Warning: HOST_DEPENDENCY_STORE_PORT uses {{DEPENDENCY_STORE_PORT}}; override it when another dependency store is running."; fi
	@if [ "$(HOST_OTEL_GRPC_PORT)" = "4317" ]; then printf '%s\n' "Warning: HOST_OTEL_GRPC_PORT uses 4317; override it when another collector is running."; fi
	@if [ "$(HOST_OTEL_HTTP_PORT)" = "4318" ]; then printf '%s\n' "Warning: HOST_OTEL_HTTP_PORT uses 4318; override it when another collector is running."; fi

clean-worktree:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) down --remove-orphans --volumes

bootstrap:
	GOPROXY=$(GOPROXY) GOSUMDB=$(GOSUMDB) $(COMPOSE) -f $(DEV_COMPOSE_FILE) build $(DEV_SERVICE)

doctor:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) ./scripts/doctor

dev:
	GOPROXY=$(GOPROXY) GOSUMDB=$(GOSUMDB) $(COMPOSE) -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE) {{DEPENDENCY_STORE}} otel-collector

dev-shell:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) bash

tidy:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go mod tidy

proto:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) buf generate ./api

lint:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) bash -lc "buf lint ./api && golangci-lint run --disable-all --enable=errcheck --enable=govet --enable=ineffassign --enable=staticcheck --enable=unused ./..."

test:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go test ./...

verify: doctor proto lint test

run:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm --service-ports $(DEV_SERVICE)

up:
	GOPROXY=$(GOPROXY) GOSUMDB=$(GOSUMDB) $(COMPOSE) -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE) {{DEPENDENCY_STORE}} otel-collector

down:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) down --remove-orphans

logs:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) logs -f

build:
	$(COMPOSE) -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go build -o bin/$(APP_NAME) ./cmd/server

docker-build:
	docker build --platform $(DOCKER_PLATFORM) --build-arg BUILDER_IMAGE=$(BUILDER_IMAGE) --build-arg RUNTIME_IMAGE=$(RUNTIME_IMAGE) --build-arg GOPROXY=$(GOPROXY) --build-arg GOSUMDB=$(GOSUMDB) -t $(IMAGE_REF) .

docker-run:
	docker run --rm -p $(HOST_HTTP_PORT):$(HTTP_PORT) -p $(HOST_GRPC_PORT):$(GRPC_PORT) $(IMAGE_REF)
