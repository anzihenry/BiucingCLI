APP_NAME={{SERVICE_NAME}}
IMAGE ?=$(APP_NAME)
TAG ?=latest
IMAGE_REF := $(IMAGE):$(TAG)
CONTAINER_PORT ?={{HTTP_PORT}}
HOST_PORT ?={{HTTP_PORT}}
DEV_COMPOSE_FILE ?=compose.dev.yaml
DEV_SERVICE ?=app-dev
DOCKER_VARIANT ?=alpine
DOCKER_PLATFORM ?=linux/arm64
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

.PHONY: bootstrap doctor dev dev-shell tidy lint test verify run build docker-build docker-run docker-push

bootstrap:
	docker compose -f $(DEV_COMPOSE_FILE) build $(DEV_SERVICE)

doctor:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) ./scripts/doctor

dev:
	docker compose -f $(DEV_COMPOSE_FILE) up $(DEV_SERVICE)

dev-shell:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) bash

tidy:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go mod tidy

lint:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) golangci-lint run --disable-all --enable=errcheck --enable=govet --enable=ineffassign --enable=staticcheck --enable=unused ./...

test:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go test ./...

verify: doctor lint test

run:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm --service-ports $(DEV_SERVICE)

build:
	docker compose -f $(DEV_COMPOSE_FILE) run --rm $(DEV_SERVICE) go build -o bin/$(APP_NAME) ./cmd/server

docker-build:
	docker build --platform $(DOCKER_PLATFORM) --build-arg BUILDER_IMAGE=$(BUILDER_IMAGE) --build-arg RUNTIME_IMAGE=$(RUNTIME_IMAGE) -t $(IMAGE_REF) .

docker-run:
	docker run --rm -p $(HOST_PORT):$(CONTAINER_PORT) $(IMAGE_REF)

docker-push:
	docker push $(IMAGE_REF)
