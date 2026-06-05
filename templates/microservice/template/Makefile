APP_NAME={{SERVICE_NAME}}
IMAGE ?=$(APP_NAME)
TAG ?=latest
IMAGE_REF := $(IMAGE):$(TAG)
HTTP_PORT ?={{HTTP_PORT}}
GRPC_PORT ?={{GRPC_PORT}}
HOST_HTTP_PORT ?={{HTTP_PORT}}
HOST_GRPC_PORT ?={{GRPC_PORT}}
DOCKER_VARIANT ?=alpine
DOCKER_PLATFORM ?=linux/arm64
COMPOSE_FILE ?=deploy/compose.yaml
GOCACHE ?= $(CURDIR)/.cache/go-build
GOLANGCI_LINT_CACHE ?= $(CURDIR)/.cache/golangci-lint
export GOCACHE
export GOLANGCI_LINT_CACHE

ifeq ($(DOCKER_VARIANT),ubuntu)
BUILDER_IMAGE ?= public.ecr.aws/docker/library/golang:1.26
RUNTIME_IMAGE ?= public.ecr.aws/docker/library/ubuntu:26.04
else
BUILDER_IMAGE ?= golang:1.26-alpine
RUNTIME_IMAGE ?= alpine:3.20
endif

.PHONY: bootstrap doctor tidy proto lint test verify run up down logs build docker-build docker-run

bootstrap:
	./scripts/bootstrap

doctor:
	./scripts/doctor

tidy:
	@mkdir -p "$(GOCACHE)"
	go mod tidy

proto:
	@if ! command -v buf >/dev/null 2>&1; then \
		echo "buf is not installed. Run ./scripts/bootstrap or install it via Brewfile."; \
		exit 1; \
	fi
	buf generate ./api

lint:
	@if ! command -v buf >/dev/null 2>&1; then \
		echo "buf is not installed. Run ./scripts/bootstrap or install it via Brewfile."; \
		exit 1; \
	fi
	@if ! command -v golangci-lint >/dev/null 2>&1; then \
		echo "golangci-lint is not installed. Run ./scripts/bootstrap or install it via Brewfile."; \
		exit 1; \
	fi
	@mkdir -p "$(GOCACHE)"
	@mkdir -p "$(GOLANGCI_LINT_CACHE)"
	buf lint ./api
	golangci-lint run --disable-all --enable=errcheck --enable=govet --enable=ineffassign --enable=staticcheck --enable=unused ./...

test:
	@mkdir -p "$(GOCACHE)"
	go test ./...

verify: doctor proto lint test

run:
	@mkdir -p "$(GOCACHE)"
	go run ./cmd/server

up:
	docker compose -f $(COMPOSE_FILE) up --build

down:
	docker compose -f $(COMPOSE_FILE) down --remove-orphans

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

build:
	@mkdir -p "$(GOCACHE)"
	go build -o bin/$(APP_NAME) ./cmd/server

docker-build:
	docker build --platform $(DOCKER_PLATFORM) --build-arg BUILDER_IMAGE=$(BUILDER_IMAGE) --build-arg RUNTIME_IMAGE=$(RUNTIME_IMAGE) -t $(IMAGE_REF) .

docker-run:
	docker run --rm -p $(HOST_HTTP_PORT):$(HTTP_PORT) -p $(HOST_GRPC_PORT):$(GRPC_PORT) $(IMAGE_REF)
